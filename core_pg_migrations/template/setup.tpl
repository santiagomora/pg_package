CREATE OR REPLACE PROCEDURE {procedure_name} ()
LANGUAGE plpgsql
AS $mgr$
DECLARE 
    v_error_message text;
    v_error_detail text;
    v_error_hint text;
    v_error_context text;
BEGIN

RAISE NOTICE 'Checking if core_pg_migrations is already installed...';
IF EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = {procedure_schema})
THEN
    RAISE EXCEPTION 'core_pg_migrations already installed. Exiting...';
END IF;

RAISE NOTICE 'core_pg_migrations not installed, applying setup script...';


{setup_script_transactions}


END $mgr$;
