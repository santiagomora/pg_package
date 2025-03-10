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
GENERATED_AT: str = '2025-03-09 07:26:37+00:00'
DEPENDS_ON: list[str] = ['create_execution_table', 'create_snapshot_table']
DATAFIX_NAME: Optional[str] = None


def upgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .table('execution_snapshot_relation').create()\
        .table('execution_snapshot_relation').column('execution_id').add()\
        .table('execution_snapshot_relation').column('snapshot_id').add()\
        .table('execution_snapshot_relation').column('integrity_hash').add()\
        .table('execution_snapshot_relation').primary_key('execution_snapshot_relation_pk').add()\
        .table('execution_snapshot_relation').unique_constraint('execution_snapshot_relation_uix').add()\
        .table('execution_snapshot_relation').foreign_key('execution_snapshot_relation_execution_id_fk').add()\
        .table('execution_snapshot_relation').foreign_key('execution_snapshot_relation_snapshot_id_fk').add()


def downgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .table('execution_snapshot_relation').foreign_key('execution_snapshot_relation_snapshot_id_fk').drop()\
        .table('execution_snapshot_relation').foreign_key('execution_snapshot_relation_execution_id_fk').drop()\
        .table('execution_snapshot_relation').unique_constraint('execution_snapshot_relation_uix').drop()\
        .table('execution_snapshot_relation').primary_key('execution_snapshot_relation_pk').drop()\
        .table('execution_snapshot_relation').column('integrity_hash').drop()\
        .table('execution_snapshot_relation').column('snapshot_id').drop()\
        .table('execution_snapshot_relation').column('execution_id').drop()\
        .table('execution_snapshot_relation').drop()
