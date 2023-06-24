import typing as t
from functools import partial

import click

from vbcore.date_helper import DateFmt, DateTimeFmt
from vbcore.types import OptFloat, OptInt


def option_as_dict(ctx, param, value):
    _ = ctx, param
    option = {}
    for opt in value:
        tokens = opt.split("=", 2)
        key, val = tokens if len(tokens) > 1 else (tokens, None)
        option[key] = val
    return option


CliFile = partial(click.Path, file_okay=True, dir_okay=False)
CliDir = partial(click.Path, file_okay=False, dir_okay=True)

CliOutputFile = partial(CliFile, writable=True)
CliInputFile = partial(CliFile, exists=True, readable=True)
CliOutputDir = partial(CliDir, exists=True, writable=True)
CliInputDir = partial(CliDir, exists=True, readable=True)


class Cli:
    option: t.ClassVar = partial(
        click.option, show_default=True, show_envvar=True, default=None
    )
    print: t.ClassVar = partial(click.echo, color=True)
    error: t.ClassVar = partial(click.echo, color=True, err=True)
    argument: t.ClassVar = partial(click.argument, required=True)

    @classmethod
    def abort(cls, message: str, exit_code: int = -1):
        cls.error(TextBold.red(message))
        raise click.exceptions.Exit(exit_code)


class CliOpt:
    string: t.ClassVar = partial(Cli.option, type=click.STRING)
    boolean: t.ClassVar = partial(Cli.option, type=click.BOOL)
    date: t.ClassVar = partial(Cli.option, type=click.DateTime(DateFmt.ISO))
    datetime: t.ClassVar = partial(Cli.option, type=click.DateTime(DateTimeFmt.ISO))
    multi: t.ClassVar = partial(Cli.option, multiple=True, metavar="(multiple)")
    flag: t.ClassVar = partial(
        boolean, is_flag=True, default=False, help="[default: False]"
    )
    dict: t.ClassVar = partial(
        multi, default={}, callback=option_as_dict, metavar="KEY[=VAL]"
    )
    verbose: t.ClassVar = partial(Cli.option, "-v", "--verbose", count=True)

    @classmethod
    def choice(
        cls, *args, values: t.Sequence[str], case_sensitive: bool = True, **kwargs
    ):
        return Cli.option(*args, type=click.Choice(values, case_sensitive), **kwargs)

    @classmethod
    def integer(
        cls,
        *args,
        min_val: OptInt = None,
        max_val: OptInt = None,
        min_open: bool = False,
        max_open: bool = False,
        clamp: bool = False,
        **kwargs,
    ):
        opt_type = click.INT
        if min_val is not None or max_val is not None:
            opt_type = click.IntRange(
                min=min_val,
                max=max_val,
                min_open=min_open,
                max_open=max_open,
                clamp=clamp,
            )
        return Cli.option(*args, **kwargs, type=opt_type)

    @classmethod
    def decimal(
        cls,
        *args,
        min_val: OptFloat = None,
        max_val: OptFloat = None,
        min_open: bool = False,
        max_open: bool = False,
        clamp: bool = False,
        **kwargs,
    ):
        opt_type = click.FLOAT
        if min_val is not None or max_val is not None:
            opt_type = click.FloatRange(
                min=min_val,
                max=max_val,
                min_open=min_open,
                max_open=max_open,
                clamp=clamp,
            )
        return Cli.option(*args, **kwargs, type=opt_type)

    @classmethod
    def debug(cls):
        return partial(cls.flag, "-D", "--debug")


class CliReqOpt:
    string: t.ClassVar = partial(CliOpt.string, required=True)
    boolean: t.ClassVar = partial(CliOpt.boolean, required=True)
    date: t.ClassVar = partial(CliOpt.date, required=True)
    datetime: t.ClassVar = partial(CliOpt.datetime, required=True)
    multi: t.ClassVar = partial(CliOpt.multi, required=True)
    integer: t.ClassVar = partial(CliOpt.integer, required=True)
    decimal: t.ClassVar = partial(CliOpt.decimal, required=True)
    choice: t.ClassVar = partial(CliOpt.choice, required=True)


class Text:
    black: t.ClassVar = partial(click.style, fg="black")
    red: t.ClassVar = partial(click.style, fg="red")
    green: t.ClassVar = partial(click.style, fg="green")
    yellow: t.ClassVar = partial(click.style, fg="yellow")
    blue: t.ClassVar = partial(click.style, fg="blue")
    magenta: t.ClassVar = partial(click.style, fg="magenta")
    cyan: t.ClassVar = partial(click.style, fg="cyan")
    white: t.ClassVar = partial(click.style, fg="white")
    reset: t.ClassVar = partial(click.style, fg="reset")


class TextBright:
    black: t.ClassVar = partial(click.style, fg="bright_black")
    red: t.ClassVar = partial(click.style, fg="bright_red")
    green: t.ClassVar = partial(click.style, fg="bright_green")
    yellow: t.ClassVar = partial(click.style, fg="bright_yellow")
    blue: t.ClassVar = partial(click.style, fg="bright_blue")
    magenta: t.ClassVar = partial(click.style, fg="bright_magenta")
    cyan: t.ClassVar = partial(click.style, fg="bright_cyan")
    white: t.ClassVar = partial(click.style, fg="bright_white")


class TextBold:
    black: t.ClassVar = partial(click.style, fg="black", bold=True)
    red: t.ClassVar = partial(click.style, fg="red", bold=True)
    green: t.ClassVar = partial(click.style, fg="green", bold=True)
    yellow: t.ClassVar = partial(click.style, fg="yellow", bold=True)
    blue: t.ClassVar = partial(click.style, fg="blue", bold=True)
    magenta: t.ClassVar = partial(click.style, fg="magenta", bold=True)
    cyan: t.ClassVar = partial(click.style, fg="cyan", bold=True)
    white: t.ClassVar = partial(click.style, fg="white", bold=True)


class TextBrightBold:
    black: t.ClassVar = partial(click.style, fg="bright_black", bold=True)
    red: t.ClassVar = partial(click.style, fg="bright_red", bold=True)
    green: t.ClassVar = partial(click.style, fg="bright_green", bold=True)
    yellow: t.ClassVar = partial(click.style, fg="bright_yellow", bold=True)
    blue: t.ClassVar = partial(click.style, fg="bright_blue", bold=True)
    magenta: t.ClassVar = partial(click.style, fg="bright_magenta", bold=True)
    cyan: t.ClassVar = partial(click.style, fg="bright_cyan", bold=True)
    white: t.ClassVar = partial(click.style, fg="bright_white", bold=True)
