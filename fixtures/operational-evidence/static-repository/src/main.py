from .helper import VALUE

import importlib

module_name = "src.dynamic"
dynamic_module = importlib.import_module(module_name)

RESULT = VALUE
