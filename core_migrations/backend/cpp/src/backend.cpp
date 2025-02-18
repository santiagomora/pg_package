#include "core_migrations/backend/namespace.hpp"
#include "core_migrations/database/queries.hpp"
#include "core_migrations/util.hpp"


namespace cm_db_q = core_migrations::database::queries;
namespace cm_bk  = core_migrations::backend;
namespace cm_u  = core_migrations::util;


void cm_bk::create_and_execute_setup_script(
    pqxx::work& p_tx, pg::text& p_proc_schema, pg::text& p_script_name,
    pg::text& p_setup_script
) {
    std::ostringstream v_message;
    std::string v_proc_schema_identifier = cm_u::identifier(p_tx, *p_proc_schema);
    std::string v_script_name_identifier = cm_u::identifier(p_tx, *p_script_name);
    v_message << "Creating \"" << v_proc_schema_identifier << "\" schema";
    cm_u::prompt_notice(v_message);
    p_tx.exec(std::string("CREATE SCHEMA IF NOT EXISTS ") + v_proc_schema_identifier).no_rows();
    v_message << "Creating \"" << v_script_name_identifier << "\" procedure in \"" << v_proc_schema_identifier << "\" schema";
    cm_u::prompt_notice(v_message);
    p_tx.exec(std::string("SET search_path to ") + v_proc_schema_identifier).no_rows();
    p_tx.exec(*p_setup_script).no_rows();
    v_message << "Calling \"" << v_script_name_identifier << "\" procedure in \"" << v_proc_schema_identifier << "\" schema";
    cm_u::prompt_notice(v_message);
    p_tx.exec(std::string("CALL ") + v_script_name_identifier + "()");
    v_message << "Script \"" << v_script_name_identifier << "\" executed successfully registering execution";
    cm_u::prompt_notice(v_message);
}


void cm_bk::register_setup_package_and_execution(
    pqxx::work& p_tx, pg::text& p_package_name, pg::text& p_tracked_branch,
    std::vector<pg::text>& p_commit_hashes, std::vector<pg::text>& p_migration_names
) {
    cm_db_dec::package v_package = cm_db_q::create_package{}(p_tx, p_package_name, p_tracked_branch, p_commit_hashes[0]);
    cm_db_dec::execution_action v_action = cm_db_dec::execution_action_enum::setup;
    cm_db_dec::execution v_execution = cm_db_q::create_execution{}(p_tx, v_package, v_package.current_commit_hash, v_action);
    cm_db_q::register_execution{}(p_tx, v_execution, p_commit_hashes, p_migration_names);
}
