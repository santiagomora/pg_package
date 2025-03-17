from typing import Any
from core_pg_migrations.backend import package, migration, snapshot
from .environment import UpgradeEnvironment, DowngradeEnvironment
from .snapshot import SnapshotList
from .execution import ExecutionHeap
import core_pg_migrations.backend.cpp.backend_wrapper as cmbw
import core_pg_bindings.pg_catalog as pg
import psycopg
from .prompt import prompt_error, prompt_notice
import core_pg_migrations.database.core_pg_migrations as mgr
from .execution import MigrationWrapper, get_execution_heap


def get_migration_upgrade_script(
    cursor: psycopg.ClientCursor, config: UpgradeEnvironment, migration: MigrationWrapper,
    snapshot: SnapshotList.Node
) -> tuple[str, str, str, str]:
    # prompt_notice(f'Generating migration upgrade script: {migration.NAME}')
    queries: list[str] = []
    procedure_name: str = config.get_migration_upgrade_sql_procedure_name(snapshot.commit_hash, migration.NAME)
    try:
        for sentence in migration.upgrade(snapshot.payload_data):
            sql_sentence, identifiers, params = sentence.sql_sentence_params()
            sql_sentence = psycopg.sql.SQL(sql_sentence)
            if len(identifiers) > 0:
                sql_sentence = sql_sentence.format(*identifiers)
            if len(params) > 0:
                queries.append(cursor.mogrify(sql_sentence.as_string(cursor.connection), params))
            else:
                queries.append(cursor.mogrify(sql_sentence.as_string(cursor.connection)))
        script: str = config.fill_template(
            template_name='migration_sql_body', name=migration.NAME, search_path=config.SEARCH_PATH,
            script=f'{"\n".join(queries)}', procedure_name=procedure_name,
            action=str(mgr.execution_action.enum.upgrade).split('.')[-1]
        )
        return script, procedure_name
    except psycopg.Error as e:
        prompt_error(f"Migration \"{migration.NAME}\" upgrade script  error: {e}", e)
        exit(1)


def get_migration_downgrade_script(
    cursor: psycopg.ClientCursor, config: UpgradeEnvironment, migration: MigrationWrapper,
    snapshot: SnapshotList.Node
) -> tuple[str, str, str, str]:
    # prompt_notice(f'Generating migration downgrade script: {migration.NAME}')
    queries: list[str] = []
    procedure_name: str = config.get_migration_downgrade_sql_procedure_name(snapshot.commit_hash, migration.NAME)
    try:
        for sentence in migration.downgrade(snapshot.payload_data):
            sql_sentence, identifiers, params = sentence.sql_sentence_params()
            queries.append(cursor.mogrify(
                psycopg.sql.SQL(sql_sentence).format(*identifiers).as_string(cursor.connection),
                params
            ))
        script: str = config.fill_template(
            template_name='migration_sql_body', name=migration.NAME, search_path=config.SEARCH_PATH,
            script=f'{"\n".join(queries)}', procedure_name=procedure_name,
            action=str(mgr.execution_action.enum.downgrade).split('.')[-1]
        )
        return script, procedure_name
    except psycopg.Error as e:
        prompt_error(f"Migration \"{migration.NAME}\" downgrade script error: {e}")
        exit(1)


def get_snapshot_migrations(
    config: UpgradeEnvironment, snapshot: SnapshotList.Node
) -> list[migration]:
    execution_heap: ExecutionHeap = get_execution_heap(config, snapshot)
    res: list[migration] = []
    with psycopg.connect(config.DSN) as connection:
        with psycopg.ClientCursor(connection) as cursor:
            prompt_notice(f'Generating migration script for package "{config.PACKAGE_NAME}" at snapshot "{snapshot.commit_hash}".')
            transaction_queries: list[str] = []
            while len(execution_heap) > 0:
                migration_wrapper: MigrationWrapper = execution_heap.pop()
                upgrade_procedure, upgrade_procedure_name = get_migration_upgrade_script(
                    cursor, config, migration_wrapper, snapshot
                )
                downgrade_procedure, downgrade_procedure_name = get_migration_downgrade_script(
                    cursor, config, migration_wrapper, snapshot
                )
                res.append(migration(
                    name=migration_wrapper.NAME, datafix_name=migration_wrapper.DATAFIX_NAME,
                    upgrade_procedure=upgrade_procedure, downgrade_procedure=downgrade_procedure,
                    upgrade_procedure_name=upgrade_procedure_name, downgrade_procedure_name=downgrade_procedure_name,
                    dependencies=migration_wrapper.DEPENDS_ON
                ))
    return res


def get_snapshot_as_backend_type(
    config: UpgradeEnvironment, node: SnapshotList.Node
) -> snapshot:
    previous_hash: Optional[str] = getattr(node.previous_node, 'commit_hash', None)
    next_hash: Optional[str] = getattr(node.next_node, 'commit_hash', None)
    return snapshot(
        hash=node.commit_hash, previous_hash=previous_hash, next_hash=next_hash,
        migrations=get_snapshot_migrations(config, node), payload=str(node.payload_data)
    )


def get_current_state(config: UpgradeEnvironment) -> tuple[package, pg.int8]:
    snapshots: list[snapshot] = [get_snapshot_as_backend_type(config, node) for node in config.GENERATED_SNAPSHOTS_LIST]
    current_packate_state: package = package(
        name=config.PACKAGE_NAME, schema_name=config.SCHEMA_NAME, remote_name=config.REMOTE_NAME,
        tracked_branch_name=config.TRACKED_BRANCH, procedure_schema_name=config.PROCEDURE_SCHEMA_NAME,
        snapshots=snapshots
    )
    return current_packate_state


def upgrade_to_package_snapshot_hash(
    config: UpgradeEnvironment, _package: package, starting_at: str
) -> None:
    cmbw.upgrade_to_package_snapshot_hash(config.DSN, _package, starting_at)


def get_unapplied_package_snapshots_for_upgrade_dry_run(
    config: UpgradeEnvironment, _package: package, starting_at: str
) -> list[snapshot]:
    return cmbw.get_unapplied_package_snapshots_for_upgrade_dry_run(config.DSN, _package, starting_at)


def downgrade_to_package_snapshot_hash(
    config: DowngradeEnvironment, _package: package, ending_at: str
) -> None:
    cmbw.downgrade_to_package_snapshot_hash(config.DSN, _package, ending_at)


def get_applied_package_snapshots_for_downgrade_dry_run(
    config: DowngradeEnvironment, _package: package, ending_at: str
) -> list[snapshot]:
    return cmbw.get_applied_package_snapshots_for_downgrade_dry_run(config.DSN, _package, ending_at)
