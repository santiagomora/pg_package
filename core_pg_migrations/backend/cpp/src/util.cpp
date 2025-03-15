#include <openssl/sha.h>
#include <iomanip>
#include <sstream>
#include "core_pg_migrations/util.hpp"


namespace cm_u_i = core_pg_migrations::util::interface;
namespace cm_u  = core_pg_migrations::util;
namespace ct  = core_types;


namespace core_pg_migrations::util
{
void prompt_error (
    std::ostringstream& p_stream
) {
    ct::timestamptz v_now = ct::utcnow();
    std::cout << "[ERROR - " << ct::to_str(v_now, "%Y-%m-%dT%H:%M:%S") << "] " << p_stream.str() << std::endl;
    p_stream.str("");
    p_stream.clear();
    p_stream.seekp(0);
}


void prompt_notice (
    std::ostringstream& p_stream
) {
    ct::timestamptz v_now = ct::utcnow();
    std::cout << "[NOTICE - " << ct::to_str(v_now, "%Y-%m-%dT%H:%M:%S") << "] " << p_stream.str() << std::endl;
    p_stream.str("");
    p_stream.clear();
    p_stream.seekp(0);
}


std::string identifier (
    const pqxx::work& tx, const std::string& name
) {
    std::regex hasupper("A-Z");
    std::regex begins_with_number("^0-9");
    if (std::regex_search(name, hasupper) || std::regex_search(name, begins_with_number))
    {
        return tx.quote_name(name);
    }
    return name;
}


std::string sha512(
    const std::string& data
) {
    unsigned char hash[SHA512_DIGEST_LENGTH];
    SHA512(reinterpret_cast<const unsigned char*>(data.c_str()), data.size(), hash);
    std::stringstream ss;
    for (unsigned char c : hash)
    {
        ss << std::hex << std::setw(2) << std::setfill('0') << (int)c;
    }
    return ss.str();
}

}


namespace core_pg_migrations::util::interface
{

void prompt_notice (
    const std::string& p_notice
) {
    std::ostringstream oss;
    oss << p_notice;
    cm_u::prompt_notice(oss);
}


void prompt_error (
    const std::string& p_error, const std::optional<std::string>& p_traceback
) {
    std::ostringstream oss;
    oss << p_error;
    if (p_traceback.has_value())
    {
        oss << std::endl << p_traceback.value() << std::endl;
    }
    cm_u::prompt_error(oss);
}

}






// void prompt_server_p_notice(
//    const std::string& p_notice
//) {
//     v_now = datetime.v_now(timezone.utc)
//     sys.stdout.write(f"[SERVER - {v_now.isoformat()}] {diag.severity} - {diag.message_primary}\n")
// 
//     void prompt_notice(const std::string&);
//     void prompt_server_p_notice(const std::string&);
//     void prompt_error(const std::string&);
// }

