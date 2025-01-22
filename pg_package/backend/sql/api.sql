

CREATE OR REPLACE FUNCTION get_migration_by_name(
    p_name text
) RETURNS mgr_migration AS $$
DECLARE 
    v_migration mgr_migration;
BEGIN
    SELECT * FROM mgr_migration
        INTO v_migration
        WHERE name = p_name;
    RETURN v_migration;
END;
$$ LANGUAGE plpgsql STABLE STRICT;


CREATE OR REPLACE FUNCTION register_dependency(
    p_migration mgr_migration,
    p_dependency mgr_migration
) RETURNS void AS $$
BEGIN
    INSERT INTO mgr_migration_dependency(migration_id, depends_on_id)
    VALUES (p_migration.id, p_dependency.id);
END;
$$ LANGUAGE plpgsql VOLATILE;


CREATE OR REPLACE FUNCTION get_dependencies(
    p_migration mgr_migration
) RETURNS SETOF mgr_migration AS $$
BEGIN
    RETURN QUERY
        SELECT * FROM mgr_migration m
        INNER JOIN mgr_migration_dependency md
        ON m.id = md.migration_id
        WHERE m.id = p_migration.id
    ;
END;
$$ LANGUAGE plpgsql STABLE;


CREATE OR REPLACE FUNCTION get_last_execution_action(
    p_migration mgr_migration
) RETURNS mgr_execution_action AS $$
DECLARE 
    v_execution mgr_migration_execution;
BEGIN
    SELECT * FROM mgr_migration_execution
        INTO v_execution
        WHERE migration_id = p_migration.id
        ORDER BY execution_id DESC
        LIMIT 1
    ;
    RETURN v_execution.action;
END;
$$ LANGUAGE plpgsql STABLE STRICT;

