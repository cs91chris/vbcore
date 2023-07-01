# taken from: https://github.com/openstack/oslo.db
# and adapted for my coding style and use cases
#
# latest ref: 7d62b3664e4acad9161d849a111bdb8b4d707f61
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections
import re
import sys
import typing as t
from dataclasses import dataclass

from sqlalchemy import exc as sqla_exc
from sqlalchemy.engine import ExceptionContext
from sqlalchemy.exc import DBAPIError

from vbcore.db.exceptions import (
    DBConnectionError,
    DBConstraintError,
    DBDataError,
    DBDeadlock,
    DBDuplicateEntry,
    DBError,
    DBInvalidUnicodeParameter,
    DBNonExistentConstraint,
    DBNonExistentDatabase,
    DBNonExistentTable,
    DBNotSupportedError,
    DBReferenceError,
)
from vbcore.db.listener import Listener

ROLLBACK_CAUSE_KEY = "vbcore.db.sp_rollback_cause"

ExcType = t.Union[t.Type[DBAPIError], t.Type[Exception]]
FilterType = t.Callable[["ExceptionData"], None]

__REGISTRY: t.Dict[
    str, t.Dict[ExcType, t.List[t.Tuple[FilterType, re.Pattern]]]
] = collections.defaultdict(lambda: collections.defaultdict(list))


@dataclass(frozen=True)
class ExceptionData:
    exc: Exception
    match: re.Match
    context: ExceptionContext


def try_match(match: re.Match, key: str):
    try:
        return match.group(key)
    except IndexError:
        return None


def filters(dbname: str, exception_type: ExcType, *regexes: str) -> t.Callable:
    """
    Mark a function as receiving a filtered exception.

    @param dbname: string database name, e.g. 'mysql'
    @param exception_type: a SQLAlchemy database exception class, which
             extends from :class:`sqlalchemy.exc.DBAPIError`.
    @param regexes: strings that will be processed as matching regular expressions.
    """

    def _receive(fn: FilterType) -> FilterType:
        __REGISTRY[dbname][exception_type].extend(
            (fn, re.compile(reg, re.DOTALL)) for reg in regexes
        )
        return fn

    return _receive


@filters(
    "mysql",
    sqla_exc.OperationalError,
    r"^.*\b1213\b.*Deadlock found.*",
)
@filters(
    "mysql",
    sqla_exc.DatabaseError,
    r"^.*\b1205\b.*Lock wait timeout exceeded.*",
)
@filters(
    "mysql",
    sqla_exc.InternalError,
    r"^.*\b1213\b.*Deadlock found.*",
    r"^.*\b1213\b.*detected deadlock/conflict.*",
    r"^.*\b1213\b.*Deadlock: wsrep aborted.*",
)
@filters(
    "postgresql",
    sqla_exc.OperationalError,
    r"^.*deadlock detected.*",
)
@filters(
    "postgresql",
    sqla_exc.DBAPIError,
    r"^.*deadlock detected.*",
)
def _deadlock_error(data: ExceptionData):
    """
    Filter for MySQL or Postgresql deadlock error.

    mysql+mysqldb::
        (OperationalError) (1213, 'Deadlock found when trying to get lock; '
            'try restarting transaction') <query_str> <query_args>
    mysql+mysqlconnector::
        (InternalError) 1213 (40001): Deadlock found when trying to get lock;
            try restarting transaction
    postgresql::
        (TransactionRollbackError) deadlock detected <deadlock_details>
    """
    raise DBDeadlock(data.exc)


@filters(
    "mysql",
    sqla_exc.IntegrityError,
    r"^.*\b1062\b.*Duplicate entry '(?P<value>.*)' for key '(?P<columns>[^']+)'.*$",
    r"^.*\b1062\b.*Duplicate entry \\'(?P<value>.*)\\' for key \\'(?P<columns>.+)\\'.*$",
)
@filters(
    "postgresql",
    sqla_exc.IntegrityError,
    (
        r'^.*duplicate\s+key.*"(?P<columns>[^"]+)"\s*\n.*'
        r"Key\s+\((?P<key>.*)\)=\((?P<value>.*)\)\s+already\s+exists.*$"
    ),
    r"^.*duplicate\s+key.*\"(?P<columns>[^\"]+)\"\s*\n.*$",
)
def _default_dupe_key_error(data: ExceptionData):
    """
    Filter for MySQL or Postgresql duplicate key error.

    postgres:
    1 column - (IntegrityError) duplicate key value violates unique
               constraint "users_c1_key"
    N columns - (IntegrityError) duplicate key value violates unique
               constraint "name_of_our_constraint"
    mysql since 8.0.19:
    1 column - (IntegrityError) (1062, "Duplicate entry 'value_of_c1' for key
               'table_name.c1'")
    N columns - (IntegrityError) (1062, "Duplicate entry 'values joined
               with -' for key 'table_name.name_of_our_constraint'")
    mysql+mysqldb:
    1 column - (IntegrityError) (1062, "Duplicate entry 'value_of_c1' for key
               'c1'")
    N columns - (IntegrityError) (1062, "Duplicate entry 'values joined
               with -' for key 'name_of_our_constraint'")
    mysql+mysqlconnector:
    1 column - (IntegrityError) 1062 (23000): Duplicate entry 'value_of_c1' for
               key 'c1'
    N columns - (IntegrityError) 1062 (23000): Duplicate entry 'values
               joined with -' for key 'name_of_our_constraint'
    """
    engine_name = data.context.engine.dialect.name
    columns = data.match.group("columns")

    unique_base = "uniq_"
    if not columns.startswith(unique_base):
        if engine_name == "postgresql":
            columns = [columns[columns.index("_") + 1 : columns.rindex("_")]]
        elif (engine_name == "mysql") and (unique_base in str(columns.split("0")[:1])):
            columns = columns.split("0")[1:]
        else:
            columns = [columns]
    else:
        columns = columns[len(unique_base) :].split("0")[1:]

    value = data.match.groupdict().get("value")
    raise DBDuplicateEntry(columns, value, data.exc)


@filters(
    "sqlite",
    sqla_exc.IntegrityError,
    r"^.*columns?(?P<columns>[^)]+)(is|are)\s+not\s+unique$",
    r"^.*UNIQUE\s+constraint\s+failed:\s+(?P<columns>.+)$",
    r"^.*PRIMARY\s+KEY\s+must\s+be\s+unique.*$",
)
def _sqlite_dupe_key_error(data: ExceptionData):
    """
    Filter for SQLite duplicate key error.
    note(boris-42): In current versions of DB backends unique constraint
    violation messages follow the structure:

    sqlite:
    1 column - (IntegrityError) column c1 is not unique
    N columns - (IntegrityError) column c1, c2, ..., N are not unique
    sqlite since 3.7.16:
    1 column - (IntegrityError) UNIQUE constraint failed: tbl.k1
    N columns - (IntegrityError) UNIQUE constraint failed: tbl.k1, tbl.k2
    sqlite since 3.8.2:
    (IntegrityError) PRIMARY KEY must be unique
    """
    try:
        _columns = data.match.group("columns").strip()
        columns = [c.split(".")[-1] for c in _columns.split(", ")]
    except IndexError:
        columns = []

    raise DBDuplicateEntry(columns, inner_exception=data.exc)


@filters(
    "sqlite",
    sqla_exc.IntegrityError,
    r"(?i).*foreign key constraint failed",
)
@filters(
    "postgresql",
    sqla_exc.IntegrityError,
    (
        r".*on table \"(?P<table>[^\"]+)\" violates "
        r"foreign key constraint \"(?P<constraint>[^\"]+)\".*\n"
        r"DETAIL: {2}Key \((?P<key>.+)\)=\(.+\) "
        r"is (not present in|still referenced from) table "
        r"\"(?P<key_table>[^\"]+)\"."
    ),
)
@filters(
    "mysql",
    sqla_exc.IntegrityError,
    (
        r".*Cannot (add|delete) or update a (child|parent) row: "
        r'a foreign key constraint fails \([`"].+[`"]\.[`"](?P<table>.+)[`"], '
        r'CONSTRAINT [`"](?P<constraint>.+)[`"] FOREIGN KEY '
        r'\([`"](?P<key>.+)[`"]\) REFERENCES [`"](?P<key_table>.+)[`"] '
    ),
)
def _foreign_key_error(data: ExceptionData):
    raise DBReferenceError(
        try_match(data.match, "table"),
        try_match(data.match, "constraint"),
        try_match(data.match, "key"),
        try_match(data.match, "key_table"),
        data.exc,
    )


@filters(
    "postgresql",
    sqla_exc.IntegrityError,
    (
        r".*new row for relation \"(?P<table>.+)\" "
        "violates check constraint "
        '"(?P<check_name>.+)"'
    ),
)
def _check_constraint_error(data: ExceptionData):
    raise DBConstraintError(
        try_match(data.match, "table"),
        try_match(data.match, "check_name"),
        data.exc,
    )


@filters(
    "postgresql",
    sqla_exc.ProgrammingError,
    (
        r".* constraint \"(?P<constraint>.+)\" "
        "of relation "
        '"(?P<relation>.+)" does not exist'
    ),
)
@filters(
    "mysql",
    sqla_exc.InternalError,
    r".*1025,.*Error on rename of '.+/(?P<relation>.+)' to ",
    (
        ".*1091,.*Can't DROP (?:FOREIGN KEY )?['`](?P<constraint>.+)['`]; "
        "check that .* exists"
    ),
)
@filters(
    "mysql",
    sqla_exc.OperationalError,
    (
        r".*1091,.*Can't DROP (?:FOREIGN KEY )?['`](?P<constraint>.+)['`]; "
        "check that .* exists"
    ),
)
def _check_constraint_non_existing(data: ExceptionData):
    raise DBNonExistentConstraint(
        try_match(data.match, "relation"),
        try_match(data.match, "constraint"),
        data.exc,
    )


@filters(
    "sqlite",
    sqla_exc.OperationalError,
    r".* no such table: (?P<table>.+)",
)
@filters(
    "mysql",
    sqla_exc.InternalError,
    r".*1051,.*Unknown table '(.+\.)?(?P<table>.+)'\"",
)
@filters(
    "mysql",
    sqla_exc.OperationalError,
    r".*1051,.*Unknown table '(.+\.)?(?P<table>.+)'\"",
)
@filters(
    "postgresql",
    sqla_exc.ProgrammingError,
    r".* table \"(?P<table>.+)\" does not exist",
)
def _check_table_non_existing(data: ExceptionData):
    raise DBNonExistentTable(data.match.group("table"), data.exc)


@filters(
    "mysql",
    sqla_exc.InternalError,
    r".*1049,.*Unknown database '(?P<database>.+)'\"",
)
@filters(
    "mysql",
    sqla_exc.OperationalError,
    r".*1049,.*Unknown database '(?P<database>.+)'\"",
)
@filters(
    "postgresql",
    sqla_exc.OperationalError,
    r".*database \"(?P<database>.+)\" does not exist",
)
@filters(
    "sqlite",
    sqla_exc.OperationalError,
    r".*unable to open database file.*",
)
def _check_database_non_existing(data: ExceptionData):
    raise DBNonExistentDatabase(try_match(data.match, "database"), data.exc)


@filters("mysql", sqla_exc.DBAPIError, r".*\b1146\b")
def _raise_mysql_table_doesnt_exist_as_is(data: ExceptionData):
    """
    Raise MySQL error 1146 as is, so that it does not conflict with
    the MySQL dialect's checking a table not existing.
    """
    raise data.exc


@filters(
    "mysql",
    sqla_exc.OperationalError,
    r".*(1292|1366).*Incorrect \w+ value.*",
)
@filters(
    "mysql",
    sqla_exc.DataError,
    r".*1265.*Data truncated for column.*",
    r".*1264.*Out of range value for column.*",
    r".*1406.*Data too long for column.*",
)
@filters(
    "mysql",
    sqla_exc.InternalError,
    r"^.*1366.*Incorrect string value:*",
)
@filters(
    "sqlite",
    sqla_exc.ProgrammingError,
    r"(?i).*You must not use 8-bit bytestrings*",
)
def _raise_data_error(data: ExceptionData):
    raise DBDataError(data.exc)


@filters(
    "mysql",
    sqla_exc.OperationalError,
    r".*\(1305,\s+\'SAVEPOINT\s+(.+)\s+does not exist\'\)",
)
def _raise_savepoint_as_db_error(data: ExceptionData):
    raise DBError(data.exc)


@filters("*", sqla_exc.OperationalError, r".*")
def _raise_operational_errors_directly_filter(data: ExceptionData):
    if data.context.is_disconnect:
        raise DBConnectionError(data.exc)
    raise DBError(data.exc)


@filters(
    "mysql",
    sqla_exc.OperationalError,
    r".*\(.*(?:2002|2003|2006|2013|1047)",
)
@filters(
    "mysql",
    sqla_exc.InternalError,
    r".*\(.*(?:1927)",
    r".*Packet sequence number wrong",
)
@filters(
    "postgresql",
    sqla_exc.OperationalError,
    r".*could not connect to server",
)
def _is_db_connection_error(data: ExceptionData):
    raise DBConnectionError(data.exc)


@filters("*", sqla_exc.NotSupportedError, r".*")
def _raise_for_not_supported_error(data: ExceptionData):
    raise DBNotSupportedError(data.exc)


@filters("*", sqla_exc.DBAPIError, r".*")
def _raise_for_remaining_db_api_error(data: ExceptionData):
    if data.context.is_disconnect:
        raise DBConnectionError(data.exc)
    raise DBError(data.exc)


@filters("*", UnicodeEncodeError, r".*")
def _raise_for_unicode_encode(_: ExceptionData):
    raise DBInvalidUnicodeParameter()


@filters("*", Exception, r".*")
def _raise_for_all_others(data: ExceptionData):
    raise DBError(data.exc)


def _dialect_registries(engine):
    if engine.dialect.name in __REGISTRY:
        yield __REGISTRY[engine.dialect.name]
    if "*" in __REGISTRY:
        yield __REGISTRY["*"]
    yield


def _exception_handler(
    callback: FilterType,
    context: ExceptionContext,
    exc: Exception,
    regexp: re.Pattern,
):
    match = regexp.match(exc.args[0])
    if not match:
        return None

    try:
        callback(ExceptionData(exc=exc, match=match, context=context))
        return None
    except DBError as dbe:
        if (
            context.connection is not None
            and not context.connection.closed
            and not context.connection.invalidated
            and ROLLBACK_CAUSE_KEY in context.connection.info
        ):
            dbe.cause = context.connection.info.pop(ROLLBACK_CAUSE_KEY)  # type: ignore

        if isinstance(dbe, DBConnectionError):
            # noinspection PyDunderSlots
            context.is_disconnect = True  # type: ignore

            if hasattr(context, "is_pre_ping") and context.is_pre_ping:
                # if this is a pre-ping, need to integrate
                # with the built-in pre-ping handler that doesn't know
                # about DBConnectionError, just needs the updated status
                return None
        return dbe


def _per_dialect_handler(context: ExceptionContext, per_dialect: dict):
    """
    Method resolution order is used so that filter rules indicating a
    more specific exception class are attempted first.
    """
    for exc in (context.sqlalchemy_exception, context.original_exception):
        for super_ in exc.__class__.__mro__:
            for fn, regexp in per_dialect.get(super_) or ():
                _exception = t.cast(Exception, exc)
                handled = _exception_handler(fn, context, _exception, regexp)
                if handled:
                    return handled
    return None


class ErrorsHandler:
    @classmethod
    def handler(cls, context: ExceptionContext):
        """
        Iterate through available filters and invoke those which match.
        The first one which returns exception wins.
        The order in which the filters are attempted is sorted
        by specificity-dialect name or "*" (for all)
        """
        for per_dialect in _dialect_registries(context.engine):
            handled = _per_dialect_handler(context, per_dialect)
            if handled:
                return handled
        return None

    @classmethod
    def register(cls, engine) -> None:
        Listener.register_handle_error(engine, cls.handler, retval=True)

        @Listener.listens_for_rollback_savepoint(engine)
        def save_cause_on_rollback_savepoint(conn, _, __):
            exc_info = sys.exc_info()
            if exc_info[1] and not conn.invalidated:
                conn.info[ROLLBACK_CAUSE_KEY] = exc_info[1]
            del exc_info

        @Listener.listens_for_rollback(engine)
        @Listener.listens_for_commit(engine)
        def pop_cause_on_transaction(conn):
            if not conn.invalidated:
                conn.info.pop(ROLLBACK_CAUSE_KEY, None)

        @Listener.listens_for_checkin(engine)
        def pop_cause_on_checkin(_, conn):
            conn.info.pop(ROLLBACK_CAUSE_KEY, None)
