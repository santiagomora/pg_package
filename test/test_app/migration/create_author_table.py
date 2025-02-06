import core_pg_bindings.builder.schema as sb
import core_pg_bindings.builder.role as rb
from core_pg_bindings.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
import sys
sys.path.append('../../')
import test_app


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-21 04:13:02+00:00'
DEPENDS_ON: list[str] = ['create_test_app_schema']
DATAFIX_NAME: Optional[str] = None


def up() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(test_app.test)\
        .sequence('author_id_sequence').create()
    yield from sb.builder(test_app.test)\
        .table('author').create()\
        .table('author').column('id').add()\
        .table('author').column('id').default().set()\
        .table('author').column('name').add()\
        .table('author').primary_key('author_pk').add()


def down() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(test_app.test)\
        .table('author').primary_key('author_pk').drop()
    yield from sb.builder(test_app.test)\
        .table('author').drop()
    yield from sb.builder(test_app.test)\
        .sequence('author_id_sequence').drop()
