BEGIN
RAISE NOTICE 'EXECUTING MIGRATION {migration_name}';
{migration_script}
EXCEPTION WHEN OTHERS THEN
GET STACKED DIAGNOSTICS v_error_message = MESSAGE_TEXT,
                        v_error_detail = PG_EXCEPTION_DETAIL,
                        v_error_hint = PG_EXCEPTION_HINT,
                        v_error_context = PG_EXCEPTION_CONTEXT;
RAISE NOTICE 'MIGRATION {migration_name} ERROR';
RAISE EXCEPTION 'ERROR SQLSTATE: %, MESSAGE: %, DETAIL: %, HINT: %, CONTEXT: %',
             SQLSTATE, v_error_message, v_error_detail, v_error_hint, v_error_context;
END;
