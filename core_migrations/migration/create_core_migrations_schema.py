import core_pg_bindings.builder.schema as sb
import core_pg_bindings.builder.role as rb
from core_pg_bindings.builder.common import\
    GeneratesSQLSentence,\
    schema_name,\
    identifier
from typing import\
    Generator,\
    Optional
from core_migrations.database import core_migrations as mgr


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:50:07+00:00'
DEPENDS_ON: list[str] = []
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr).create().set_search_path()


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr).drop()
