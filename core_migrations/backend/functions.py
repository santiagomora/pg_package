# import core_pg_bindings as pg
# from .types import\
#     migration,\
#     execution_action
# 
# 
# @pg.register_overload({'p_migration': migration})
# class get_last_execution_action(pg.single_result_function[execution_action]):
#     pass
# 
# 
# @pg.register_overload({'p_migration': migration})
# class get_migration_by_name(pg.single_result_function[migration]):
#     pass
