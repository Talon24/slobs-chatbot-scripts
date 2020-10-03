"""Build the projects."""

import os
import zipfile

EXCLUDEDIRS = ["release"]


def main():
    """Main"""
    for folder in os.listdir():
        if os.path.isdir(folder) and not folder.startswith(".") and folder not in EXCLUDEDIRS:
            # print(folder)
            with zipfile.ZipFile(folder + '.zip', 'w') as myzip:
                for file in os.listdir(folder):
                    if file.endswith(".py") or file == "UI_Config.json":
                        myzip.write(os.path.join(folder, file))


if __name__ == '__main__':
    main()
