cmake_minimum_required(VERSION 3.10)

project(core_pg_migrations_db)

set(PYBIND11_FINDPYTHON ON)
set(CMAKE_CXX_STANDARD 20)
set(PYTHON_VERSION 3.12)
set(PYBIND11_PYTHON_VERSION ${PYTHON_VERSION})
set(PYTHON_VENV_PATH $ENV{VIRTUAL_ENV})
set(SGS_INCLUDE_PATH ${PYTHON_VENV_PATH}/include/python${PYTHON_VERSION}/)
set(SGS_LIB_PATH ${PYTHON_VENV_PATH}/lib/python${PYTHON_VERSION}/)
set(pybind11_DIR ${PYTHON_VENV_PATH}/lib/python${PYTHON_VERSION}/site-packages/pybind11/share/cmake/pybind11)
set(CMAKE_CXX_FLAGS "-Wall -Wextra -fPIC -O2 -march=native -flto=auto -Wno-attributes -Wno-deprecated")

find_package(pybind11 REQUIRED)

add_library(${PROJECT_NAME} SHARED
    src/declarations.cpp
)

target_link_directories(${PROJECT_NAME} PRIVATE ${SGS_LIB_PATH})
target_link_directories(${PROJECT_NAME} PRIVATE $ENV{BUILD_TMP_DATA_LIB_DIR})

target_include_directories(${PROJECT_NAME} PRIVATE ${SGS_INCLUDE_PATH})
target_include_directories(${PROJECT_NAME} PRIVATE ./include)
target_include_directories(${PROJECT_NAME} PRIVATE ${PYBIND11_INCLUDE_DIRS})

target_link_libraries(${PROJECT_NAME} PRIVATE pybind11::module)
target_link_libraries(${PROJECT_NAME} PRIVATE core_types)
target_link_libraries(${PROJECT_NAME} PRIVATE core_pg_bindings)
target_link_libraries(${PROJECT_NAME} PRIVATE pqxx)
target_link_libraries(${PROJECT_NAME} PRIVATE pq)
