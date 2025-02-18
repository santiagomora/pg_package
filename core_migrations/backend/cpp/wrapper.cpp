#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "core_migrations/interface/namespace.hpp"
#include "core_migrations/util.hpp"


namespace py = pybind11;
namespace cm_bk_i = core_migrations::backend::interface;
namespace cm_u_i = core_migrations::util::interface;


PYBIND11_MODULE (wrapper, m) 
{
    CT_CLASSDEF_REGISTER_INSTANCEABLE(CORE_MIGRATIONS_BACKEND_INTERFACE_SETUP_PARAMETERS, m);
    m.def("prompt_error", py::overload_cast<const std::string&, const std::optional<std::string>&>(&cm_u_i::prompt_error));
    m.def("prompt_notice", py::overload_cast<const std::string&>(&cm_u_i::prompt_notice));
    m.def("setup_core_migrations_in_database", &cm_bk_i::setup_core_migrations_in_database);
}

