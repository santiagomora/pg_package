#include "core_pg_migrations/database/namespace.hpp"


namespace core_pg_migrations::database::functions
{

std::vector<std::string_view> register_migration_dependencies::overloads = {
R"###(
CREATE OR REPLACE FUNCTION register_migration_dependencies (
    p_migration migration, p_dependency_names text[]
) RETURNS void AS $$
BEGIN
    INSERT INTO migration_dependency_relation (migration_id, depends_on_id)
    SELECT p_migration.id, m.id
    FROM migration m
    WHERE m.name = ANY(p_dependency_names);
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


std::vector<std::string_view> set_package_integrity_hash::overloads = {
R"###(
CREATE OR REPLACE FUNCTION set_package_integrity_hash (
    p_package package, p_integrity_hash text
) RETURNS void AS $$
BEGIN
    UPDATE package SET integrity_hash = p_integrity_hash 
    WHERE id = p_package.id;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


std::vector<std::string_view> create_execution::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_execution (
    p_package package, p_action execution_action
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


std::vector<std::string_view> register_execution_snapshot_relation::overloads = {
R"###(
CREATE OR REPLACE FUNCTION register_execution_snapshot_relation (
    p_execution execution, p_snapshot snapshot, p_integrity_hash text
) RETURNS void AS $$
BEGIN
    INSERT INTO execution_snapshot_relation(execution_id, snapshot_id, integrity_hash)
    VALUES (p_execution.id, p_snapshot.id, p_integrity_hash);
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


std::vector<std::string_view> create_migration::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_migration (
    p_snapshot snapshot, p_name text, p_upgrade_procedure_name text,
    p_downgrade_procedure_name text, p_datafix_name text = NULL
) RETURNS migration AS $$
DECLARE 
    v_migration migration;
BEGIN
    INSERT INTO migration(name, upgrade_script_name, downgrade_script_name, datafix_name, snapshot_id)
    VALUES (p_name, p_upgrade_procedure_name, p_downgrade_procedure_name, p_datafix_name, p_snapshot.id)
    RETURNING * INTO v_migration;
    RETURN v_migration;
END;
$$ LANGUAGE plpgsql VOLATILE;
)###"
};


std::vector<std::string_view> create_package::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_package (
    p_name text, p_remote_name text, p_tracked_branch_name text,
    p_schema_name text, p_procedure_schema_name text
) RETURNS package AS $$
DECLARE 
    v_package package;
BEGIN
    INSERT INTO package(name, remote_name, tracked_branch_name, schema_name, procedure_schema_name)
    VALUES (p_name, p_remote_name, p_tracked_branch_name, p_schema_name, p_procedure_schema_name)
    RETURNING * INTO v_package;
    RETURN v_package;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


std::vector<std::string_view> create_snapshot::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_snapshot (
    p_package_id int8, p_hash text,
    p_parent_hash text = NULL, p_child_hash text = NULL
) RETURNS snapshot AS $$
DECLARE
    v_snapshot snapshot;
    v_package package;
    v_child_snapshot snapshot;
    v_parent_snapshot snapshot;
BEGIN
    SELECT * FROM package p
        INTO v_package
        WHERE id = p_package_id
    ;
    SELECT * FROM snapshot s
        INTO v_parent_snapshot
        WHERE commit_hash = p_parent_hash
    ;
    SELECT * FROM snapshot s
        INTO v_child_snapshot
        WHERE commit_hash = p_child_hash
    ;
    RETURN create_snapshot(v_package, p_hash, v_parent_snapshot, v_child_snapshot);
END;
$$ LANGUAGE plpgsql VOLATILE;
)###",
R"###(
CREATE OR REPLACE FUNCTION create_snapshot (
    p_package package, p_hash text,
    p_parent snapshot, p_child snapshot
) RETURNS snapshot AS $$
DECLARE
    v_snapshot snapshot;
BEGIN
    INSERT INTO snapshot(package_id, commit_hash, child_id, parent_id, created_at)
    VALUES (p_package.id, p_hash, id(p_child), id(p_parent), now())
    RETURNING * INTO v_snapshot;
    RETURN v_snapshot;
END;
$$ LANGUAGE plpgsql VOLATILE;
)###"
};


std::vector<std::string_view> get_applied_snapshots::overloads = {
R"###(
CREATE OR REPLACE FUNCTION get_applied_snapshots (
    p_package_name text
) RETURNS SETOF text AS $$
DECLARE
    v_package package;
BEGIN
    SELECT * INTO v_package
    FROM package WHERE name = p_package_name LIMIT 1;
    IF v_package IS NULL THEN
        RETURN;
    ELSE
        RETURN QUERY
            SELECT * FROM get_applied_snapshots(v_package);
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;
)###",
R"###(
CREATE OR REPLACE FUNCTION get_applied_snapshots (
    p_package package
) RETURNS SETOF text AS $$
BEGIN
    RETURN QUERY
        WITH snapshot_last_action AS (
            SELECT
                s.commit_hash, e.action,
                ROW_NUMBER() OVER(PARTITION BY s.id ORDER BY e.created_at DESC) AS rank
            FROM execution_snapshot_relation esr
            INNER JOIN execution e ON esr.execution_id = e.id
            INNER JOIN snapshot s ON esr.snapshot_id = s.id
            INNER JOIN package p ON e.package_id = p.id
            WHERE p.id = p_package.id
        )
        SELECT commit_hash
        FROM snapshot_last_action sla
        WHERE sla.action = 'upgrade' AND rank = 1
    ;
END;
$$ LANGUAGE plpgsql STABLE STRICT;
)###"
};


std::vector<std::string_view> get_integrity_hash::overloads = {
R"###(
CREATE OR REPLACE FUNCTION get_integrity_hash (
    p_package_name text
) RETURNS text AS $$
DECLARE
    v_package package;
BEGIN
    SELECT * INTO v_package
    FROM package WHERE name = p_package_name LIMIT 1;
    IF v_package IS NULL THEN
        RETURN;
    ELSE
        RETURN get_integrity_hash(v_package);
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;
)###",
R"###(
CREATE OR REPLACE FUNCTION get_integrity_hash (
    p_package package
) RETURNS text AS $$
DECLARE
    v_integrity_hash text;
BEGIN
    SELECT esr.integrity_hash
        INTO v_integrity_hash
        FROM execution_snapshot_relation esr
        INNER JOIN execution e ON esr.execution_id = e.id
        INNER JOIN package p ON e.package_id = p.id
        WHERE p.id = p_package.id
        ORDER BY e.created_at DESC LIMIT 1
    ;
    RETURN v_integrity_hash;
END;
$$ LANGUAGE plpgsql STABLE STRICT;
)###"
};


}
