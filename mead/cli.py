import logging
import sys
import typer
import importlib
import importlib.util
from pathlib import Path

from typer.core import TyperGroup

from mead import __version__


class OrderedGroup(TyperGroup):
    def list_commands(self, ctx):
        return sorted(self.commands)


cli = typer.Typer(
    no_args_is_help=True, add_completion=False, name="mead", cls=OrderedGroup
)

logger = logging.getLogger("mead.cli")


@cli.command()
def version():
    """
    Show mead version
    """
    logger.info("received command version()")
    logger.debug(f"version loaded: {__version__}")
    typer.echo(f"mead {__version__}")


@cli.command()
def run(model_name: str):
    importlib.import_module(f"mead.models.{model_name}")


@cli.command()
def list():
    specs = importlib.util.find_spec("mead.models")
    if specs is not None and specs.submodule_search_locations is not None:
        location = specs.submodule_search_locations[0]
        model_loc = Path(location)
        for m in model_loc.glob("*.py"):
            print(m.stem)


@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable info logging"),
):
    log_level = logging.FATAL
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO

    logging.basicConfig(level=log_level)

    # call help on the absence of a command
    if ctx.invoked_subcommand is None:
        logger.info("no subcommand given, default to help message")
        typer.echo(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    sys.exit(cli())
