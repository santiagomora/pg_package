import core_types as ct
import core_pg_migrations.backend.cpp.backend_wrapper as cw


class SetupParameters(cw.setup_parameters, metaclass=ct.compound):
    pass
