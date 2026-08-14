import importlib.util
import inspect
import logging
import os
import subprocess
import sys
from abc import ABC
from pathlib import Path
from types import FunctionType, ModuleType

logger = logging.getLogger(__name__)

DEFAULT_CONNECTION_PORT = 5000
LIB_NAME = "srpcLib"


def get_service_name(full_interface_path: str):
    interface_file_name = os.path.basename(full_interface_path).split(".")[0]
    return interface_file_name.split("_")[0]


def get_service_interface_class_name(full_interface_path: str) -> str:
    interface_file_name = os.path.basename(full_interface_path).split(".")[0]
    chunks = interface_file_name.split("_")
    class_name = ""
    for chunk in chunks:
        class_name += chunk.capitalize()
    return class_name


def remove_type_hint_from_param_list(param_list: list[str]) -> list[str]:
    return [param_str.split(":")[0] for param_str in param_list]


def get_service_dir(full_interface_path: str):
    return os.path.dirname(full_interface_path)


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


def check_file_type_hints(file_path: str) -> tuple[bool, str]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--disallow-untyped-defs",
            "--disallow-any-generics",
            file_path,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout
    if output[0:7] == "Success":
        return True, "Passed"
    else:
        output = result.stderr
        return False, output


def check_service_definition(full_interface_path: str):
    file_path = Path(full_interface_path)
    if not (file_path.suffix == ".py"):
        raise ValueError(f"{full_interface_path} is not a .py file")
    try:
        passed, msg = check_file_type_hints(full_interface_path)
        if not passed:
            raise ValueError(f"Error during SRPC type hint Check.\n{msg}")
    except ValueError as e:
        logger.error(str(e))
        exit(1)


def get_proc_id_dict(full_interface_path: str) -> dict[str, int]:
    module = load_module_from_path(full_interface_path)
    interface = get_interface_from_module(module)

    index: int = 0
    procs = {}
    procedures = {
        name: obj
        for name, obj in interface.__dict__.items()
        if inspect.isfunction(obj) and not name.startswith("__")
    }
    for proc_name in procedures:
        procs[proc_name] = index
        index = index + 1

    return procs


def get_proc_param_list(proc: FunctionType) -> str:
    sig = inspect.signature(proc)
    formatted_args = []
    for name, param in sig.parameters.items():
        if name not in ("self", "cls"):
            # Get the class name as a string (e.g., 'int') [1]
            type_name = (
                param.annotation.__name__
                if param.annotation is not inspect.Parameter.empty
                else "Any"
            )
            formatted_args.append(f"{name}:{type_name}")

    return formatted_args


def get_procedures(full_interface_path: str) -> list[tuple[str, str, str]]:
    module = load_module_from_path(full_interface_path)
    interface = get_interface_from_module(module)

    procedures = {
        name: obj
        for name, obj in interface.__dict__.items()
        if inspect.isfunction(obj) and not name.startswith("__")
    }
    procs = []
    for proc_name, proc in procedures.items():
        proc_param_list = get_proc_param_list(proc)
        proc_return_type = inspect.signature(proc).__str__().split("->")[1].strip(" ")
        procs.append((proc_name, proc_return_type, proc_param_list))

    return procs
