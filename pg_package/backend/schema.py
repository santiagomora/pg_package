from .types import *
import pg_definition as pg


@pg.register_function_path_alias(
    alias='mgr_api', current_file_path=__file__,
    function_path='sql/api.sql')
class mgr(pg.schema):
    # sequence
    execution_id_seq: type[execution_id_seq] = execution_id_seq
    package_id_seq: type[package_id_seq] = package_id_seq
    migration_id_seq: type[migration_id_seq] = migration_id_seq
    # enum
    execution_action: type[execution_action] = execution_action
    # table
    package: type[package] = package
    execution: type[execution] = execution
    migration: type[migration] = migration
    migration_execution: type[migration_execution] = migration_execution
