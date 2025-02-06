import psycopg
import mgr_manager.scripts._common as cm
import argparse
import sys


# executes pip install for a package
# pip install git+git+https://github.com/username/repository.git@<commit-hash>
# its meant to be run when the script is installed in an environment
def generate_setup_script(config: cm.SetupConfiguration) -> None:
    cm.prompt_notice('The migrations will be executed by the following plan:')
    execution_heap: cm.ExecutionHeap = cm.get_migration_setup_heap(config)
    cm.prompt_notice(f'Execution plan:\n{execution_heap}')
    setup_script_transactions: list[str] = []
    with psycopg.connect(execution_heap.config.DB_DSN) as connection:
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
                        'migration_transaction', migration_name=migration.NAME,
                        migration_script=f'{";\n".join(transaction_queries)};'
                    ))
                except psycopg.Error as e:
                    cm.prompt_error(f"Migration {migration.NAME} error: {e}")
                    exit(1)
    config.save_migration_script(config.fill_template(
        'setup', setup_script_transactions="\n\n".join(setup_script_transactions)
    ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Setup Migration',
        description='Initizalizes migration tables when mgr_manager is first installed',
        epilog='')
    parser.add_argument('--commit-hash', required=True, type=str, help='Indicate a commit hash to setup')
    args: argparse.Namespace = parser.parse_args(sys.argv[1:])
    config = cm.SetupConfiguration(args)
    try:
        cm.check_mgr_manager_installed_correctly(config)
        cm.prompt_error('mgr_manager set up correctly. Exiting ...')
        exit(1)
    except cm.InstallException:
        pass
    generate_setup_script(config)
