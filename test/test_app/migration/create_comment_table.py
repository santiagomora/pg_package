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
GENERATED_AT: str = '2024-12-21 05:47:30+00:00'
DEPENDS_ON: list[str] = ['create_test_app_schema', 'create_with_timestamps_table', 'create_authored_table']
DATAFIX_NAME: Optional[str] = None


def up() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(test_app.test)\
        .sequence('comment_id_sequence').create()
    yield from sb.builder(test_app.test)\
        .table('comment').create()\
        .table('comment').column('id').add()\
        .table('comment').column('post_id').add()\
        .table('comment').column('post_id').default().set()\
        .table('comment').primary_key('comment_pk').add()\
        .table('comment').foreign_key('comment_post_fk').add()
    yield from sb.builder(test_app.test)\
        .composite('comment_post').create()\
        .composite('comment_post').attribute('comment').add()\
        .composite('comment_post').attribute('post').add()\
        .composite('comment_post').attribute('description').add()\
        .composite('comment_post').attribute('author').add()


def down() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(test_app.test)\
        .table('comment').primary_key('comment_pk').drop()\
        .table('comment').foreign_key('comment_post_fk').drop()
    yield from sb.builder(test_app.test)\
        .sequence('comment_id_sequence').drop()
    yield from sb.builder(test_app.test)\
        .table('comment').drop()
    yield from sb.builder(test_app.test)\
        .composite('comment_post').drop()
