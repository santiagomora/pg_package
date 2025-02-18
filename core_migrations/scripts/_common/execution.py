import importlib
import os
import psycopg
import core_migrations
import heapq
from .config import\
    ActionConfiguration
from typing import\
    Optional,\
    Any
from .check_install import\
    check_core_migrations_installed_correctly
import core_pg_bindings.builder.schema as sb
from .prompt import\
    prompt_error
from core_pg_bindings import\
    load_functions_from_file
import math
import functools


mgr = core_migrations.database.core_migrations


class ConsistencyException(Exception):
    pass


class MigrationWrapper:
    def __init__(
        self, module, config: ActionConfiguration
    ) -> None:
        self.module = module
        self.last_executed_action: Optional[mgr.execution_action] = None
        self.config = config
        if module.DATAFIX_NAME is not None:
            with open(f'{config.DATAFIX_PATH}/{module.DATAFIX_NAME}.sql') as fns:
                load_functions_from_file(
                    self.datafix_functions, fns, config.DATAFIX_TMP_SCHEMA, None
                )

    def __repr__(self):
        return f'Migration(NAME={self.NAME}, DEPENDS_ON={self.DEPENDS_ON})'

    @property
    @functools.cache
    def NAME(self):
        return self.module.__name__.split('.')[-1]

    def __getattr__(self, name: str) -> Any:
        return getattr(self.module, name)

    def __lt__(self, other: 'MigrationWrapper') -> bool:
        return self.config.compare_migrations(self, other)

    def check_consistency(self):
        '''
        Check that sentences yielded by commit script are consistent with those
        yielded by rollback script. all the sentences in commit script must have
        their opposite in rollback script.
        '''
        errors: list[str] = []
        creating: list[str] = []
        opposite_script: mgr.execution_action.enum = self.config.opposite_action()
        for c_sentence in self.upgrade():
            if isinstance(c_sentence, sb.Create):
                creating.append(c_sentence.component.name)
            if c_sentence.component.name in creating\
                and isinstance(c_sentence, sb.Alter)\
                    and isinstance(c_sentence.change, sb.Add):
                # we are defining some type, we only need the drop constraint, we ignore following alters that add things to definition
                continue
            # if isinstance(c_sentence, sb.Function.Execute):
            #     # try to execute a function
            #     if c_sentence.component.name not in self.datafix_functions:
            #         errors.append(f'"{c_sentence}" can only execute datafix functions in {self.execution_action} script. Please associate a datafix file.')
            #         continue
            has_opposite: bool = False
            for rb_sentence in self.downgrade():
                has_opposite = has_opposite or c_sentence.is_opposite(rb_sentence)
            if not has_opposite:
                errors.append(f'"{c_sentence}" must have an opposite sentence in {opposite_script} script')
        if len(errors) > 0:
            raise ConsistencyException(f'Migration "{self.NAME}" error: {"\n".join(errors)}')


class ExecutionHeap(list[MigrationWrapper]):
    def __init__(
        self, config: ActionConfiguration
    ) -> None:
        self.config = config

    def __str__(self) -> str:
        copy: list[MigrationWrapper] = [e for e in self]
        res: str = ''
        level = 1
        ctr = 0
        while len(copy) > 0:
            migration: MigrationWrapper = heapq.heappop(copy)
            spacing = "  "*int(math.log(level, 2))
            extrapadding = "        "
            dependencies = f'{spacing}{extrapadding}'+f"\n{spacing}{extrapadding}".join(migration.DEPENDS_ON)
            res += f'{spacing}*** NAME: {migration.NAME}\n{spacing}    DEPENDS_ON: [\n{dependencies}]\n\n'
            if ctr % level == 0:
                level *= 2
                ctr = 0
            ctr += 1
        return res

    def pop(self) -> MigrationWrapper:
        return heapq.heappop(self)

    def get_migration(
        self, module_name: str, with_last_execution: bool = False
    ) -> MigrationWrapper:
        module: MigrationWrapper = MigrationWrapper(
            importlib.import_module(module_name, package=self.config.PACKAGE_NAME),
            self.config
        )
        if with_last_execution:
            with psycopg.connect(self.config.DB_DSN) as conn:
                with conn.cursor() as cursor:
                    if cursor is not None:
                        module.last_executed_action = mgr.get_last_action(
                            cursor, p_migration=mgr.get_migration_by_name(cursor, p_name=module.NAME)
                        )
        return module

    @staticmethod
    def unfold_dependencies(exec_heap: list[MigrationWrapper]) -> list[MigrationWrapper]:
        relations_matrix: list[list[int]] = [[0 for _ in range(len(exec_heap))] for _ in range(len(exec_heap))]
        names_ids: dict[str, int] = dict(zip([m.NAME for m in exec_heap], range(0, len(exec_heap))))
        for module in exec_heap:
            mod_id: int = names_ids[module.NAME]
            for dependency in module.DEPENDS_ON:
                dep_id: int = names_ids[dependency]
                relations_matrix[mod_id][dep_id] = 1

        @functools.cache
        def determine_dependencies(row: int) -> set[str]:
            if row > len(relations_matrix):
                return []
            res = set(exec_heap[row].DEPENDS_ON)
            for ix in range(0, len(relations_matrix[row])):
                if relations_matrix[row][ix]:
                    res = res.union(determine_dependencies(ix))
            return res

        for ix in range(0, len(exec_heap)):
            setattr(exec_heap[ix], '_DEPENDS_ON', determine_dependencies(ix))



def get_migration_execution_heap(
    config: ActionConfiguration, name: Optional[str] = None
) -> ExecutionHeap:
    exec_heap: ExecutionHeap = ExecutionHeap(config)
    check_core_migrations_installed_correctly(config)
    if name is None:
        # get all migration modules and see their status in the database
        for f in os.listdir(config.MIGRATION_PATH):
            migrations.push(exec_heap.get_migration(f.split('.')[0]), True)
    else:
        # get single migration module and see its status in the database
        # and the status of its dependencies
        module = exec_heap.get_migration(f.split('.')[0], True)
        migrations.push(module)
        for dependency in module.DEPENDS_ON:
            migrations.push(exec_heap.get_migration(dependency, True))
    return exec_heap


def get_migration_setup_heap(config: ActionConfiguration) -> ExecutionHeap:
    exec_heap: ExecutionHeap = ExecutionHeap(config)
    # get all migration modules and see their status in the database
    for f in os.listdir(config.MIGRATION_PATH):
        if f.startswith('__'):
            continue
        module = exec_heap.get_migration(f'{config.MIGRATION_SUBMODULE.__name__}.{f.split('.')[0]}')
        module.check_consistency()
        exec_heap.append(module)
    ExecutionHeap.unfold_dependencies(exec_heap)
    heapq.heapify(exec_heap)
    return exec_heap
