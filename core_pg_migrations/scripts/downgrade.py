import core_pg_migrations.backend.scripts as cm
import argparse
import sys
from core_pg_migrations.backend.scripts.package import get_current_state, snapshot, get_applied_package_snapshots_for_downgrade_dry_run, downgrade_to_package_snapshot_hash


def downgrade_to_package_snapshot_hash_dry_run(_snapshot: snapshot) -> None:
    cm.prompt_notice(f'SNAPSHOT "{_snapshot.hash}" DRY RUN. SHOWING MIGRATIONS...')
    for m in _snapshot.migrations:
        cm.prompt_notice(f"""
****NAME: {m.name} DATAFIX_NAME: {m.datafix_name}
****UPGRADE_PROCEDURE_NAME: {m.downgrade_procedure_name} SQL:\n{m.downgrade_procedure}
****DOWNGRADE_PROCEDURE_NAME: {m.downgrade_procedure_name} SQL:\n{m.downgrade_procedure}
""")


def run(
    script_arguments: argparse.Namespace
) -> None:
    if script_arguments.using_package is not None:
        cm.prompt_notice(f'Downgrading package "{script_arguments.package}" to snapshot "{script_arguments.snapshot}" using "{script_arguments.using_package}" configuration...')
        package_config = cm.DowngradeEnvironment(script_arguments.using_package, script_arguments, None)
        config = cm.DowngradeEnvironment(script_arguments.package, script_arguments, script_arguments.snapshot, package_config)
    else:
        cm.prompt_notice(f'Downgrading package "{script_arguments.package}" to snapshot "{script_arguments.snapshot}". Checking if "core_pg_migrations" is up to date...')
        package_config = cm.DowngradeEnvironment(script_arguments.package, script_arguments, script_arguments.snapshot)
        migrations_config = cm.DowngradeEnvironment("core_pg_migrations", script_arguments, None, package_config)
        core_pg_migrations_unapplied = get_unapplied_package_snapshots_for_upgrade_dry_run(migrations_config, get_current_state(migrations_config), migrations_config.LAST_SNAPSHOT.commit_hash)
        if len(core_pg_migrations_unapplied) > 0:
            cm.prompt_error('Package "core_pg_migrations" is not up to date...')
            exit(1)
        else:
            cm.prompt_notice(f'Package "core_pg_migrations" is up to date...')
        config = package_config
    current_package_state = get_current_state(config)
    if config.DRY_RUN:
        cm.prompt_notice(f"""
UPGRADE MIGRATION SCRIPT DRY RUN:
PACKAGE:\t{config.PACKAGE_NAME} 
CONNECTION:\t{config.DSN}""")
        for _snapshot in get_applied_package_snapshots_for_downgrade_dry_run(config, current_package_state, config.LAST_SNAPSHOT.commit_hash):
            downgrade_to_package_snapshot_hash_dry_run(_snapshot)
    else:
        cm.prompt_notice(f'Downgrading using database connection "{config.DSN}"...')
        downgrade_to_package_snapshot_hash(config, current_package_state, config.LAST_SNAPSHOT.commit_hash)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Downgrade To Snapshot',
        description="""Runs downgrade migrations to revert schema to a certain snapshot.
The snapshot is already stored in the database so this will call downgrade migration for all snapshots executed after the indicated snapshot.
""",
        epilog=''
    )
    parser.add_argument('--dry-run', action='store_true', help='Output the setup script to command interface without applying it')
    parser.add_argument('--snapshot', required=True, type=str, help='downgrade to snapshot inclusive.')
    parser.add_argument('--package', required=True, type=str, help='Indicate which package to downgrade')
    parser.add_argument('--using-package', type=str, help='Only valid if [PACKAGE] is "core_pg_migrations". Upgrade core_pg_migrations using [USING_PACKAGE] database connection')
    #
    script_arguments = parser.parse_args(sys.argv[1:])
    if script_arguments.using_package is None and script_arguments.package == 'core_pg_migrations':
        cm.prompt_error('Incorrect parameters for downgrade script. If [PACKAGE] is "core_pg_migrations", then [USING_PACKAGE] must be present')
        exit(1)
    if script_arguments.using_package is not None and script_arguments.package != 'core_pg_migrations':
        cm.prompt_error('Incorrect parameters for downgrade script. If [USING_PACKAGE] is present, then [PACKAGE] must be "core_pg_migrations"')
        exit(1)
    run(script_arguments)
