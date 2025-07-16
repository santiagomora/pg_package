#ifndef CORE_PG_MIGRATIONS_DATABASE__DEFINITIONS
#define CORE_PG_MIGRATIONS_DATABASE__DEFINITIONS
#include "core_pg_bindings/all.hpp"
#include "core_types/all.hpp"


#define CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION PG_ENUM_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION,\
    (core_pg_migrations::database, execution_action),\
    (PG_ENUM_VALUE(upgrade))\
    (PG_ENUM_VALUE(downgrade)),\
    (core_pg_migrations::database::interface, execution_action)\
)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION)


#define CORE_PG_MIGRATIONS_DB_PACKAGE PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_PACKAGE,\
    (core_pg_migrations::database, package),\
    (PG_COLUMN(PG_INT8, id))\
    (PG_COLUMN(PG_TEXT, name))\
    (PG_COLUMN(PG_TEXT, remote_name))\
    (PG_COLUMN(PG_TEXT, tracked_branch_name))\
    (PG_COLUMN(PG_TEXT, schema_name))\
    (PG_COLUMN(PG_TEXT, procedure_schema_name)),\
    NONE,\
    (core_pg_migrations::database::interface, package)\
)
#define CORE_PG_MIGRATIONS_DB_PACKAGE_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_PACKAGE)
#define CORE_PG_MIGRATIONS_DB_PACKAGE_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_PACKAGE)


#define CORE_PG_MIGRATIONS_DB_SNAPSHOT PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_SNAPSHOT,\
    (core_pg_migrations::database, snapshot),\
    (PG_COLUMN(PG_INT8, id))\
    (PG_COLUMN(PG_INT8, package_id))\
    (PG_COLUMN(STD_OPTIONAL(PG_INT8), parent_id))\
    (PG_COLUMN(STD_OPTIONAL(PG_INT8), child_id))\
    (PG_COLUMN(PG_TEXT, commit_hash))\
    (PG_COLUMN(PG_TEXT, created_at)),\
    NONE,\
    (core_pg_migrations::database::interface, snapshot)\
)
#define CORE_PG_MIGRATIONS_DB_SNAPSHOT_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_SNAPSHOT)
#define CORE_PG_MIGRATIONS_DB_SNAPSHOT_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_SNAPSHOT)


#define CORE_PG_MIGRATIONS_DB_EXECUTION PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_EXECUTION,\
    (core_pg_migrations::database, execution),\
    (PG_COLUMN(PG_INT8, id))\
    (PG_COLUMN(PG_INT8, package_id))\
    (PG_COLUMN(CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION, action))\
    (PG_COLUMN(PG_TIMESTAMPTZ, created_at)),\
    NONE,\
    (core_pg_migrations::database::interface, execution)\
)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_EXECUTION)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_EXECUTION)


#define CORE_PG_MIGRATIONS_DB_EXECUTION_SNAPSHOT_RELATION PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_EXECUTION_SNAPSHOT_RELATION,\
    (core_pg_migrations::database, execution_snapshot_relation),\
    (PG_COLUMN(PG_INT8, execution_id))\
    (PG_COLUMN(PG_INT8, snapshot_id))\
    (PG_COLUMN(PG_TEXT, integrity_hash)),\
    NONE,\
    (core_pg_migrations::database::interface, execution_snapshot_relation)\
)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_SNAPSHOT_RELATION_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_EXECUTION_SNAPSHOT_RELATION)
#define CORE_PG_MIGRATIONS_DB_EXECUTION_SNAPSHOT_RELATION_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_EXECUTION_SNAPSHOT_RELATION)


#define CORE_PG_MIGRATIONS_DB_MIGRATION PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_MIGRATION,\
    (core_pg_migrations::database, migration),\
    (PG_COLUMN(PG_INT8, id))\
    (PG_COLUMN(PG_INT8, snapshot_id))\
    (PG_COLUMN(PG_INT8, heap_position))\
    (PG_COLUMN(PG_TEXT, name))\
    (PG_COLUMN(STD_OPTIONAL(PG_TEXT), datafix_name))\
    (PG_COLUMN(PG_TEXT, upgrade_script_name))\
    (PG_COLUMN(PG_TEXT, downgrade_script_name)),\
    NONE,\
    (core_pg_migrations::database::interface, migration)\
)
#define CORE_PG_MIGRATIONS_DB_MIGRATION_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_MIGRATION)
#define CORE_PG_MIGRATIONS_DB_MIGRATION_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_MIGRATION)


#define CORE_PG_MIGRATIONS_DB_MIGRATION_DEPENDENCY_RELATION PG_TABLE_DEFINITION(\
    CORE_PG_MIGRATIONS_DB_MIGRATION_DEPENDENCY_RELATION,\
    (core_pg_migrations::database, migration_dependency_relation),\
    (PG_COLUMN(PG_INT8, migration_id))\
    (PG_COLUMN(PG_INT8, depends_on_id)),\
    NONE,\
    (core_pg_migrations::database::interface, migration_dependency_relation)\
)
#define CORE_PG_MIGRATIONS_DB_MIGRATION_DEPENDENCY_RELATION_CONSTRUCTORS (CORE_PG_MIGRATIONS_DB_MIGRATION_DEPENDENCY_RELATION)
#define CORE_PG_MIGRATIONS_DB_MIGRATION_DEPENDENCY_RELATION_MEMBERS T_MEMBERS(CORE_PG_MIGRATIONS_DB_MIGRATION_DEPENDENCY_RELATION)


#define CORE_PG_MIGRATIONS_DB_CREATE_EXECUTION PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_CREATE_EXECUTION,\
    (core_pg_migrations::database::functions, create_execution)\
)


#define CORE_PG_MIGRATIONS_DB_CREATE_MIGRATION PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_CREATE_MIGRATION,\
    (core_pg_migrations::database::functions, create_or_update_migration)\
)


#define CORE_PG_MIGRATIONS_DB_CREATE_PACKAGE PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_CREATE_PACKAGE,\
    (core_pg_migrations::database::functions, create_or_update_package)\
)


#define CORE_PG_MIGRATIONS_DB_CREATE_SNAPSHOT PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_CREATE_SNAPSHOT,\
    (core_pg_migrations::database::functions, create_or_update_snapshot)\
)


#define CORE_PG_MIGRATIONS_DB_GET_APPLIED_SNAPSHOTS PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_GET_APPLIED_SNAPSHOTS,\
    (core_pg_migrations::database::functions, get_applied_snapshots)\
)


#define CORE_PG_MIGRATIONS_DB_SYNCHRONIZE_MIGRATION_DEPENDENCIES PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_SYNCHRONIZE_MIGRATION_DEPENDENCIES,\
    (core_pg_migrations::database::functions, synchronize_migration_dependencies)\
)


#define CORE_PG_MIGRATIONS_DB_SET_PACKAGE_INTEGRITY_HASH PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_SET_PACKAGE_INTEGRITY_HASH,\
    (core_pg_migrations::database::functions, set_package_integrity_hash)\
)


#define CORE_PG_MIGRATIONS_DB_REGISTER_EXECUTION_SNAPSHOT_RELATION PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_REGISTER_EXECUTION_SNAPSHOT_RELATION,\
    (core_pg_migrations::database::functions, register_execution_snapshot_relation)\
)


#define CORE_PG_MIGRATIONS_DB_GET_INTEGRITY_HASH PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_GET_INTEGRITY_HASH,\
    (core_pg_migrations::database::functions, get_package_integrity_hash_at_snapshot)\
)


#define CORE_PG_MIGRATIONS_DB_KEEP_SNAPSHOT_MIGRATION_IDS PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_KEEP_SNAPSHOT_MIGRATION_IDS,\
    (core_pg_migrations::database::functions, keep_snapshot_migration_ids)\
)


#define CORE_PG_MIGRATIONS_DB_DESTROY_MIGRATION PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_DESTROY_MIGRATION,\
    (core_pg_migrations::database::functions, destroy_migration)\
)


#define CORE_PG_MIGRATIONS_DB_GET_SNAPSHOT_MIGRATIONS PG_INVOKABLE(\
    CORE_PG_MIGRATIONS_DB_GET_SNAPSHOT_MIGRATIONS,\
    (core_pg_migrations::database::functions, get_snapshot_migrations)\
)

#endif
