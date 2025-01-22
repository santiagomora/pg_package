import pg_definition.builder.schema as sb
import pg_definition.builder.role as rb
from pg_definition.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
import sys
sys.path.append('../../')
import test_app



# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-21 04:31:27+00:00'
DEPENDS_ON: list[str] = ['create_author_table', 'create_test_app_schema']
DATAFIX_NAME: Optional[str] = None


def up() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(test_app.test)\
        .table('authored').create()\
        .table('authored').column('author_id').add()\
        .table('authored').column('content').add()\
        .table('authored').foreign_key('authorable_author_fk').add()


def down() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(test_app.test)\
        .table('authored').foreign_key('authorable_author_fk').drop()\
        .table('authored').drop()
