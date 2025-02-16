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
import core_migrations
from datetime import datetime, timezone


mgr = core_migrations.database.core_migrations


class _ExecutionConfiguration:
    def __init__(
        self, package_name: str, args: argparse.Namespace
    ) -> None:
        sys.path.append('/home/smora/sgs/dev/python/core/pgdriver/test/')
        self.args = args
        package = importlib.import_module(package_name)
        package_install_path: str = os.path.dirname(package.__file__)
        with open(f'{package_install_path}/config.toml', 'r') as f:
            self.config = toml.load(f)
        self.package = package

    @property
    @functools.cache
    def PACKAGE_NAME(self) -> str:
        return self.package.__name__

    @property
    @functools.cache
    def PROCEDURE_SCHEMA(self) -> str:
        return self.config["migration"]["procedure_schema"]

    @property
    @functools.cache
    def MIGRATION_SUBMODULE(self) -> str:
        return importlib.import_module(self.config["migration"]["migration_submodule"], package=self.package.__name__)

    @property
    @functools.cache
    def MIGRATION_SCHEMA(self) -> str:
        return self.config["migration"]["schema"]

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
        return f'{os.path.dirname(core_migrations.__file__)}/template'

    @property
    @functools.cache
    def DB_DSN(self) -> str:
        return self.config['migration']['database_dsn']

    @property
    @functools.cache
    def DATAFIX_TMP_SCHEMA(self) -> str:
        return f'execution_tmp_namespace_{time.time_ns()}'


    # @functools.cache
    # def register_migration_types(self):
    #     with core_pg_bindings.adapter_registry(self.DB_DSN) as ar:
    #         register_types(ar)

    @property
    @functools.cache
    def TRACKED_BRANCH(self):
        return self.config["migration"]["tracked_branch"]

    @property
    @functools.cache
    def COMMIT_HASH(self):
        return self.args.commit_hash

    @property
    @functools.cache
    def DRY_RUN(self):
        return self.args.dry_run

    @property
    @functools.cache
    def SEARCH_PATH(self) -> str:
        return self.config["migration"]["search_path"]

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

    @property
    @abstractmethod
    def SCRIPT_NAME(self) -> None:
        pass



# FIXME dont remember what this does
class GenerateConfiguration(_ExecutionConfiguration):
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
        return core_migrations.execution_action.downgrade

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
        return core_migrations.execution_action.downgrade

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
        ActionConfiguration.__init__(self, "core_migrations", args)
        self.execution_action = mgr.execution_action.enum.setup

    def opposite_action(self) -> mgr.execution_action.enum:
        return mgr.execution_action.enum.downgrade

    @staticmethod
    def compare_migrations(mgr1: 'MigrationWrapper', mgr2: 'MigrationWrapper') -> bool:
        return mgr2.NAME not in mgr1._DEPENDS_ON

    @property
    def SCRIPT_NAME(self) -> str:
        now: str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f'setup_{self.COMMIT_HASH}_{now}'
