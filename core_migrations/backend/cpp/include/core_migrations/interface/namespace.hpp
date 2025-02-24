#ifndef CORE_MIGRATIONS_BACKEND_INTERFACE_NAMESPACE
#define CORE_MIGRATIONS_BACKEND_INTERFACE_NAMESPACE
#include "core_migrations/interface/_definitions.hpp"
#include <pqxx/pqxx>


namespace core_migrations::backend
{
/*
 * NOTE TYPES
 */
CPP_CLASSDEF_DECLARATION(CORE_MIGRATIONS_BACKEND_INTERFACE_SETUP_PARAMETERS);
}

namespace core_migrations::backend::interface
{
/*
 * NOTE TYPES
 */
IFACE_CPP_CLASSDEF_DECLARATION(CORE_MIGRATIONS_BACKEND_INTERFACE_SETUP_PARAMETERS);
/*
 * NOTE SETUP ENTRY
 * For the setup we need to create and run the migration script and then:
 * 1. register the core_migrations package
 * 2. register the execution
 * 3. register the commits involved in the execution
 * 4. register the migrations involved in the execution
 */
void setup_core_migrations_in_database(setup_parameters& p_params, std::string& p_db_dsn);
}

#endif
