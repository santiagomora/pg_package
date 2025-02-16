#ifndef CORE_MIGRATIONS_DATABASE_INTERFACE_QUERIES
#define CORE_MIGRATIONS_DATABASE_INTERFACE_QUERIES
#include "core_pg_bindings/execution/environment.hpp"
#include "core_pg_bindings/execution/invokable.hpp"
#include "core_migrations/database/typing/namespace.hpp"
#include "core_migrations/database/interface/types.hpp"


namespace pg = core_pg_bindings;
namespace db = core_migrations::database;


namespace core_migrations::database::interface
{

class environment
{
private:
    static std::optional<pg::db_environment> _env;
public:
    static pg::db_environment& env ();
};


class create_execution
    : public pg::queries_database_on_transaction<
          pg::fetch_one_functor, pg::SingleResult_<db::execution>,
          const db::package&, const pg::text&, const db::execution_action&>
{
protected:
    std::shared_ptr<pg::query_configuration> query_config () const override;
};


class register_execution_commit_hash
    : public pg::queries_database_on_transaction<
          pg::fetch_none_functor, pg::NoResult_,
          const db::execution&, const pg::text&>
{
protected:
    std::shared_ptr<pg::query_configuration> query_config () const override;
};


class register_execution_migration
    : public pg::queries_database_on_transaction<
          pg::fetch_none_functor, pg::NoResult_,
          const db::execution&, const db::migration&>
{
protected:
    std::shared_ptr<pg::query_configuration> query_config () const override;
};


class create_migration
    : public pg::queries_database_on_transaction<
          pg::fetch_one_functor, pg::SingleResult_<db::migration>,
          const db::execution&, const pg::text&, const std::optional<pg::text>>
{
protected:
    std::shared_ptr<pg::query_configuration> query_config () const override;
};


class create_package
    : public pg::queries_database_on_transaction<
          pg::fetch_one_functor, pg::SingleResult_<db::package>,
          const pg::text&, const pg::text&, const pg::text&, const pg::text&>
{
protected:
    std::shared_ptr<pg::query_configuration> query_config () const override;
};

}

#endif
