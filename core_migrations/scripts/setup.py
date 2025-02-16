import psycopg
import core_migrations.scripts._common as cm
import argparse
import sys
from datetime import datetime, timezone
from psycopg import sql
from core_pg_bindings.builder.common import identifier


# executes pip install for a package
# pip install git+git+https://github.com/username/repository.git@<commit-hash>
# its meant to be run when the script is installed in an environment
def generate_setup_script(config: cm.SetupConfiguration) -> None:
    cm.prompt_notice('The migrations will be executed by the following plan:')
    execution_heap: cm.ExecutionHeap = cm.get_migration_setup_heap(config)
    cm.prompt_notice(f'EXECUTION PLAN:\n\n{execution_heap}')
    setup_script_transactions: list[str] = []
    with psycopg.connect(config.DB_DSN) as connection:
        with psycopg.ClientCursor(connection) as cursor:
            cm.prompt_notice('Generating migration script.')
            transaction_queries: list[str] = []
            while len(execution_heap) > 0:
                migration: cm.MigrationWrapper = execution_heap.pop()
                cm.prompt_notice(f'Generating migration: {migration.NAME}')
                transaction_queries = []
                try:
                    for sentence in migration.upgrade():
                        sql_sentence, identifiers, params = sentence.sql_sentence_params()
                        transaction_queries.append(cursor.mogrify(
                            psycopg.sql.SQL(sql_sentence).format(*identifiers).as_string(connection),
                            params
                        ))
                    setup_script_transactions.append(config.fill_template(
                        'required_migration_transaction', migration_name=migration.NAME,
                        migration_script=f'{"\n".join(transaction_queries)}'
                    ))
                except psycopg.Error as e:
                    cm.prompt_error(f"Migration {migration.NAME} error: {e}")
                    exit(1)
    now: str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    setup_proc_name: str = f'setup_{now}_{config.COMMIT_HASH}'
    cm_schema = config.MIGRATION_SCHEMA
    cm_proc_schema = config.PROCEDURE_SCHEMA
    cm.prompt_notice(f'Generated migration script, applying to the database')
    script: str = config.fill_template(
        'setup', setup_script_transactions="\n\n".join(setup_script_transactions),
        procedure_name="{}", procedure_schema="{}"
    )
    with psycopg.connect(config.DB_DSN) as connection:
        if config.DRY_RUN:
            cm.prompt_notice(sql.SQL(script).format(identifier(setup_proc_name), sql.Literal(cm_schema)).as_string(connection))
            exit(0)
        connection.add_notice_handler(cm.log_notice)
        try:
            with connection.cursor() as cursor:
                with connection.transaction():
                    cm.prompt_notice(f'Creating "{cm_proc_schema}" schema')
                    cursor.execute(sql.SQL('CREATE SCHEMA IF NOT EXISTS {};').format(identifier(cm_proc_schema)))
                    cm.prompt_notice(f'Creating "{setup_proc_name}" procedure in "{cm_proc_schema}" schema')
                    cursor.execute(sql.SQL("SET search_path to {};").format(identifier(cm_proc_schema)))
                    cursor.execute(sql.SQL(script).format(identifier(setup_proc_name), sql.Literal(cm_schema)))
                    cm.prompt_notice(f'Calling "{setup_proc_name}" procedure')
                    cursor.execute(sql.SQL('CALL {}();').format(identifier(setup_proc_name)))
        except Exception as e:
            cm.prompt_notice(f'Failed to apply migration script "{setup_proc_name}"')
            cm.prompt_error(str(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Setup Migration',
        description='Initizalizes migration tables when core_migrations is first installed',
        epilog='')
    parser.add_argument('--commit-hash', required=True, type=str, help='Indicate a commit hash to setup')
    parser.add_argument('--dry-run', action='store_true', help='Output the setup script to command interface without applying it')
    args: argparse.Namespace = parser.parse_args(sys.argv[1:])
    config = cm.SetupConfiguration(args)
    try:
        cm.check_core_migrations_installed_correctly(config)
        cm.prompt_error('core_migrations set up correctly. Exiting ...')
        exit(1)
    except cm.InstallException:
        pass
    generate_setup_script(config)
