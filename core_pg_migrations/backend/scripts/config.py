import sys
import importlib
import os
import toml
import functools
import time
from abc import\
    abstractmethod
import argparse
from .prompt import\
    prompt_notice
import core_pg_migrations
from datetime import datetime, timezone
from core_pg_migrations.backend import SetupParameters
from typing import Any
import json


mgr = core_pg_migrations.database.core_pg_migrations


class _ExecutionConfiguration:
    def __init__(
        self, package_name: str, args: argparse.Namespace
    ) -> None:
        # sys.path.append('/home/smora/sgs/dev/python/core/core_pg_bindings/')
        self.args = args
        package = importlib.import_module(package_name)
        package_install_path: str = os.path.dirname(package.__file__)
        with open(f'{package_install_path}/config.toml', 'r') as f:
            self.config = toml.load(f)
        self.package = package
        self.schema_package = None
        self.snapshots: dict[str, Any] = {
            name.split('.')[0]: None for name in os.listdir(self.SNAPSHOT_PATH)
        }

    @property
    @functools.cache
    def PACKAGE_NAME(self) -> str:
        return self.package.__name__

    @property
    @functools.cache
    def MIGRATION_SUBMODULE(self) -> str:
        return importlib.import_module(self.config["migration"]["migration_submodule"], package=self.package.__name__)

    @property
    @functools.cache
    def MIGRATION_SCHEMA(self) -> str:
        return importlib.import_module(self.config["migration"]["schema"], package=self.package.__name__)

    @property
    @functools.cache
    def MIGRATION_PATH(self) -> str:
        return os.path.dirname(importlib.import_module(self.config["migration"]["migration_submodule"], package=self.package.__name__).__file__)

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
    def DB_DSN(self) -> str:
        return self.config['migration']['database_dsn']

    @property
    @functools.cache
    def DATAFIX_TMP_SCHEMA(self) -> str:
        return f'execution_tmp_namespace_{time.time_ns()}'

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
        return self.config["migration"]["search_path"]

    @property
    @functools.cache
    def SNAPSHOT_PATH(self) -> str:
        return os.path.join(self.MIGRATION_PATH, 'snapshots')

    def fill_template(self, name: str, **kwargs) -> str:
        template: str = ''
        with open(f'{self.TEMPLATE_PATH}/{name}.tpl', 'r') as mgrtpl:
            template = mgrtpl.read()
        return template.format(**kwargs)

    def save_migration_script(self, script: str) -> None:
        destination_file: str = f'{self.SCRIPT_OUTPUT_PATH}/{self.SCRIPT_OUTPUT_NAME}.sql'
        prompt_notice(f'Saving migration script to: "{destination_file}"')
        with open(destination_file, 'w') as f:
            f.write(script)

    @functools.cache
    def get_snapshot(self, name: str) -> dict[str, Any]:
        if name not in self.snapshots:
            raise FileNotFoundError
        with open(os.path.join(self.SNAPSHOT_PATH, f'{name}.json')) as f:
            self.snapshots[name] = json.load(f)
        return self.snapshots[name]

    @property
    @abstractmethod
    def SCRIPT_NAME(self) -> None:
        pass


class ActionConfiguration(_ExecutionConfiguration):
    @abstractmethod
    def opposite_action(self) -> mgr.execution_action.enum:
        pass

    @staticmethod
    @abstractmethod
    def compare_migrations(mgr1: 'MigrationWrapper', mgr2: 'MigrationWrapper') -> bool:
        pass


class DowngradeConfiguration(ActionConfiguration):
    def __init__(
        self, args: argparse.Namespace
    ) -> None:
        ActionConfiguration.__init__(self, args.package, args)
        self.execution_action = mgr.execution_action.enum.downgrade

    def opposite_action(self) -> mgr.execution_action.enum:
        return core_pg_migrations.execution_action.downgrade

    @staticmethod
    def compare_migrations(mgr1: 'MigrationWrapper', mgr2: 'MigrationWrapper') -> bool:
        return mgr2.NAME in mgr1._DEPENDS_ON

    @property
    def SCRIPT_NAME(self) -> str:
        # TODO have to configure this to work with git commits
        return f'{self.PACKAGE_NAME}_{self.TRACKED_BRANCH}_{self.COMMIT_HASH}_downgrade'


class UpgradeConfiguration(ActionConfiguration):
    def __init__(
        self, args: argparse.Namespace
    ) -> None:
        ActionConfiguration.__init__(self, args.package, args)
        self.migration = args.migration
        self.dry_run = args.dry_run
        self.execution_action = mgr.execution_action.enum.upgrade

    def opposite_action(self) -> mgr.execution_action.enum:
        return core_pg_migrations.execution_action.downgrade

    @staticmethod
    def compare_migrations(mgr1: 'MigrationWrapper', mgr2: 'MigrationWrapper') -> bool:
        return mgr2.NAME not in mgr1._DEPENDS_ON

    @property
    def SCRIPT_NAME(self) -> str:
        # TODO have to configure this to work with git commits
        return f'{self.PACKAGE_NAME}_{self.TRACKED_BRANCH}_{self.COMMIT_HASH}_upgrade'


class SetupConfiguration(ActionConfiguration):
    def __init__(
        self, args: argparse.Namespace
    ) -> None:
        ActionConfiguration.__init__(self, "core_pg_migrations", args)
        self.execution_action = mgr.execution_action.enum.setup
        self.procedure_package = None

    def opposite_action(self) -> mgr.execution_action.enum:
        return mgr.execution_action.enum.downgrade

    @staticmethod
    def compare_migrations(mgr1: 'MigrationWrapper', mgr2: 'MigrationWrapper') -> bool:
        return mgr2.NAME not in mgr1._DEPENDS_ON

    @property
    def SCRIPT_NAME(self) -> str:
        now: str = datetime.now(timezone.utc).strftime("%Y_%m_%d_%H_%M_%S")
        return f'setup_{now}'

    @property
    @functools.cache
    def PROCEDURE_SCHEMA(self) -> str:
        return importlib.import_module(self.config["migration"]["procedure_schema"], package=self.package.__name__)


class SnapshotConfiguration(ActionConfiguration):
    def __init__(
        self, args: argparse.Namespace
    ) -> None:
        ActionConfiguration.__init__(self, args.package, args)

    @property
    @functools.cache
    def COMMIT_HASH(self):
        return self.args.commit_hash
