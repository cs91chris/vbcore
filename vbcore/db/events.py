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
import logging
import re
import sys
import typing as t

from sqlalchemy import exc as sqla_exc
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

LOG = logging.getLogger(__name__)

ROLLBACK_CAUSE_KEY = "vbcore.db.sp_rollback_cause"

ExcType = t.Union[t.Type[DBAPIError], t.Type[Exception]]
FilterType = t.Callable[[ExcType, re.Match, str, bool], None]

__REGISTRY: t.Dict[
    str, t.Dict[ExcType, t.List[t.Tuple[FilterType, re.Pattern]]]
] = collections.defaultdict(lambda: collections.defaultdict(list))


def try_match(match, key):
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


# NOTE(zzzeek) - for Postgresql, catch both OperationalError, as the
# actual error is
# psycopg2.extensions.TransactionRollbackError(OperationalError),
# as well as sqlalchemy.exc.DBAPIError, as SQLAlchemy will reraise it
# as this until issue #3075 is fixed.
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
)
@filters(
    "mysql",
    sqla_exc.InternalError,
    r"^.*\b1213\b.*detected deadlock/conflict.*",
)
@filters(
    "mysql",
    sqla_exc.InternalError,
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
def _deadlock_error(operational_error, match, engine_name, is_disconnect):
    """
    Filter for MySQL or Postgresql deadlock error.
    NOTE(comstud): In current versions of DB backends, Deadlock violation
    messages follow the structure:

    mysql+mysqldb::
        (OperationalError) (1213, 'Deadlock found when trying to get lock; '
            'try restarting transaction') <query_str> <query_args>
    mysql+mysqlconnector::
        (InternalError) 1213 (40001): Deadlock found when trying to get lock;
            try restarting transaction
    postgresql::
        (TransactionRollbackError) deadlock detected <deadlock_details>
    """
    _ = match, engine_name, is_disconnect
    raise DBDeadlock(operational_error)


@filters(
    "mysql",
    sqla_exc.IntegrityError,
    r"^.*\b1062\b.*Duplicate entry '(?P<value>.*)' for key '(?P<columns>[^']+)'.*$",
)
@filters(
    "mysql",
    sqla_exc.IntegrityError,
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
def _default_dupe_key_error(integrity_error, match, engine_name, is_disconnect):
    """
    Filter for MySQL or Postgresql duplicate key error.
    note(boris-42): In current versions of DB backends unique constraint
    violation messages follow the structure:

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
    _ = is_disconnect
    columns = match.group("columns")

    # note(vsergeyev): UniqueConstraint name convention: "uniq_t0c10c2"
    #                  where `t` it is table name and columns `c1`, `c2`
    #                  are in UniqueConstraint.
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

    value = match.groupdict().get("value")
    raise DBDuplicateEntry(columns, value, integrity_error)


@filters(
    "sqlite",
    sqla_exc.IntegrityError,
    r"^.*columns?(?P<columns>[^)]+)(is|are)\s+not\s+unique$",
    r"^.*UNIQUE\s+constraint\s+failed:\s+(?P<columns>.+)$",
    r"^.*PRIMARY\s+KEY\s+must\s+be\s+unique.*$",
)
@filters(
    "sqlite",
    sqla_exc.IntegrityError,
    r"^.*columns?(?P<columns>[^)]+)(is|are)\s+not\s+unique$",
    r"^.*UNIQUE\s+constraint\s+failed:\s+(?P<columns>.+)$",
    r"^.*PRIMARY\s+KEY\s+must\s+be\s+unique.*$",
)
def _sqlite_dupe_key_error(integrity_error, match, engine_name, is_disconnect):
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
    _ = engine_name, is_disconnect
    columns = []
    # NOTE(ochuprykov): We can get here by last filter in which there are no
    #                   groups. Trying to access the substring that matched by
    #                   the group will lead to IndexError. In this case just
    #                   pass empty list to DBDuplicateEntry
    try:
        columns = match.group("columns")
        columns = [c.split(".")[-1] for c in columns.strip().split(", ")]
    except IndexError:
        pass

    raise DBDuplicateEntry(columns, inner_exception=integrity_error)


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
def _foreign_key_error(integrity_error, match, engine_name, is_disconnect):
    _ = engine_name, is_disconnect
    raise DBReferenceError(
        try_match(match, "table"),
        try_match(match, "constraint"),
        try_match(match, "key"),
        try_match(match, "key_table"),
        integrity_error,
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
def _check_constraint_error(integrity_error, match, engine_name, is_disconnect):
    _ = engine_name, is_disconnect
    raise DBConstraintError(
        try_match(match, "table"),
        try_match(match, "check_name"),
        integrity_error,
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
@filters(
    "mysql",
    sqla_exc.InternalError,
    r".*1025,.*Error on rename of '.+/(?P<relation>.+)' to ",
)
def _check_constraint_non_existing(
    programming_error, match, engine_name, is_disconnect
):
    _ = engine_name, is_disconnect
    raise DBNonExistentConstraint(
        try_match(match, "relation"),
        try_match(match, "constraint"),
        programming_error,
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
def _check_table_non_existing(programming_error, match, engine_name, is_disconnect):
    _ = engine_name, is_disconnect
    raise DBNonExistentTable(match.group("table"), programming_error)


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
def _check_database_non_existing(error, match, engine_name, is_disconnect):
    _ = engine_name, is_disconnect
    raise DBNonExistentDatabase(try_match(match, "database"), error)


@filters(
    "mysql",
    sqla_exc.DBAPIError,
    r".*\b1146\b",
)
def _raise_mysql_table_doesnt_exist_as_is(error, match, engine_name, is_disconnect):
    """
    Raise MySQL error 1146 as is.
    Raise MySQL error 1146 as is, so that it does not conflict with
    the MySQL dialect's checking a table not existing.
    """
    _ = match, engine_name, is_disconnect
    raise error


@filters(
    "mysql",
    sqla_exc.OperationalError,
    r".*(1292|1366).*Incorrect \w+ value.*",
)
@filters(
    "mysql",
    sqla_exc.DataError,
    r".*1265.*Data truncated for column.*",
)
@filters(
    "mysql",
    sqla_exc.DataError,
    r".*1264.*Out of range value for column.*",
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
@filters(
    "mysql",
    sqla_exc.DataError,
    r".*1406.*Data too long for column.*",
)
def _raise_data_error(error, match, engine_name, is_disconnect):
    _ = match, engine_name, is_disconnect
    raise DBDataError(error)


@filters(
    "mysql",
    sqla_exc.OperationalError,
    r".*\(1305,\s+\'SAVEPOINT\s+(.+)\s+does not exist\'\)",
)
def _raise_savepoints_as_dberrors(error, match, engine_name, is_disconnect):
    # NOTE(rpodolyaka): this is a special case of an OperationalError that used
    # to be an InternalError. It's expected to be wrapped into oslo.db error.
    _ = match, engine_name, is_disconnect
    raise DBError(error)


@filters("*", sqla_exc.OperationalError, r".*")
def _raise_operational_errors_directly_filter(
    operational_error, match, engine_name, is_disconnect
):
    _ = match, engine_name
    if is_disconnect:
        # operational errors that represent disconnect
        # should be wrapped
        raise DBConnectionError(operational_error)
    # NOTE(comstud): A lot of code is checking for OperationalError
    # so let's not wrap it for now.
    raise DBError(operational_error)


@filters(
    "mysql",
    sqla_exc.OperationalError,
    r".*\(.*(?:2002|2003|2006|2013|1047)",
)
@filters(
    "mysql",
    sqla_exc.InternalError,
    r".*\(.*(?:1927)",
)
@filters(
    "mysql",
    sqla_exc.InternalError,
    r".*Packet sequence number wrong",
)
@filters(
    "postgresql",
    sqla_exc.OperationalError,
    r".*could not connect to server",
)
def _is_db_connection_error(operational_error, match, engine_name, is_disconnect):
    _ = match, engine_name, is_disconnect
    raise DBConnectionError(operational_error)


@filters("*", sqla_exc.NotSupportedError, r".*")
def _raise_for_not_supported_error(error, match, engine_name, is_disconnect):
    _ = match, engine_name, is_disconnect
    raise DBNotSupportedError(error)


@filters("*", sqla_exc.DBAPIError, r".*")
def _raise_for_remaining_db_api_error(error, match, engine_name, is_disconnect):
    _ = match, engine_name
    if is_disconnect:
        raise DBConnectionError(error)
    LOG.warning("DBAPIError exception wrapped.", exc_info=True)
    raise DBError(error)


@filters("*", UnicodeEncodeError, r".*")
def _raise_for_unicode_encode(error, match, engine_name, is_disconnect):
    _ = error, match, engine_name, is_disconnect
    raise DBInvalidUnicodeParameter()


@filters("*", Exception, r".*")
def _raise_for_all_others(error, match, engine_name, is_disconnect):
    _ = match, engine_name, is_disconnect
    LOG.warning("DB exception wrapped.", exc_info=True)
    raise DBError(error)


def _dialect_registries(engine):
    if engine.dialect.name in __REGISTRY:
        yield __REGISTRY[engine.dialect.name]
    if "*" in __REGISTRY:
        yield __REGISTRY["*"]
    yield


def _exception_handler(fn, context, exc, regexp):
    match = regexp.match(exc.args[0])
    if not match:
        return None

    try:
        fn(
            exc,
            match,
            context.engine.dialect.name,
            context.is_disconnect,
        )
        return None
    except DBError as dbe:
        if (
            context.connection is not None
            and not context.connection.closed
            and not context.connection.invalidated
            and ROLLBACK_CAUSE_KEY in context.connection.info
        ):
            dbe.cause = context.connection.info.pop(ROLLBACK_CAUSE_KEY)

        if isinstance(dbe, DBConnectionError):
            context.is_disconnect = True

            if hasattr(context, "is_pre_ping") and context.is_pre_ping:
                # if this is a pre-ping, need to integrate
                # with the built-in pre-ping handler that doesn't know
                # about DBConnectionError, just needs the updated status
                return None
        return dbe


def _per_dialect_handler(context, per_dialect):
    for exc in (context.sqlalchemy_exception, context.original_exception):
        for super_ in exc.__class__.__mro__:
            for fn, regexp in per_dialect.get(super_) or ():
                handled = _exception_handler(fn, context, exc, regexp)
                if handled:
                    return handled
    return None


def handler(context):
    """
    Iterate through available filters and invoke those which match.
    The first one which raises wins.
    The order in which the filters are attempted is sorted by specificity-dialect name or "*"
    exception class per method resolution order (``__mro__``).
    Method resolution order is used so that filter rules indicating a
    more specific exception class are attempted first.
    """
    for per_dialect in _dialect_registries(context.engine):
        handled = _per_dialect_handler(context, per_dialect)
        if handled:
            return handled
    return None


def register_error_handlers(engine):
    Listener.register_handle_error(engine, handler, retval=True)

    @Listener.listens_for_rollback_savepoint(engine)
    def save_cause_on_rollback_savepoint(conn, name, context):
        _ = name, context
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
    def pop_cause_on_checkin(dbapi_conn, connection_record):
        _ = dbapi_conn
        connection_record.info.pop(ROLLBACK_CAUSE_KEY, None)
