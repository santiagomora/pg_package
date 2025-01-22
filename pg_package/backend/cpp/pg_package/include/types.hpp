#ifndef MGR_TYPES
#define MGR_TYPES


#include "./definitions.hpp"

// DEBUG clear && g++ -P -E -I/usr/include/boost -I../../../../../base_types/cpp -I./ -I../../../../../../pg_definition/venv/lib/python3.12/site-packages/pybind11/include wrapper.cpp

namespace mgr {

CPP_ENUM(MGR_EXECUTION_ACTION);
CPP_DATACLASS(MGR_PACKAGE);
CPP_DATACLASS(MGR_EXECUTION);
CPP_DATACLASS(MGR_MIGRATION);
CPP_DATACLASS(MGR_MIGRATION_EXECUTION);

}


#endif
