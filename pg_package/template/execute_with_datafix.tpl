DO $$
BEGIN
    -- locks migration tables
    LOCK TABLE mgr.package IN EXCLUSIVE MODE;
    LOCK TABLE mgr.execution IN EXCLUSIVE MODE;
    LOCK TABLE mgr.migration IN EXCLUSIVE MODE;
    LOCK TABLE mgr.migration_execution IN EXCLUSIVE MODE;

    -- generates temporary schema and creates datafix procedures
    CREATE TEMPORARY SCHEMA {tmp_schema_name};
    {create_temporary_procedures}

    -- locks modified tables
    {lock_modified_tables}

    -- backup modified tables and store insert files in specified folder
    {backup_modified_tables}

    -- execution script sentences
    {execution_script_sentences}
END $$;
