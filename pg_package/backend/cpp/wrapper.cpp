

#include <pybind11/pybind11.h>
#include "pg_package/include/types.hpp"
#include "pg_package/include/definitions.hpp"
#include "base_types/include/macros/register.hpp"


namespace py = pybind11;


PYBIND11_MODULE(wrapper, m) {
    PY_ENUM_REGISTER(MGR_EXECUTION_ACTION, m);
    PY_DATACLASS_REGISTER(MGR_PACKAGE, m);
    PY_DATACLASS_REGISTER(MGR_EXECUTION, m);
    PY_DATACLASS_REGISTER(MGR_MIGRATION, m);
    PY_DATACLASS_REGISTER(MGR_MIGRATION_EXECUTION, m);
}

