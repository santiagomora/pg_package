import core_pg_bindings.builder.schema as sb
import core_pg_bindings.builder.role as rb
from core_pg_bindings.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
import core_types as ct
from typing import Any


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:08+00:00'
DEPENDS_ON: list[str] = ['create_core_pg_migrations_schema']
DATAFIX_NAME: Optional[str] = None
SNAPSHOT: str = '4d72aca8a7ebb5ea378335e26c5e9434492d8121'


def upgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .sequence('package_id_seq').create()

    yield from sb.builder(snapshot)\
        .table('package').create()\
        .table('package').column('id').add()\
        .table('package').column('id').default().set_from(ct.Undefined)\
        .table('package').column('name').add()\
        .table('package').column('branch_name').add()\
        .table('package').column('current_snapshot').add()\
        .table('package').column('last_updated_at').add()\
        .table('package').primary_key('package_pk').add()\
        .table('package').unique_constraint('package_unique_name_constraint').add()


def downgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .table('package').unique_constraint('package_unique_name_constraint').drop()\
        .table('package').primary_key('package_pk').drop()\
        .table('package').column('last_updated_at').drop()\
        .table('package').column('current_snapshot').drop()\
        .table('package').column('branch_name').drop()\
        .table('package').column('name').drop()\
        .table('package').column('id').default().drop()\
        .table('package').column('id').drop()\
        .table('package').drop()

    yield from sb.builder(snapshot)\
        .sequence('package_id_seq').drop()
