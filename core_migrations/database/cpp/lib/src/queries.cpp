#include "core_migrations/database/queries.hpp"


namespace pg        = core_pg_bindings;
namespace cm_db_dec = core_migrations::database::declarations;
namespace cm_db_q = core_migrations::database::queries;


void cm_db_q::register_execution::operator() (
    pqxx::work& p_tx, cm_db_dec::execution& p_execution, std::vector<pg::text>& p_commit_hashes,
    std::vector<pg::text>& p_migration_names
) {
    cm_db_q::register_execution_commit_hash rech;
    cm_db_q::register_execution_migration rem;
    cm_db_q::create_migration cm;
    // FIXME this must be done through array_traits specialization, calling a database function specific for this
    // but array_traits macro is not created yet
    for(pg::text hash : p_commit_hashes)
    {
        rech(p_tx, p_execution, hash);
    }
    for(pg::text name : p_migration_names)
    {
        cm_db_dec::migration v_migration = cm(p_tx, p_execution, name, std::nullopt);
        rem(p_tx, p_execution, v_migration);
    }
}
