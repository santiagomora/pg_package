#include "core_pg_migrations/backend/namespace.hpp"
#include "core_pg_migrations/database/namespace.hpp"
#include "core_pg_migrations/util.hpp"
#include <stdexcept>
#include <iostream>
#include <sstream>


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
    // return (pg::text) sha512(ct::to_str(v_hash_tuple));
    std::regex v_ignored_chars("( |\n|\t)+");
    std::string v_normalized_package_state = std::regex_replace(ct::to_str(v_hash_tuple), v_ignored_chars, "");
    return (pg::text) cm_u::sha512(v_normalized_package_state);
}


void check_package_integrity (
    pqxx::work& p_tx, const package& p_package, const std::deque<snapshot>& p_applied_snapshots,
    const std::vector<pg::text>& p_applied_snapshot_hashes
) {
    // FIXME show failing hashes
    if (p_applied_snapshots.size() == 0)
    {
        return;
    }
    size_t ix = 0;
    for (const snapshot& v_snapshot : p_applied_snapshots)
    {
        if (v_snapshot.hash != p_applied_snapshot_hashes[ix++])
        {
            throw std::invalid_argument("Package integrity exception. Repository snapshot hash does not match database hash.");
        }
    }
    pg::text v_db_integrity_hash = cm_db::get_package_integrity_hash_at_snapshot::query(
        p_tx, p_package.name, p_applied_snapshots.back().hash
    );
    if (get_package_integrity_hash(p_package, p_applied_snapshots) != v_db_integrity_hash)
    {
        throw std::invalid_argument("Package integrity exception. Repository calculated integrity hash does not match database integrity hash.");
    }
}


size_t get_snapshot_index_by_hash (
    std::string p_snapshot_hash, std::deque<snapshot> p_list
) {
    ssize_t v_res = -1; size_t ix = 0;
    for (const snapshot& v_snapshot : p_list)
    {
        v_res = (v_snapshot.hash == p_snapshot_hash) ? ix : v_res;
        if (v_res >= 0) break;
    }
    if (v_res < 0)
    {
        throw std::invalid_argument("Hash not found in snapshot list...");
    }
    return (size_t) v_res;
}


std::vector<pg::text> determine_package_applied_snapshots (
    pqxx::work& p_tx, const package& p_package
) {
    if (!cm_db::schema_exists::query(p_tx, p_package.procedure_schema_name))
    {
        return {};
    }
    return cm_db::get_applied_snapshots::query(p_tx, p_package.name);
}


std::tuple<std::deque<snapshot>, std::deque<snapshot>> get_request_snapshot_list (
    pqxx::work& p_tx, const package& p_package, const std::string& p_hash,
    const cm_db::execution_action& p_action
) {
    std::vector<pg::text> v_applied_snapshot_hashes = determine_package_applied_snapshots(p_tx, p_package);
    std::deque<snapshot> v_applied_snapshots = std::deque<snapshot>(
        p_package.snapshots.begin(), p_package.snapshots.begin() + v_applied_snapshot_hashes.size()
    );
    std::deque<snapshot> v_unapplied_snapshots;
    size_t v_request_snapshot_position;
    switch (p_action)
    {
        case cm_db::execution_action::upgrade:
        {
            v_unapplied_snapshots = std::deque<snapshot>(
                p_package.snapshots.begin() + v_applied_snapshot_hashes.size(), p_package.snapshots.end()
            );
            check_package_integrity(p_tx, p_package, v_applied_snapshots, v_applied_snapshot_hashes);
            v_request_snapshot_position = get_snapshot_index_by_hash(p_hash, v_unapplied_snapshots);
            v_unapplied_snapshots = std::deque<snapshot>(
                v_unapplied_snapshots.begin(), v_unapplied_snapshots.begin() + v_request_snapshot_position + 1
            );
            break;
        }
        case cm_db::execution_action::downgrade:
        {
            v_request_snapshot_position = get_snapshot_index_by_hash(p_hash, v_applied_snapshots);
            v_applied_snapshots = std::deque<snapshot>(
                p_package.snapshots.begin(), p_package.snapshots.begin() + v_request_snapshot_position
            );
            check_package_integrity(p_tx, p_package, v_applied_snapshots, v_applied_snapshot_hashes);
            v_unapplied_snapshots = std::deque<snapshot>(
                p_package.snapshots.begin() + v_request_snapshot_position, p_package.snapshots.end()
            );
            break;
        }
    }
    return std::make_tuple(v_applied_snapshots, v_unapplied_snapshots);
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
        v_message << "Calling migration \"" << v_migration.upgrade_procedure_name << "\" upgrade script..."; cm_u::prompt_notice(v_message);
        p_tx.exec(std::string("CALL ") + v_migration.upgrade_procedure_name + "()").no_rows();
    }
}


void register_snapshot_migrations (
    pqxx::dbtransaction& p_tx, const cm_db::snapshot& p_db_snapshot, const std::vector<migration>& p_migrations
) {
    std::vector<pg::int8> v_db_migration_ids;
    std::ostringstream v_message;
    pg::int8 v_added = 0;
    for (const auto& v_migration : p_migrations)
    {
        v_message << "Saving migration \"" << v_migration.name << "\"..."; cm_u::prompt_notice(v_message);
        const cm_db::migration v_db_migration = cm_db::create_or_update_migration::query(
            p_tx, p_db_snapshot, v_migration.name, v_migration.upgrade_procedure_name,
            v_migration.downgrade_procedure_name, v_migration.datafix_name, std::as_const(v_added)
        );
        const pg::text v_migration_dependencies = ct::to_str(v_migration.dependencies);
        cm_db::synchronize_migration_dependencies::query(p_tx, v_db_migration, v_migration_dependencies);
        v_db_migration_ids.emplace_back(v_db_migration.id);
        v_added ++;
    }
    const pg::text v_db_migration_ids_str = ct::to_str(v_db_migration_ids);
    cm_db::keep_snapshot_migration_ids::query(p_tx, p_db_snapshot, v_db_migration_ids_str);
}


void set_search_path_for_package(
    pqxx::work& p_tx, const package& p_package
) {
    std::ostringstream v_search_path;
    v_search_path << "SET search_path TO ";
    v_search_path << p_package.schema_name << ", " << p_package.procedure_schema_name;
    if (p_package.schema_name != "core_pg_migrations")
    {
        v_search_path << ", " << "core_pg_migrations";
    }
    p_tx.exec(v_search_path.str()).no_rows();
}


void apply_snapshots_on_core_pg_migrations (
    pqxx::work& p_tx, const package& p_package, std::deque<snapshot> p_applied,
    std::deque<snapshot> p_unapplied, const cm_db::execution_action& p_action
) {
    // p_applied represents the snapshots applied in the database
    // p_unapplied represents the to be applied in the database
    std::ostringstream v_message;
    cm_db::package v_db_package;
    pg::text v_integrity_hash;
    cm_db::execution v_db_execution;
    cm_db::snapshot v_db_snapshot;
    if (p_applied.size() > 0)
    {
        v_db_package = cm_db::get_package_by_name::query(p_tx, p_package.name);
        v_db_execution = cm_db::create_execution::query(p_tx, std::as_const(v_db_package), p_action);
    }
    else
    {
        v_message << "Detected first upgrade of \"" << p_package.name << "\"..."; cm_u::prompt_notice(v_message);
        p_tx.exec(std::string("CREATE SCHEMA ") + cm_u::identifier(p_tx, p_package.procedure_schema_name)).no_rows();
        const snapshot v_snapshot = p_unapplied.front();
        p_unapplied.pop_front();
        p_applied.emplace_back(v_snapshot);
        core_pg_migrations_apply_snapshot_migrations(p_tx, v_snapshot);
        v_message << "Creating \"" << p_package.name << "\" package..."; cm_u::prompt_notice(v_message);
        v_db_package = cm_db::create_or_update_package::query(
            p_tx, p_package.name, p_package.remote_name, p_package.tracked_branch_name,
            p_package.schema_name, p_package.procedure_schema_name
        );
        v_integrity_hash = get_package_integrity_hash(p_package, p_applied);
        v_db_execution = cm_db::create_execution::query(p_tx, std::as_const(v_db_package), p_action);
        v_message << "Saving snapshot \"" << v_snapshot.hash << "\"..."; cm_u::prompt_notice(v_message);
        v_db_snapshot = cm_db::create_or_update_snapshot::query(
            p_tx, std::as_const(v_db_execution.package_id), v_snapshot.hash,
            v_snapshot.previous_hash, v_snapshot.next_hash
        );
        register_snapshot_migrations(p_tx, v_db_snapshot, v_snapshot.migrations);
        v_message << "Saving execution integrity hash: \"" << v_integrity_hash << "\"..."; cm_u::prompt_notice(v_message);
        cm_db::register_execution_snapshot_relation::query(
            p_tx, std::as_const(v_db_execution), std::as_const(v_db_snapshot), std::as_const(v_integrity_hash)
        );
    }
    while (p_unapplied.size() > 0)
    {
        try
        {
            const snapshot v_snapshot = p_unapplied.front();
            p_unapplied.pop_front();
            p_applied.emplace_back(v_snapshot);
            pqxx::subtransaction v_tx_sub(p_tx, std::string("apply_snapshot_") + v_snapshot.hash);
            v_integrity_hash = get_package_integrity_hash(p_package, p_applied);
            core_pg_migrations_apply_snapshot_migrations(v_tx_sub, v_snapshot);
            v_message << "Saving snapshot \"" << v_snapshot.hash << "\"..."; cm_u::prompt_notice(v_message);
            v_db_snapshot = cm_db::create_or_update_snapshot::query(
                v_tx_sub, std::as_const(v_db_execution.package_id), v_snapshot.hash,
                v_snapshot.previous_hash, v_snapshot.next_hash
            );
            register_snapshot_migrations(v_tx_sub, v_db_snapshot, v_snapshot.migrations);
            v_message << "Saving execution integrity hash: \"" << v_integrity_hash << "\"..."; cm_u::prompt_notice(v_message);
            cm_db::register_execution_snapshot_relation::query(
                v_tx_sub, std::as_const(v_db_execution), std::as_const(v_db_snapshot), std::as_const(v_integrity_hash)
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


// void apply_snapshots_on_package (
//     pqxx::dbtransaction& p_tx, const package& p_package, std::deque<snapshot> p_applied,
//     std::deque<snapshot> p_unapplied
// ) {
//     
// }


void upgrade_to_package_snapshot_hash (
    pqxx::work& p_tx, const package& p_package, const pg::text& p_hash
) {
    std::ostringstream v_message;
    v_message << "Upgrading package \"" << p_package.name << "\"..."; cm_u::prompt_notice(v_message);
    std::deque<snapshot> v_applied_snapshots, v_unapplied_snapshots;
    cm_db::execution_action v_action = cm_db::execution_action::upgrade;
    std::tie(v_applied_snapshots, v_unapplied_snapshots) = get_request_snapshot_list(
        p_tx, p_package, p_hash, v_action
    );
    if (p_package.name == "core_pg_migrations")
    {
        apply_snapshots_on_core_pg_migrations(
            p_tx, p_package, v_applied_snapshots, v_unapplied_snapshots, v_action
        );
    }
    else
    {
        // apply_snapshots_on_package(
        //     p_tx, p_package, v_applied_snapshots, v_unapplied_snapshots
        // );
    }
}


void core_pg_migrations_unapply_snapshot_migrations (
    pqxx::dbtransaction& p_tx, const cm_db::snapshot& p_db_snapshot, const cm_db::execution_action& p_action
) {
    std::ostringstream v_message;
    v_message << "Unapplying snapshot \"" << p_db_snapshot.commit_hash << "\"..."; cm_u::prompt_notice(v_message);
    std::vector<cm_db::migration> v_db_migrations = cm_db::get_snapshot_migrations::query(p_tx, p_db_snapshot, p_action);
    for (auto& v_db_migration : v_db_migrations)
    {
        v_message << "Calling migration \"" << v_db_migration.downgrade_script_name << "\" downgrade procedure..."; cm_u::prompt_notice(v_message);
        p_tx.exec(std::string("CALL ") + v_db_migration.downgrade_script_name + "()").no_rows();
    }
}


void unapply_snapshots_from_core_pg_migrations (
    pqxx::work& p_tx, const package& p_package, std::deque<snapshot> p_applied,
    std::deque<snapshot> p_unapply, const cm_db::execution_action& p_action
) {
    // p_applied represents the snapshots that remain applied in the database
    // p_unapplied represents the snapshots to be unapplied from the database
    p_applied.insert(p_applied.end(), p_unapply.begin(), p_unapply.end());
    if (p_applied.size() == 0)
    {
        throw std::invalid_argument("Package must exist in database to apply downgrade...");
    }
    std::ostringstream v_message;
    const cm_db::package v_db_package = cm_db::get_package_by_name::query(p_tx, p_package.name);
    const cm_db::execution v_db_execution = cm_db::create_execution::query(p_tx, v_db_package, p_action);
    // here p_applied represents the applied snapshots of the database
    while (p_unapply.size() > 0)
    {
        try
        {
            const snapshot v_snapshot = p_applied.back();
            p_applied.pop_back();
            p_unapply.pop_back();
            const pg::text v_integrity_hash = get_package_integrity_hash(p_package, p_applied);
            pqxx::subtransaction v_tx_sub(p_tx, std::string("unapply_snapshot_") + v_snapshot.hash);
            const cm_db::snapshot v_db_snapshot = cm_db::get_snapshot_by_commit_hash::query(v_tx_sub, v_snapshot.hash);
            core_pg_migrations_unapply_snapshot_migrations(v_tx_sub, v_db_snapshot, p_action);
            if (cm_db::schema_exists::query(p_tx, p_package.schema_name))
            {
                v_message << "Saving execution integrity hash: \"" << v_integrity_hash << "\"..."; cm_u::prompt_notice(v_message);
                cm_db::register_execution_snapshot_relation::query(
                    v_tx_sub, v_db_execution, v_db_snapshot, v_integrity_hash
                );
            }
            else
            {
                v_message << "Package: \"" << p_package.name << "\" removed. Destroying procedure schema...";
                cm_u::prompt_notice(v_message);
                p_tx.exec(std::string("DROP SCHEMA ") + cm_u::identifier(p_tx, p_package.procedure_schema_name) + " CASCADE").no_rows();
            }
            v_tx_sub.commit();
        }
        catch (std::exception& e)
        {
            v_message << e.what(); cm_u::prompt_error(v_message);
            break;
        }
    }
}


// void unapply_snapshots_on_package (
//     pqxx::dbtransaction& p_tx, const package& p_package, std::deque<snapshot> p_applied,
//     std::deque<snapshot> p_unapplied
// ) {
//     
// }


void downgrade_to_package_snapshot_hash (
    pqxx::work& p_tx, const package& p_package, const pg::text& p_hash
) {
    std::ostringstream v_message;
    v_message << "Downgrading package \"" << p_package.name << "\"..."; cm_u::prompt_notice(v_message);
    std::deque<snapshot> v_applied_snapshots, v_unapplied_snapshots;
    cm_db::execution_action v_action = cm_db::execution_action::downgrade;
    std::tie(v_applied_snapshots, v_unapplied_snapshots) = get_request_snapshot_list(
        p_tx, p_package, p_hash, v_action
    );
    if (p_package.name == "core_pg_migrations")
    {
        unapply_snapshots_from_core_pg_migrations(
            p_tx, p_package, v_applied_snapshots, v_unapplied_snapshots, v_action
        );
    }
    else
    {
        // unapply_snapshots_from_package(
        //     p_tx, p_package, v_applied_snapshots, v_unapplied_snapshots, v_action
        // );
    }
}

}
