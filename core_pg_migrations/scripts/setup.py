import psycopg
import core_pg_migrations.scripts._common as cm
import argparse
import sys
from datetime import datetime, timezone
from psycopg import sql
from core_pg_bindings.builder.common import identifier
from core_pg_migrations.backend import SetupParameters
import core_pg_migrations.backend.cpp.backend_wrapper as cmw


# executes pip install for a package
# pip install git+git+https://github.com/username/repository.git@<commit-hash>
# its meant to be run when the script is installed in an environment
def generate_setup_script(config: cm.SetupConfiguration) -> None:
    cm.prompt_notice('The migrations will be executed by the following plan:')
    execution_heap: cm.ExecutionHeap = cm.get_migration_setup_heap(config)
    cm.prompt_notice(f'EXECUTION PLAN:\n\n{execution_heap}')
    setup_script_transactions: list[str] = []
    migrations = []
    with psycopg.connect(config.DB_DSN) as connection:
        with psycopg.ClientCursor(connection) as cursor:
            cm.prompt_notice('Generating migration script.')
            transaction_queries: list[str] = []
            while len(execution_heap) > 0:
                migration: cm.MigrationWrapper = execution_heap.pop()
                cm.prompt_notice(f'Generating migration: {migration.NAME}')
                migrations.append(migration.NAME)
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
        script: str = config.fill_template(
            'setup', setup_script_transactions="\n\n".join(setup_script_transactions),
            procedure_name="{}", procedure_schema="{}"
        )
        script = sql.SQL(script).format(identifier(config.SCRIPT_NAME), sql.Literal(config.MIGRATION_SCHEMA))\
            .as_string(connection)
    commits = ['test', 'commit 1', 'commit 2']
    if config.DRY_RUN:
        cm.prompt_notice(f'Migration script dry run:\
                             \nCONNECTION:\n\t{config.DB_DSN}\
                             \nSCRIPT NAME:\n\t{config.SCRIPT_NAME}\
                             \nCOMMITS:\n\t{"\n\t".join(commits)}\
                             \nMIGRATIONS:\n\t{"\n\t".join(migrations)}\
                             \nSCRIPT:\n{script}')
    else:
        cmw.setup_core_pg_migrations_in_database(SetupParameters(
            script_name=config.SCRIPT_NAME,
            commit_hashes_sequence=commits,
            migration_names=migrations,
            proc_schema=config.PROCEDURE_SCHEMA,
            tracked_branch=config.TRACKED_BRANCH,
            package_name='core_pg_migrations',
            setup_script=script
        ), config.DB_DSN)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Setup Migration',
        description='Initizalizes migration tables when core_pg_migrations is first installed',
        epilog='')
    parser.add_argument('--commit-hash', required=True, type=str, help='Indicate a commit hash to setup')
    parser.add_argument('--dry-run', action='store_true', help='Output the setup script to command interface without applying it')
    args: argparse.Namespace = parser.parse_args(sys.argv[1:])
    config = cm.SetupConfiguration(args)
    try:
        cm.check_core_pg_migrations_installed_correctly(config)
        cm.prompt_error('core_pg_migrations set up correctly. Exiting ...')
        exit(1)
    except cm.InstallException:
        pass
    generate_setup_script(config)
