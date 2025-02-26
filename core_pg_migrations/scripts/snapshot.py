import psycopg
import core_pg_migrations.backend.scripts as cm
import argparse
import sys
from datetime import datetime, timezone
from psycopg import sql
from core_pg_bindings.builder.common import identifier
from core_pg_migrations.backend import SetupParameters
import core_pg_migrations.backend.cpp.backend_wrapper as cmw
import os
import core_pg_bindings as pg
from typing import Any
import json
from types import ModuleType
from core_pg_bindings.common.inspection import schema_name


def serialize(definition: dict[str, Any]):
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
            ser[key] = serialize(value)
        elif isinstance(value, tuple) or isinstance(value, list):
            ser[key] = [{
                    'schema': schema_name(value._postgres_definition['schema']),
                    'type': value.__name__
                } if isinstance(v, type) else str(v) for v in value]
        elif isinstance(value, pg.sequence.nextval):
            ser[key] = {
                'type': 'sequence_nextval', 'name': value.seq.__name__,
                'schema': schema_name(value.seq._postgres_definition['schema'])
            }
        elif value is pg.Undefined:
            continue
        elif isinstance(value, pg.Operand):
            ser[key] = {'type': 'operand', 'value': str(value), 'name': value.name}
        elif isinstance(value, bool):
            ser[key] = value
        elif value is None:
            ser[key] = None
        else:
            ser[key] = str(value)
    return ser


# executes pip install for a package
# pip install git+git+https://github.com/username/repository.git@<commit-hash>
# its meant to be run when the script is installed in an environment
def generate_snapshot(config: cm.SnapshotConfiguration) -> None:
    definitions_ser = {}
    for name, definition in config.MIGRATION_SCHEMA.__dict__.items():
        if not hasattr(definition, '_postgres_definition'):
            continue
        pg_def = definition._postgres_definition
        definitions_ser[name] = serialize(pg_def)
    os.makedirs(config.SNAPSHOT_PATH, exist_ok=True)
    with open(os.path.join(config.SNAPSHOT_PATH, f'{config.COMMIT_HASH}.json'), 'w') as f:
        f.write(json.dumps(
            {schema_name(config.MIGRATION_SCHEMA): definitions_ser},
            indent=4,
            separators=(',', ': ', )
        ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Package snapshot',
        description='Generates a snapshot of the current state of a certain schema and bind it to the latest commit hash. The snapshot will be use by migrations to generate the migration script.',
        epilog='')
    parser.add_argument('--package', required=True, type=str, help='Indicate which package will the snapshot belong to')
    parser.add_argument('--commit-hash', required=True, type=str, help='Indicate the commit hash of the snapshot')
    parser.add_argument('--dry-run', action='store_true', help='Output the snaptshot to console instead of generating the file')
    commit_hash: str = os.popen('git rev-parse HEAD').read().rstrip()
    args: argparse.Namespace = parser.parse_args(sys.argv[1:] + ['--commit-hash', commit_hash])
    config = cm.SnapshotConfiguration(args)
    generate_snapshot(config)
