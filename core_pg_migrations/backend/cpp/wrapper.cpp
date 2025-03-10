#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include "core_pg_migrations/interface/namespace.hpp"
#include "core_pg_migrations/util.hpp"


namespace py = pybind11;
namespace cm_bk_i = core_pg_migrations::backend::interface;
namespace cm_u_i = core_pg_migrations::util::interface;


CT_CLASSDEF_REGISTER_SUBCLASS_REG(CORE_PG_MIGRATIONS_BK_MIGRATION);
CT_CLASSDEF_REGISTER_SUBCLASS_REG(CORE_PG_MIGRATIONS_BK_SNAPSHOT);
CT_CLASSDEF_REGISTER_SUBCLASS_REG(CORE_PG_MIGRATIONS_BK_PACKAGE);


PYBIND11_MODULE (backend_wrapper, m) 
{
    CT_CLASSDEF_REGISTER_INSTANCEABLE(CORE_PG_MIGRATIONS_BK_MIGRATION, m);
    CT_CLASSDEF_REGISTER_INSTANCEABLE(CORE_PG_MIGRATIONS_BK_SNAPSHOT, m);
    CT_CLASSDEF_REGISTER_INSTANCEABLE(CORE_PG_MIGRATIONS_BK_PACKAGE, m);
    m.def("prompt_error", py::overload_cast<const std::string&, const std::optional<std::string>&>(&cm_u_i::prompt_error));
    m.def("prompt_notice", py::overload_cast<const std::string&>(&cm_u_i::prompt_notice));
    // m.def("setup_core_pg_migrations_in_database", &cm_bk_i::setup_core_pg_migrations_in_database);
    // m.def("get_applied_snapshots", &cm_bk_i::get_applied_snapshots);
    // m.def("apply_package_snapshots_until_hash", &cm_bk_i::apply_package_snapshots_until_hash);
    // m.def("determine_package_unapplied_snapshot_range", &cm_bk_i::determine_package_unapplied_snapshot_range);
    m.def("apply_package_snapshots_until_hash", &cm_bk_i::apply_package_snapshots_until_hash);
}

