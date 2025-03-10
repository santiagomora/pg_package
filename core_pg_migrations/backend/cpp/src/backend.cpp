#include "core_pg_migrations/backend/namespace.hpp"
#include "core_pg_migrations/database/namespace.hpp"
#include "core_pg_migrations/util.hpp"
#include <stdexcept>
#include <iostream>
#include <sstream>

namespace cm_db = core_pg_migrations::database;
namespace cm_bk = core_pg_migrations::backend;
namespace cm_u  = core_pg_migrations::util;
namespace ct = core_types;
namespace pg = core_pg_bindings;


// PROPOSED FLOW FOR PACKAGE UPGRADING:
// | Generate an upgrade request:
// | 1. the upgrade request consists of all the snapshots
// |    and all their migrations, because we need to check the integrity (that migrations and snapshots
// |    coincide)
// | 2. check the snapshot list is consistent:
// |    (How? send the request to the backend. the backend should compare the snapshot list with that stored in the 
// |     database and each migration associated: the procedures and the dependencies)
// | 3. package snapshot structure is correct?
// |
// +-> T: | 1. backend generates a request of unapplied snapshots. we must apply these snapshots in the database
// |      | 2. upgraded package is core_pg_migrations?
// |      |    (core_pg_migrations follows a different workflow)
// |      |
// |      +-> T: | 1. package is not installed?
// |      |      |
// |      |      +-> T: | 1. register package
// |      |      |      | 2. get first snapshot
// |      |      |      | 3. register snapshot
// |      |      |      | 4. loop through snapshot migrations
// |      |      |      | 4.1. create upgrade migration
// |      |      |      | 4.2. apply upgrade migration
// |      |      |      | 4.3. create downgrade migration
// |      |      |      | 4.4. register migration
// |      |      |      | 5. register execution
// |      |      |
// |      |      | 6. loop through remaining snapshots
// |      |      | 6.1 register snapshot
// |      |      | 6.2. loop through snapshot migrations
// |      |      | 6.2.1. create upgrade migration
// |      |      | 6.2.2. apply upgrade migration
// |      |      | 6.2.3. create downgrade migration
// |      |      | 6.2.4. register migration
// |      |      | 7. register execution
// |      |
// |      +-> F: | core_pg_migrations is installed?
// |             |
// |             +-> T: | 1. lock core_pg_migrations tables
// |             |      | package is not installed?
// |             |      |
// |             |      +-> T: | 2. create package procedure schema
// |             |      |      | 3. register the package
// |             |      |
// |             |      | 4. loop through snapshots:
// |             |      | 4.1. register snapshot
// |             |      | 4.2. loop through snapshot migrations
// |             |      | 4.2.1. create upgrade migration
// |             |      | 4.2.3. create downgrade migration
// |             |      | 4.2.4. register migration
// |             |      | 4.3. call the procedures using the api
// |             |      | 4.4. register the execution
// |             |
// |             +-> F: | raise exception and exit
// |
// +-> F: | raise exception and exit


namespace core_pg_migrations::backend
{

pg::text get_package_integrity_hash (
    const package& p_package, const std::deque<snapshot>& p_applied_snapshots
) {
    std::vector<pg::text> v_snapshot_payloads = {};
    for (const auto& v_snapshot : p_applied_snapshots)
    {
        v_snapshot_payloads.emplace_back(v_snapshot.payload);
    }
    auto v_hash_tuple = std::make_tuple(p_package.name, p_package.schema_name, p_package.procedure_schema_name, p_package.remote_name, p_package.tracked_branch_name, v_snapshot_payloads);
    // return (pg::text) sha512(ct::tp_to_string(v_hash_tuple));
    std::regex v_ignored_chars("( |\n|\t)+");
    std::string v_normalized_package_state = std::regex_replace(ct::tp_to_string(v_hash_tuple), v_ignored_chars, "");
    return (pg::text) cm_u::sha512(v_normalized_package_state);
}


std::deque<snapshot> get_package_applied_snapshots (
    const package& p_package, const std::vector<pg::text>& p_applied_snapshot_hashes
) {
    if (p_applied_snapshot_hashes.size() == 0)
    {
        return {};
    }
    std::deque<snapshot> v_res = {};
    for (size_t ix = 0; ix < p_applied_snapshot_hashes.size(); ix++)
    {
        if (p_package.snapshots[ix].hash != p_applied_snapshot_hashes[ix])
        {
            throw std::invalid_argument("package integrity exception"); // FIXME
        }
        v_res.emplace_back(p_package.snapshots[ix]);
    }
    return v_res;
}


std::deque<snapshot> get_package_unapplied_snapshots (
    const package& p_package, const std::deque<snapshot>& p_applied_snapshots,
    const pg::text& p_until_hash
) {
    if (p_applied_snapshots.size() == 0)
    {
        return std::deque<snapshot>(p_package.snapshots.begin(), p_package.snapshots.end());
    }
    std::deque<snapshot> v_res = {};
    bool v_found = false;
    for (size_t ix = p_applied_snapshots.size() - 1; ix < p_package.snapshots.size(); ix++)
    {
        v_res.emplace_back(p_package.snapshots[ix]);
        if (p_package.snapshots[ix].hash == p_until_hash)
        {
            v_found = true;
            break;
        }
    }
    if (!v_found)
    {
        throw std::invalid_argument("until snapshot not found"); // FIXME
    }
    return v_res;
}


void check_package_integrity (
    pqxx::work& p_tx, const package& p_package, const std::deque<snapshot>& p_applied_snapshots
) {
    if (p_applied_snapshots.size() == 0)
    {
        return;
    }
    pg::text v_db_integrity_hash = cm_db::get_integrity_hash::query(p_tx, p_package.name);
    if (get_package_integrity_hash(p_package, p_applied_snapshots) != v_db_integrity_hash)
    {
        throw std::invalid_argument("package integrity exception"); // FIXME
    }
}


std::vector<pg::text> determine_package_applied_snapshots (
    pqxx::work& p_tx, const package& p_package
) {
    if (!cm_db::package_procedure_schema_exists::query(p_tx, p_package.procedure_schema_name))
    {
        return {};
    }
    const cm_db::package v_db_package = cm_db::get_package_by_name::query(p_tx, p_package.name);
    return cm_db::get_applied_snapshots::query(p_tx, v_db_package);
}


void core_pg_migrations_apply_snapshot_migrations (
    pqxx::dbtransaction& p_tx, const snapshot& p_snapshot
) {
    std::ostringstream v_message;
    v_message << "Applying snapshot \"" << p_snapshot.hash << "\"..."; cm_u::prompt_notice(v_message);
    for (auto& v_migration : p_snapshot.migrations)
    {
        p_tx.exec(v_migration.upgrade_procedure).no_rows();
        p_tx.exec(v_migration.downgrade_procedure).no_rows();
        v_message << "Calling migration \"" << v_migration.upgrade_procedure_name << "\"..."; cm_u::prompt_notice(v_message);
        p_tx.exec(std::string("CALL ") + v_migration.upgrade_procedure_name + "()").no_rows();
    }
}


void register_execution_snapshot (
    pqxx::dbtransaction& p_tx, const cm_db::execution& p_execution, const snapshot& p_snapshot,
    const pg::text& p_integrity_hash
) {
    std::ostringstream v_message;
    v_message << "Saving snapshot \"" << p_snapshot.hash << "\"..."; cm_u::prompt_notice(v_message);
    const cm_db::snapshot v_db_snapshot = cm_db::create_snapshot::query(
        p_tx, p_execution.package_id, p_snapshot.hash,
        p_snapshot.previous_hash, p_snapshot.next_hash
    );
    for (const auto& v_migration : p_snapshot.migrations)
    {
        v_message << "Saving migration \"" << v_migration.name << "\"..."; cm_u::prompt_notice(v_message);
        const cm_db::migration v_db_migration = cm_db::create_migration::query(
            p_tx, v_db_snapshot, v_migration.name, v_migration.upgrade_procedure_name,
            v_migration.downgrade_procedure_name, v_migration.datafix_name
        );
        const pg::text v_migration_dependencies = ct::tp_to_string(v_migration.dependencies);
        cm_db::register_migration_dependencies::query(p_tx, v_db_migration, v_migration_dependencies);
    }
    v_message << "Saving execution integrity hash: \"" << p_integrity_hash << "\"..."; cm_u::prompt_notice(v_message);
    cm_db::register_execution_snapshot_relation::query(
        p_tx, p_execution, v_db_snapshot, p_integrity_hash
    );
}


void apply_snapshots_on_core_pg_migrations (
    pqxx::work& p_tx, const package& p_package, std::deque<snapshot> p_applied,
    std::deque<snapshot> p_unapplied
) {
    std::ostringstream v_message;
    cm_db::package v_db_package;
    const cm_db::execution_action v_action = cm_db::execution_action::upgrade;
    pg::text v_integrity_hash;
    cm_db::execution v_db_execution;
    if (!cm_db::package_procedure_schema_exists::query(p_tx, p_package.procedure_schema_name))
    {
        v_message << "Detected first upgrade of \"" << p_package.name << "\"..."; cm_u::prompt_notice(v_message);
        p_tx.exec(std::string("CREATE SCHEMA ") + cm_u::identifier(p_tx, p_package.procedure_schema_name)).no_rows();
        const snapshot v_snapshot = p_unapplied.front();
        p_unapplied.pop_front();
        p_applied.emplace_back(v_snapshot);
        core_pg_migrations_apply_snapshot_migrations(p_tx, v_snapshot);
        v_message << "Creating \"" << p_package.name << "\" package..."; cm_u::prompt_notice(v_message);
        v_db_package = cm_db::create_package::query(
            p_tx, p_package.name, p_package.remote_name, p_package.tracked_branch_name,
            p_package.schema_name, p_package.procedure_schema_name
        );
        v_integrity_hash = get_package_integrity_hash(p_package, p_applied);
        v_db_execution = cm_db::create_execution::query(p_tx, std::as_const(v_db_package), v_action);
        register_execution_snapshot(p_tx, v_db_execution, v_snapshot, v_integrity_hash);
    }
    else
    {
        v_db_package = cm_db::get_package_by_name::query(p_tx, p_package.name);
        v_db_execution = cm_db::create_execution::query(p_tx, std::as_const(v_db_package), v_action);
    }
    while(p_unapplied.size() > 0)
    {
        try
        {
            const snapshot v_snapshot = p_unapplied.front();
            p_unapplied.pop_front();
            p_applied.emplace_back(v_snapshot);
            pqxx::subtransaction v_tx_sub(p_tx, std::string("create_snapshot_") + v_snapshot.hash);
            v_integrity_hash = get_package_integrity_hash(p_package, p_applied);
            core_pg_migrations_apply_snapshot_migrations(v_tx_sub, v_snapshot);
            register_execution_snapshot(
                v_tx_sub, v_db_execution, v_snapshot, v_integrity_hash
            );
            v_tx_sub.commit();
        }
        catch (std::exception& e)
        {
            v_message << e.what(); cm_u::prompt_error(v_message);
            break;
        }
    }
}


void apply_snapshots_on_package (
    pqxx::dbtransaction& p_tx, const package& p_package, std::deque<snapshot> p_applied,
    std::deque<snapshot> p_unapplied
) {
//     for(pg::int8 ix = p_start_index; ix < p_package.snapshots.size(); ix++)
//     {
//         
//     }
}


void apply_package_snapshots_until_hash (
    pqxx::connection& p_conn, const package& p_package, const pg::text& p_until_hash
) {
    std::ostringstream v_message;
    v_message << "Upgrading package \"" << p_package.name << "\"..."; cm_u::prompt_notice(v_message);
    pqxx::work v_tx(p_conn);
    v_tx.exec(std::string("SET search_path TO ") + p_package.schema_name + ", " + p_package.procedure_schema_name).no_rows();
    std::vector<pg::text> v_applied_snapshot_hashes = determine_package_applied_snapshots(v_tx, p_package);
    if (std::find(v_applied_snapshot_hashes.begin(), v_applied_snapshot_hashes.end(), p_until_hash) != v_applied_snapshot_hashes.end())
    {
        throw std::invalid_argument("Requested snapshot already applied");
    }
    std::deque<snapshot> v_applied_snapshots = get_package_applied_snapshots(p_package, v_applied_snapshot_hashes);
    std::deque<snapshot> v_unapplied_snapshots = get_package_unapplied_snapshots(p_package, v_applied_snapshots, p_until_hash);
    check_package_integrity(v_tx, p_package, v_applied_snapshots);
    if (p_package.name == "core_pg_migrations")
    {
        apply_snapshots_on_core_pg_migrations(
            v_tx, p_package, v_applied_snapshots, v_unapplied_snapshots
        );
    }
    else
    {
        apply_snapshots_on_package(
            v_tx, p_package, v_applied_snapshots, v_unapplied_snapshots
        );
    }
    v_tx.commit();
}

}
