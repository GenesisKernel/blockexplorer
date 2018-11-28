"""

Genesis Block Explorer CLI Manager

Usage:
  genbc-blex-cli config-add-sqla-bind --name=<name> --value=<value> [--config=<config-path>]
  genbc-blex-cli config-clear-sqla-binds [--config=<config-path>]
  genbc-blex-cli config-add-backend-api-url --name=<name> --value=<value> [--config=<config-path>]
  genbc-blex-cli config-clear-backend-api-urls [--config=<config-path>]
  genbc-blex-cli config-add-db-engine --bind-name=<bind-name> --backend-version=<backend-version> [--config=<config-path>]
  genbc-blex-cli config-clear-db-engines [--config=<config-path>]
  genbc-blex-cli config-add-aux-db-engine --bind-name=<bind-name> --backend-version=<backend-version> [--config=<config-path>]
  genbc-blex-cli config-clear-aux-db-engines [--config=<config-path>]
  genbc-blex-cli config-set-redis-url <value> [--config=<config-path>]
  genbc-blex-cli config-set-enable-database-explorer <value> [--config=<config-path>]
  genbc-blex-cli config-set-enable-database-selector <value> [--config=<config-path>]
  genbc-blex-cli config-set-celery-broker-url <value> [--config=<config-path>]
  genbc-blex-cli config-set-celery-result-backend <value> [--config=<config-path>]
  genbc-blex-cli config-set-socketio-host <value> [--config=<config-path>]
  genbc-blex-cli config-set-socketio-port <value> [--config=<config-path>]
  genbc-blex-cli config-set-aux-helpers-bind-name <value> [--config=<config-path>]
  genbc-blex-cli aux-blocks-stat <seq-num> [--config=<config-path>]
  genbc-blex-cli aux-blocks-lock <seq-num> [--config=<config-path>]
  genbc-blex-cli aux-blocks-is-locked <seq-num> [--config=<config-path>]
  genbc-blex-cli aux-blocks-clear <seq-num> [--config=<config-path>]
  genbc-blex-cli aux-blocks-update <seq-num> [--config=<config-path>]
  genbc-blex-cli aux-blocks-unlock <seq-num> [--config=<config-path>]
  genbc-blex-cli -h | --help
  genbc-blex-cli --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --config=<config-path>            Path to configuration file.

Examples:
  genbc-blex-cli config-add-sqla-bind --name genesis-node1 --value postgres://user:password@dbhost:5000/dbname

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
            except TypeError as e:
                pass
