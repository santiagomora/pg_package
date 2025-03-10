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
DEPENDS_ON: list[str] = ['create_snapshot_table']
DATAFIX_NAME: Optional[str] = None


def upgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .sequence('execution_id_seq').create()

    yield from sb.builder(snapshot)\
        .enum('execution_action').create()

    yield from sb.builder(snapshot)\
        .table('execution').create()\
        .table('execution').column('id').add()\
        .table('execution').column('package_id').add()\
        .table('execution').column('action').add()\
        .table('execution').column('created_at').add()\
        .table('execution').primary_key('execution_pk').add()\
        .table('execution').foreign_key('execution_package_id_fk').add()


def downgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .table('execution').foreign_key('execution_package_id_fk').drop()\
        .table('execution').primary_key('execution_pk').drop()\
        .table('execution').column('created_at').drop()\
        .table('execution').column('action').drop()\
        .table('execution').column('package_id').drop()\
        .table('execution').column('id').drop()\
        .table('execution').drop()

    yield from sb.builder(snapshot)\
        .enum('execution_action').drop()

    yield from sb.builder(snapshot)\
        .sequence('execution_id_seq').drop()
