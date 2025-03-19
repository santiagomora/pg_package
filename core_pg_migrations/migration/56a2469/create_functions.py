import core_pg_migrations.builder.schema as sb
import core_pg_migrations.builder.role as rb
from core_pg_migrations.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
from typing import Any


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:40+00:00'
DEPENDS_ON: list[str] = ['create_package_table', 'create_execution_table', 'create_migration_table', 'create_snapshot_table', 'create_migration_dependency_relation_table']
DATAFIX_NAME: Optional[str] = None


def upgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .function('create_or_update_migration').create('snapshot, text, text, text, text, int8')\
        .function('create_or_update_package').create('text, text, text, text, text')\
        .function('create_or_update_snapshot').create('package, text, snapshot, snapshot')\
        .function('create_or_update_snapshot').create('int8, text, text, text')\
        .function('get_applied_snapshots').create('text')\
        .function('get_applied_snapshots').create('package')\
        .function('create_execution').create('package, execution_action')\
        .function('synchronize_migration_dependencies').create('migration, text[]')\
        .function('set_package_integrity_hash').create('package, text')\
        .function('register_execution_snapshot_relation').create('execution, snapshot, text')\
        .function('keep_snapshot_migration_ids').create('snapshot, int8[]')\
        .function('destroy_migration').create('migration')\
        .function('get_package_integrity_hash_at_snapshot').create('text, text')\
        .function('get_package_integrity_hash_at_snapshot').create('package, snapshot')\
        .function('get_snapshot_migrations').create('snapshot, execution_action')


def downgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .function('get_package_integrity_hash_at_snapshot').drop('package, snapshot')\
        .function('get_package_integrity_hash_at_snapshot').drop('text, text')\
        .function('destroy_migration').drop('migration')\
        .function('keep_snapshot_migration_ids').drop('snapshot, int8[]')\
        .function('register_execution_snapshot_relation').drop('execution, snapshot, text')\
        .function('set_package_integrity_hash').drop('package, text')\
        .function('synchronize_migration_dependencies').drop('migration, text[]')\
        .function('create_execution').drop('package, execution_action')\
        .function('get_applied_snapshots').drop('package')\
        .function('get_applied_snapshots').drop('text')\
        .function('create_or_update_snapshot').drop('int8, text, text, text')\
        .function('create_or_update_snapshot').drop('package, text, snapshot, snapshot')\
        .function('create_or_update_package').drop('text, text, text, text, text')\
        .function('create_or_update_migration').drop('snapshot, text, text, text, text, int8')\
        .function('get_snapshot_migrations').drop('snapshot, execution_action')
