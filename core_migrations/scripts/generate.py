import os
import argparse
import sys
import re
from datetime import datetime,\
    timezone
from typing import\
    Optional
from ._common.config import\
    GenerateConfiguration
from ._common.prompt import\
    prompt_notice


CONFIG: Optional[GenerateConfiguration] = None


def valid_package_submodule_name(name: str) -> str:
    return re.sub(r'[^A-Za-z\.0-9]', '_', name).strip()


def create_migration_from_template(
    *, config: argparse.Namespace, dest_path: str, template_path: str,
    datafix_name: Optional[str]
) -> Optional[str]:
    if config.migration is None:
        return None

    NAME: str = valid_package_submodule_name(config.migration)
    FILENAME: str = f'{NAME}.py'

    """
    The migration is presumed to apply changes on the extensions database objects, tables and
    so on. these changes must be reflected in the pg objects defined by the extension.
    """
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    PATH: str = f'{dest_path}/{FILENAME}'

    if os.path.exists(PATH):
        prompt_error(f'There is already a migration with name "{NAME}" at destination path "{dest_path}"')
        return False

    core_migrations_template: str = ''
    with open(f'{template_path}/migration_body.tpl', 'r') as mgrtpl:
        core_migrations_template = mgrtpl.read()

    DEPENDS = []
    if config.depends_on:
        DEPENDS = [valid_package_submodule_name(name) for name in config.depends_on.split(',')]

    errors: bool = False
    for name in DEPENDS:
        depends_filename = f'{name}.py'
        if not os.path.exists(f'{dest_path}/{depends_filename}'):
            prompt_error(f'Unmet dependency. "{depends_filename}" must be a migration in path "{dest_path}"')
            errors = True

    if errors:
        return None

    with open(PATH, 'w') as mgrdest:
        generated_at: str = datetime.now(timezone.utc).isoformat(' ', 'seconds')
        mgrdest.write(core_migrations_template.format(
            depends_on=DEPENDS, generated_at=f"'{generated_at}'",
            datafix_name=f"'{datafix_name}'" if datafix_name is not None else None
        ))
    prompt_notice(f'Migration "{NAME}" generated at path "{PATH}"')
    return NAME


def create_datafix_from_template(
    *, config: argparse.Namespace, dest_path: str, template_path: str
) -> Optional[str]:
    if config.datafix is None and config.with_datafix is None:
        return None
    if config.with_datafix is not None:
        NAME: str = valid_package_submodule_name(config.with_datafix)
    else:
        NAME: str = valid_package_submodule_name(config.datafix)

    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

    FILENAME = f'{NAME}.sql'
    PATH: str = f'{dest_path}/{FILENAME}'

    if os.path.exists(PATH):
        prompt_error(f'There is already a datafix with name "{NAME}" at destination path "{dest_path}"')
        return None

    df_template: str = ''
    with open(f'{template_path}/datafix.tpl', 'r') as dftpl:
        df_template = dftpl.read()

    with open(PATH, 'w') as dfdest:
        generated_at: str = datetime.now(timezone.utc).isoformat(' ', 'seconds')
        dfdest.write(df_template.format(datafix_name=NAME, generated_at=generated_at))
    prompt_notice(f'Datafix "{NAME}" generated at path "{PATH}"')
    return NAME


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Migration Generator',
        description='Generates database migrations for ordered database changes and datafixes',
        epilog='')

    parser.add_argument('--package', help='Indicate a package to run the migrations upon', required=True)
    group_exc = parser.add_mutually_exclusive_group(required=True)
    group_exc.add_argument('--datafix', type=str, help='Generate a datafix file with the given name. The name must be unique amongst existing datafixes')
    group_exc.add_argument('--migration', type=str, help='Generate a migration file with the given name. The name must be unique amongst existing migrations')

    core_migrations_group = parser.add_argument_group('Migration Options')
    core_migrations_group_exc = core_migrations_group.add_mutually_exclusive_group()
    core_migrations_group_exc.add_argument('--with-datafix', help='Generate migration, datafix and bind with them together')
    core_migrations_group.add_argument('--depends-on', type=str, help='Indicate a comma separated list of existing migration names that this migration depends on')

    df_group = parser.add_argument_group('Datafix Options')

    args = parser.parse_args(sys.argv[1:])

    CONFIG = GenerateConfiguration(args.package, args)

    # will have to look in the package installation directory to see these paths. Each extension package will have its own migration directory
    dfx_name: Optional[str] = create_datafix_from_template(
        config=args, dest_path=CONFIG.DATAFIX_PATH,
        template_path=CONFIG.TEMPLATE_PATH
    )
    core_migrations_name: Optional[str] = create_migration_from_template(
        config=args, dest_path=CONFIG.MIGRATION_PATH,
        template_path=CONFIG.TEMPLATE_PATH,
        datafix_name=dfx_name
    )
    if dfx_name is None and core_migrations_name is None:
        prompt_error('ERROR')
        exit(1)
