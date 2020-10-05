"""Build the projects."""

import os
import re
import json
import zipfile
import pathlib

EXCLUDEDIRS = ["build"]


def main():
    """Main"""
    try:
        os.mkdir("build")
    except FileExistsError:
        pass
    for folder in os.listdir():
        folder = pathlib.Path(folder)
        if folder.is_dir() and not folder.name.startswith(".") and folder.name not in EXCLUDEDIRS:
            mainscript = [file for file in folder.iterdir()
                          if file.name.endswith("StreamlabsSystem.py")][0]
            with open(mainscript) as readfile:
                text = readfile.read()
            version = re.search(r"""Version = ["'](.+)["']""", text).group(1)
            zipname = "{}-{}.zip".format(folder, version)
            with zipfile.ZipFile(os.path.join("build", zipname), 'w') as myzip:
                settings, settings_name = create_basic_settings(folder)
                print("File {} added to {}".format(settings_name.name, zipname))
                myzip.writestr(str(settings_name), settings)
                for file in folder.iterdir():
                    if file.suffix == ".py" or file.name == "UI_Config.json":
                        myzip.write(file)
                        print("File {} added to {}".format(file.name, zipname))


def create_basic_settings(folder):
    """Create initial settings.json file."""
    with open(folder / "UI_Config.json") as readfile:
        data = json.load(readfile)
    outfile_name = folder / data["output_file"]
    del data["output_file"]
    outdata = {key: value["value"] for key, value in data.items()}
    out = json.dumps(outdata, indent=4)
    return out, outfile_name




if __name__ == '__main__':
    main()
