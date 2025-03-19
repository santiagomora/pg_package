import importlib
import os
import psycopg
import core_pg_migrations
import heapq
from .environment import\
    UpgradeEnvironment
from typing import\
    Optional,\
    Any
import core_pg_migrations.builder.schema as sb
from .prompt import\
    prompt_error,\
    prompt_notice
import math
import functools
from .snapshot import SnapshotList
from types import ModuleType
from core_pg_migrations.builder.common import\
    GeneratesSQLSentence


mgr = core_pg_migrations.database.core_pg_migrations


class ConsistencyException(Exception):
    pass


class DatafixWrapper:
    def __init__(self, definition: str) -> None:
        self._definition = definition


@functools.total_ordering
class MigrationWrapper:
    def __init__(
        self, module, config: UpgradeEnvironment, snapshot: SnapshotList.Node
    ) -> None:
        self.module = module
        self.last_executed_action: Optional[mgr.execution_action] = None
        self.config = config
        self.snapshot = snapshot
        self.datafix = None
        # FIXME think of datafix logic
        # if module.DATAFIX_NAME is not None:
        #     with open(f'{config.DATAFIX_PATH}/{module.DATAFIX_NAME}.sql') as fns:
        #         load_functions_from_file(
        #             self.datafix_functions, fns, config.DATAFIX_TMP_SCHEMA, None
        #         )
        #         self.datafix = 

    @property
    @functools.cache
    def NAME(self):
        name: str = self.module.__name__.split('.')[-1]
        return name.replace(f"{self.snapshot.commit_hash}_", "")

    def __getattr__(self, name: str) -> Any:
        return getattr(self.module, name)

    def __lt__(self, other: 'MigrationWrapper') -> bool:
        return self._PRIORITY < other._PRIORITY

    def check_consistency(self):
        '''
        Check that sentences yielded by commit script are consistent with those
        yielded by rollback script. all the sentences in commit script must have
        their opposite in rollback script.
        '''
        def check_sentences_consistency(
            sentence_list: list[GeneratesSQLSentence],
            opposite_sentence_list: list[GeneratesSQLSentence]
        ) -> list[str]:
            errors: list[str] = []
            creating: list[str] = []
            for c_sentence in sentence_list:
                if isinstance(c_sentence, sb.Create):
                    creating.append(c_sentence.component.name)
                has_opposite: bool = False
                for rb_sentence in opposite_sentence_list:
                    has_opposite = has_opposite or c_sentence.is_opposite(rb_sentence)
                if not has_opposite:
                    errors.append(f'"{c_sentence}" must have an opposite sentence in opposite script')
            return errors
        upgrade_sentences = [s for s in self.upgrade(self.snapshot.payload_data)]
        downgrade_sentences = [s for s in self.downgrade(self.snapshot.payload_data)]
        u_errors = check_sentences_consistency(upgrade_sentences, downgrade_sentences)
        d_errors = check_sentences_consistency(downgrade_sentences, upgrade_sentences)
        if len(u_errors) > 0:
            raise ConsistencyException(f'Migration "{self.NAME}" error: {"\n".join(u_errors)}')
        if len(d_errors) > 0:
            raise ConsistencyException(f'Migration "{self.NAME}" error: {"\n".join(d_errors)}')


class ExecutionHeap(list[MigrationWrapper]):
    def __init__(
        self, config: UpgradeEnvironment
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
            dependencies = f'{spacing}{extrapadding}'+f"\n{spacing}{extrapadding}".join(migration._DEPENDS_ON)
            res += f'{spacing}**** NAME: {migration.NAME}\n{spacing}    DEPENDS_ON: [\n{dependencies}]\n{spacing}    SNAPSHOT: {migration.snapshot.commit_hash}\n'
            if len(copy) >= 1:
                res += '\n'
            if ctr % level == 0:
                level *= 2
                ctr = 0
            ctr += 1
        return res

    def pop(self) -> MigrationWrapper:
        return heapq.heappop(self)

    @staticmethod
    def unfold_dependencies(exec_heap: list[MigrationWrapper]) -> list[MigrationWrapper]:
        relations_matrix: list[list[int]] = [[0 for _ in range(len(exec_heap))] for _ in range(len(exec_heap))]
        names_ids: dict[str, int] = dict(zip([m.NAME for m in exec_heap], range(0, len(exec_heap))))
        priorities: dict[str, int] = {name: 0 for name in names_ids}
        for module in exec_heap:
            mod_id: int = names_ids[module.NAME]
            for dependency in module.DEPENDS_ON:
                dep_id: int = names_ids[dependency]
                relations_matrix[mod_id][dep_id] = 1

        @functools.cache
        def determine_dependencies(row: int) -> set[str]:
            res = set(exec_heap[row].DEPENDS_ON)
            for ix in range(0, len(relations_matrix[row])):
                if relations_matrix[row][ix]:
                    res = res.union(determine_dependencies(ix))
            return res

        @functools.cache
        def resolve_priority(name: str) -> int:
            row = names_ids[name]
            for ix in range(0, len(relations_matrix[row])):
                if relations_matrix[row][ix]:
                    priorities[name] += 1 + resolve_priority(exec_heap[ix].NAME)
            return priorities[name]

        for ix in range(0, len(exec_heap)):
            setattr(exec_heap[ix], '_DEPENDS_ON', determine_dependencies(ix))
            setattr(exec_heap[ix], '_PRIORITY', resolve_priority(exec_heap[ix].NAME))


def get_execution_heap(
    config: UpgradeEnvironment, snapshot: SnapshotList.Node
) -> ExecutionHeap:
    exec_heap: ExecutionHeap = ExecutionHeap(config)
    for module in config.get_migration_modules(snapshot):
        wrapper = MigrationWrapper(module, config, snapshot)
        wrapper.check_consistency()
        exec_heap.append(wrapper)
    ExecutionHeap.unfold_dependencies(exec_heap)
    heapq.heapify(exec_heap)
    return exec_heap
