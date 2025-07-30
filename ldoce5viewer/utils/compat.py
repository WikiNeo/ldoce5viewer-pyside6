#!/usr/bin/env python3


try:
    import __builtin__ as builtins
except:
    import builtins

import itertools

range = getattr(builtins, "xrange", builtins.range)
basestring = getattr(builtins, "basestring", str)
zip = getattr(itertools, "izip", zip)
