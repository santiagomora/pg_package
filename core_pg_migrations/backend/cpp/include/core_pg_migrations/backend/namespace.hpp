#ifndef CORE_PG_MIGRATIONS_BACKEND_NAMESPACE
#define CORE_PG_MIGRATIONS_BACKEND_NAMESPACE
#include "core_pg_migrations/backend/_definitions.hpp"


namespace pg = core_pg_bindings;


namespace core_pg_migrations::backend
{
/*
 * NOTE TYPES
 */
CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BACKEND_MIGRATION_PARAM);
CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BACKEND_SETUP_PARAMETERS);
/*
 * NOTE FUNCTIONS
 */
void create_and_execute_setup_script(
    pqxx::work& p_tx, pg::text& p_proc_schema, pg::text& p_script_name,
    pg::text& p_setup_script
);
void register_setup_package_and_execution(
    pqxx::work& p_tx, pg::text& p_package_name, pg::text& p_tracked_branch,
    std::vector<migration_param>& p_migrations
);
}

#endif
