import logging
import sys
import typer

from typer.core import TyperGroup

from mead import __version__


class OrderedGroup(TyperGroup):
    def list_commands(self, ctx):
        return sorted(self.commands)


cli = typer.Typer(
    no_args_is_help=True, 
    add_completion=False,
    name="mead", 
    cls=OrderedGroup
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
