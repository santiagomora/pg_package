import core_pg_bindings.builder.schema as sb
import core_pg_bindings.builder.role as rb
from core_pg_bindings.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
from core_migrations.database import core_migrations as mgr
import core_pg_bindings as pg


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:03:40+00:00'
DEPENDS_ON: list[str] = ['create_core_migrations_package_table', 'create_core_migrations_execution_table', 'create_core_migrations_migration_table', 'create_core_migrations_execution_migration_table']
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr)\
        .function('create_migration').create('execution, text, text')\

    yield from sb.builder(mgr)\
        .function('create_execution').create('package, text, execution_action')\
        .function('register_execution_commit_hash').create('execution, text')\
        .function('register_execution_migration').create('execution, migration')

    yield from sb.builder(mgr)\
        .function('create_package').create('text, text, text')


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr)\
        .function('create_package').drop('text, text, text')

    yield from sb.builder(mgr)\
        .function('register_execution_migration').drop('execution, migration')\
        .function('register_execution_commit_hash').drop('execution, text')\
        .function('create_execution').drop('package, text, execution_action')

    yield from sb.builder(mgr)\
        .function('create_migration').drop('execution, text, text')
