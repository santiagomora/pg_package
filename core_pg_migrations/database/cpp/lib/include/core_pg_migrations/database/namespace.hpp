#ifndef CORE_PG_MIGRATIONS_DATABASE_NAMESPACE
#define CORE_PG_MIGRATIONS_DATABASE_NAMESPACE
#include "core_pg_migrations/database/_definitions.hpp"


namespace pg = core_pg_bindings;


namespace core_pg_migrations::database
{
PG_CPP_ENUM_DECLARATION(CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION);
PG_CPP_TABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_PACKAGE);
PG_CPP_TABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_SNAPSHOT);
PG_CPP_TABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_EXECUTION);
PG_CPP_TABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_MIGRATION);
PG_CPP_TABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_MIGRATION_DEPENDENCY_RELATION);
PG_CPP_TABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_EXECUTION_SNAPSHOT_RELATION);
}


namespace core_pg_migrations::database
{

struct schema_exists
: public pg::queries_database_on_transaction<
    schema_exists,
    pg::fetch_one_functor,
    pg::SingleResult_<pg::boolean>>
{
    static constexpr const std::string_view query_string (
        const pg::text&
    ) {
        return "SELECT EXISTS(\
            SELECT schema_name FROM information_schema.schemata\
            WHERE schema_name = $1\
        )";
    }
};


struct get_package_by_name
: public pg::queries_database_on_transaction<
    get_package_by_name,
    pg::fetch_one_functor,
    pg::SingleResult_<package>>
{
    static constexpr const std::string_view query_string (
        const pg::text&
    ) {
        return "SELECT p FROM package p WHERE name = $1 LIMIT 1";
    }
};


struct get_snapshot_migrations
: public pg::queries_database_on_transaction<
    get_snapshot_migrations,
    pg::fetch_many_functor,
    pg::ContainedResult_<migration, std::vector>>
{
    static constexpr const std::string_view query_string (
        const snapshot&, const execution_action&
    ) {
        return "SELECT get_snapshot_migrations(p_snapshot := $1, p_action := $2)";
    }
};


struct get_snapshot_by_commit_hash
: public pg::queries_database_on_transaction<
    get_snapshot_by_commit_hash,
    pg::fetch_one_functor,
    pg::SingleResult_<snapshot>>
{
    static constexpr const std::string_view query_string (
        const pg::text&
    ) {
        return "SELECT s FROM snapshot s WHERE commit_hash = $1";
    }
};


struct create_execution
: public pg::queries_database_on_transaction<
    create_execution,
    pg::fetch_one_functor,
    pg::SingleResult_<execution>>
{
    static constexpr const std::string_view query_string (
        const package&, const execution_action
    ) {
        return "SELECT create_execution(\
            p_package := $1,\
            p_action  := $2)";
    }
};


struct create_migration
: public pg::queries_database_on_transaction<
    create_migration,
    pg::fetch_one_functor,
    pg::SingleResult_<migration>>
{
    static constexpr const std::string_view query_string (
        const snapshot&, const pg::text&, const pg::text&, const pg::text&, const std::optional<pg::text>&,
        const pg::int8&
    ) {
        return "SELECT create_migration(\
            p_snapshot                 := $1,\
            p_name                     := $2,\
            p_upgrade_procedure_name   := $3,\
            p_downgrade_procedure_name := $4,\
            p_datafix_name             := $5,\
            p_heap_position            := $6)";
    }
};


struct create_package
: public pg::queries_database_on_transaction<
    create_package,
    pg::fetch_one_functor,
    pg::SingleResult_<package>>
{
    static constexpr const std::string_view query_string (
        const pg::text&, const pg::text&, const pg::text&, const pg::text&, const pg::text&
    ) {
        return "SELECT create_package(\
            p_name                  := $1,\
            p_remote_name           := $2,\
            p_tracked_branch_name   := $3,\
            p_schema_name           := $4,\
            p_procedure_schema_name := $5\
        )";
    }
};


struct get_applied_snapshots
: public pg::queries_database_on_transaction<
    get_applied_snapshots,
    pg::fetch_many_functor,
    pg::ContainedResult_<pg::text, std::vector>>
{
    static constexpr const std::string_view query_string (
        const pg::text&
    ) {
        return "SELECT get_applied_snapshots(\
            p_package_name := $1\
        )";
    }
    static constexpr const std::string_view query_string (
        const package&
    ) {
        return "SELECT get_applied_snapshots(\
            p_package := $1\
        )";
    }
};


struct create_snapshot
: public pg::queries_database_on_transaction<
    create_snapshot,
    pg::fetch_one_functor,
    pg::SingleResult_<snapshot>>
{
    static constexpr const std::string_view query_string (
        const pg::int8&, const pg::text&, const std::optional<pg::text>&, const std::optional<pg::text>&
    ) {
        return "SELECT create_snapshot (\
            p_package_id  := $1,\
            p_hash        := $2,\
            p_parent_hash := $3,\
            p_child_hash  := $4\
        )";
    }
    static constexpr const std::string_view query_string (
        const package&, const pg::text&, const std::optional<snapshot>&, const std::optional<snapshot>&
    ) {
        return "SELECT create_snapshot (\
            p_package     := $1,\
            p_hash        := $2,\
            p_parent_hash := $3,\
            p_child_hash  := $4\
        )";
    }
};


struct synchronize_migration_dependencies
: public pg::queries_database_on_transaction<
    synchronize_migration_dependencies,
    pg::fetch_none_functor,
    pg::NoResult_>
{
    static constexpr const std::string_view query_string (
        const migration&, const pg::text&
    ) {
        return "SELECT synchronize_migration_dependencies (\
            p_migration        := $1,\
            p_dependency_names := $2::text[]\
        )";
    }
};


struct set_package_integrity_hash
: public pg::queries_database_on_transaction<
    set_package_integrity_hash,
    pg::fetch_none_functor,
    pg::NoResult_>
{
    static constexpr const std::string_view query_string (
        const package&, const pg::text&
    ) {
        return "SELECT set_package_integrity_hash (\
            p_package        := $1,\
            p_integrity_hash := $2\
        )";
    }
};


struct register_execution_snapshot_relation
: public pg::queries_database_on_transaction<
    register_execution_snapshot_relation,
    pg::fetch_none_functor,
    pg::NoResult_>
{
    static constexpr const std::string_view query_string (
        const execution&, const snapshot&, const pg::text&
    ) {
        return "SELECT register_execution_snapshot_relation (\
            p_execution := $1,\
            p_snapshot  := $2,\
            p_integrity_hash := $3\
        )";
    }
};


struct get_integrity_hash
: public pg::queries_database_on_transaction<
    get_integrity_hash,
    pg::fetch_one_functor,
    pg::SingleResult_<pg::text>>
{
    static constexpr const std::string_view query_string (
        const pg::text&
    ) {
        return "SELECT get_integrity_hash (\
            p_package_name := $1\
        )";
    }
};


struct keep_snapshot_migration_ids
: public pg::queries_database_on_transaction<
    keep_snapshot_migration_ids,
    pg::fetch_none_functor,
    pg::NoResult_>
{
    static constexpr const std::string_view query_string (
        const snapshot&, const pg::text&
    ) {
        return "SELECT keep_snapshot_migration_ids (\
            p_snapshot      := $1,\
            p_migration_ids := $2::int8[]\
        )";
    }
};


}


namespace core_pg_migrations::database::interface
{
// NOTE TYPES
IFACE_CPP_ENUMDEF_DECLARATION(CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION);
IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_DB_PACKAGE);
IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_DB_SNAPSHOT);
IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_DB_EXECUTION);
IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_DB_MIGRATION);
IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_DB_MIGRATION_DEPENDENCY_RELATION);
IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_DB_EXECUTION_SNAPSHOT_RELATION);
};


namespace core_pg_migrations::database::functions
{
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_CREATE_EXECUTION);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_CREATE_MIGRATION);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_CREATE_PACKAGE);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_CREATE_SNAPSHOT);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_GET_APPLIED_SNAPSHOTS);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_SYNCHRONIZE_MIGRATION_DEPENDENCIES);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_SET_PACKAGE_INTEGRITY_HASH);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_REGISTER_EXECUTION_SNAPSHOT_RELATION);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_GET_INTEGRITY_HASH);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_KEEP_SNAPSHOT_MIGRATION_IDS);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_DESTROY_MIGRATION);
PG_CPP_INVOKABLE_DECLARATION(CORE_PG_MIGRATIONS_DB_GET_SNAPSHOT_MIGRATIONS);
};


namespace pqxx
{
PG_DECLARE_ENUM_CONVERSION(CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION);
PG_DECLARE_TABLE_CONVERSION(CORE_PG_MIGRATIONS_DB_PACKAGE);
PG_DECLARE_TABLE_CONVERSION(CORE_PG_MIGRATIONS_DB_SNAPSHOT);
PG_DECLARE_TABLE_CONVERSION(CORE_PG_MIGRATIONS_DB_EXECUTION);
PG_DECLARE_TABLE_CONVERSION(CORE_PG_MIGRATIONS_DB_MIGRATION);
PG_DECLARE_TABLE_CONVERSION(CORE_PG_MIGRATIONS_DB_MIGRATION_DEPENDENCY_RELATION);
PG_DECLARE_TABLE_CONVERSION(CORE_PG_MIGRATIONS_DB_EXECUTION_SNAPSHOT_RELATION);
}

#endif
