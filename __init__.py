import os
import settings
import json
import copy
import sys
import git
import shutil

cwd = os.getcwd()
path = os.path.dirname(os.path.realpath(__file__))

class Package:
    def __init__(self, ppath: str, exists: bool = False):
        self.exists = exists
        self.path = ppath
        self.initialized = False
        self.data = {}

    def init(self, data: dict | None = None):
        """Used for initializing new packages"""
        if self.exists:
            raise ValueError("Package aleady exists, use fill instead")
        if self.initialized:
            raise ValueError("Package has already been initialized")
        if not data:
            data = copy(self.default_data)
        self.data = data

        os.makedirs(f"{self.path}/.xod")

        with open(f"{self.path}/.xod/xod.json", "w") as package_json:
            package_json.write(json.dumps(data, indent=4))
                        
        os.mkdir(f"{self.path}/.xod/packages")

        self.initialized = True
        self.exists = True

    def fill(self): 
        """Used for initializing existing packages"""
        if not self.exists:
            raise ValueError("Package doesn't exist, use init instead.")
        with open(f"{self.path}/.xod/xod.json") as xod_json:
            self.data = json.loads(xod_json.read())

        self.initialized = True

    def write_to_file(self):
        with open(f"{self.path}/.xod/xod.json", "w") as package_json:
            package_json.write(json.dumps(self.data, indent=4))

    default_data = {
        "name": "Unnamed",
        "description": "",
        "version": "v1.0.0",
        "programming-lang": None,
        "author": None,
        "repo-url": None,
        "entry": None,
        "test-entry": None,
        "docs": None,
    }

    def install(self, name):
        package_dir_path = f"{self.path}/.xod/packages"
        install_path = f"{package_dir_path}/{name}"
        if name in os.listdir(package_dir_path):
            raise ValueError("Package is already installed")
            return
        if name not in settings.get_setting(f"repos"):
            raise ValueError("Unknown package")
            return
        repo = settings.get_setting(f"repos/{name}")
        git.Repo.clone_from(repo, install_path)
        
        self.data["dependencies"].append(name)
        self.write_to_file()
        shutil.rmtree(f"{install_path}/.git", ignore_errors=True)

    def remove(self, name):
        package_dir_path = f"{self.path}/.xod/packages"
        path_to_remove = f"{package_dir_path}/{name}"
        if name not in os.listdir(package_dir_path):
            raise ValueError("Package is not installed")
            return
        shutil.rmtree(f"{path_to_remove}", ignore_errors=True)

    def get_package(self, name) -> str: # Returns a path
        package_dir_path = f"{self.path}/.xod/packages"
        if name not in os.listdir(package_dir_path):
            raise ValueError("Package is not installed")
            return
        return f"{package_dir_path}/{name}"
    
    def get_module_path(self, package: str|None=None, module: str|None=None) -> str:

        if package is None:
            package_ = self
        else:
            package_path = self.get_package(package)
            package_ = Package(package_path, exists=True)
            package_.fill()
        return package_.get_local_module_path(module)
    
    def get_local_module_path(self, module: str|None = None):
        if module is None:
            entry = self.data["entry"]
            if entry is None:
                raise ValueError("No entry module.")
            return f"{self.path}/{entry}"
        return f"{self.path}/{module}"
    
    def get_local_module(self, module: str|None = None):
        import importlib.util
        spec=importlib.util.spec_from_file_location(
            module if module else "__entry__", self.get_local_module_path(module)
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    
    def get_module(self, package: str|None=None, module: str|None=None):
        import importlib.util
        path = self.get_module_path(package, module)
        package = package if package else "__self__"
        module = module if module else "__entry__"
        spec=importlib.util.spec_from_file_location(
            f"{package}.{module}", path
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

def get_package_path(ppath):
    if os.path.isfile(f"{ppath}/.xod/xod.json"):
        return cwd
    elif (global_ := settings.get_setting("vars/.global")) != None:
        package = Package(global_["path"])
        package.fill()
        return package.path
    else:
        raise ValueError("Not a package")
    
def is_var(text: str):
    return text.startswith(".")
def get_var(var: str):
    special = [".self", ".xod-dir"]
    if var not in special:
        if "/" in var:
            raise ValueError("Variable name cannot contain slashes")
        settings.get_setting(f"vars/{var}")
    else:
        match var:
            case ".self":
                return {
                    "type": "package",
                    "path": get_package_path(cwd)
                }
            case ".xod-dir":
                return {
                    "type": "package",
                    "path": path
                }
def parse_var(text: str):
    if is_var(text):
        return get_var(text)
    if text.startswith("\\."):
        text = text[1:]
    return text

def require(package_name: str|None=None, module: str|None=None):
    package = Package(get_package_path(cwd), True)
    package.fill()
    global_package_json = get_var(".global")
    global_package = None
    if global_package_json:
        global_package = Package(
            get_package_path(global_package_json["path"]), True
        )
        global_package.fill()
    try:
        return package.get_module(package_name, module)
    except ValueError as err:
        if not global_package: raise err
        return global_package.get_module(package_name, module)
