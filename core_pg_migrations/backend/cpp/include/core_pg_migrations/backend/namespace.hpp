#ifndef CORE_PG_MIGRATIONS_BACKEND_NAMESPACE
#define CORE_PG_MIGRATIONS_BACKEND_NAMESPACE
#include "core_pg_migrations/backend/_definitions.hpp"
#include "core_pg_migrations/database/namespace.hpp"


namespace pg = core_pg_bindings;
namespace cm_db = core_pg_migrations::database;


 /* in this sense the snapshot can be represented as a std::map with keys:
 * <snapshot>: next: str, previous: str, hash: str, migrations: std::vector<migration>
 * <migration>: name: str, datafix_name: str, script: str, procedure_name: str, dependencies: std::vector<str>
 * <package>: procedure_schema_name: str, schema_name: str, snapshots: std::vector<snapshot>*/
namespace core_pg_migrations::backend
{
    CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_MIGRATION);
    CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_SNAPSHOT);
    CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_PACKAGE);
}


namespace core_pg_migrations::backend
{
void apply_package_snapshots_until_hash (
    pqxx::connection& p_conn, const package& p_package, const pg::text& p_until_hash
);
}

#endif
