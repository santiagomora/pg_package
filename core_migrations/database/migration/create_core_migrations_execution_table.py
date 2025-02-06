import core_pg_bindings.builder.schema as sb
import core_pg_bindings.builder.role as rb
from core_pg_bindings.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
import core_migrations.backend as mgr


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:08+00:00'
DEPENDS_ON: list[str] = ['create_core_migrations_package_table']
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema)\
        .sequence('execution_id_seq').create()

    yield from sb.builder(mgr.schema)\
        .enum('execution_action').create()\
        .enum('execution_action').value('upgrade').add()\
        .enum('execution_action').value('downgrade').add()\
        .enum('execution_action').value('install').add()

    yield from sb.builder(mgr.schema)\
        .table('execution').create()\
        .table('execution').column('id').add()\
        .table('execution').column('package_id').add()\
        .table('execution').column('created_at').add()\
        .table('execution').column('commit_hash').add()\
        .table('execution').column('action').add()\
        .table('execution').primary_key('execution_pk').add()\
        .table('execution').foreign_key('execution_package_id_fk').add()


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema)\
        .table('execution').foreign_key('execution_package_id_fk').drop()\
        .table('execution').primary_key('execution_pk').drop()\
        .table('execution').column('action').drop()\
        .table('execution').column('commit_hash').drop()\
        .table('execution').column('created_at').drop()\
        .table('execution').column('package_id').drop()\
        .table('execution').column('id').drop()\
        .table('execution').drop()

    yield from sb.builder(mgr.schema)\
        .enum('execution_action').drop()

    yield from sb.builder(mgr.schema)\
        .sequence('execution_id_seq').drop()
