import core_pg_migrations.builder.schema as sb
import core_pg_migrations.builder.role as rb
import core_types as ct
from core_pg_migrations.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional,\
    Any


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2025-03-04 02:01:37+00:00'
DEPENDS_ON: list[str] = ["create_package_table"]
DATAFIX_NAME: Optional[str] = None


def upgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .sequence('snapshot_id_seq').create()

    yield from sb.builder(snapshot)\
        .table('snapshot').create()\
        .table('snapshot').column('id').add()\
        .table('snapshot').column('package_id').add()\
        .table('snapshot').column('parent_id').add()\
        .table('snapshot').column('child_id').add()\
        .table('snapshot').column('commit_hash').add()\
        .table('snapshot').column('created_at').add()\
        .table('snapshot').primary_key('snapshot_pk').add()\
        .table('snapshot').unique_constraint('snapshot_unique_commit_hash_constraint').add()\
        .table('snapshot').foreign_key('snapshot_child_id_fk').add()\
        .table('snapshot').foreign_key('snapshot_parent_id_fk').add()\
        .table('snapshot').foreign_key('snapshot_package_id_fk').add()


def downgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .table('snapshot').foreign_key('snapshot_package_id_fk').drop()\
        .table('snapshot').foreign_key('snapshot_parent_id_fk').drop()\
        .table('snapshot').foreign_key('snapshot_child_id_fk').drop()\
        .table('snapshot').unique_constraint('snapshot_unique_commit_hash_constraint').drop()\
        .table('snapshot').primary_key('snapshot_pk').drop()\
        .table('snapshot').column('created_at').drop()\
        .table('snapshot').column('commit_hash').drop()\
        .table('snapshot').column('child_id').drop()\
        .table('snapshot').column('parent_id').drop()\
        .table('snapshot').column('package_id').drop()\
        .table('snapshot').column('id').drop()\
        .table('snapshot').drop()

    yield from sb.builder(snapshot)\
        .sequence('snapshot_id_seq').drop()
