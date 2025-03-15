CREATE OR REPLACE PROCEDURE {procedure_name} ()
AS $_mgr_$
DECLARE
v_error_message    text;
v_error_detail     text;
v_error_hint       text;
v_error_context    text;
v_migration_name   text := '{name}';
v_execution_action text := '{action}';
BEGIN
RAISE NOTICE 'EXECUTING MIGRATION %, action %', v_migration_name, v_execution_action;
{script}
EXCEPTION WHEN OTHERS THEN
    GET STACKED DIAGNOSTICS v_error_message = MESSAGE_TEXT,
                            v_error_detail = PG_EXCEPTION_DETAIL,
                            v_error_hint = PG_EXCEPTION_HINT,
                            v_error_context = PG_EXCEPTION_CONTEXT;
    RAISE NOTICE 'MIGRATION % ACTION % ERROR', v_migration_name, v_execution_action;
    RAISE EXCEPTION 'ERROR SQLSTATE: %, MESSAGE: %, DETAIL: %, HINT: %, CONTEXT: %',
                SQLSTATE, v_error_message, v_error_detail, v_error_hint, v_error_context;
END;
$_mgr_$ LANGUAGE plpgsql SET SEARCH_PATH TO {search_path};
