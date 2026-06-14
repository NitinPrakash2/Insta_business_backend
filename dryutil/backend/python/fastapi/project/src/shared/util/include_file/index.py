import os
import importlib
import types
from typing import Callable, Union, List, Tuple


def include_file(
    path: str,
    callback: Callable[[str, types.ModuleType], None],
    recursive: bool = False
) -> None:
    """
    Import Python files from a file or folder path.
    
    Args:
        path: File path ("controllers/user.py") or folder path ("controllers/api/v1").
        callback: Function to execute for each loaded module (name, module).
        recursive: If True, include nested folders as well.
    """

    #set vars..
    modules: List[Tuple[str, types.ModuleType]] = []


    def to_package_path(folder_path: str) -> str:
        return folder_path.replace("/", ".").replace("\\", ".")

    if os.path.isfile(path):
        # case: direct file
        folder, file = os.path.split(path)
        base_package = to_package_path(folder)
        module_name = f"{base_package}.{file[:-3]}"
        module = importlib.import_module(module_name)
        callback(module_name, module)
        modules.append((module_name, module))


    elif os.path.isdir(path):
        # case: folder
        base_package = to_package_path(path)

        if recursive:
            for root, _, files in os.walk(path):
                rel_root = os.path.relpath(root, path).replace(os.sep, ".")
                prefix = f"{base_package}" if rel_root == "." else f"{base_package}.{rel_root}"

                for file in files:
                    if file.endswith(".py") and file != "__init__.py" and file.endswith("__OLD.py")==False :
                        module_name = f"{prefix}.{file[:-3]}"
                        module = importlib.import_module(module_name)
                        callback(module_name, module)
                        modules.append((module_name, module))

        else:
            for file in os.listdir(path):
                if file.endswith(".py") and file != "__init__.py" and file.endswith("__OLD.py")==False :
                    module_name = f"{base_package}.{file[:-3]}"
                    module = importlib.import_module(module_name)
                    callback(module_name, module)
                    modules.append((module_name, module))





    #set..
    return modules







"""
==USAGE==
include_file("controllers/api/v1/user.py", lambda name, module: print(name, module))
def callback(name, module):
    print(f"✅ Loaded {name}")
include_file("controllers/api/v1/user.py", callback)


==eg==

def handle_module(name, module):
    print(f"✅ Loaded {name}")
    if hasattr(module, "router"):
        app.include_router(module.router)

# Load a single file
include_file("controllers/api/v1/user.py", handle_module)

# Load files in a folder (no recursion)
include_file("controllers/api/v1", handle_module)

# Load files in a folder (with recursion)
include_file("controllers", handle_module, recursive=True)



==inline-eg==
include_file("src/parties/party_1/schema/instance.py", lambda name, module: ())[0][1].body


"""