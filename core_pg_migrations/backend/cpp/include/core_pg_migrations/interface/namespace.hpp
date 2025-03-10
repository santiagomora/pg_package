#ifndef CORE_PG_MIGRATIONS_INTERFACE_NAMESPACE
#define CORE_PG_MIGRATIONS_INTERFACE_NAMESPACE
#include "core_pg_migrations/backend/namespace.hpp"


namespace pg = core_pg_bindings;
namespace ct_i = core_types;


namespace core_pg_migrations::backend::interface
{
    IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_MIGRATION);
    IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_SNAPSHOT);
    IFACE_CPP_CLASSDEF_DECLARATION(CORE_PG_MIGRATIONS_BK_PACKAGE);
}


namespace core_pg_migrations::backend::interface
{
void apply_package_snapshots_until_hash (
    const pg::text& p_dsn, const package& p_package, const pg::text& p_until_hash
);
}

#endif
