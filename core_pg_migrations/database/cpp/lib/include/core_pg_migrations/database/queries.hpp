#ifndef CORE_PG_MIGRATIONS_DATABASE_QUERIES
#define CORE_PG_MIGRATIONS_DATABASE_QUERIES
#include "core_pg_migrations/database/declarations.hpp"


namespace pg        = core_pg_bindings;
namespace cm_db_dec = core_pg_migrations::database::declarations;


namespace core_pg_migrations::database::queries
{
class create_execution
    : public pg::queries_database_on_transaction<
          pg::fetch_one_functor, pg::SingleResult_<cm_db_dec::execution>,
          const cm_db_dec::package&, const cm_db_dec::execution_action&>
{
protected:
    constexpr std::string_view query() const override
    {
        return "SELECT create_execution(\
            p_package := $1,\
            p_action := $2)";
    }
};


class register_execution_migration
    : public pg::queries_database_on_transaction<
          pg::fetch_none_functor, pg::NoResult_,
          const cm_db_dec::execution&, const cm_db_dec::migration&>
{
protected:
    constexpr std::string_view query() const override 
    {
        return "SELECT register_execution_migration(\
            p_execution := $1,\
            p_migration := $2)";
    }
};


class create_migration
    : public pg::queries_database_on_transaction<
          pg::fetch_one_functor, pg::SingleResult_<cm_db_dec::migration>,
          const cm_db_dec::execution&, const pg::text&, const pg::text&, const std::optional<pg::text>&>
{
protected:
    constexpr std::string_view query() const override 
    {
        return "SELECT create_migration(\
            p_execution := $1,\
            p_name := $2,\
            p_snapshot := $3,\
            p_datafix_name := $4)";
    }
};


class create_package
    : public pg::queries_database_on_transaction<
          pg::fetch_one_functor, pg::SingleResult_<cm_db_dec::package>,
          const pg::text&, const pg::text&, const pg::text&>
{
protected:
    constexpr std::string_view query() const override 
    {
        return "SELECT create_package(\
            p_name := $1,\
            p_branch_name := $2,\
            p_current_snapshot := $3)";
    }
};

}

#endif
