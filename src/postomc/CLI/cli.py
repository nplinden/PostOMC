import click
from postomc.CLI.convert import convert

@click.group()
def cli():
    """Command line utility for post-processing OpenMC depletion results."""
    pass

cli.add_command(convert)