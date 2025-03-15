#include "core_pg_migrations/interface/namespace.hpp"
#include "core_pg_migrations/util.hpp"


namespace core_pg_migrations::backend::interface
{

std::deque<snapshot> get_unapplied_package_snapshots_for_upgrade_dry_run(
    const pg::text& p_dsn, const package& p_package, const pg::text& p_hash
) {
    std::ostringstream v_message;
    cm_bk::package v_package = ct_i::unwrap(p_package);
    std::deque<snapshot> v_res;
    try
    {
        pqxx::connection v_conn(p_dsn);
        pqxx::work v_tx(v_conn);
        cm_bk::set_search_path_for_package(v_tx, v_package);
        std::deque<cm_bk::snapshot> v_applied_snapshots, v_unapplied_snapshots;
        cm_db::execution_action v_action = cm_db::execution_action::upgrade;
        std::tie(v_applied_snapshots, v_unapplied_snapshots) = get_request_snapshot_list(
            v_tx, v_package, p_hash, v_action
        );
        v_res = ct_i::wrap<std::deque<snapshot>>(v_unapplied_snapshots);
        v_tx.commit();
    }
    catch (const std::exception& e)
    {
        v_message << "Error when attempting to upgrade package \"" << v_package.name << "\"..."  << std::endl;
        cm_u_i::prompt_error(v_message.str(), e.what());
    }
    return v_res;
}


void upgrade_to_package_snapshot_hash (
    const pg::text& p_dsn, const package& p_package, const pg::text& p_hash
) {
    std::ostringstream v_message;
    cm_bk::package v_package = ct_i::unwrap(p_package);
    try
    {
        pqxx::connection v_conn(p_dsn);
        pqxx::work v_tx(v_conn);
        cm_bk::set_search_path_for_package(v_tx, v_package);
        cm_bk::upgrade_to_package_snapshot_hash(v_tx, v_package, p_hash);
        v_tx.commit();
    }
    catch (const std::exception& e)
    {
        v_message << "Error when attempting to upgrade package \"" << v_package.name << "\"..."  << std::endl;
        cm_u_i::prompt_error(v_message.str(), e.what());
    }
}


void downgrade_to_package_snapshot_hash (
    const pg::text& p_dsn, const package& p_package, const pg::text& p_hash
) {
    std::ostringstream v_message;
    cm_bk::package v_package = ct_i::unwrap(p_package);
    try
    {
        pqxx::connection v_conn(p_dsn);
        pqxx::work v_tx(v_conn);
        cm_bk::set_search_path_for_package(v_tx, v_package);
        cm_bk::downgrade_to_package_snapshot_hash(v_tx, v_package, p_hash);
        v_tx.commit();
    }
    catch (const std::exception& e)
    {
        v_message << "Error when attempting to downgrade package \"" << v_package.name << "\"..."  << std::endl;
        cm_u_i::prompt_error(v_message.str(), e.what());
    }
}


std::deque<snapshot> get_applied_package_snapshots_for_downgrade_dry_run (
    const pg::text& p_dsn, const package& p_package, const pg::text& p_hash
) {
    std::ostringstream v_message;
    cm_bk::package v_package = ct_i::unwrap(p_package);
    std::deque<snapshot> v_res;
    try
    {
        pqxx::connection v_conn(p_dsn);
        pqxx::work v_tx(v_conn);
        cm_bk::set_search_path_for_package(v_tx, v_package);
        std::deque<cm_bk::snapshot> v_applied_snapshots, v_unapply_snapshots;
        cm_db::execution_action v_action = cm_db::execution_action::upgrade;
        std::tie(v_applied_snapshots, v_unapply_snapshots) = get_request_snapshot_list(
            v_tx, v_package, p_hash, v_action
        );
        v_res = ct_i::wrap<std::deque<snapshot>>(v_unapply_snapshots);
        v_tx.commit();
    }
    catch (const std::exception& e)
    {
        v_message << "Error when attempting to downgrade package \"" << v_package.name << "\"..."  << std::endl;
        cm_u_i::prompt_error(v_message.str(), e.what());
    }
    return v_res;
}
}
