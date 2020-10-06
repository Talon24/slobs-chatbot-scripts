"""Build the projects."""

import os
import re
import json
import zipfile
import pathlib

EXCLUDEDIRS = ["build", ".git", ".github"]


def main():
    """Main"""
    try:
        os.mkdir("build")
    except FileExistsError:
        pass
    for folder in pathlib.Path(".").iterdir():
        if folder.is_dir() and folder.name not in EXCLUDEDIRS:
            mainfile = find_mainfile(folder)
            version = get_version(mainfile)
            zipname = "{}-{}.zip".format(folder, version)
            with zipfile.ZipFile(os.path.join("build", zipname), 'w') as myzip:
                zip_content(folder, myzip)
                zip_basic_settings(folder, myzip)


def find_mainfile(folder):
    """Find the File that the chatbot can read in the directory."""
    for file in folder.iterdir():
        if file.name.endswith("StreamlabsSystem.py"):
            return file
    raise FileNotFoundError


def get_version(file_path):
    """Import the module at file_path, import it and extract its Version."""
    # module_path = ".".join([*file_path.parts[:-1], file_path.stem])
    # version = importlib.import_module(module_path).Version
    with open(file_path) as readfile:
        text = readfile.read()
    version = re.search(r"""Version = ["'](.+)["']""", text).group(1)
    return version


def zip_content(folder, myzip):
    """Zip the content of the module."""
    for file in folder.iterdir():
        if file.suffix == ".py" or file.name == "UI_Config.json":
            myzip.write(file)
            print("File {} added to {}".format(file.name, myzip.filename))


def zip_basic_settings(folder, myzip):
    """Create initial settings.json file."""
    try:
        with open(folder / "UI_Config.json") as readfile:
            data = json.load(readfile)
    except FileNotFoundError:
        return  # No GUI, so no settings required
    settings_name = folder / data["output_file"]
    del data["output_file"]
    # "value" is not in button-fields
    outdata = {key: value["value"] for key, value in data.items() if "value" in value}
    settings = json.dumps(outdata, indent=4)
    myzip.writestr(str(settings_name), settings)
    print("File {} added to {}".format(settings_name.name, myzip.filename))


if __name__ == '__main__':
    main()
