import core_pg_bindings as pg
import core_pg_migrations.database.cpp.module.database_wrapper as pw
from typing_extensions import Self


class execution_id_seq(pg.sequence, base=pg.catalog.int8):
    pass


class package_id_seq(pg.sequence, base=pg.catalog.int8):
    pass


class snapshot_id_seq(pg.sequence, base=pg.catalog.int8):
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


@pg.table.foreign_key(
    name='snapshot_package_id_fk', columns=('package_id',),
    references=package, referenced_columns=('id',))
@pg.table.foreign_key(
    name='snapshot_parent_id_fk', columns=('parent_id',),
    references=Self, referenced_columns=('id',))
@pg.table.foreign_key(
    name='snapshot_child_id_fk', columns=('child_id',),
    references=Self, referenced_columns=('id',))
@pg.table.unique_constraint(
    name='snapshot_unique_commit_hash_constraint', columns=('package_id', 'commit_hash',))
@pg.table.serial(column='id', sequence=snapshot_id_seq)
@pg.table.primary_key(
    name='snapshot_pk', columns=('id',))
class snapshot(pw.snapshot, metaclass=pg.table):
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
    name='migration_unique_name_constraint', columns=('snapshot_id', 'name',))
@pg.table.unique_constraint(
    name='migration_unique_heap_position_constraint', columns=('snapshot_id', 'heap_position',))
@pg.table.unique_constraint(
    name='migration_unique_datafix_name_constraint', columns=('snapshot_id', 'datafix_name',))
@pg.table.foreign_key(
    name='migration_snapshot_id_fk', columns=('snapshot_id',),
    references=snapshot, referenced_columns=('id',))
@pg.table.serial(column='id', sequence=migration_id_seq)
class migration(pw.migration, metaclass=pg.table):
    pass


@pg.table.primary_key(
    name='migration_dependency_relation_pk', columns=('migration_id', 'depends_on_id', ))
@pg.table.foreign_key(
    name='migration_dependency_relation_migration_id_fk', columns=('migration_id',),
    references=migration, referenced_columns=('id',))
@pg.table.foreign_key(
    name='migration_dependency_relation_depends_on_id_fk', columns=('depends_on_id',),
    references=migration, referenced_columns=('id',))
class migration_dependency_relation(pw.migration_dependency_relation, metaclass=pg.table):
    pass


@pg.table.primary_key(
    name='execution_snapshot_relation_pk', columns=('execution_id', 'snapshot_id', ))
@pg.table.foreign_key(
    name='execution_snapshot_relation_execution_id_fk', columns=('execution_id',),
    references=execution, referenced_columns=('id',))
@pg.table.foreign_key(
    name='execution_snapshot_relation_snapshot_id_fk', columns=('snapshot_id',),
    references=snapshot, referenced_columns=('id',))
@pg.table.unique_constraint(
    name='execution_snapshot_relation_uix', columns=('execution_id', 'snapshot_id', 'integrity_hash'))
class execution_snapshot_relation(pw.execution_snapshot_relation, metaclass=pg.table):
    pass


class create_execution(pw.create_execution, metaclass=pg.function):
    pass


class create_or_update_migration(pw.create_or_update_migration, metaclass=pg.function):
    pass


class create_or_update_package(pw.create_or_update_package, metaclass=pg.function):
    pass


class create_or_update_snapshot(pw.create_or_update_snapshot, metaclass=pg.function):
    pass


class get_applied_snapshots(pw.get_applied_snapshots, metaclass=pg.function):
    pass


class synchronize_migration_dependencies(pw.synchronize_migration_dependencies, metaclass=pg.function):
    pass


class set_package_integrity_hash(pw.set_package_integrity_hash, metaclass=pg.function):
    pass


class register_execution_snapshot_relation(pw.register_execution_snapshot_relation, metaclass=pg.function):
    pass


class keep_snapshot_migration_ids(pw.keep_snapshot_migration_ids, metaclass=pg.function):
    pass


class destroy_migration(pw.destroy_migration, metaclass=pg.function):
    pass


class get_package_integrity_hash_at_snapshot(pw.get_package_integrity_hash_at_snapshot, metaclass=pg.function):
    pass


class get_snapshot_migrations(pw.get_snapshot_migrations, metaclass=pg.function):
    pass

