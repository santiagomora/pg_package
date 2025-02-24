#include "core_pg_migrations/backend/namespace.hpp"
#include "core_pg_migrations/interface/namespace.hpp"
#include "core_pg_migrations/util.hpp"


namespace cm_bk  = core_pg_migrations::backend;
namespace cm_bk_i = cm_bk::interface;
namespace cm_u  = core_pg_migrations::util;
namespace cm_u_i  = cm_u::interface;


CT_CLASSDEF_REGISTER_SUBCLASS_REG(CORE_PG_MIGRATIONS_BACKEND_INTERFACE_SETUP_PARAMETERS);


void cm_bk_i::setup_core_pg_migrations_in_database (cm_bk_i::setup_parameters& p_params, std::string& p_db_dsn)
{
    std::ostringstream v_message;
    pqxx::connection v_conn(p_db_dsn);
    cm_bk::setup_parameters v_params = p_params.value();
    try
    {
        pqxx::work v_tx1(v_conn);
        cm_bk::create_and_execute_setup_script(v_tx1, v_params.proc_schema, v_params.script_name, v_params.setup_script);
        v_message << "Setup script called successfully, registering package..." << std::endl;
        cm_u::prompt_notice(v_message);
        cm_bk::register_setup_package_and_execution(v_tx1,  v_params.package_name, v_params.tracked_branch, v_params.commit_hashes_sequence, v_params.migration_names);
        v_tx1.commit();
        v_message << "Package and execution registered successfully" << std::endl;
        cm_u::prompt_notice(v_message);
    }
    catch (const std::exception& e)
    {
        v_message << "Failed to register package \"" << v_params.package_name << "\"" << std::endl;
        cm_u_i::prompt_error(v_message.str(), e.what());
    }
}
