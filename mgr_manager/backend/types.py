import pg_definition as pg
import mgr_manager.backend.cpp.wrapper as pw


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


@pg.table.primary_key(
    name='migration_pk', columns=('id',))
@pg.table.unique_constraint(
    name='migration_unique_name_constraint', columns=('package_id', 'name',))
@pg.table.foreign_key(
    name='migration_package_id_fk', columns=('package_id',),
    references=package, referenced_columns=('id',))
# @pg.foreign_key( implement self class references
#     name='migration_parent_id_fk', columns=('parent_id',),
#     references=migration, referenced_columns=('id',))
@pg.table.serial(column='id', sequence=migration_id_seq)
class migration(pw.migration, metaclass=pg.table):
    pass


@pg.table.primary_key(
    name='migration_execution_pk', columns=('execution_id', 'migration_id',))
@pg.table.foreign_key(
    name='migration_execution_execution_id_fk', columns=('execution_id',),
    references=execution, referenced_columns=('id',))
@pg.table.foreign_key(
    name='migration_execution_migration_id_fk', columns=('migration_id',),
    references=migration, referenced_columns=('id',))
class migration_execution(pw.migration_execution, metaclass=pg.table):
    pass
