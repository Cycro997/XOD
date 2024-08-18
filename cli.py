import git
import sys
import os
import json
import settings
import shutil
import __init__ as xod
import copy

cli_args = sys.argv[1:]
if len(cli_args) == 0:
    command = "help"
else:
    command = cli_args[0]
cwd = os.getcwd()
path = os.path.dirname(os.path.realpath(__file__))

def process_cmd():
    def first_arg_is_help():
        if len(cli_args) == 1:
            return False
        return cli_args[1] == "--help"

    match command:
        case "init":
            if not first_arg_is_help():
                config = copy.copy(xod.Package.default_data)
                inp = None

                print("Creating a xod package.")
                print(
                    "You will be asked several questions to help you create the"
                    " package."
                )
                print("Text in (square) brackets is the default answer")

                inp = input("Package name [Unnamed]> ") or "Unnamed"
                config["name"] = inp
                inp = input("Description []> ")
                config["description"] = inp
                inp = input("Version [v1.0.0]> ") or "v1.0.0"
                config["version"] = inp
                inp = input("Programming language [null]> ") or None
                config["programming-lang"] = inp
                inp = input("Author [null]> ") or None
                config["author"] = inp
                inp = input("Repository URL [null]> ") or None
                config["repo-url"] = inp
                inp = input("Entry point [null]> ") or None
                config["entry"] = inp
                inp = input("Test entry point [null]> ") or None
                config["test-entry"] = inp
                inp = input("Documentation path [null]> ") or None
                config["docs"] = inp
                while 1:
                    print("Package type [project]")
                    print("(project, install)")
                    inp = input("> ") or "install"
                    if inp in ["project", "install"]:
                        config["type"] = inp
                        break
                    else:
                        print("Invalid package type", file=sys.stderr)
                inp = input("Entry command (posix) [null]> ") or None
                config["entry-cmd-posix"] = inp
                inp = input("Entry command (nt) [null]> ") or None
                config["entry-cmd-nt"] = inp

                package = xod.Package(".")
                package.init(config)

            else:
                print("xod init")
                print("Creates a new xod package")
                print(
                    "Asks multiple questions so you don't have to manually "
                    "add the info to your package"    
                )
        case "help":
            print("Xod package manager")
            print(
                "Commands (for extra help, add --help to the"
                "end of a command):"
            )
            print("init - creates a new package")
        case "set":
            if not first_arg_is_help():
                if not cli_args[1].startswith("."):
                    print("Expected variable", file=sys.stderr)
                    return
                try:
                    cli_args[2] = xod.parse_var(cli_args[2])
                except KeyError as err:
                    print(err, file=sys.stderr)
                settings.set_setting(f"vars/{cli_args[1]}", cli_args[2])
            else:
                print("xod set")
                print("Sets a variable")
                print(
                    "First argument is the variable name starting with"
                    " a dot and the second is the new value"
                )
        case "get":
            if not first_arg_is_help():
                try:
                    if cli_args[1].startswith("."):
                        print(xod.get_var(cli_args[1]))
                    else:
                        print(
                            "Variable name must start with '.'",
                            file=sys.stderr
                        )
                except KeyError:
                    print(
                        f"Variable {cli_args[1]} is not defined",
                        file=sys.stderr
                    )
                except ValueError as err:
                    print(str(err), file=sys.stderr)
            else:
                print("xod get")
                print("Gets a variable's value")
                print(
                    "Takes the variable name starting with a dot "
                    "and returns its value"
                )
        case "install":
            if not first_arg_is_help():
                name = cli_args[1]
                package = xod.Package(cwd, True)
                package.fill()
                package.install(name)
            else:
                print("xod install")
                print(
                    "Installs the package whose name is the 1st "
                    "argument."
                )
        case "remove":
            if not first_arg_is_help():
                name = cli_args[1]
                name = cli_args[1]
                package = xod.Package(cwd, True)
                package.fill()
                package.remove(name)
                print("xod install")
                print(
                    "Installs the package whose name is the 1st "
                    "argument."
                )

process_cmd()

print(command)
