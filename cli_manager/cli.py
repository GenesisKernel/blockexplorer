"""

Genesis Block Explorer CLI Manager

Usage:
  cli_manage add-bind --name=<name> --value=<value> [--config-path=<config-path>]
  cli_manage add-be-url --name=<name> --value=<value> [--config-path=<config-path>]
  cli_manage add-db-engine --bind-name=<bind-name> --backend-version=<backend-version> [--config-path=<config-path>]
  cli_manage add-aux-db-engine --bind-name=<bind-name> --backend-version=<backend-version> [--config-path=<config-path>]
  cli_manage set-redis-url --value=<value> [--config-path=<config-path>]
  cli_manage set-enable-database-explorer --value=<value> [--config-path=<config-path>]
  cli_manage set-enable-database-selector --value=<value> [--config-path=<config-path>]
  cli_manage set-celery-broker-url --value=<value> [--config-path=<config-path>]
  cli_manage set-celery-result-backend --value=<value> [--config-path=<config-path>]
  cli_manage set-socketio-host --value=<value> [--config-path=<config-path>]
  cli_manage set-socketio-port --value=<value> [--config-path=<config-path>]
  cli_manage set-aux-helpers-bind-name --value=<value> [--config-path=<config-path>]
  cli_manage aux-blocks-stat <seq-num>
  cli_manage aux-blocks-lock <seq-num>
  cli_manage aux-blocks-is-locked <seq-num>
  cli_manage aux-blocks-clear <seq-num>
  cli_manage aux-blocks-update <seq-num>
  cli_manage aux-blocks-unlock <seq-num>
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
            try:
                command = command(options)
                command.run()
            except TypeError:
                pass
