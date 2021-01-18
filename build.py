"""Build the projects."""

import os
import re
import json
import zipfile
import pathlib

EXCLUDEDIRS = ["build", ".git", ".github"]


def main():
    """Main"""
    generate_script_zips()
    gather_all()


def generate_script_zips():
    """Make the script zipfiles, build the settings-json file from defaults."""
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


def gather_all():
    """Make a File with all the zips and the readme file."""
    version = "0.0.0"
    build = pathlib.Path("./build")
    zips = []
    for folder in pathlib.Path(".").iterdir():
        if folder.is_dir() and folder.name not in EXCLUDEDIRS:
            mainfile = find_mainfile(folder)
            file_version = get_version(mainfile)
            version = version_add(version, file_version)
            zips.append(build / "{}-{}.zip".format(folder, file_version))
    target = build / "All Scripts-{}.zip".format(version)
    with zipfile.ZipFile(target, "w") as myzip:
        print("Generating collection file {}".format(target))
        for file in zips:
            myzip.write(file)
            print("Added to collection file: {}".format(file))
        myzip.write("README.md")
        myzip.write("LICENSE")


def version_add(version1, version2):
    """Add two tuples elementwise."""
    version = [int(first) + int(second) for first, second
               in zip(version1.split("."), version2.split("."))]
    return "{}.{}.{}".format(*version)


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
        if file.suffix in (".py", ".txt") or file.name == "UI_Config.json":
            myzip.write(file)
            print("In {} this was added: {}".format(myzip.filename, file.name))


def zip_basic_settings(folder, myzip):
    """Create initial settings.json file."""
    try:
        with open(folder / "UI_Config.json", encoding="utf-8-sig") as readfile:
            data = json.load(readfile)
    except FileNotFoundError:
        return  # No GUI, so no settings required
    settings_name = folder / data["output_file"]
    del data["output_file"]
    # "value" is not in button-fields
    outdata = {key: value["value"] for key, value in data.items() if "value" in value}
    settings = json.dumps(outdata, indent=4, ensure_ascii=False)
    myzip.writestr(str(settings_name), settings)
    print("In {} this was added: {}".format(myzip.filename, settings_name.name))


if __name__ == '__main__':
    main()
