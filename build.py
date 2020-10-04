"""Build the projects."""

import os
import re
import zipfile

EXCLUDEDIRS = ["build"]


def main():
    """Main"""
    join = os.path.join
    try:
        os.mkdir("build")
    except FileExistsError:
        pass
    for folder in os.listdir():
        if os.path.isdir(folder) and not folder.startswith(".") and folder not in EXCLUDEDIRS:
            mainscript = [file for file in os.listdir(folder)
                          if file.endswith("StreamlabsSystem.py")][0]
            with open(join(folder, mainscript)) as readfile:
                text = readfile.read()
            version = re.search(r"""Version = ["'](.+)["']""", text).group(1)
            zipname = "{}-{}.zip".format(folder, version)
            with zipfile.ZipFile(os.path.join("build", zipname), 'w') as myzip:
                for file in os.listdir(folder):
                    if file.endswith(".py") or file == "UI_Config.json":
                        myzip.write(join(folder, file))
                        print("File {} added to {}".format(file, zipname))


if __name__ == '__main__':
    main()
