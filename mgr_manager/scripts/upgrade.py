import argparse
import sys
from ._common.config import\
    UpgradeConfiguration
from ._common.check_install import\
    InstallException
from ._common.execution import\
    get_migration_setup_heap,\
    get_migration_execution_heap,\
    MigrationWrapper,\
    ExecutionHeap
from ._common.prompt import\
    prompt_yes_no,\
    prompt_notice,\
    prompt_error,\
    prompt_sql_command
import psycopg


# upgrades a package version to a certain revision
# executes pip install for a package
# pip install git+git+https://github.com/username/repository.git@<commit-hash>


def execute_commit_script(config: UpgradeConfiguration) -> None:
    if config.migration is None:
        prompt_notice(f'Commiting pending migrations for package "{config.package.__name__}"')
    else:
        prompt_notice(f'Commiting migration {config.migration} for package "{config.package.__name__}"')
    execution_heap: ExecutionHeap = get_migration_execution_heap(config)
    prompt_notice('The migrations will be executed by the following plan:')
    prompt_notice(f'Execution plan:\n{execution_heap}')
    with psycopg.connect(execution_heap.config.DB_DSN) as connection:
        with connection.cursor() as cursor:
            while len(execution_heap) > 0:
                migration: MigrationWrapper = execution_heap.pop()
                prompt_notice(f'Executing migration: {migration.NAME}')
                for sentence in migration.commit():
                    print(sentence)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Commit Migration',
        description='Generates database migrations for ordered database changes and datafixes',
        epilog='')

    parser.add_argument('--package', help='Indicate a package to run the migrations upon', required=True)
    parser.add_argument('--dry-run', help='Print the sql sentences in screen', action='store_true')
    parser.add_argument('--migration', type=str, help='The name of the migration to be commited')

    args: argparse.Namespace = parser.parse_args(sys.argv[1:])
    config = UpgradeConfiguration(args)
    base_install_error: bool = False
    try:
        execute_commit_script(config)
    except InstallException as e:
        prompt_error(str(e))
        base_install_error = True
    if base_install_error:
        execute_install_script(config)
