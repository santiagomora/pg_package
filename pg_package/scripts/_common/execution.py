import importlib
import os
import psycopg
from ...backend import mgr
import heapq
from .config import\
    ActionConfiguration
from typing import\
    Optional,\
    Any
from .check_install import\
    check_pg_package_installed_correctly
import pg_definition.builder.schema as sb
from .prompt import\
    prompt_error
from pg_definition.builder.common import\
    load_functions_from_file
import math


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
            self.datafix_functions = load_functions_from_file(
                f'{config.DATAFIX_PATH}/{module.DATAFIX_NAME}.sql',
                config.DATAFIX_TMP_SCHEMA, None
            )

    def __repr__(self):
        return f'Migration({self.NAME}, DEPENDS_ON={self.DEPENDS_ON})'

    @property
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
        opposite_script: mgr.execution_action = self.config.opposite_action()
        for c_sentence in self.upgrade():
            if isinstance(c_sentence, sb.Create):
                creating.append(c_sentence.component.name)
            if c_sentence.component.name in creating\
                and isinstance(c_sentence, sb.Alter)\
                    and isinstance(c_sentence.change, sb.Add):
                # we are defining some type, we only need the drop constraint, we ignore following alters that add things to definition
                continue
            if isinstance(c_sentence, sb.Function.Execute):
                # try to execute a function
                if c_sentence.component.name not in self.datafix_functions:
                    errors.append(f'"{c_sentence}" can only execute datafix functions in {self.execution_action} script. Please associate a datafix file.')
                    continue
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

    def pop(self):
        return heapq.heappop(self)

    def push(self, item: MigrationWrapper):
        heapq.heappush(self, item)

    def __str__(self) -> None:
        copy: list[MigrationWrapper] = [e for e in self]
        res: str = ''
        level = 1
        ctr = 0
        while len(copy) > 0:
            migration: MigrationWrapper = heapq.heappop(copy)
            dependencies: str = f'({", ".join(migration.DEPENDS_ON)})' if len(migration.DEPENDS_ON) > 0 else ''
            res += f'{"  "*int(math.log(level, 2))}{repr(migration)}\n'
            if ctr % level == 0:
                level *= 2
                ctr = 0
            ctr += 1
        return res

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


def get_migration_execution_heap(
    config: ActionConfiguration, name: Optional[str] = None
) -> ExecutionHeap:
    exec_heap: ExecutionHeap = ExecutionHeap(config)
    check_pg_package_installed_correctly(config)
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
        exec_heap.push(module)
    return exec_heap
