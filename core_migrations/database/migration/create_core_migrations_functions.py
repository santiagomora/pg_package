import core_pg_bindings.builder.schema as sb
import core_pg_bindings.builder.role as rb
from core_pg_bindings.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
import core_migrations.backend as mgr
import core_pg_bindings as pg


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:40+00:00'
DEPENDS_ON: list[str] = ['create_core_migrations_package_table', 'create_core_migrations_execution_table', 'create_core_migrations_migration_table', 'create_core_migrations_execution_migration_table']
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema)\
        .function('get_last_execution_action').load(from_function_path_alias='core_migrations_api').create({'p_migration': mgr.schema.migration})\
        .function('get_migration_by_name').load(from_function_path_alias='core_migrations_api').create({'p_name': pg.catalog.text})


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema)\
        .function('get_last_execution_action').drop({'p_migration': mgr.schema.migration})\
        .function('get_migration_by_name').drop({'p_name': pg.catalog.text})
