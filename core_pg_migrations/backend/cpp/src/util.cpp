#include "core_pg_migrations/util.hpp"


namespace cm_u_i = core_pg_migrations::util::interface;
namespace cm_u  = core_pg_migrations::util;
namespace ct  = core_types;


void cm_u_i::prompt_notice(const std::string& p_notice)
{
    std::ostringstream oss;
    oss << p_notice;
    cm_u::prompt_notice(oss);
}


void cm_u_i::prompt_error(const std::string& p_error, const std::optional<std::string>& p_traceback)
{
    std::ostringstream oss;
    oss << p_error;
    if (p_traceback.has_value()) 
    {
        oss << "\n" << p_traceback.value() << std::endl;
    }
    cm_u::prompt_error(oss);
}


void cm_u::prompt_error(std::ostringstream& p_stream)
{
    ct::timestamptz v_now = ct::utcnow();
    std::cout << "[ERROR - " << ct::tp_to_string(v_now, "%Y-%m-%dT%H:%M:%S") << "] " << p_stream.str() << std::endl;
    p_stream.str("");
    p_stream.clear();
    p_stream.seekp(0);
}


void cm_u::prompt_notice(std::ostringstream& p_stream)
{
    ct::timestamptz v_now = ct::utcnow();
    std::cout << "[NOTICE - " << ct::tp_to_string(v_now, "%Y-%m-%dT%H:%M:%S") << "] " << p_stream.str() << std::endl;
    p_stream.str("");
    p_stream.clear();
    p_stream.seekp(0);
}


std::string cm_u::identifier (const pqxx::work& tx, const std::string& name)
{
    std::regex hasupper("A-Z");
    std::regex begins_with_number("^0-9");
    if (std::regex_search(name, hasupper) || std::regex_search(name, begins_with_number))
    {
        return tx.quote_name(name);
    }
    return name;
}



// void prompt_server_p_notice(const std::string& p_notice)
// {
//     v_now = datetime.v_now(timezone.utc)
//     sys.stdout.write(f"[SERVER - {v_now.isoformat()}] {diag.severity} - {diag.message_primary}\n")
// 
//     void prompt_notice(const std::string&);
//     void prompt_server_p_notice(const std::string&);
//     void prompt_error(const std::string&);
// }

