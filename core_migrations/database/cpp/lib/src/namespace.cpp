#include "core_pg_bindings/macros/register.hpp"
#include "core_migrations/database/typing/namespace.hpp"


namespace cm = core_migrations::database;
namespace py = pybind11;


PG_ENUM_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_EXECUTION_ACTION);
PG_TABLE_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_PACKAGE);
PG_TABLE_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_EXECUTION);
PG_TABLE_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_MIGRATION);
PG_TABLE_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_EXECUTION_MIGRATION);
PG_TABLE_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_EXECUTION_COMMIT_HASH);


PG_INVOKABLE_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_CREATE_EXECUTION);
std::vector<std::string_view> cm::create_execution::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_execution (
    p_package package,
    p_commit_hash text,
    p_action execution_action
) RETURNS execution AS $$
DECLARE 
    v_execution execution;
BEGIN
    INSERT INTO execution(package_id, created_at, commit_hash, action)
    VALUES (p_package.id, now(), p_commit_hash, p_action)
    RETURNING * INTO v_execution;
    RETURN v_execution;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


PG_INVOKABLE_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_REGISTER_EXECUTION_COMMIT_HASH);
std::vector<std::string_view> cm::register_execution_commit_hash::overloads = {
R"###(
CREATE OR REPLACE FUNCTION register_execution_commit_hash (
    p_execution execution,
    p_commit_hash text
) RETURNS void AS $$
BEGIN
    INSERT INTO execution_commit_hash(execution_id, commit_hash)
    VALUES (p_execution.id, p_commit_hash);
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


PG_INVOKABLE_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_REGISTER_EXECUTION_MIGRATION);
std::vector<std::string_view> cm::register_execution_migration::overloads = {
R"###(
CREATE OR REPLACE FUNCTION register_execution_migration (
    p_execution execution,
    p_migration migration
) RETURNS void AS $$
BEGIN
    INSERT INTO execution_migration(execution_id, migration_id)
    VALUES (p_execution.id, p_migration.id);
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


PG_INVOKABLE_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_CREATE_MIGRATION);
std::vector<std::string_view> cm::create_migration::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_migration (
    p_execution execution,
    p_name text,
    p_datafix_name text = NULL
) RETURNS migration AS $$
DECLARE 
    v_migration execution;
BEGIN
    INSERT INTO migration(execution_id, name, datafix_name, created_at)
    VALUES (p_execution.id, p_name, p_datafix_name, now())
    RETURNING * INTO v_migration;
    RETURN v_migration;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


PG_INVOKABLE_REGISTER_SUBCLASS_REG(CORE_MIGRATIONS_DB_CREATE_PACKAGE);
std::vector<std::string_view> cm::create_package::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_package (
    p_name text,
    p_version text,
    p_branch_name text,
    p_current_commit_hash text
) RETURNS package AS $$
DECLARE 
    v_package package;
BEGIN
    INSERT INTO package(name, version, branch_name, current_commit_hash, last_updated_at)
    VALUES (p_name, p_version, p_branch_name, p_current_commit_hash, now())
    RETURNING * INTO v_package;
    RETURN v_package;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};
