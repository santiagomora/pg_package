import pg_definition.builder.schema as sb
import pg_definition.builder.role as rb
from pg_definition.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
import mgr_manager.backend as mgr
import pg_definition as pg


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:40+00:00'
DEPENDS_ON: list[str] = ['create_mgr_package_table', 'create_mgr_execution_table', 'create_mgr_migration_table', 'create_mgr_migration_execution_table']
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema)\
        .function('get_last_execution_action').load(from_function_path_alias='mgr_api').create({'p_migration': mgr.migration})\
        .function('get_migration_by_name').load(from_function_path_alias='mgr_api').create({'p_name': pg.text})


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema)\
        .function('get_last_execution_action').drop({'p_migration': mgr.migration})\
        .function('get_migration_by_name').drop({'p_name': pg.text})
