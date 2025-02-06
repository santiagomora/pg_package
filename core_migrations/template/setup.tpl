DO $mgr$
DECLARE
    v_commit_hash text = {commit_hash};
BEGIN


{setup_script_transactions}

SET SEARCH_PATH TO {search_path};



END $mgr$;
