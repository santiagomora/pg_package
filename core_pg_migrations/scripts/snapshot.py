import core_pg_migrations.backend.scripts.environment as cm
import core_pg_migrations.backend.cpp.backend_wrapper as cmbw
import argparse
import sys
import os
import core_pg_bindings as pg
from typing import Any
import json
from types import ModuleType
from core_pg_migrations.builder.common import schema_name


# git log -n 1 --pretty=format:%H create_core_pg_migrations_migration_table.py
def _serialize(definition: dict[str, Any]):
    ser: dict[str, Any] = {}
    ctr = 0
    for key, value in definition.items():
        if not isinstance(key, str):
            ser[ctr] = str(value).split('.')[-1]
            ctr += 1
        elif isinstance(value, ModuleType):
            ser[key] = schema_name(value)
        elif isinstance(value, type):
            ser[key] = {
                'schema': schema_name(value._postgres_definition['schema']),
                'type': value.__name__
            }
        elif isinstance(value, dict):
            ser[key] = _serialize(value)
        elif isinstance(value, tuple) or isinstance(value, list):
            ser[key] = [{
                    'schema': schema_name(v._postgres_definition['schema']),
                    'type': v.__name__
                } if isinstance(v, type) else str(v) for v in value]
        elif isinstance(value, pg.sequence.nextval):
            ser[key] = {
                'type': 'sequence_nextval', 'name': value.seq.__name__,
                'schema': schema_name(value.seq._postgres_definition['schema'])
            }
        elif value is pg.Undefined:
            continue
        elif isinstance(value, pg.ArithmeticOperand):
            ser[key] = {'type': 'operand', 'value': str(value), 'name': value.name}
        elif isinstance(value, pg.ArithmeticOperation):
            ser[key] = {'type': 'operation', 'value': str(value), 'name': value.name}
        elif isinstance(value, pg.LogicOperand):
            ser[key] = {'type': 'logic-operation', 'value': str(value), 'name': value.name}
        elif isinstance(value, bool):
            ser[key] = value
        elif value is None:
            ser[key] = None
        else:
            ser[key] = str(value)
    return ser


def run(config: cm.SnapshotEnvironment) -> None:
    definitions_ser = {}
    for name, definition in config.SCHEMA_MODULE.__dict__.items():
        if not hasattr(definition, '_postgres_definition'):
            continue
        pg_def = definition._postgres_definition
        definitions_ser[name] = _serialize(pg_def)
    os.makedirs(config.SNAPSHOT_PATH, exist_ok=True)
    cm.prompt_notice(f'Generating snapshot for package {config.PACKAGE_NAME} at commit "{config.COMMIT_HASH}" tracking branch "{config.TRACKED_BRANCH}" in branch "{config.CURRENT_BRANCH}"...')
    # Get the snapshot
    cm.prompt_notice(f'Checking if package has snapshots...')
    last_snapshot = config.LAST_SNAPSHOT
    if last_snapshot is None:
        # 1. last snapshot is none, then user is generating first package snapshot
        cm.prompt_notice(f'No snapshots detected. Generating first snapshot at "{config.COMMIT_HASH}"...')
        new_snapshot = cm.SnapshotList.Node(
            config.COMMIT_HASH, {
                'previous_snapshot': None, 'next_snapshot': None,
                config.SCHEMA_NAME: definitions_ser
            }, config.SCHEMA_NAME
        )
        last_snapshot = new_snapshot
    elif last_snapshot.commit_hash == config.COMMIT_HASH:
        # 2. last snapshot is the same as the genrated snapshot, we need to update the payload
        cm.prompt_notice(f'Detected snapshot "{last_snapshot.commit_hash}" is the same as last execution. Updating last contents...')
        last_snapshot.payload[config.SCHEMA_NAME] = definitions_ser
    else:
        # 3. last snapshot is different than new snapshot, this means the package has snapshots but not of the commit hash
        cm.prompt_notice(f'Detected last snapshot at "{last_snapshot.commit_hash}". Generating next snapshot "{new_snapshot.commit_hash}"...')
        new_snapshot = cm.SnapshotList.Node(
            config.COMMIT_HASH, {
                'previous_snapshot': None, 'next_snapshot': None,
                config.SCHEMA_NAME: definitions_ser
            }, config.SCHEMA_NAME
        )
        last_snapshot.next_node = new_snapshot
        new_snapshot.previous_node = last_snapshot
        config.persist_snapshot(new_snapshot)
    cm.prompt_notice(f'Storing "{last_snapshot.commit_hash}" contents...')
    config.persist_snapshot(last_snapshot)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Package snapshot',
        description='Generates a snapshot of the current state of a certain schema and bind it to the latest commit hash. The snapshot will be use by migrations to generate the migration script.',
        epilog='')
    parser.add_argument('--package', required=True, type=str, help='Indicate which package will the snapshot belong to')
    parser.add_argument('--dry-run', action='store_true', help='Output the snaptshot to console instead of generating the file')
    args: argparse.Namespace = parser.parse_args(sys.argv[1:])
    config = cm.SnapshotEnvironment(args)
    run(config)
