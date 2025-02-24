import core_pg_bindings.builder.schema as sb
import core_pg_bindings.builder.role as rb
from core_pg_migrations.database import core_pg_migrations as mgr
from core_pg_bindings.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2025-02-06 19:19:17+00:00'
DEPENDS_ON: list[str] = ['create_core_pg_migrations_execution_table']
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr)\
        .table('execution_commit_hash').create()\
        .table('execution_commit_hash').column('execution_id').add()\
        .table('execution_commit_hash').column('commit_hash').add()\
        .table('execution_commit_hash').primary_key('execution_commit_hash_pk').add()\
        .table('execution_commit_hash').foreign_key('execution_commit_hash_execution_id_fk').add()


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr)\
        .table('execution_commit_hash').foreign_key('execution_commit_hash_execution_id_fk').drop()\
        .table('execution_commit_hash').primary_key('execution_commit_hash_pk').drop()\
        .table('execution_commit_hash').column('commit_hash').drop()\
        .table('execution_commit_hash').column('execution_id').drop()\
        .table('execution_commit_hash').drop()
