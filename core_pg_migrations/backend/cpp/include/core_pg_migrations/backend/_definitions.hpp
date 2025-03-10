#ifndef CORE_PG_MIGRATIONS_BACKEND__DEFINITIONS
#define CORE_PG_MIGRATIONS_BACKEND__DEFINITIONS
#include "core_types/all.hpp"
#include "core_pg_bindings/all.hpp"


#define CORE_PG_MIGRATIONS_BK_MIGRATION DATACLASS_DEFINITION(\
    CORE_PG_MIGRATIONS_BK_MIGRATION,\
    (core_pg_migrations::backend, migration),\
    (PG_COLUMN(PG_TEXT, name))\
    (PG_COLUMN(PG_TEXT, upgrade_procedure_name))\
    (PG_COLUMN(PG_TEXT, downgrade_procedure_name))\
    (PG_COLUMN(PG_TEXT, upgrade_procedure))\
    (PG_COLUMN(PG_TEXT, downgrade_procedure))\
    (PG_COLUMN(STD_OPTIONAL(PG_TEXT), datafix_name))\
    (PG_COLUMN(STD_VECTOR(PG_TEXT), dependencies)),\
    NONE,\
    (core_pg_migrations::backend::interface, migration)\
)
#define CORE_PG_MIGRATIONS_BK_MIGRATION_CONSTRUCTORS (CORE_PG_MIGRATIONS_BK_MIGRATION)
#define CORE_PG_MIGRATIONS_BK_MIGRATION_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_BK_MIGRATION)


#define CORE_PG_MIGRATIONS_BK_SNAPSHOT DATACLASS_DEFINITION(\
    CORE_PG_MIGRATIONS_BK_SNAPSHOT,\
    (core_pg_migrations::backend, snapshot),\
    (DATACLASS_MEMBER(PG_TEXT, hash))\
    (DATACLASS_MEMBER(STD_OPTIONAL(PG_TEXT), previous_hash))\
    (DATACLASS_MEMBER(STD_OPTIONAL(PG_TEXT), next_hash))\
    (DATACLASS_MEMBER(PG_TEXT, payload))\
    (DATACLASS_MEMBER(STD_VECTOR(CORE_PG_MIGRATIONS_BK_MIGRATION), migrations)),\
    NONE,\
    (core_pg_migrations::backend::interface, snapshot)\
)
#define CORE_PG_MIGRATIONS_BK_SNAPSHOT_CONSTRUCTORS (CORE_PG_MIGRATIONS_BK_SNAPSHOT)
#define CORE_PG_MIGRATIONS_BK_SNAPSHOT_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_BK_SNAPSHOT)


#define CORE_PG_MIGRATIONS_BK_PACKAGE DATACLASS_DEFINITION(\
    CORE_PG_MIGRATIONS_BK_PACKAGE,\
    (core_pg_migrations::backend, package),\
    (DATACLASS_MEMBER(PG_TEXT, name))\
    (DATACLASS_MEMBER(PG_TEXT, schema_name))\
    (DATACLASS_MEMBER(PG_TEXT, procedure_schema_name))\
    (DATACLASS_MEMBER(PG_TEXT, remote_name))\
    (DATACLASS_MEMBER(PG_TEXT, tracked_branch_name))\
    (DATACLASS_MEMBER(STD_VECTOR(CORE_PG_MIGRATIONS_BK_SNAPSHOT), snapshots)),\
    NONE,\
    (core_pg_migrations::backend::interface, package)\
)
#define CORE_PG_MIGRATIONS_BK_PACKAGE_CONSTRUCTORS (CORE_PG_MIGRATIONS_BK_PACKAGE)
#define CORE_PG_MIGRATIONS_BK_PACKAGE_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_BK_PACKAGE)


#endif
