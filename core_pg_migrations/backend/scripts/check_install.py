import psycopg
from core_pg_migrations.database import core_pg_migrations as mgr
from .config import\
    ActionConfiguration


# FIXME we should see if all the types declared in the last snapshot exist in the database
tables = [
    mgr.package,
    mgr.execution,
    mgr.migration,
    mgr.execution_migration]


functions = [
    mgr.create_execution,
    mgr.register_execution_migration,
    mgr.create_migration,
    mgr.create_package]


class InstallException(Exception):
    pass


def check_core_pg_migrations_schema_exists(cursor) -> None:
    cursor.execute(
        'SELECT EXISTS(\
            SELECT schema_name FROM information_schema.schemata\
            WHERE schema_name = %s\
        )',
        (mgr.__name__, )
    )
    exists: bool = cursor.fetchone()[0]
    if not exists:
        raise InstallException(f'Schema "{mgr.__name__}" does not exist in database. Check that "install_schema" migration is commited')


def check_core_pg_migrations_tables_exist(cursor) -> None:
    tables: list[str] = [table.__name__ for table in tables]
    cursor.execute(
        'SELECT NOT EXISTS(\
            SELECT req FROM unnest(%s::text[]) req\
            LEFT JOIN information_schema.tables tbs\
            ON tbs.table_name = req\
            WHERE tbs.table_schema = %s AND tbs.table_name IS NULL\
        )',
        (tables, mgr.__name__, )
    )
    exists: bool = cursor.fetchone()[0]
    if exists:
        raise InstallException(f'There is missing tables in schema "{mgr.__name__}". Check that "install_tables" migration is commited "{tables}"')


def check_core_pg_migrations_functions_exist(cursor) -> None:
    functions: list[str, ...] = [function.__name__ for function in functions]
    cursor.execute(
        'SELECT NOT EXISTS(\
            SELECT req FROM unnest(%s::text[]) req\
            LEFT JOIN pg_catalog.pg_proc fn\
            ON fn.proname = req\
            WHERE fn.pronamespace = %s AND fn.proname IS NULL\
        )'
        (functions, mgr.__name__, )
    )
    exists: bool = cursor.fetchone()[0]
    if not exists:
        raise InstallException(f'There is missing functions in schema "{mgr.__name__}". Check that "install_functions" migration is commited: "{functions}"')


def check_core_pg_migrations_installed_correctly(config: ActionConfiguration) -> None:
    with psycopg.connect(config.DB_DSN) as conn:
        with conn.cursor() as cursor:
            check_core_pg_migrations_schema_exists(cursor)
            check_core_pg_migrations_tables_exist(cursor)
            check_core_pg_migrations_functions_exist(cursor)
