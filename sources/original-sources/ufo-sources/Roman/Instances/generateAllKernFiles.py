"""
This script takes a path to a folder as input, finds all
the UFOs inside that folder and its subdirectories, and outputs each
font's kerning in feature file syntax. If a path is not provided, the
script uses the current path as the top-most directory. The name of
the resulting kerning FEA file is managed by the kernFeatureWriter
module.
"""

from __future__ import print_function

import os
import sys
import time

libraryNotFound = False

try:
    from defcon import Font
except ImportError:
    print(
        "ERROR: This script requires defcon. It can be downloaded from "
        "https://github.com/typesupply/defcon"
    )
    libraryNotFound = True
try:
    import kernFeatureWriter
except ImportError:
    print(
        "ERROR: This script requires kernFeatureWriter.py. It can be "
        "downloaded from https://github.com/adobe-type-tools/python-modules"
    )
    libraryNotFound = True


def getFontPaths(startpath):
    font_paths = []
    for dir_path, _, _ in os.walk(startpath):
        if dir_path.lower().endswith('.ufo'):
            font_paths.append(dir_path)
    return sorted(font_paths)


def doTask(fonts, startpath):
    totalFonts = len(fonts)
    print("%d fonts found\n" % totalFonts)

    for i, font in enumerate(fonts, 1):
        folderPath, fontFileName = os.path.split(font)
        styleName = os.path.basename(folderPath)
        folderPath = os.path.abspath(folderPath)

        os.chdir(folderPath)

        exportMessage = 'Exporting kern files for %s...(%d/%d)' % (
            styleName, i, totalFonts)
        print('*' * len(exportMessage))
        print(exportMessage)

        ufoFont = Font(fontFileName)
        kernFeatureWriter.run(ufoFont, folderPath, writeSubtables=True)

        os.chdir(startpath)


def run():
    # if a path is provided
    if len(sys.argv[1:]):
        baseFolderPath = os.path.normpath(sys.argv[1])

        # make sure the path is valid
        if not os.path.isdir(baseFolderPath):
            print('Invalid directory.')
            return 1

    # if a path is not provided, use the current directory
    else:
        baseFolderPath = os.getcwd()

    t1 = time.time()
    fontsList = getFontPaths(baseFolderPath)
    startpath = os.path.abspath(os.path.curdir)
    if len(fontsList):
        doTask(fontsList, startpath)
    else:
        print("No fonts found")
        return 1

    t2 = time.time()
    elapsedSeconds = t2 - t1
    elapsedMinutes = elapsedSeconds / 60

    if elapsedMinutes < 1:
        print(('Completed in %.1f seconds.' % elapsedSeconds))
    else:
        print(('Completed in %.1f minutes.' % elapsedMinutes))


if __name__ == '__main__':
    if libraryNotFound:
        sys.exit(1)
    run()
