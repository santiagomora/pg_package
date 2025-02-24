#ifndef CORE_PG_MIGRATIONS_DATABASE_DEFINITIONS
#define CORE_PG_MIGRATIONS_DATABASE_DEFINITIONS
#include "core_pg_bindings/all.hpp"
#include "core_types/all.hpp"


#define CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION PG_ENUM_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION,\
    (core_pg_migrations::database::declarations, execution_action),\
    (PG_ENUM_VALUE(setup))\
    (PG_ENUM_VALUE(upgrade))\
    (PG_ENUM_VALUE(downgrade))\
    (PG_ENUM_VALUE(install)),\
    (core_pg_migrations::database::declarations::interface, execution_action)\
)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION)


#define CORE_PG_MIGRATIONS_DB_PACKAGE PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_PACKAGE,\
    (core_pg_migrations::database::declarations, package),\
    (PG_COLUMN(PG_INT8, id))\
    (PG_COLUMN(PG_TEXT, name))\
    (PG_COLUMN(PG_TEXT, branch_name))\
    (PG_COLUMN(PG_TEXT, current_commit_hash))\
    (PG_COLUMN(PG_TIMESTAMPTZ, last_updated_at)),\
    NONE,\
    (core_pg_migrations::database::declarations::interface, package)\
)
#define CORE_PG_MIGRATIONS_DB_PACKAGE_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_PACKAGE)
#define CORE_PG_MIGRATIONS_DB_PACKAGE_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_PACKAGE)


#define CORE_PG_MIGRATIONS_DB_EXECUTION PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_EXECUTION,\
    (core_pg_migrations::database::declarations, execution),\
    (PG_COLUMN(PG_INT8, id))\
    (PG_COLUMN(PG_INT8, package_id))\
    (PG_COLUMN(PG_TIMESTAMPTZ, created_at))\
    (PG_COLUMN(PG_TEXT, commit_hash))\
    (PG_COLUMN(CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION, action)),\
    NONE,\
    (core_pg_migrations::database::declarations::interface, execution)\
)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_EXECUTION)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_EXECUTION)


#define CORE_PG_MIGRATIONS_DB_EXECUTION_COMMIT_HASH PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_EXECUTION_COMMIT_HASH,\
    (core_pg_migrations::database::declarations, execution_commit_hash),\
    (PG_COLUMN(PG_INT8, execution_id))\
    (PG_COLUMN(PG_TEXT, commit_hash)),\
    NONE,\
    (core_pg_migrations::database::declarations::interface, execution_commit_hash)\
)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_COMMIT_HASH_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_EXECUTION_COMMIT_HASH)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_COMMIT_HASH_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_EXECUTION_COMMIT_HASH)


#define CORE_PG_MIGRATIONS_DB_MIGRATION PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_MIGRATION,\
    (core_pg_migrations::database::declarations, migration),\
    (PG_COLUMN(PG_INT8, id))\
    (PG_COLUMN(PG_INT8, execution_id))\
    (PG_COLUMN(PG_TEXT, name))\
    (PG_COLUMN(STD_OPTIONAL(PG_TEXT), datafix_name))\
    (PG_COLUMN(PG_TIMESTAMPTZ, created_at)),\
    NONE,\
    (core_pg_migrations::database::declarations::interface, migration)\
)
#define CORE_PG_MIGRATIONS_DB_MIGRATION_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_MIGRATION)
#define CORE_PG_MIGRATIONS_DB_MIGRATION_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_MIGRATION)


#define CORE_PG_MIGRATIONS_DB_EXECUTION_MIGRATION PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_EXECUTION_MIGRATION,\
    (core_pg_migrations::database::declarations, execution_migration),\
    (PG_COLUMN(PG_INT8, migration_id))\
    (PG_COLUMN(PG_INT8, execution_id)),\
    NONE,\
    (core_pg_migrations::database::declarations::interface, execution_migration)\
)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_MIGRATION_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_EXECUTION_MIGRATION)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_MIGRATION_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_EXECUTION_MIGRATION)


#define CORE_PG_MIGRATIONS_DB_CREATE_EXECUTION PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_CREATE_EXECUTION,\
    (core_pg_migrations::database::declarations, create_execution)\
)


#define CORE_PG_MIGRATIONS_DB_REGISTER_EXECUTION_COMMIT_HASH PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_REGISTER_EXECUTION_COMMIT_HASH,\
    (core_pg_migrations::database::declarations, register_execution_commit_hash)\
)


#define CORE_PG_MIGRATIONS_DB_REGISTER_EXECUTION_MIGRATION PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_REGISTER_EXECUTION_MIGRATION,\
    (core_pg_migrations::database::declarations, register_execution_migration)\
)


#define CORE_PG_MIGRATIONS_DB_CREATE_MIGRATION PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_CREATE_MIGRATION,\
    (core_pg_migrations::database::declarations, create_migration)\
)


#define CORE_PG_MIGRATIONS_DB_CREATE_PACKAGE PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_CREATE_PACKAGE,\
    (core_pg_migrations::database::declarations, create_package)\
)


#endif
