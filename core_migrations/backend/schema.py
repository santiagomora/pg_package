import core_pg_bindings as pg
from .types import\
    execution_id_seq,\
    package_id_seq,\
    migration_id_seq,\
    execution_action,\
    package,\
    execution,\
    migration,\
    execution_migration,\
    execution_commit_hash


@pg.schema.register_function_path_alias(
    alias='core_migrations_api', current_file_path=__file__,
    function_path='sql/api.sql')
class core_migrations(pg.schema):
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
    execution_migration: type[execution_migration] = execution_migration
    execution_commit_hash: type[execution_commit_hash] = execution_commit_hash
