DO $mgr$
BEGIN
    -- locks migration tables
    LOCK TABLE core_pg_migrations.package IN EXCLUSIVE MODE;
    LOCK TABLE core_pg_migrations.execution IN EXCLUSIVE MODE;
    LOCK TABLE core_pg_migrations.migration IN EXCLUSIVE MODE;
    LOCK TABLE core_pg_migrations.execution_migration IN EXCLUSIVE MODE;

    -- locks modified tables
    {lock_modified_tables}

    -- backup modified tables and store insert files in specified folder
    {backup_modified_tables}

    -- execution script sentences
    {execution_script_sentences}
END $mgr$;
