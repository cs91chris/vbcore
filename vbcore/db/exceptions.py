# taken from: https://github.com/openstack/oslo.db

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

"""
Define exception redefinitions for SQLAlchemy DBAPI exceptions
"""
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from vbcore.types import OptAny, OptExc, OptStr, StrList


class DBError(SQLAlchemyError):
    """
    Base exception for all custom database exceptions.
    """

    default_message: OptStr = None

    def __init__(self, inner_exception: OptExc = None, message: OptStr = None):
        """
        @param inner_exception: an original exception which was wrapped
            with DBError or its subclasses
        @param message: a given error message
        """
        self.message = message or self.default_message
        self.inner_exception = inner_exception
        super().__init__(str(inner_exception))

    @property
    def error_type(self) -> str:
        return self.__class__.__name__

    def as_dict(self) -> dict:
        return {
            "error": self.error_type,
            "message": self.message,
        }


class DBDuplicateEntry(DBError):
    def __init__(
        self,
        columns: Optional[StrList] = None,
        value: OptAny = None,
        inner_exception: OptExc = None,
        message: OptStr = None,
    ):
        self.value = value
        self.columns = columns or []
        super().__init__(inner_exception, message)

    def as_dict(self):
        return {
            **super().as_dict(),
            "columns": self.columns,
            "value": self.value,
        }


class DBConstraintError(DBError):
    def __init__(
        self,
        table: str,
        check_name: str,
        inner_exception: OptExc = None,
        message: OptStr = None,
    ):
        self.table = table
        self.check_name = check_name
        super().__init__(inner_exception, message)

    def as_dict(self) -> dict:
        return {
            **super().as_dict(),
            "table": self.table,
            "check_name": self.check_name,
        }


class DBReferenceError(DBError):
    def __init__(
        self,
        table: str,
        constraint: str,
        key: str,
        key_table: str,
        inner_exception: OptExc = None,
        message: OptStr = None,
    ):
        self.key = key
        self.table = table
        self.key_table = key_table
        self.constraint = constraint
        super().__init__(inner_exception, message)

    def as_dict(self) -> dict:
        return {
            **super().as_dict(),
            "table": self.table,
            "key_table": self.key_table,
            "key": self.key,
            "constraint": self.constraint,
        }


class DBNonExistentConstraint(DBError):
    def __init__(
        self,
        table: str,
        constraint: str,
        inner_exception: OptExc = None,
        message: OptStr = None,
    ):
        self.table = table
        self.constraint = constraint
        super().__init__(inner_exception, message)

    def as_dict(self) -> dict:
        return {
            **super().as_dict(),
            "table": self.table,
            "constraint": self.constraint,
        }


class DBNonExistentTable(DBError):
    def __init__(
        self,
        table: str,
        inner_exception: OptExc = None,
        message: OptStr = None,
    ):
        self.table = table
        super().__init__(inner_exception, message)

    def as_dict(self) -> dict:
        return {
            **super().as_dict(),
            "table": self.table,
        }


class DBNonExistentDatabase(DBError):
    def __init__(
        self,
        database: str,
        inner_exception: OptExc = None,
        message: OptStr = None,
    ):
        self.database = database
        super().__init__(inner_exception, message)

    def as_dict(self) -> dict:
        return {
            **super().as_dict(),
            "database": self.database,
        }


class DBInvalidUnicodeParameter(DBError):
    default_message = "invalid parameter: encoding directive was not provided"


class DBDataError(DBError):
    default_message = "an error on data occurred on database"


class DBNotSupportedError(DBError):
    default_message = "operation not supported on database"


class DBDeadlock(DBError):
    default_message = "a deadlock occurred on database"


class DBConnectionError(DBError):
    default_message = "database connection error"
