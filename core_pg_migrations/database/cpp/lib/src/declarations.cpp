#include "core_pg_migrations/database/declarations.hpp"


namespace cm_db_dec = core_pg_migrations::database::declarations;


PG_ENUM_REGISTER_SUBCLASS_REG(CORE_PG_MIGRATIONS_DB_EXECUTION_ACTION);
PG_TABLE_REGISTER_SUBCLASS_REG(CORE_PG_MIGRATIONS_DB_PACKAGE);
PG_TABLE_REGISTER_SUBCLASS_REG(CORE_PG_MIGRATIONS_DB_EXECUTION);
PG_TABLE_REGISTER_SUBCLASS_REG(CORE_PG_MIGRATIONS_DB_MIGRATION);
PG_TABLE_REGISTER_SUBCLASS_REG(CORE_PG_MIGRATIONS_DB_EXECUTION_MIGRATION);


std::vector<std::string_view> cm_db_dec::create_execution::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_execution (
    p_package package,
    p_action execution_action
) RETURNS execution AS $$
DECLARE 
    v_execution execution;
BEGIN
    INSERT INTO execution(package_id, created_at, action)
    VALUES (p_package.id, now(), p_action)
    RETURNING * INTO v_execution;
    RETURN v_execution;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


std::vector<std::string_view> cm_db_dec::register_execution_migration::overloads = {
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


std::vector<std::string_view> cm_db_dec::create_migration::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_migration (
    p_execution execution,
    p_name text,
    p_snapshot text,
    p_datafix_name text = NULL
) RETURNS migration AS $$
DECLARE 
    v_migration migration;
BEGIN
    INSERT INTO migration(execution_id, name, datafix_name, snapshot, created_at)
    VALUES (p_execution.id, p_name, p_datafix_name, p_snapshot, now())
    RETURNING * INTO v_migration;
    RETURN v_migration;
END;
$$ LANGUAGE plpgsql VOLATILE;
)###"
};


std::vector<std::string_view> cm_db_dec::create_package::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_package (
    p_name text,
    p_branch_name text,
    p_current_snapshot text
) RETURNS package AS $$
DECLARE 
    v_package package;
BEGIN
    INSERT INTO package(name, branch_name, current_snapshot, last_updated_at)
    VALUES (p_name, p_branch_name, p_current_snapshot, now())
    RETURNING * INTO v_package;
    RETURN v_package;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};
