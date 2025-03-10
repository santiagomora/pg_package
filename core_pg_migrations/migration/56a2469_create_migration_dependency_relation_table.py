import core_pg_migrations.builder.schema as sb
import core_pg_migrations.builder.role as rb
import core_types as ct
from core_pg_migrations.builder.common import\
    GeneratesSQLSentence
from typing import\
    Generator,\
    Optional,\
    Any


# NOTE: These functions are designed to yield a builder that holds all the
# operations that the migration is set to perform to update the postgres objects.
GENERATED_AT: str = '2025-03-05 15:40:58+00:00'
DEPENDS_ON: list[str] = ['create_migration_table']
DATAFIX_NAME: Optional[str] = None


def upgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .table('migration_dependency_relation').create()\
        .table('migration_dependency_relation').column('migration_id').add()\
        .table('migration_dependency_relation').column('depends_on_id').add()\
        .table('migration_dependency_relation').primary_key('migration_dependency_relation_pk').add()\
        .table('migration_dependency_relation').foreign_key('migration_dependency_relation_depends_on_id_fk').add()\
        .table('migration_dependency_relation').foreign_key('migration_dependency_relation_migration_id_fk').add()


def downgrade(snapshot: dict[str, Any]) -> Generator[GeneratesSQLSentence, None, None]:
    yield from sb.builder(snapshot)\
        .table('migration_dependency_relation').foreign_key('migration_dependency_relation_migration_id_fk').drop()\
        .table('migration_dependency_relation').foreign_key('migration_dependency_relation_depends_on_id_fk').drop()\
        .table('migration_dependency_relation').primary_key('migration_dependency_relation_pk').drop()\
        .table('migration_dependency_relation').column('depends_on_id').drop()\
        .table('migration_dependency_relation').column('migration_id').drop()\
        .table('migration_dependency_relation').drop()
