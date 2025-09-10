import importlib.util
import sys
import os
import inspect
import logging

from abc import ABC
from types import ModuleType

logger = logging.getLogger(__name__)

DEFAULT_BINDER_PORT = 5000


def load_module_from_path(path: str) -> ModuleType:
    module_name = os.path.basename(path).split(".")[0]
    module = None
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Module path {path} does not exist.")

        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except FileNotFoundError as e:
        logger.error(str(e))
        exit(1)
    else:
        logger.info(f"Module {module_name} loaded successfully from {path}.")
        return module


def get_interface_from_module(module: ModuleType) -> ABC:
    interface_name, interface = inspect.getmembers(module, inspect.isclass)[1]
    str1 = module.__name__.split("_")[0]
    expected_interface_name = str1[0].upper() + str1[1:] + "Interface"
    try:
        if not issubclass(interface, ABC):
            raise TypeError(
                f"{module.__name__}, do not contain an implementation of ABC class."
            )
        if not interface_name == expected_interface_name:
            raise NameError(
                f"{module.__name__}, do not contain an ABC class called {expected_interface_name}."
            )
    except TypeError as e:
        logger.error(str(e))
        exit(1)
    except NameError as e:
        logger.error(str(e))
        exit(1)
    else:
        logger.info(f"Interface {interface_name} found in module {module.__name__}.")
        return interface


def get_methodname_signature_map_from_interface(interface) -> dict[str, str]:
    dictionary = {}
    try:
        if not inspect.isclass(interface) or not issubclass(interface, ABC):
            raise TypeError("Provided interface is not a valid ABC class.")

        for name, func in inspect.getmembers(interface, inspect.isfunction):
            dictionary[name] = inspect.signature(func).__str__()

    except TypeError as e:
        logger.error(str(e))
        return {}
    else:
        logger.info(
            f"Methods and signatures extracted successfully from interface {interface.__name__}."
        )
        return dictionary


def extract_params_from_method_sig(method_signature: str) -> list[str]:
    start = method_signature.find("(")
    end = method_signature.find(")", start)
    params = []
    method_signature_raw = method_signature.split("->")[0].strip("()")
    try:
        if start == -1 or end == -1:
            raise ValueError("Invalid signature format")

        param_block = method_signature_raw.split(",")
        param_block.remove("self")

        for raw_param in param_block:
            params.append(raw_param.split(":")[0].strip())
    except ValueError as e:
        logger.error(str(e))
        exit(1)
    else:
        return params


def build_param_tuple(params: list[str]) -> str:
    return f"({', '.join(params)})"
