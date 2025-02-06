import psycopg
import mgr_manager.backend as mgr
from .config import\
    ActionConfiguration


class InstallException(Exception):
    pass


def check_mgr_manager_schema_exists(cursor) -> None:
    cursor.execute(
        'SELECT EXISTS(\
            SELECT schema_name FROM information_schema.schemata\
            WHERE schema_name = %s\
        )',
        (mgr.schema.__name__, )
    )
    exists: bool = cursor.fetchone()[0]
    if not exists:
        raise InstallException(f'Schema "{mgr.schema.__name__}" does not exist in database. Check that "install_schema" migration is commited')


def check_mgr_manager_tables_exist(cursor) -> None:
    tables: list[str] = [table.__name__ for table in mgr.schema.tables]
    cursor.execute(
        'SELECT NOT EXISTS(\
            SELECT req FROM unnest(%s::text[]) req\
            LEFT JOIN information_schema.tables tbs\
            ON tbs.table_name = req\
            WHERE tbs.table_schema = %s AND tbs.table_name IS NULL\
        )',
        (tables, mgr.schema.__name__, )
    )
    exists: bool = cursor.fetchone()[0]
    if exists:
        raise InstallException(f'There is missing tables in schema "{mgr.schema.__name__}". Check that "install_tables" migration is commited "{tables}"')


def check_mgr_manager_functions_exist(cursor) -> None:
    functions: tuple[str, ...] = [function.__name__ for function in mgr.schema.functions]
    cursor.execute(
        'SELECT NOT EXISTS(\
            SELECT req FROM unnest(%s::text[]) req\
            LEFT JOIN pg_catalog.pg_proc fn\
            ON fn.proname = req\
            WHERE fn.pronamespace = %s AND fn.proname IS NULL\
        )'
        (functions, mgr.schema.__name__, )
    )
    exists: bool = cursor.fetchone()[0]
    if not exists:
        raise InstallException(f'There is missing functions in schema "{mgr.schema.__name__}". Check that "install_functions" migration is commited: "{functions}"')


def check_mgr_manager_installed_correctly(config: ActionConfiguration) -> None:
    with psycopg.connect(config.DB_DSN) as conn:
        with conn.cursor() as cursor:
            check_mgr_manager_schema_exists(cursor)
            check_mgr_manager_tables_exist(cursor)
            check_mgr_manager_functions_exist(cursor)
