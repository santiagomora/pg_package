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
        .function('create_migration').create('snapshot, text, text, text, text')\
        .function('create_package').create('text, text, text, text, text')\
        .function('create_snapshot').create('package, text, snapshot, snapshot')\
        .function('create_snapshot').create('int8, text, text, text')\
        .function('get_applied_snapshots').create('text')\
        .function('get_applied_snapshots').create('package')\
        .function('create_execution').create('package, execution_action')\
        .function('register_migration_dependencies').create('migration, text[]')\
        .function('set_package_integrity_hash').create('package, text')\
        .function('register_execution_snapshot_relation').create('execution, snapshot, text')


def downgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .function('register_migration_dependencies').drop('migration, text[]')\
        .function('set_package_integrity_hash').drop('package, text')\
        .function('register_execution_snapshot_relation').drop('execution, snapshot, text')\
        .function('create_migration').drop('snapshot, text, text, text, text')\
        .function('create_package').drop('text, text, text, text, text')\
        .function('create_snapshot').drop('package, text, snapshot, snapshot')\
        .function('create_snapshot').drop('int8, text, text, text')\
        .function('get_applied_snapshots').drop('text')\
        .function('get_applied_snapshots').drop('package')\
        .function('create_execution').drop('package, execution_action')
