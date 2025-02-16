#include "core_migrations/backend/prompt.hpp"
#include "core_types/typing/types.hpp"
#include <memory>


namespace ct = core_types;
namespace cm = core_migrations;


void cm::prompt_notice(const std::string& notice)
{
    std::shared_ptr<ct::timestamptz> now = ct::timestamptz::utcnow();
    std::cout << "[NOTICE - " << now->to_string("%Y-%m-%dT%H:%M:%S") << "] " << notice << std::endl;
}


void cm::prompt_error(const std::string& error, const std::string& traceback)
{
    std::shared_ptr<ct::timestamptz> now = ct::timestamptz::utcnow();
    std::cout << "[ERROR - " << now->to_string("%Y-%m-%dT%H:%M:%S") << "] " << error << std::endl;
    std::cout << traceback << std::endl;
}


// void prompt_server_notice(const std::string& notice)
// {
//     now = datetime.now(timezone.utc)
//     sys.stdout.write(f"[SERVER - {now.isoformat()}] {diag.severity} - {diag.message_primary}\n")
// 
//     void prompt_notice(const std::string&);
//     void prompt_server_notice(const std::string&);
//     void prompt_error(const std::string&);
// }
