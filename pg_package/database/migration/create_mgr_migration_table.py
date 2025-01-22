import pg_definition.builder.schema as sb
import pg_definition.builder.role as rb
from pg_definition.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
from pg_package.backend import mgr


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:08+00:00'
DEPENDS_ON: list[str] = ['create_mgr_package_table']
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr)\
        .sequence('migration_id_seq').create()

    yield from sb.builder(mgr)\
        .table('migration').create()\
        .table('migration').column('id').add()\
        .table('migration').column('package_id').add()\
        .table('migration').column('name').add()\
        .table('migration').column('datafix_name').add()\
        .table('migration').column('created_at').add()\
        .table('migration').primary_key('migration_pk').add()\
        .table('migration').unique_constraint('migration_unique_name_constraint').add()\
        .table('migration').foreign_key('migration_package_id_fk').add()


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr)\
        .table('migration').unique_constraint('migration_unique_name_constraint').drop()\
        .table('migration').foreign_key('migration_package_id_fk').drop()\
        .table('migration').primary_key('migration_pk').drop()\
        .table('migration').column('created_at').drop()\
        .table('migration').column('datafix_name').drop()\
        .table('migration').column('name').drop()\
        .table('migration').column('package_id').drop()\
        .table('migration').column('id').drop()\
        .table('migration').drop()

    yield from sb.builder(mgr)\
        .sequence('migration_id_seq').drop()
