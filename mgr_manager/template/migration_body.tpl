import pg_definition.builder.schema as sb
import pg_definition.builder.role as rb
from pg_definition.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = {generated_at}
DEPENDS_ON: list[str] = {depends_on}
DATAFIX_NAME: Optional[str] = {datafix_name}


def upgrade() -> Generator[GeneratesSQLSentence, None, None]:
    pass


def downgrade() -> Generator[GeneratesSQLSentence, None, None]:
    pass
