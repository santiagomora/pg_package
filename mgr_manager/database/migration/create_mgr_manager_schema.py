import pg_definition.builder.schema as sb
import pg_definition.builder.role as rb
from pg_definition.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional
import mgr_manager.backend as mgr


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2024-12-23 17:50:07+00:00'
DEPENDS_ON: list[str] = []
DATAFIX_NAME: Optional[str] = None


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema).create()


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(mgr.schema).drop()
