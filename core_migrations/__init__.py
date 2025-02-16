# BEGIN
# RAISE NOTICE 'EXECUTING MIGRATION create_core_migrations_schema';
# CREATE SCHEMA "core_migrations";
# EXCEPTION WHEN OTHERS THEN
# RAISE NOTICE 'MIGRATION create_core_migrations_schema ERROR';
# RAISE NOTICE 'STATE: %s, ERROR: %s.', SQLSTATE, SQLERRM;
# RAISE NOTICE 'ROLLING BACK...';
# ROLLBACK;
# END;
# 
# 
# BEGIN
# RAISE NOTICE 'EXECUTING MIGRATION create_core_migrations_package_table';
# CREATE SEQUENCE "core_migrations"."package_id_seq" AS "pg_catalog"."int8";
# CREATE TABLE "core_migrations"."package" ();
# ALTER TABLE "core_migrations"."package" ADD COLUMN "id" "pg_catalog"."int8";
# ALTER TABLE "core_migrations"."package" ADD COLUMN "name" "pg_catalog"."text";
# ALTER TABLE "core_migrations"."package" ADD COLUMN "version" "pg_catalog"."text";
# ALTER TABLE "core_migrations"."package" ADD COLUMN "branch_name" "pg_catalog"."text";
# ALTER TABLE "core_migrations"."package" ADD COLUMN "current_commit_hash" "pg_catalog"."text";
# ALTER TABLE "core_migrations"."package" ADD COLUMN "last_updated_at" "pg_catalog"."timestamptz";
# ALTER TABLE "core_migrations"."package" ADD CONSTRAINT "package_pk" PRIMARY KEY ("id");
# ALTER TABLE "core_migrations"."package" ADD CONSTRAINT "package_unique_name_constraint" UNIQUE ("name");
# EXCEPTION WHEN OTHERS THEN
# RAISE NOTICE 'MIGRATION create_core_migrations_package_table ERROR';
# RAISE NOTICE 'STATE: %s, ERROR: %s.', SQLSTATE, SQLERRM;
# RAISE NOTICE 'ROLLING BACK...';
# ROLLBACK;
# END;
# 
# 
# BEGIN
# RAISE NOTICE 'EXECUTING MIGRATION create_core_migrations_migration_table';
# CREATE SEQUENCE "core_migrations"."migration_id_seq" AS "pg_catalog"."int8";
# CREATE TABLE "core_migrations"."migration" ();
# ALTER TABLE "core_migrations"."migration" ADD COLUMN "id" "pg_catalog"."int8";
# ALTER TABLE "core_migrations"."migration" ADD COLUMN "package_id" "pg_catalog"."int8";
# ALTER TABLE "core_migrations"."migration" ADD COLUMN "name" "pg_catalog"."text";
# ALTER TABLE "core_migrations"."migration" ADD COLUMN "datafix_name" "pg_catalog"."text";
# ALTER TABLE "core_migrations"."migration" ADD COLUMN "created_at" "pg_catalog"."timestamptz";
# ALTER TABLE "core_migrations"."migration" ADD CONSTRAINT "migration_pk" PRIMARY KEY ("id");
# ALTER TABLE "core_migrations"."migration" ADD CONSTRAINT "migration_unique_name_constraint" UNIQUE ("package_id", "name");
# ALTER TABLE "core_migrations"."migration" ADD CONSTRAINT "migration_package_id_fk" FOREIGN KEY ("package_id") REFERENCES "core_migrations"."package" ("id");
# EXCEPTION WHEN OTHERS THEN
# RAISE NOTICE 'MIGRATION create_core_migrations_migration_table ERROR';
# RAISE NOTICE 'STATE: %s, ERROR: %s.', SQLSTATE, SQLERRM;
# RAISE NOTICE 'ROLLING BACK...';
# ROLLBACK;
# END;
# 
# 
# BEGIN
# RAISE NOTICE 'EXECUTING MIGRATION create_core_migrations_execution_table';
# CREATE SEQUENCE "core_migrations"."execution_id_seq" AS "pg_catalog"."int8";
# CREATE TYPE "core_migrations"."execution_action" AS ENUM ();
# ALTER TYPE "core_migrations"."execution_action" ADD VALUE 'upgrade';
# ALTER TYPE "core_migrations"."execution_action" ADD VALUE 'downgrade';
# ALTER TYPE "core_migrations"."execution_action" ADD VALUE 'install';
# CREATE TABLE "core_migrations"."execution" ();
# ALTER TABLE "core_migrations"."execution" ADD COLUMN "id" "pg_catalog"."int8";
# ALTER TABLE "core_migrations"."execution" ADD COLUMN "package_id" "pg_catalog"."int8";
# ALTER TABLE "core_migrations"."execution" ADD COLUMN "created_at" "pg_catalog"."timestamptz";
# ALTER TABLE "core_migrations"."execution" ADD COLUMN "commit_hash" "pg_catalog"."text";
# ALTER TABLE "core_migrations"."execution" ADD COLUMN "action" "core_migrations"."execution_action";
# ALTER TABLE "core_migrations"."execution" ADD CONSTRAINT "execution_pk" PRIMARY KEY ("id");
# ALTER TABLE "core_migrations"."execution" ADD CONSTRAINT "execution_package_id_fk" FOREIGN KEY ("package_id") REFERENCES "core_migrations"."package" ("id");
# EXCEPTION WHEN OTHERS THEN
# RAISE NOTICE 'MIGRATION create_core_migrations_execution_table ERROR';
# RAISE NOTICE 'STATE: %s, ERROR: %s.', SQLSTATE, SQLERRM;
# RAISE NOTICE 'ROLLING BACK...';
# ROLLBACK;
# END;
# 
# 
# BEGIN
# RAISE NOTICE 'EXECUTING MIGRATION create_core_migrations_execution_migration_table';
# CREATE TABLE "core_migrations"."execution_migration" ();
# ALTER TABLE "core_migrations"."execution_migration" ADD COLUMN "execution_id" "pg_catalog"."int8";
# ALTER TABLE "core_migrations"."execution_migration" ADD COLUMN "migration_id" "pg_catalog"."int8";
# ALTER TABLE "core_migrations"."execution_migration" ADD CONSTRAINT "execution_migration_pk" PRIMARY KEY ("execution_id", "migration_id");
# ALTER TABLE "core_migrations"."execution_migration" ADD CONSTRAINT "execution_migration_execution_id_fk" FOREIGN KEY ("execution_id") REFERENCES "core_migrations"."execution" ("id");
# ALTER TABLE "core_migrations"."execution_migration" ADD CONSTRAINT "execution_migration_migration_id_fk" FOREIGN KEY ("migration_id") REFERENCES "core_migrations"."migration" ("id");
# EXCEPTION WHEN OTHERS THEN
# RAISE NOTICE 'MIGRATION create_core_migrations_execution_migration_table ERROR';
# RAISE NOTICE 'STATE: %s, ERROR: %s.', SQLSTATE, SQLERRM;
# RAISE NOTICE 'ROLLING BACK...';
# ROLLBACK;
# END;
# 
# 
# BEGIN
# RAISE NOTICE 'EXECUTING MIGRATION create_core_migrations_execution_commit_hash_table';
# CREATE TABLE "core_migrations"."execution_commit_hash" ();
# ALTER TABLE "core_migrations"."execution_commit_hash" ADD COLUMN "execution_id" "pg_catalog"."int8";
# ALTER TABLE "core_migrations"."execution_commit_hash" ADD COLUMN "commit_hash" "pg_catalog"."text";
# ALTER TABLE "core_migrations"."execution_commit_hash" ADD CONSTRAINT "execution_commit_hash_pk" PRIMARY KEY ("execution_id", "commit_hash");
# ALTER TABLE "core_migrations"."execution_commit_hash" ADD CONSTRAINT "execution_commit_hash_execution_id_fk" FOREIGN KEY ("execution_id") REFERENCES "core_migrations"."execution" ("id");
# EXCEPTION WHEN OTHERS THEN
# RAISE NOTICE 'MIGRATION create_core_migrations_execution_commit_hash_table ERROR';
# RAISE NOTICE 'STATE: %s, ERROR: %s.', SQLSTATE, SQLERRM;
# RAISE NOTICE 'ROLLING BACK...';
# ROLLBACK;
# END;
# 
# 
# BEGIN
# RAISE NOTICE 'EXECUTING MIGRATION create_core_migrations_functions';
# 
# CREATE OR REPLACE FUNCTION create_migration (
#     p_execution execution,
#     p_name text,
#     p_datafix_name text = NULL
# ) RETURNS migration AS $$
# DECLARE 
#     v_migration execution;
# BEGIN
#     INSERT INTO migration(execution_id, name, datafix_name, created_at)
#     RETURNING * INTO v_migration
#     VALUES (p_execution.id, p_name, p_datafix_name, now());
#     RETURN v_migration;
# END;
# $$ LANGUAGE plpgsql VOLATILE STRICT;
# 
# 
# CREATE OR REPLACE FUNCTION create_execution (
#     p_package package,
#     p_commit_hash text,
#     p_action execution_action
# ) RETURNS execution AS $$
# DECLARE 
#     v_execution execution;
# BEGIN
#     INSERT INTO execution(package_id, created_at, commit_hash, action)
#     RETURNING * INTO v_execution
#     VALUES (p_package.id, now(), p_commit_hash, p_action);
#     RETURN v_execution;
# END;
# $$ LANGUAGE plpgsql VOLATILE STRICT;
# 
# 
# CREATE OR REPLACE FUNCTION register_execution_commit_hash (
#     p_execution execution,
#     p_commit_hash text
# ) RETURNS void AS $$
# BEGIN
#     INSERT INTO execution_commit_hash(execution_id, commit_hash)
#     VALUES (p_execution.id, p_commit_hash);
# END;
# $$ LANGUAGE plpgsql VOLATILE STRICT;
# 
# 
# CREATE OR REPLACE FUNCTION register_execution_migration (
#     p_execution execution,
#     p_migration migration
# ) RETURNS void AS $$
# BEGIN
#     INSERT INTO execution_migration(execution_id, migration_id)
#     VALUES (p_execution.id, p_migration.id);
# END;
# $$ LANGUAGE plpgsql VOLATILE STRICT;
# 
# 
# CREATE OR REPLACE FUNCTION create_package (
#     p_name text,
#     p_version text,
#     p_branch_name text,
#     p_current_commit_hash text
# ) RETURNS package AS $$
# DECLARE 
#     v_package package;
# BEGIN
#     INSERT INTO package(name, version, branch_name, current_commit_hash, last_updated_at)
#     RETURNING * INTO v_package
#     VALUES (p_name, p_version, p_branch_name, p_current_commit_hash, now());
#     RETURN v_package;
# END;
# $$ LANGUAGE plpgsql VOLATILE STRICT;
# 
# EXCEPTION WHEN OTHERS THEN
# RAISE NOTICE 'MIGRATION create_core_migrations_functions ERROR';
# RAISE NOTICE 'STATE: %s, ERROR: %s.', SQLSTATE, SQLERRM;
# RAISE NOTICE 'ROLLING BACK...';
# ROLLBACK;
# END;
# 
# 
# 
# END $mgr$;
