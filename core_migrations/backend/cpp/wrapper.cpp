#include <pybind11/pybind11.h>
#include "core_migrations/backend/prompt.hpp"


namespace py = pybind11;
namespace cm = core_migrations;


PYBIND11_MODULE (wrapper, m) 
{
    m.def("prompt_error", &cm::prompt_error);
    m.def("prompt_notice", &cm::prompt_notice);
}

