#ifndef CORE_PG_MIGRATIONS_BACKEND_NAMESPACE
#define CORE_PG_MIGRATIONS_BACKEND_NAMESPACE
#include "core_pg_migrations/backend/_definitions.hpp"
#include "core_pg_migrations/database/namespace.hpp"
#include "core_pg_migrations/util.hpp"


namespace py = pybind11;
namespace pg = core_pg_bindings;
namespace ct = core_types;
namespace cm_db = core_pg_migrations::database;


namespace core_pg_migrations::backend
{
CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_MIGRATION);
CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_SNAPSHOT);
CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_PACKAGE);
}


namespace core_pg_migrations::backend
{
void set_search_path_for_package(
    pqxx::dbtransaction& p_tx, const package& p_package
);
void upgrade_to_package_snapshot_hash (
    pqxx::work& p_tx, const package& p_package, const pg::text& p_hash
);
void downgrade_to_package_snapshot_hash (
    pqxx::work& p_tx, const package& p_package, const pg::text& p_hash
);
std::tuple<std::deque<snapshot>, std::deque<snapshot>> get_applied_and_unapplied_package_snapshots (
    pqxx::work& p_tx, const package& p_package, const pg::text& p_until_hash
);
std::tuple<std::deque<snapshot>, std::deque<snapshot>> get_request_snapshot_list (
    pqxx::work& p_tx, const package& p_package, const std::string& p_hash,
    const cm_db::execution_action& p_action
);
}

namespace cm_bk = core_pg_migrations::backend;

#endif
