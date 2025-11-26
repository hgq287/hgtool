from argparse import ArgumentParser, Namespace, _ArgumentGroup
from functools import partial
from pathlib import Path
from typing import Any, Optional, Union

from hgf.commands.cli_options import AVAILABLE_CLI_OPTIONS
from hgf.constants import DEFAULT_CONFIG

ARGS_COMMON = [
    "logfile", 
    "version"
    ]

NO_CONF_REQUIRED = [
]

NO_CONF_ALLOWED = []

ARGS_WEBSERVER: list[str] = []

ARGS_FILES_CONVERTER: list[str] = [
    "convert_to_csv",
]

class Arguments:
    """
    Arguments Class. Manage the arguments received by the cli
    """

    def __init__(self, args: Optional[list[str]]) -> None:
        self.args = args
        self._parsed_arg: Optional[Namespace] = None

    def get_parsed_arg(self) -> dict[str, Any]:
        if self._parsed_arg is None:
            self._build_subcommands()
            self._parsed_arg = self._parse_args()

        return vars(self._parsed_arg)

    def _parse_args(self) -> Namespace:
        """
        Parses given arguments and returns an argparse Namespace instance.
        """
        parsed_arg = self.parser.parse_args(self.args)
        return parsed_arg

    def _build_args(
        self, optionlist: list[str], parser: Union[ArgumentParser, _ArgumentGroup]
    ) -> None:
        for val in optionlist:
            opt = AVAILABLE_CLI_OPTIONS[val]
            parser.add_argument(*opt.cli, dest=val, **opt.kwargs)

    def _build_subcommands(self) -> None:
        """
        Builds and attaches all subcommands.
        :return: None
        """
        # Build shared arguments (as group Common Options)
        _common_parser = ArgumentParser(add_help=False)
        group = _common_parser.add_argument_group("Common arguments")
        self._build_args(optionlist=ARGS_COMMON, parser=group)

        # Build main command
        self.parser = ArgumentParser(
        prog="hgf", description="A toolkit for developers.",
        )

        self._build_args(optionlist=["version_main"], parser=self.parser)

        from hgf.commands import (
        start_webserver,
        convert_file,
        )

        subparsers = self.parser.add_subparsers(
            dest="command",
            # Use custom message when no subhandler is added
            # shown from `main.py`
            # required=True
        )

        # Add serve subcommand
        serve_cmd = subparsers.add_parser(
            "serve", help="Serve module.", parents=[_common_parser]
        )

        serve_cmd.set_defaults(func=start_webserver)
        self._build_args(optionlist=ARGS_WEBSERVER, parser=serve_cmd)

        # Add file converter subcommand

        file_converter_cmd = subparsers.add_parser(
            "file-converter", help="File converter module.", parents=[_common_parser]
        )
        file_converter_cmd.set_defaults(func=convert_file)

        self._build_args(
            optionlist=ARGS_FILES_CONVERTER, parser=file_converter_cmd
        )