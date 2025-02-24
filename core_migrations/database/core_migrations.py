import core_pg_bindings as pg
import core_migrations.database.cpp.module.database_wrapper as pw


class execution_id_seq(pg.sequence, base=pg.catalog.int8):
    pass


class package_id_seq(pg.sequence, base=pg.catalog.int8):
    pass


class migration_id_seq(pg.sequence, base=pg.catalog.int8):
    pass


class execution_action(pw.execution_action, metaclass=pg.enum):
    pass


@pg.table.primary_key(
    name='package_pk', columns=('id',))
@pg.table.unique_constraint(
    name='package_unique_name_constraint', columns=('name',))
@pg.table.serial(column='id', sequence=package_id_seq)
class package(pw.package, metaclass=pg.table):
    pass


@pg.table.primary_key(
    name='execution_pk', columns=('id',))
@pg.table.foreign_key(
    name='execution_package_id_fk', columns=('package_id',),
    references=package, referenced_columns=('id',))
@pg.table.serial(column='id', sequence=execution_id_seq)
class execution(pw.execution, metaclass=pg.table):
    pass


# get the commits with git rev-list fd426b1cbe40d263f322e0ead00361e477eb58d9^..HEAD
@pg.table.primary_key(
    name='execution_commit_hash_pk', columns=('execution_id', 'commit_hash',))
@pg.table.foreign_key(
    name='execution_commit_hash_execution_id_fk', columns=('execution_id',),
    references=execution, referenced_columns=('id',))
class execution_commit_hash(pw.execution_commit_hash, metaclass=pg.table):
    pass


@pg.table.primary_key(
    name='migration_pk', columns=('id',))
@pg.table.unique_constraint(
    name='migration_unique_name_constraint', columns=('execution_id', 'name',))
@pg.table.foreign_key(
    name='migration_package_id_fk', columns=('execution_id',),
    references=execution, referenced_columns=('id',))
# @pg.foreign_key( implement self class references
#     name='migration_parent_id_fk', columns=('parent_id',),
#     references=migration, referenced_columns=('id',))
@pg.table.serial(column='id', sequence=migration_id_seq)
class migration(pw.migration, metaclass=pg.table):
    pass


@pg.table.primary_key(
    name='execution_migration_pk', columns=('execution_id', 'migration_id',))
@pg.table.foreign_key(
    name='execution_migration_execution_id_fk', columns=('execution_id',),
    references=execution, referenced_columns=('id',))
@pg.table.foreign_key(
    name='execution_migration_migration_id_fk', columns=('migration_id',),
    references=migration, referenced_columns=('id',))
class execution_migration(pw.execution_migration, metaclass=pg.table):
    pass


class create_execution(pw.create_execution, metaclass=pg.function):
    pass


class register_execution_commit_hash(pw.register_execution_commit_hash, metaclass=pg.function):
    pass


class register_execution_migration(pw.register_execution_migration, metaclass=pg.function):
    pass


class create_migration(pw.create_migration, metaclass=pg.function):
    pass


class create_package(pw.create_package, metaclass=pg.function):
    pass

