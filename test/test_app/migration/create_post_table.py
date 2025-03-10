import core_pg_migrations.builder.schema as sb
import core_pg_migrations.builder.role as rb
from core_pg_migrations.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
import sys
sys.path.append('../../')
import test_app


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-21 04:50:47+00:00'
DEPENDS_ON: list[str] = ['create_test_app_schema', 'create_with_timestamps_table', 'create_authored_table']
DATAFIX_NAME: Optional[str] = None


def up() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(test_app.test)\
        .sequence('post_id_sequence').create()
    yield from sb.builder(test_app.test)\
        .enum('post_status_enum').create()\
        .enum('post_status_enum').value('published').add()\
        .enum('post_status_enum').value('waiting_approval').add()\
        .enum('post_status_enum').value('draft').add()
    yield from sb.builder(test_app.test)\
        .table('post').create()\
        .table('post').column('id').add()\
        .table('post').column('id').default().set()\
        .table('post').column('status').add()\
        .table('post').column('title').add()\
        .table('post').primary_key('title').add()


def down() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(test_app.test)\
        .table('post').primary_key('title').drop()\
        .table('post').drop()
    yield from sb.builder(test_app.test)\
        .enum('post_status_enum').drop()
    yield from sb.builder(test_app.test)\
        .sequence('post_id_sequence').drop()
