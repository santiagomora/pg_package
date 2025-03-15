#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include "core_pg_migrations/interface/namespace.hpp"
#include "core_pg_migrations/util.hpp"


PYBIND11_MODULE (backend_wrapper, m) 
{
    CT_CLASSDEF_REGISTER_INSTANCEABLE(CORE_PG_MIGRATIONS_BK_MIGRATION, m);
    CT_CLASSDEF_REGISTER_INSTANCEABLE(CORE_PG_MIGRATIONS_BK_SNAPSHOT, m);
    CT_CLASSDEF_REGISTER_INSTANCEABLE(CORE_PG_MIGRATIONS_BK_PACKAGE, m);
    m.def("prompt_error", [](const std::string& p_error, const std::optional<std::string>& p_traceback){
        return cm_u_i::prompt_error(p_error, p_traceback);
    });
    m.def("prompt_notice", [](const std::string& p_notice){
        return cm_u_i::prompt_notice(p_notice);
    });
    m.def("upgrade_to_package_snapshot_hash", [](
        const pg::text& p_dsn, const cm_bk_i::package& p_package, const pg::text& p_hash
    ){
        cm_bk_i::upgrade_to_package_snapshot_hash(p_dsn, p_package, p_hash);
    });
    m.def("downgrade_to_package_snapshot_hash", [](
        const pg::text& p_dsn, const cm_bk_i::package& p_package, const pg::text& p_hash
    ) {
        cm_bk_i::downgrade_to_package_snapshot_hash(p_dsn, p_package, p_hash);
    });
    m.def("get_unapplied_package_snapshots_for_upgrade_dry_run", [](
        const pg::text& p_dsn, const cm_bk_i::package& p_package, const pg::text& p_hash
    ) {
        return ct_i::to_py(cm_bk_i::get_unapplied_package_snapshots_for_upgrade_dry_run(p_dsn, p_package, p_hash));
    });
    m.def("get_applied_package_snapshots_for_downgrade_dry_run", [](
        const pg::text& p_dsn, const cm_bk_i::package& p_package, const pg::text& p_hash
    ) {
        return ct_i::to_py(cm_bk_i::get_applied_package_snapshots_for_downgrade_dry_run(p_dsn, p_package, p_hash));
    });
}

