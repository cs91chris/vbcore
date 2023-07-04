import io
import os
import tarfile
import typing as t
from dataclasses import dataclass
from datetime import datetime
from itertools import groupby
from subprocess import CompletedProcess, PIPE, run as run_subprocess  # nosec

from vbcore.date_helper import DateTimeFmt
from vbcore.loggers import VBLoggerMixin
from vbcore.net.helpers import Url
from vbcore.types import CoupleStr, OptInt, OptStr, StrList, StrTuple

CmdLine = StrList


@dataclass(frozen=True)
class MySQLDump:
    database: str
    table: str
    dump: bytes


class MySQLDumper:
    def __init__(
        self,
        username: str,
        password: str,
        hostname: OptStr = None,
        port: OptInt = None,
        ignore_databases: t.Optional[StrList] = None,
    ):
        self.username = username
        self.password = password
        self.port = port or 3306
        self.hostname = hostname or "localhost"
        self.ignore_databases = (ignore_databases or []) + [
            "information_schema",
            "performance_schema",
            "mysql",
        ]

    @property
    def base_options(self) -> CmdLine:
        return [
            f"--user={self.username}",
            f"--password={self.password}",
            f"--host={self.hostname}",
            f"--port={self.port}",
        ]

    def mysql_cmdline(
        self,
        statement: str,
        *args: str,
        database: OptStr = None,
    ) -> CmdLine:
        return [
            "mysql",
            *self.base_options,
            f"--database={database}" if database else "",
            "--skip-column-names",
            "--execute",
            *args,
            f"{statement};",
        ]

    def mysqldump_cmdline(
        self,
        *args: str,
        database: OptStr = None,
        table: OptStr = None,
    ) -> CmdLine:
        dump_args: StrTuple
        if database:
            dump_args = ("--databases", database) if not table else (database, table)
        else:
            dump_args = ("--all-databases",)

        return ["mysqldump", *self.base_options, *args, *dump_args]

    @classmethod
    def execute_binary(cls, cmdline: CmdLine, **kwargs) -> CompletedProcess:
        return run_subprocess(cmdline, check=True, stdout=PIPE, **kwargs)  # nosec

    @classmethod
    def execute_text(cls, cmdline: CmdLine) -> t.Iterator[str]:
        result = cls.execute_binary(cmdline, text=True)
        return filter(None, result.stdout.split(os.linesep))

    def get_databases(self, prefix: OptStr = None) -> t.Generator[str, None, None]:
        filter_arg = f"like '{prefix}%'" if prefix else ""
        cmdline = self.mysql_cmdline(f"show databases {filter_arg}")
        for database in self.execute_text(cmdline):
            if database not in self.ignore_databases:
                yield database

    def get_tables(self, database: str) -> t.Iterator[str]:
        cmdline = self.mysql_cmdline("show tables", database=database)
        return self.execute_text(cmdline)

    def all_tables(
        self, db_prefix: OptStr = None
    ) -> t.Generator[CoupleStr, None, None]:
        for database in self.get_databases(db_prefix):
            for table in self.get_tables(database):
                yield database, table

    def dump_table(self, database: str, table: str) -> MySQLDump:
        cmdline = self.mysqldump_cmdline(database=database, table=table)
        result = self.execute_binary(cmdline)
        return MySQLDump(database=database, table=table, dump=result.stdout)


class MysqlBackup(VBLoggerMixin):
    def __init__(
        self,
        dumper: MySQLDumper,
        folder: str = ".",
        add_datetime: bool = True,
        datetime_format: OptStr = None,
    ):
        self.dumper = dumper
        self.folder = folder
        self.add_datetime = add_datetime
        self.datetime_format = datetime_format

    def prepare_filename(self, *args: str, ext: str) -> str:
        current_datetime = None
        if self.add_datetime:
            _datetime_format = self.datetime_format or DateTimeFmt.AS_NUM
            current_datetime = datetime.utcnow().strftime(_datetime_format)
        filename = "_".join(filter(None, (*args, current_datetime)))
        return os.path.join(self.folder, f"{filename}.{ext}")

    def backup_single_files(self, file_prefix: OptStr = None, db_prefix: OptStr = None):
        for database, table in self.dumper.all_tables(db_prefix):
            self.log.info("dumping table: %s.%s ......", database, table)
            dump = self.dumper.dump_table(database, table)
            filename = self.prepare_filename(
                file_prefix, f"{database}.{table}", ext="sql"
            )
            with open(filename, mode="wb") as file:
                file.write(dump.dump)

            self.log.info(
                "table: %s.%s successfully dumped at: %s",
                database,
                table,
                filename,
            )

    def backup_as_archive(
        self,
        file_prefix: OptStr = None,
        db_prefix: OptStr = None,
        mode: OptStr = None,
        ext: OptStr = None,
    ):
        _mode = mode or "w:gz"
        _ext = ext or "tar.gz"
        cursor = self.dumper.all_tables(db_prefix)
        for database, tables in groupby(cursor, key=lambda x: x[0]):
            filename = self.prepare_filename(file_prefix, database, ext=_ext)
            with tarfile.open(filename, mode=_mode) as file:
                for _, table in tables:
                    self.log.info("dumping table: %s.%s ......", database, table)
                    dump = self.dumper.dump_table(database, table)
                    tarinfo = tarfile.TarInfo(f"{dump.database}.{dump.table}.sql")
                    tarinfo.size = len(dump.dump)
                    file.addfile(tarinfo, fileobj=io.BytesIO(dump.dump))
            self.log.info("database: %s successfully dumped at: %s", database, filename)


def cli_wrapper(
    *,
    db_url: str,
    ignore_databases: t.Optional[StrList] = None,
    folder: str = ".",
    add_datetime: bool = True,
    datetime_format: OptStr = None,
    as_archive: bool = True,
    file_prefix: OptStr = None,
    db_prefix: OptStr = None,
):
    url = Url.from_raw(db_url)
    _db_prefix = db_prefix or url.path.strip("/")

    service = MysqlBackup(
        dumper=MySQLDumper(
            username=url.username,
            password=url.password,
            hostname=url.hostname,
            port=url.port,
            ignore_databases=ignore_databases,
        ),
        folder=folder,
        add_datetime=add_datetime,
        datetime_format=datetime_format,
    )

    if as_archive is True:
        service.backup_as_archive(file_prefix, _db_prefix)
    else:
        service.backup_single_files(file_prefix, _db_prefix)
