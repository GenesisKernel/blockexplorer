"""The base command."""

import os
import sys

from ... import config_editor
from ...app import get_config_path

class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

    @property
    def config_path(self):
        return get_config_path(self.options.get('--config'),
                               allow_unknown_args=True)

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')
