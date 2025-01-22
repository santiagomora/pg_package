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
GENERATED_AT: str = '2024-12-21 06:19:07+00:00'
DEPENDS_ON: list[str] = ['create_authored_table', 'create_test_app_schema', 'create_author_table.', 'create_with_timestamps_table', 'create_comment_table', 'create_post_table', 'create_test_app_functions']
DATAFIX_NAME: Optional[str] = None


def up() -> Generator[GeneratesSQLSentence, None, None]:
    # Creates all overloads
    yield from sb.builder(test_app.test).load_functions(
        ('get_post_by_id',
         'get_author_by_id',
         'get_post_comments',
         'get_author_posts',
         'create_post',
         'create_comment',
         'as_comment_post',),
        from_function_path_alias='test_functions')\
        .function('get_post_by_id').create_or_replace()\
        .function('get_author_by_id').create_or_replace()\
        .function('get_post_comments').create_or_replace()\
        .function('get_author_posts').create_or_replace()\
        .function('create_post').create_or_replace()\
        .function('create_comment').create_or_replace()\
        .function('as_comment_post').create_or_replace()


def down() -> Generator[GeneratesSQLSentence, None, None]:
    pass
