import core_pg_bindings.builder.schema as sb
import core_pg_bindings.builder.role as rb
import core_migrations.backend as mgr
from core_pg_bindings.builder.common import\
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
