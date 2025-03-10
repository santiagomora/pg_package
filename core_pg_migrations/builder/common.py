from typing import\
    Any,\
    Optional,\
    TypeAlias,\
    Union
from abc import\
    abstractmethod,\
    ABC
from types import\
    ModuleType
from psycopg import\
    sql
import re


Identifier: TypeAlias = Union[sql.SQL, sql.Identifier]


def identifier(sql_name: str) -> str:
    if re.search(r'A-Z', sql_name) is not None or re.match(r'0-9', sql_name) is not None:
        return sql.Identifier(sql_name)
    return sql.SQL(re.escape(sql_name))


def schema_name(schema: ModuleType) -> str:
    return schema.__name__.rpartition(".")[-1]


class Component:
    def __init__(
        self, name: str, parent: Optional['Component'] = None,
        definition: Optional[dict[str, Any]] = None
    ) -> None:
        self.name = name
        self.parent = parent
        self.definition = definition

    def __repr__(self):
        return f'{self.__class__.__qualname__}({self.name})'


class Builder(ABC):
    pass


class WrapsComponent:
    def __init__(self, component: Component) -> None:
        self.component = component


# string con la sentencia, una lista de identificadores, una lista de parametros
SQLSentenceParams: TypeAlias = tuple[str, list[Identifier],  Union[list[str], dict[str, Any]]]


class GeneratesSQLSentence(ABC):
    @abstractmethod
    def sql_sentence_params(self) -> SQLSentenceParams:
        pass

    @abstractmethod
    def is_opposite(self, other: 'GeneratesSQLSentence') -> bool:
        pass


class Sentence(WrapsComponent, GeneratesSQLSentence):
    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.component)})'


def qualify_overload(
    schema: str, overload: str
) -> str:
    func_name = re.sub(r'\(.*', '', overload.split("$$")[0], flags=re.DOTALL)
    func_name = re.sub(r'\s*CREATE\s+OR\s+REPLACE\s+FUNCTION\s*', '', func_name).strip()
    func_name = f'CREATE OR REPLACE FUNCTION {schema}.{func_name} '
    return re.sub(r'^.*CREATE\s+OR\s+REPLACE\s+FUNCTION.*?(?=\()', func_name, overload, flags=re.DOTALL)
