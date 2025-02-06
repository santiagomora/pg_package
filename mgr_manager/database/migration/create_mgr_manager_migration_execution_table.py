import pg_definition.builder.schema as sb
import pg_definition.builder.role as rb
from pg_definition.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
import mgr_manager.backend as mgr


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:08+00:00'
DEPENDS_ON: list[str] = ['create_mgr_migration_table', 'create_mgr_execution_table']
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema)\
        .table('migration_execution').create()\
        .table('migration_execution').column('execution_id').add()\
        .table('migration_execution').column('migration_id').add()\
        .table('migration_execution').primary_key('migration_execution_pk').add()\
        .table('migration_execution').foreign_key('migration_execution_execution_id_fk').add()\
        .table('migration_execution').foreign_key('migration_execution_migration_id_fk').add()


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema)\
        .table('migration_execution').foreign_key('migration_execution_migration_id_fk').drop()\
        .table('migration_execution').foreign_key('migration_execution_execution_id_fk').drop()\
        .table('migration_execution').primary_key('migration_execution_pk').drop()\
        .table('migration_execution').column('migration_id').drop()\
        .table('migration_execution').column('execution_id').drop()\
        .table('migration_execution').drop()
