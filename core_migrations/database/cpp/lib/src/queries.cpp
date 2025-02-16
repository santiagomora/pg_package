#include "core_pg_bindings/typing/types.hpp"
#include "core_pg_bindings/execution/invokable.hpp"
#include "core_migrations/database/interface/types.hpp"
#include "core_migrations/database/interface/queries.hpp"


namespace cm = core_migrations::database::interface;
namespace pg = core_pg_bindings;


std::optional<pg::db_environment> cm::environment::_env = std::nullopt;


pg::db_environment& cm::environment::env ()
{
    if (!cm::environment::_env.has_value()){
        cm::environment::_env = pg::db_environment("host=172.18.0.1 dbname=mutzhub port=5432 user=mutzhub password=WtbNMMpX46iynzjVobrh8Qu7omvFIL9JEvbkLYYCpCJNIwDWnBwcVquhk6vXe6En", "core_migrations");
    }
    return cm::environment::_env.value();
}


// NOTE QUERIES
std::shared_ptr<pg::query_configuration> cm::create_execution::query_config () const
{
    return std::make_shared<pg::query_configuration>(
        "SELECT create_execution(\
            p_package := $1,\
            p_commit_hash := $2,\
            p_action := $3)", cm::environment::env()
    );
}


std::shared_ptr<pg::query_configuration> cm::register_execution_commit_hash::query_config () const
{
    return std::make_shared<pg::query_configuration>(
        "SELECT register_execution_commit_hash(\
            p_execution := $1,\
            p_commit_hash := $2)", cm::environment::env()
    );
}


std::shared_ptr<pg::query_configuration> cm::register_execution_migration::query_config () const
{
    return std::make_shared<pg::query_configuration>(
        "SELECT register_execution_migration(\
            p_execution := $1,\
            p_migration := $2)", cm::environment::env()
    );
}


std::shared_ptr<pg::query_configuration> cm::create_migration::query_config () const
{
    return std::make_shared<pg::query_configuration>(
        "SELECT create_migration(\
            p_execution := $1,\
            p_name := $2,\
            p_datafix_name := $3)", cm::environment::env()
    );
}


std::shared_ptr<pg::query_configuration> cm::create_package::query_config () const
{
    return std::make_shared<pg::query_configuration>(
        "SELECT create_package(\
            p_name := $1,\
            p_version := $2,\
            p_branch_name := $3,\
            p_current_commit_hash := $4)", cm::environment::env()
    );
}


// NOTE OVERLOADS
// std::optional<cm::execution> cm::register_execution::operator() (
//     const pg::int8& p_package_id, const pg::text& p_commit_hash,
//     const cm::execution_action& p_action
// )
// {
//     std::optional<cm::package> v_package = cm::get_package_by_id{}(p_package_id);
//     if (v_package.has_value())
//     {
//         return cm::register_execution{}(v_package.value(), p_commit_hash, p_action);
//     }
//     return std::nullopt;
// }
// 
// 
// std::optional<bool> cm::register_execution_commit_hash::operator() (
//     const pg::int8& p_execution_id, const pg::text& p_commit_hash
// )
// {
//     std::optional<cm::execution> v_execution = cm::get_execution_by_id{}(p_execution_id);
//     if (v_execution.has_value())
//     {
//         return cm::register_execution_commit_hash{}(v_execution.value(), p_commit_hash);
//     }
//     return std::nullopt;
// }
// 
// 
// std::optional<bool> cm::register_execution_migration::operator() (
//     const pg::int8& p_execution_id, const pg::int8& p_migration_id
// )
// {
//     std::optional<cm::execution> v_execution = cm::get_execution_by_id{}(p_execution_id);
//     std::optional<cm::migration> v_migration = cm::get_migration_by_id{}(p_migration_id);
//     if (v_execution.has_value() && v_migration.has_value())
//     {
//         return cm::register_execution_migration{}(v_execution.value(), v_migration.value());
//     }
//     return std::nullopt;
// }

// std::optional<cm::create_migration::ResultType> cm::create_migration::operator() (
//     const pg::int8& p_execution_id, const pg::text& p_migration_name,
//     const std::optional<pg::text>& p_datafix_name
// )
// {
//     std::optional<cm::execution> v_execution = cm::get_execution_by_id{}(p_execution_id);
//     if (v_execution.has_value())
//     {
//         return cm::create_migration{}(v_execution.value(), p_migration_name, p_datafix_name);
//     }
//     return std::nullopt;
// }
