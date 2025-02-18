import core_types as ct
import core_migrations.backend.cpp.wrapper as cw


class SetupParameters(cw.setup_parameters, metaclass=ct.compound):
    pass
