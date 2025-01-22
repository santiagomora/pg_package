#include <pybind11/pybind11.h>

#include "../include/types.hpp"


namespace py = pybind11;


py::object mgr::package::cls = py::cast<py::none>(Py_None);
py::object mgr::execution::cls = py::cast<py::none>(Py_None);
py::object mgr::migration::cls = py::cast<py::none>(Py_None);
py::object mgr::migration_execution::cls = py::cast<py::none>(Py_None);
