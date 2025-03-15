#include "core_pg_migrations/database/namespace.hpp"


// TODO create_snapshot should handle conflicts on package_id, commit_hash and update to the EXCLUDED snapshot attributes (DONE)
// TODO create_migration should handle conflicts on name and update to the EXCLUDED migration attributes (DONE)
// TODO add api cm_db::get_snapshot_migrations::query has one overload for snapshot (DONE)
// TODO add api cm_db::keep_snapshot_migration_ids::query (DONE)
// TODO add get_snapshot_by_commit_hash
// FIXME get_applied_snapshots should return snapshots in order, creating the list from hashes
namespace core_pg_migrations::database::functions
{

std::vector<std::string_view> destroy_migration::overloads = {
R"###(
CREATE OR REPLACE FUNCTION destroy_migration (
    p_migration migration
) RETURNS SETOF migration AS $$
DECLARE
    v_drop_queries text[] := '{}'::text[];
    v_drop_query text;
BEGIN
    v_drop_queries := v_drop_queries || format('DROP PROCEDURE %I', p_migration.upgrade_script_name);
    v_drop_queries := v_drop_queries || format('DROP PROCEDURE %I', p_migration.downgrade_script_name);
    IF p_migration.datafix_name IS NOT NULL THEN
        v_drop_queries := v_drop_queries || format('DROP PROCEDURE %I', p_migration.datafix_name);
    END IF;
    FOR v_drop_query IN SELECT t FROM unnest(v_drop_queries) t
    LOOP
        EXECUTE v_drop_query;
    END LOOP;
    DELETE FROM migration_dependency_relation
    WHERE migration_id = p_migration.id;
    DELETE FROM migration
    WHERE id = p_migration.id;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


std::vector<std::string_view> keep_snapshot_migration_ids::overloads = {
R"###(
CREATE OR REPLACE FUNCTION keep_snapshot_migration_ids (
    p_snapshot snapshot, p_migration_ids int8[]
) RETURNS void AS $$
DECLARE
    v_migration migration;
BEGIN
    PERFORM destroy_migration(m)
    FROM migration m
    WHERE snapshot_id = p_snapshot.id AND id != ALL(p_migration_ids);
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


std::vector<std::string_view> synchronize_migration_dependencies::overloads = {
R"###(
CREATE OR REPLACE FUNCTION synchronize_migration_dependencies (
    p_migration migration, p_dependency_names text[]
) RETURNS void AS $$
DECLARE
    v_dependency_ids int8[];
BEGIN
    v_dependency_ids := ARRAY(
        SELECT id FROM migration
        WHERE name = ANY(p_dependency_names)
    );
    INSERT INTO migration_dependency_relation (migration_id, depends_on_id)
    SELECT p_migration.id, d_id
    FROM unnest(v_dependency_ids) d_id
    ON CONFLICT (migration_id, depends_on_id) DO NOTHING;
    DELETE FROM migration_dependency_relation
    WHERE migration_id = p_migration.id AND depends_on_id != ALL(v_dependency_ids);
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
$$ LANGUAGE plpgsql VOLATILE;
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
$$ LANGUAGE plpgsql VOLATILE;
)###"
};


std::vector<std::string_view> create_migration::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_migration (
    p_snapshot snapshot, p_name text, p_upgrade_procedure_name text,
    p_downgrade_procedure_name text, p_datafix_name text, p_heap_position int8
) RETURNS migration AS $$
DECLARE
    v_migration       migration;
    v_procedure_names text[];
BEGIN
    v_procedure_names := ARRAY[p_upgrade_procedure_name, p_downgrade_procedure_name];
    IF p_datafix_name IS NOT NULL THEN
        v_procedure_names := v_procedure_names || p_datafix_name;
    END IF;
    IF EXISTS (
        SELECT 1 FROM unnest(v_procedure_names) req
        LEFT JOIN pg_catalog.pg_proc fn
        ON fn.pronamespace || '.' || fn.proname = req
        WHERE fn.proname = NULL
    ) THEN
        RAISE EXCEPTION 'Cant create migration "%" because one or more procedures are missing: "%"', p_name, array_to_string(v_procedure_names, ', ');
    END IF;
    INSERT INTO migration(name, upgrade_script_name, downgrade_script_name, datafix_name, snapshot_id, heap_position)
    VALUES (p_name, p_upgrade_procedure_name, p_downgrade_procedure_name, p_datafix_name, p_snapshot.id, p_heap_position)
    ON CONFLICT (snapshot_id, name) DO UPDATE
        SET upgrade_script_name = EXCLUDED.upgrade_script_name,
            downgrade_script_name = EXCLUDED.downgrade_script_name,
            datafix_name = EXCLUDED.datafix_name,
            heap_position = EXCLUDED.heap_position
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
    ON CONFLICT (name) DO UPDATE
        SET remote_name = EXCLUDED.remote_name,
            tracked_branch_name = EXCLUDED.tracked_branch_name,
            schema_name = EXCLUDED.schema_name,
            procedure_schema_name = EXCLUDED.procedure_schema_name
    RETURNING * INTO v_package;
    RETURN v_package;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;
)###"
};


std::vector<std::string_view> create_snapshot::overloads = {
R"###(
CREATE OR REPLACE FUNCTION create_snapshot (
    p_package_id int8, p_hash text, p_parent_hash text = NULL, p_child_hash text = NULL
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
    p_package package, p_hash text, p_parent snapshot, p_child snapshot
) RETURNS snapshot AS $$
DECLARE
    v_snapshot snapshot;
BEGIN
    INSERT INTO snapshot (package_id, commit_hash, child_id, parent_id, created_at)
    VALUES (p_package.id, p_hash, id(p_child), id(p_parent), now())
    ON CONFLICT (package_id, commit_hash) DO UPDATE
        SET child_id = EXCLUDED.child_id,
            parent_id = EXCLUDED.parent_id
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
DECLARE
    v_snapshot_commit_hash text;
    v_applied_snapshot_ids int8[];
    v_snapshot snapshot;
BEGIN
    v_applied_snapshot_ids := ARRAY(
        WITH snapshot_last_action AS (
            SELECT
                s.id, e.action,
                ROW_NUMBER() OVER(PARTITION BY s.id ORDER BY e.created_at DESC) AS rank
            FROM execution_snapshot_relation esr
            INNER JOIN execution e ON esr.execution_id = e.id
            INNER JOIN snapshot s ON esr.snapshot_id = s.id
            INNER JOIN package p ON e.package_id = p.id
            WHERE p.id = p_package.id
        )
        SELECT id
        FROM snapshot_last_action sla
        WHERE sla.action = 'upgrade' AND rank = 1
    );
    IF array_length(v_applied_snapshot_ids, 1) <= 0 THEN
        RETURN;
    END IF;
    SELECT * FROM snapshot
    INTO v_snapshot
    WHERE parent_id IS NULL AND id = ANY(v_applied_snapshot_ids);
    raise notice '%', v_snapshot;
    WHILE NOT v_snapshot IS NULL
    LOOP
        RETURN NEXT(v_snapshot.commit_hash);
        SELECT * FROM snapshot
        INTO v_snapshot
        WHERE parent_id = v_snapshot.id AND id = ANY(v_applied_snapshot_ids);
    END LOOP;
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
    SELECT * FROM package
    INTO v_package
    WHERE name = p_package_name LIMIT 1;
    IF v_package IS NOT NULL THEN
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


std::vector<std::string_view> get_snapshot_migrations::overloads = {
R"###(
CREATE OR REPLACE FUNCTION get_snapshot_migrations (
    p_snapshot snapshot, p_action execution_action
) RETURNS SETOF migration AS $$
BEGIN
    RETURN QUERY
        SELECT * FROM migration
        WHERE snapshot_id = p_snapshot.id
        ORDER BY
        CASE WHEN p_action = 'upgrade'::execution_action
            THEN heap_position
            ELSE -heap_position END
    ;
END;
$$ LANGUAGE plpgsql STABLE;
)###"
};

}
