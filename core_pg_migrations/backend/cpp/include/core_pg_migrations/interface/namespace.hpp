#ifndef CORE_PG_MIGRATIONS_INTERFACE_NAMESPACE
#define CORE_PG_MIGRATIONS_INTERFACE_NAMESPACE
#include "core_pg_migrations/backend/namespace.hpp"


namespace core_pg_migrations::backend::interface
{
    IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_MIGRATION);
    IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_SNAPSHOT);
    IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_PACKAGE);
}


namespace core_pg_migrations::backend::interface
{
void upgrade_to_package_snapshot_hash (
    const pg::text& p_dsn, const package& p_package, const pg::text& p_hash
);
void downgrade_to_package_snapshot_hash (
    const pg::text& p_dsn, const package& p_package, const pg::text& p_hash
);
std::deque<snapshot> get_unapplied_package_snapshots_for_upgrade_dry_run (
    const pg::text& p_dsn, const package& p_package, const pg::text& p_hash
);
std::deque<snapshot> get_applied_package_snapshots_for_downgrade_dry_run (
    const pg::text& p_dsn, const package& p_package, const pg::text& p_hash
);
}


namespace cm_bk_i = core_pg_migrations::backend::interface;
namespace ct_i = core_types::interface;

#endif
