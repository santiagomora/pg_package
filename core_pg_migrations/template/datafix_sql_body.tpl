
-- GENERATED_AT: {generated_at}
-- DATAFIX_NAME: {datafix_name}
-- NOTE: These functions are designed to reside in a temporary schema
-- created uniquely for the purpose of executing the migration.
-- They will be executed before the up and down method in the corresponding
-- migration file if it shares name with a migration.


CREATE PROCEDURE {datafix_upgrade_name}()
AS $$
BEGIN
    -- your code here

END;
$$ LANGUAGE plpgsql;
