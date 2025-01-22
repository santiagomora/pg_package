#ifndef MGR_MACRO_DEFINITIONS
#define MGR_MACRO_DEFINITIONS


#include "base_types/include/macros/definition.hpp"
#include "base_types/include/types.hpp"


#define MGR_EXECUTION_ACTION ENUM_DEFINITION(\
    MGR_EXECUTION_ACTION,\
    (mgr, execution_action),\
    (ENUM_MEMBER(setup))\
    (ENUM_MEMBER(upgrade))\
    (ENUM_MEMBER(downgrade))\
)


#define MGR_PACKAGE DATACLASS_DEFINITION(\
    MGR_PACKAGE,\
    (mgr, package),\
    (DATACLASS_MEMBER(btp, int8_py, id))\
    (DATACLASS_MEMBER(btp, text_py, name))\
    (DATACLASS_MEMBER(btp, text_py, version))\
    (DATACLASS_MEMBER(btp, text_py, branch_name))\
    (DATACLASS_MEMBER(btp, text_py, last_commit_hash))\
    (DATACLASS_MEMBER(btp, timestamptz_py, last_updated_at)),\
    BOOST_PP_EMPTY()\
)
#define MGR_PACKAGE_MEMBERS T_DIRECT_MEMBERS(MGR_PACKAGE)


#define MGR_EXECUTION DATACLASS_DEFINITION(\
    MGR_EXECUTION,\
    (mgr, execution),\
    (DATACLASS_MEMBER(btp, int8_py, id))\
    (DATACLASS_MEMBER(btp, int8_py, package_id))\
    (DATACLASS_MEMBER(btp, timestamptz_py, created_at))\
    (DATACLASS_MEMBER(btp, text_py, commit_hash))\
    (DATACLASS_MEMBER(mgr, execution_action, action)),\
    BOOST_PP_EMPTY()\
)
#define MGR_EXECUTION_MEMBERS T_DIRECT_MEMBERS(MGR_EXECUTION)


#define MGR_MIGRATION DATACLASS_DEFINITION(\
    MGR_MIGRATION,\
    (mgr, migration),\
    (DATACLASS_MEMBER(btp, int8_py, id))\
    (DATACLASS_MEMBER(btp, int8_py, package_id))\
    (DATACLASS_MEMBER(btp, text_py, name))\
    (DATACLASS_MEMBER(btp, text_py, datafix_name))\
    (DATACLASS_MEMBER(btp, timestamptz_py, created_at)),\
    BOOST_PP_EMPTY()\
)
#define MGR_MIGRATION_MEMBERS T_DIRECT_MEMBERS(MGR_MIGRATION)


#define MGR_MIGRATION_EXECUTION DATACLASS_DEFINITION(\
    MGR_MIGRATION_EXECUTION,\
    (mgr, migration_execution),\
    (DATACLASS_MEMBER(btp, int8_py, migration_id))\
    (DATACLASS_MEMBER(btp, int8_py, execution_id)),\
    BOOST_PP_EMPTY()\
)
#define MGR_MIGRATION_EXECUTION_MEMBERS T_DIRECT_MEMBERS(MGR_MIGRATION_EXECUTION)


#endif
