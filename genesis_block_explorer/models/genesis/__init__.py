use_models = 'explicit'
use_models = 'automap'

if use_models == 'explicit':
    from .explicit import *
elif use_models == 'automap':
    from .automap import *
else:
    raise Exception("Unknown way to load models")
