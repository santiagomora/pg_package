import sys
import importlib
import os
import toml
import functools
from abc import abstractmethod
import argparse
from .prompt import prompt_notice, prompt_error
import core_pg_migrations
import core_pg_migrations.database.core_pg_migrations as mgr
from core_pg_migrations.builder.common import schema_name
from datetime import datetime, timezone
from typing import Any
import json
from typing import Optional
from .snapshot import SnapshotList


class _ExecutionEnvironment:
    def __init__(
        self, package_name: str, args: argparse.Namespace
    ) -> None:
        self.args = args
        package = importlib.import_module(package_name)
        package_install_path: str = os.path.dirname(package.__file__)
        with open(f'{package_install_path}/config.toml', 'r') as f:
            self.config = toml.load(f)
        self.package = package
        self._snapshots = None

    def _obtain_snapshot_list_from_path(self, path: str, until: Optional[str] = None):
        snapshot_dict: dict[str, SnapshotList.Node] = {}
        for file_name in os.listdir(path):
            snapshot_hash: str = file_name.split('.')[0]
            with open(os.path.join(path, file_name), 'r') as f:
                snapshot_dict[snapshot_hash] = SnapshotList.Node(snapshot_hash, json.load(f), self.SCHEMA_NAME)
            if until is not None and snapshot_hash == until:
                break
        self._snapshots = SnapshotList.from_snapshot_dict(snapshot_dict)

    def fill_template(self, *, template_name: str, **kwargs) -> str:
        template: str = ''
        with open(f'{self.TEMPLATE_PATH}/{template_name}.tpl', 'r') as mgrtpl:
            template = mgrtpl.read()
        return template.format(**kwargs)

    @property
    @functools.cache
    def PACKAGE_NAME(self) -> str:
        return self.package.__name__

    @property
    @functools.cache
    def PACKAGE_PATH(self) -> str:
        return os.path.dirname(self.package.__file__)

    @property
    @functools.cache
    def MIGRATION_SUBMODULE(self) -> str:
        return importlib.import_module(self.config["migration"]["migration_submodule"], package=self.package.__name__)

    @property
    @functools.cache
    def SCHEMA_MODULE(self) -> str:
        return importlib.import_module(self.config["migration"]["schema"], package=self.package.__name__)

    @property
    @functools.cache
    def PROCEDURE_SCHEMA_MODULE(self) -> str:
        return importlib.import_module(self.config["migration"]["procedure_schema"], package=self.package.__name__)

    @property
    @functools.cache
    def SCHEMA_NAME(self) -> str:
        return schema_name(self.SCHEMA_MODULE)

    @property
    @functools.cache
    def PROCEDURE_SCHEMA_NAME(self) -> str:
        return schema_name(self.PROCEDURE_SCHEMA_MODULE)

    @property
    @functools.cache
    def MIGRATION_PATH(self) -> str:
        return self.PACKAGE_PATH + self.config["migration"]["migration_submodule"].replace('.', '/')

    @property
    @functools.cache
    def DATAFIX_PATH(self) -> str:
        return f'{os.path.dirname(self.package.__file__)}/{self.config["migration"]["datafix_directory"]}'

    @property
    @functools.cache
    def SCRIPT_OUTPUT_PATH(self) -> str:
        return f'{os.path.dirname(self.package.__file__)}/{self.config["migration"]["var_directory"]}'

    @property
    @functools.cache
    def TEMPLATE_PATH(self) -> str:
        return f'{os.path.dirname(core_pg_migrations.__file__)}/template'

    @property
    @functools.cache
    def TRACKED_BRANCH(self):
        return self.config["migration"]["tracked_branch"]

    @property
    @functools.cache
    def DRY_RUN(self):
        return self.args.dry_run

    @property
    @functools.cache
    def SEARCH_PATH(self) -> str:
        return ", ".join([self.SCHEMA_NAME, self.PROCEDURE_SCHEMA_NAME])

    @property
    @functools.cache
    def COMMIT_HASH(self) -> str:
        return os.popen(f'git merge-base {self.CURRENT_BRANCH} {self.config["migration"]["remote_name"]}/{self.config["migration"]["tracked_branch"]} | xargs git rev-parse --short').read().rstrip()

    @property
    @functools.cache
    def CURRENT_BRANCH(self) -> str:
        return os.popen('git branch --show-current').read().rstrip()

    @property
    @functools.cache
    def REMOTE_NAME(self) -> str:
        return self.config["migration"]["remote_name"]

    @property
    @functools.cache
    def SNAPSHOT_PATH(self) -> str:
        return os.path.join(self.MIGRATION_PATH, 'snapshots')

    @property
    @functools.cache
    def GENERATED_SNAPSHOTS_LIST(self) -> SnapshotList:
        if self._snapshots is None:
            self._obtain_snapshot_list_from_path(self.SNAPSHOT_PATH)
        return self._snapshots

    @property
    def LAST_GENERATED_SNAPSHOT(self) -> SnapshotList.Node:
        return self.GENERATED_SNAPSHOTS_LIST.last_node

    @property
    @abstractmethod
    def SCRIPT_NAME(self) -> None:
        pass


class UpgradeEnvironment(_ExecutionEnvironment):
    def __init__(
        self, package: str, args: argparse.Namespace, parent_environment: Optional['UpgradeEnvironment'] = None
    ) -> None:
        _ExecutionEnvironment.__init__(self, package, args)
        self._requested_snapshot = args.snapshot if args.snapshot is not None else self.LAST_GENERATED_SNAPSHOT
        self.execution_action = mgr.execution_action.enum.upgrade
        self.parent_environment = parent_environment

    def _determine_unapplied_snapshots(
        self, applied_snapshots: list[str]
    ) -> SnapshotList:
        """
        this operation consists of getting of the database the missing snapshots,
        and checking if the snapshots in the folder are all applied. it does a consistency test too
        """
        snapshot_files = [c for c in self._snapshots]
        ix = 0
        snapshot_applied = False
        while ix < len(applied_snapshots) and not snapshot_applied:
            if snapshot_files[ix].commit_hash != applied_snapshots[ix]:
                prompt_error(f'Consistency broken, please check that commit file order concurs with the one stored in database "{self.DSN}".')
                exit(1)
            if applied_snapshots[ix] == self._requested_snapshot:
                snapshot_applied = True
            ix += 1
        if snapshot_applied:
            prompt_notice(f"Snapshot \"{self._requested_snapshot}\" already applied on the database. Exiting...")
            exit(0)
        jx = ix
        while jx < len(applied_snapshots):
            if self._requested_snapshot == snapshot_files[ix].commit_hash:
                break
            jx += 1
        return self._snapshots[ix:jx]

    def opposite_action(self) -> mgr.execution_action.enum:
        return mgr.execution_action.enum.downgrade

    @staticmethod
    def compare_migrations(mgr1: 'MigrationWrapper', mgr2: 'MigrationWrapper') -> bool:
        return mgr2.NAME not in mgr1._DEPENDS_ON

    @property
    @functools.cache
    def GENERATED_SNAPSHOTS_LIST(self) -> SnapshotList:
        if self._snapshots is None:
            self._obtain_snapshot_list_from_path(self.SNAPSHOT_PATH, self.SNAPSHOT_PARAM)
        return self._snapshots

    @property
    @functools.cache
    def SNAPSHOT(self) -> SnapshotList:
        return self.LAST_GENERATED_SNAPSHOT if self.args.snapshot is None else self.args.snapshot

    @property
    def SCRIPT_NAME(self) -> str:
        now: str = datetime.now(timezone.utc).strftime("%Y_%m_%d_%H_%M_%S")
        return f'upgrade_{self.PACKAGE_NAME}_branch_{self.TRACKED_BRANCH}_at_{now}'

    @property
    @functools.cache
    def PROCEDURE_SCHEMA(self) -> str:
        return importlib.import_module(
            self.config["migration"]["procedure_schema"], package=self.package.__name__
        )

    @property
    def DSN(self) -> str:
        if self.parent_environment is not None:
            return self.parent_environment.DSN
        else:
            return self.config['migration']['dsn']

    @property
    def SNAPSHOT_PARAM(self) -> str:
        return self.args.snapshot

    @property
    def SCHEMA_DEFINITIONS(self) -> dict[str, Any]:
        return {self.SCHEMA_NAME: self.LAST_GENERATED_SNAPSHOT.payload[self.SCHEMA_NAME]}

    def get_migration_upgrade_sql_procedure_name(self, snapshot: str, migration_name: str) -> dict[str, Any]:
        return f'{self.PROCEDURE_SCHEMA_NAME}.upgrade_{snapshot}_{migration_name}'

    def get_migration_downgrade_sql_procedure_name(self, snapshot: str, migration_name: str) -> dict[str, Any]:
        return f'{self.PROCEDURE_SCHEMA_NAME}.downgrade_{snapshot}_{migration_name}'


class DowngradeEnvironment(_ExecutionEnvironment):
    def __init__(
        self, args: argparse.Namespace, dsn: str
    ) -> None:
        _ExecutionEnvironment.__init__(self, args.package, args)
        self.execution_action = mgr.execution_action.enum.downgrade
        self._dsn = dsn

    def opposite_action(self) -> mgr.execution_action.enum:
        return mgr.execution_action.enum.upgrade

    @staticmethod
    def compare_migrations(mgr1: 'MigrationWrapper', mgr2: 'MigrationWrapper') -> bool:
        return mgr2.NAME in mgr1._DEPENDS_ON

    @property
    def SCRIPT_NAME(self) -> str:
        # TODO have to configure this to work with git commits
        return f'{self.PACKAGE_NAME}_{self.TRACKED_BRANCH}_{self.COMMIT_HASH}_downgrade'

    @property
    @functools.cache
    def PROCEDURE_SCHEMA(self) -> str:
        return importlib.import_module(self.config["migration"]["procedure_schema"], package=self.package.__name__)

    @property
    @functools.cache
    def DSN(self) -> str:
        return self._dsn


class SnapshotEnvironment(_ExecutionEnvironment):
    def __init__(
        self, args: argparse.Namespace
    ) -> None:
        _ExecutionEnvironment.__init__(self, args.package, args)

    def persist_snapshot(self, definition: SnapshotList.Node):
        with open(os.path.join(self.SNAPSHOT_PATH, f'{definition.commit_hash}.json'), 'w') as f:
            f.write(json.dumps(
                definition.payload, indent=4, separators=(',', ': ', )
            ))


class GenerateEnvironment(_ExecutionEnvironment):
    def __init__(
        self, args: argparse.Namespace
    ) -> None:
        _ExecutionEnvironment.__init__(self, args.package, args)

    def get_migration_filename(self, name: str) -> str:
        return f'{self.COMMIT_HASH}_{name}.py'

    def get_datafix_filename(self, name: str) -> str:
        return f'{self.COMMIT_HASH}_{name}.sql'
