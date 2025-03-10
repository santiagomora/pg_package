import core_types as ct
import core_pg_migrations.backend.cpp.backend_wrapper as cw


class snapshot(cw.snapshot, metaclass=ct.compound):
    pass


class migration(cw.migration, metaclass=ct.compound):
    pass


class package(cw.package, metaclass=ct.compound):
    pass


