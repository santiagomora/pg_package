#include <pybind11/pybind11.h>

#include "mgr_manager/types.hpp"
#include "pg_definition/macros/register.hpp"


namespace py = pybind11;


PYBIND11_MODULE(wrapper, m) {
    PG_PY_ENUM_REGISTER(PG_PACKAGE_EXECUTION_ACTION, m);
    PG_PY_TABLE_REGISTER(PG_PACKAGE_PACKAGE, m);
    PG_PY_TABLE_REGISTER(PG_PACKAGE_EXECUTION, m);
    PG_PY_TABLE_REGISTER(PG_PACKAGE_MIGRATION, m);
    PG_PY_TABLE_REGISTER(PG_PACKAGE_MIGRATION_EXECUTION, m);
}

