"""

Genesis Block Explorer CLI Manager

Usage:
  cli_manage add-bind --name=<name> --value=<value> [--config-path=<config-path>]
  cli_manage add-db-engine --bind-name=<bind-name> --backend-version=<backend-version> [--config-path=<config-path>]
  cli_manage -h | --help
  cli_manage --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  cli_manage add-bind --name genesis-node1 --value postgres://user:password@dbhost:5000/dbname

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/blitstern5/blockexplorer
"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    from . import commands
    options = docopt(__doc__, version=VERSION)
    for k, v in options.items(): 
        k = k.replace('-', '_')
        if hasattr(commands, k) and v:
            module = getattr(commands, k)
            commands = getmembers(module, isclass)
            command = [command[1] for command in commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
