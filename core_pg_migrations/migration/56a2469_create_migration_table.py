import core_pg_migrations.builder.schema as sb
import core_pg_migrations.builder.role as rb
import core_types as ct
from core_pg_migrations.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
from typing import Any


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:08+00:00'
DEPENDS_ON: list[str] = ['create_package_table', "create_snapshot_table"]
DATAFIX_NAME: Optional[str] = None


def upgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .sequence('migration_id_seq').create()

    yield from sb.builder(snapshot)\
        .table('migration').create()\
        .table('migration').column('id').add()\
        .table('migration').column('snapshot_id').add()\
        .table('migration').column('name').add()\
        .table('migration').column('datafix_name').add()\
        .table('migration').column('upgrade_script_name').add()\
        .table('migration').column('downgrade_script_name').add()\
        .table('migration').primary_key('migration_pk').add()\
        .table('migration').unique_constraint('migration_unique_name_constraint').add()\
        .table('migration').unique_constraint('migration_unique_datafix_name_constraint').add()\
        .table('migration').foreign_key('migration_snapshot_id_fk').add()


def downgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .table('migration').foreign_key('migration_snapshot_id_fk').drop()\
        .table('migration').unique_constraint('migration_unique_datafix_name_constraint').drop()\
        .table('migration').unique_constraint('migration_unique_name_constraint').drop()\
        .table('migration').primary_key('migration_pk').drop()\
        .table('migration').column('downgrade_script_name').drop()\
        .table('migration').column('upgrade_script_name').drop()\
        .table('migration').column('datafix_name').drop()\
        .table('migration').column('name').drop()\
        .table('migration').column('snapshot_id').drop()\
        .table('migration').column('id').drop()\
        .table('migration').drop()

    yield from sb.builder(snapshot)\
        .sequence('migration_id_seq').drop()
