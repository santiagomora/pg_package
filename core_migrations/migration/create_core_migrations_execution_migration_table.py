import core_pg_bindings.builder.schema as sb
import core_pg_bindings.builder.role as rb
from core_pg_bindings.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
from core_migrations.database import core_migrations as mgr


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:08+00:00'
DEPENDS_ON: list[str] = ['create_core_migrations_migration_table', 'create_core_migrations_execution_table']
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr)\
        .table('execution_migration').create()\
        .table('execution_migration').column('execution_id').add()\
        .table('execution_migration').column('migration_id').add()\
        .table('execution_migration').primary_key('execution_migration_pk').add()\
        .table('execution_migration').foreign_key('execution_migration_execution_id_fk').add()\
        .table('execution_migration').foreign_key('execution_migration_migration_id_fk').add()


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr)\
        .table('execution_migration').foreign_key('execution_migration_migration_id_fk').drop()\
        .table('execution_migration').foreign_key('execution_migration_execution_id_fk').drop()\
        .table('execution_migration').primary_key('execution_migration_pk').drop()\
        .table('execution_migration').column('migration_id').drop()\
        .table('execution_migration').column('execution_id').drop()\
        .table('execution_migration').drop()
