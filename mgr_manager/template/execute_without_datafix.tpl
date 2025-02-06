DO $$
BEGIN
    -- locks migration tables
    LOCK TABLE mgr_manager.package IN EXCLUSIVE MODE;
    LOCK TABLE mgr_manager.execution IN EXCLUSIVE MODE;
    LOCK TABLE mgr_manager.migration IN EXCLUSIVE MODE;
    LOCK TABLE mgr_manager.migration_execution IN EXCLUSIVE MODE;

    -- locks modified tables
    {lock_modified_tables}

    -- backup modified tables and store insert files in specified folder
    {backup_modified_tables}

    -- execution script sentences
    {execution_script_sentences}
END $$;
