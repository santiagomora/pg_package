#include "core_migrations/backend/namespace.hpp"
#include "core_migrations/interface/namespace.hpp"
#include "core_migrations/util.hpp"


namespace cm_bk  = core_migrations::backend;
namespace cm_bk_i = core_migrations::backend::interface;
namespace cm_u  = core_migrations::util;
namespace cm_u_i  = core_migrations::util::interface;


CT_CLASSDEF_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_BACKEND_INTERFACE_SETUP_PARAMETERS);


void cm_bk_i::setup_core_migrations_in_database (cm_bk_i::setup_parameters& p_params, std::string& p_db_dsn)
{
    std::ostringstream v_message;
    pqxx::connection v_conn(p_db_dsn);
    try
    {
        pqxx::work v_tx1(v_conn);
        cm_bk::create_and_execute_setup_script(v_tx1, p_params.proc_schema, p_params.script_name, p_params.setup_script);
        v_message << "Setup script called successfully, registering package..." << std::endl;
        cm_u::prompt_notice(v_message);
        cm_bk::register_setup_package_and_execution(v_tx1,  p_params.package_name, p_params.tracked_branch, p_params.commit_hashes_sequence, p_params.migration_names);
        v_tx1.commit();
        v_message << "Package and execution registered successfully" << std::endl;
        cm_u::prompt_notice(v_message);
    }
    catch (const std::exception& e)
    {
        v_message << "Failed to register package \"" << p_params->package_name() << "\"" << std::endl;
        cm_u_i::prompt_error(v_message.str(), e.what());
    }
}
