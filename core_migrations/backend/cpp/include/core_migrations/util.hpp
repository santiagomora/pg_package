#ifndef CORE_MIGRATIONS_UTIL
#define CORE_MIGRATIONS_UTIL
#include <pqxx/pqxx>
#include <regex>
#include "core_types/all.hpp"


namespace core_migrations::util::interface
{
/*
 * NOTE PROMPT HELPERS
 */
void prompt_notice(const std::string&);
void prompt_error(const std::string&, const std::optional<std::string>&);
}


namespace core_migrations::util
{
/*
 * NOTE PROMPT HELPERS
 */
void prompt_notice(std::ostringstream&);
void prompt_error(std::ostringstream&);
std::string identifier (
    const pqxx::work& tx, const std::string& name
);
}

#endif
