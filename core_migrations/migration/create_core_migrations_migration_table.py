import core_pg_bindings.builder.schema as sb
import core_pg_bindings.builder.role as rb
import core_types as ct
from core_pg_bindings.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
from core_migrations.database import core_migrations as mgr


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:08+00:00'
DEPENDS_ON: list[str] = ['create_core_migrations_package_table', "create_core_migrations_execution_table"]
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr)\
        .sequence('migration_id_seq').create()

    yield from sb.builder(mgr)\
        .table('migration').create()\
        .table('migration').column('id').add()\
        .table('migration').column('id').default().set_from(ct.Undefined)\
        .table('migration').column('execution_id').add()\
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
        .table('migration').column('execution_id').drop()\
        .table('migration').column('id').default().drop()\
        .table('migration').column('id').drop()\
        .table('migration').drop()

    yield from sb.builder(mgr)\
        .sequence('migration_id_seq').drop()
