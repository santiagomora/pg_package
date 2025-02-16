#ifndef CORE_MIGRATIONS_BACKEND_PROMPT
#define CORE_MIGRATIONS_BACKEND_PROMPT
#include <string>


namespace core_migrations
{
    void prompt_notice(const std::string&);
    void prompt_error(const std::string&, const std::string&);
    // void prompt_server_notice(const std::string&);
}

#endif
