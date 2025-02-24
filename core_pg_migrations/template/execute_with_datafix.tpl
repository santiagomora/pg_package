DO $mgr$
BEGIN
    -- locks migration tables
    LOCK TABLE core_pg_migrations.package IN EXCLUSIVE MODE;
    LOCK TABLE core_pg_migrations.execution IN EXCLUSIVE MODE;
    LOCK TABLE core_pg_migrations.migration IN EXCLUSIVE MODE;
    LOCK TABLE core_pg_migrations.execution_migration IN EXCLUSIVE MODE;

    -- generates temporary schema and creates datafix procedures
    CREATE TEMPORARY SCHEMA {tmp_schema_name};
    {create_temporary_procedures}

    -- locks modified tables
    {lock_modified_tables}

    -- backup modified tables and store insert files in specified folder
    {backup_modified_tables}

    -- execution script sentences
    {execution_script_sentences}
END $mgr$;
