#include "core_pg_migrations/interface/namespace.hpp"
#include "core_pg_migrations/util.hpp"


namespace cm_bk  = core_pg_migrations::backend;
namespace cm_bk_i = cm_bk::interface;
namespace cm_u  = core_pg_migrations::util;
namespace cm_u_i  = cm_u::interface;
namespace cm_db_i = core_pg_migrations::database::interface;
namespace pg = core_pg_bindings;


namespace core_pg_migrations::backend::interface
{

void apply_package_snapshots_until_hash (
    const pg::text& p_dsn, const package& p_package, const pg::text& p_until_hash
) {
    std::ostringstream v_message;
    cm_bk::package v_package = p_package.wrapped();
    try
    {
        pqxx::connection v_conn(p_dsn);
        cm_bk::apply_package_snapshots_until_hash(v_conn, v_package, p_until_hash);
    }
    catch (const std::exception& e)
    {
        v_message << "Error when attempting to upgrade package \"" << v_package.name << "\"..."  << std::endl;
        cm_u_i::prompt_error(v_message.str(), e.what());
    }
}

}
