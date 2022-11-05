from vbcore.date_helper import DateFmt
from vbcore.db.mysql_dumper import MySQLDumper, MysqlBackup


def backup_as_archive(_dumper: MySQLDumper, **kwargs):
    MysqlBackup(_dumper, **kwargs).backup_as_archive(file_prefix="backup")


def backup_single_files(_dumper: MySQLDumper, **kwargs):
    MysqlBackup(_dumper, **kwargs).backup_single_files(file_prefix="database")


if __name__ == "__main__":
    fmt = DateFmt.AS_NUM
    dumper = MySQLDumper(username="test", password="test")
    backup_as_archive(dumper, add_datetime=True, datetime_format=fmt)
    backup_single_files(dumper, add_datetime=False, datetime_format=fmt)
