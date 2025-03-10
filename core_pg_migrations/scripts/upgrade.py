import core_pg_migrations.backend.scripts as cm
import argparse
import sys
from core_pg_migrations.backend.scripts.package import get_current_state, snapshot, migration, apply_package_snapshots_until_hash


def apply_package_snapshots_until_hash_dry_run(_snapshot: snapshot) -> None:
    cm.prompt_notice(f'SNAPSHOT "{_snapshot.hash}" DRY RUN. SHOWING MIGRATIONS...')
    for m in _snapshot.migrations:
        cm.prompt_notice(f"""
****NAME: {m.name} DATAFIX_NAME: {m.datafix_name}
****UPGRADE_PROCEDURE_NAME: {m.upgrade_procedure_name} SQL:\n{m.upgrade_procedure}
****DOWNGRADE_PROCEDURE_NAME: {m.downgrade_procedure_name} SQL:\n{m.downgrade_procedure}
""")


def run(
    script_arguments: argparse.Namespace
) -> None:
    if script_arguments.using_package is not None:
        cm.prompt_notice(f'Upgrading package "{script_arguments.package}" to snapshot "{script_arguments.snapshot}" using "{script_arguments.using_package}" configuration...')
        config = cm.UpgradeEnvironment(script_arguments.package, script_arguments, cm.UpgradeEnvironment(script_arguments.using_package, script_arguments))
    else:
        cm.prompt_notice(f'Upgrading package "{script_arguments.package}" to snapshot "{script_arguments.snapshot}". Checking if "core_pg_migrations" is up to date...')
        package_config = cm.UpgradeEnvironment(script_arguments.package, script_arguments)
        migrations_config = cm.UpgradeEnvironment("core_pg_migrations", script_arguments, package_config)
        check_core_pg_migrations_is_up_to_date(migrations_config)
        config = package_config
    current_packate_state = get_current_state(config)
    if config.DRY_RUN:
        cm.prompt_notice(f"""
UPGRADE MIGRATION SCRIPT DRY RUN:
PACKAGE:\t{config.PACKAGE_NAME} 
CONNECTION:\t{config.DSN}""")
        # for _snapshot in current_packate_state.snapshots[unapplied_begins_at:]:
        #     apply_package_snapshots_until_hash_dry_run(_snapshot)
    else:
        apply_package_snapshots_until_hash(config, current_packate_state, config.SNAPSHOT)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Upgrade To Snapshot',
        description="""Runs migrations to upgrade schema to a certain snapshot.
There is two different concepts involved in the migration process.
    1. Snapshot: represents all the database definitions at a given point of time
    2. Migration: represents all the operations required to take the database to a given snapshot.
some considerations:
    1. To upgrade to a certain snapshot, the last action needs to be downgraded in the database or not exist. This means that in order to add a new migration to the applied snapshot (or to change an existing migration), the user needs to downgrade it first. it doesnt matter if its the last or an earlier snapshot. Consider this when working in multiple environments.

    2. Once the upgrade script is applied it also stores the donwgrade script so when calling downgrade that script is called, not the script in the migration files. this is to preserve database integrity. Only when the script is upgraded again the downgrade script will change.

    3. Each migration will be stored as a procedure (downgrade and upgrade) in the database, upgrade is the action of calling each of those scripts and raise an exception if one of them fails
""",
        epilog=''
    )
    parser.add_argument('--dry-run', action='store_true', help='Output the setup script to command interface without applying it')
    parser.add_argument('--snapshot', type=str, help='Upgrade to a single unapplied snapshot. If not present, then upgrade to the latest snapshot available. If present, attempt to upgrade incrementally')
    parser.add_argument('--package', required=True, type=str, help='Indicate which package to upgrade')
    parser.add_argument('--using-package', type=str, help='Only valid if [PACKAGE] is "core_pg_migrations". Upgrade core_pg_migrations using [USING_PACKAGE] database connection')
    #
    script_arguments = parser.parse_args(sys.argv[1:])
    if script_arguments.using_package is None and script_arguments.package == 'core_pg_migrations':
        cm.prompt_error('Incorrect parameters for upgrade script. If [PACKAGE] is "core_pg_migrations", then [USING_PACKAGE] must be present')
        exit(1)
    if script_arguments.using_package is not None and script_arguments.package != 'core_pg_migrations':
        cm.prompt_error('Incorrect parameters for upgrade script. If [USING_PACKAGE] is present, then [PACKAGE] must be "core_pg_migrations"')
        exit(1)
    run(script_arguments)
