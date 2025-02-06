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
DEPENDS_ON: list[str] = ['create_mgr_schema']
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema)\
        .sequence('package_id_seq').create()

    yield from sb.builder(mgr.schema)\
        .table('package').create()\
        .table('package').column('id').add()\
        .table('package').column('name').add()\
        .table('package').column('version').add()\
        .table('package').column('branch_name').add()\
        .table('package').column('last_commit_hash').add()\
        .table('package').column('last_updated_at').add()\
        .table('package').primary_key('package_pk').add()\
        .table('package').unique_constraint('package_unique_name_constraint').add()


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema)\
        .table('package').unique_constraint('package_unique_name_constraint').drop()\
        .table('package').primary_key('package_pk').drop()\
        .table('package').column('last_updated_at').drop()\
        .table('package').column('last_commit_hash').drop()\
        .table('package').column('branch_name').drop()\
        .table('package').column('version').drop()\
        .table('package').column('name').drop()\
        .table('package').column('id').drop()\
        .table('package').drop()

    yield from sb.builder(mgr.schema)\
        .sequence('package_id_seq').drop()
