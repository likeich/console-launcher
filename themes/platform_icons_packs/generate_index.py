# MIT License
# 
# Copyright (c) 2022 TapiocaFox (Yves Chen)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of 
# the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

import json
import os
import re

indexFilename = "index.json"

regex = re.compile("^(?!(?:\._|\.).*).*\.json$")

platformIconsPacks = [f for f in os.listdir('.') if os.path.isdir(f)]
platformIconsPacks = sorted(platformIconsPacks, key=str.casefold)

index = {
    "baseUri": "https://github.com/likeich/Console-Launcher-Public/tree/main/themes/platform_icons_packs",
    "platformIconsPackList": []
}

for d in platformIconsPacks:
    platformIconsPackDir = d
    files = [f for f in os.listdir(platformIconsPackDir) if os.path.isfile(platformIconsPackDir + '/' + f)]
    # files = sorted(files, key=str.casefold)

    for f in files:
        if f == indexFilename:
            f = platformIconsPackDir + '/' + f
            with open(f, encoding='utf-8') as jsonFile:
                try:
                    platformIconsPackIndex = json.load(jsonFile)
                    print(platformIconsPackIndex['name'])
                    print("  Author(s): " + ", ".join(platformIconsPackIndex['authors']) + "")
                    print("  Description: " + str(platformIconsPackIndex['description']))
                    if 'isNSFW' in platformIconsPackIndex.keys():
                        print("  IsNSFW: " + str(platformIconsPackIndex['isNSFW']))
                    else:
                        print("  IsNSFW: " + str(False))
                    print("")

                    platformIconsPackName = platformIconsPackIndex['name']
                    platformIconsPackDescription = platformIconsPackIndex['description']
                    platformIconsPackAuthors = platformIconsPackIndex['authors']
                    platformIconsPackPreviewThumbnailFilename = platformIconsPackIndex[
                        'previewThumbnailFilename']
                    platformIconsPackIsNSFW = platformIconsPackIndex[
                        'isNSFW'] if 'isNSFW' in platformIconsPackIndex.keys() else False

                    index['platformIconsPackList'].append({
                        "platformIconsPackRootPath": platformIconsPackDir,
                        # "platformWallpaperPackIndexPath": f,
                        "platformIconsPackPreviewThumbnailPath": platformIconsPackDir + '/'
                                                                 + platformIconsPackPreviewThumbnailFilename,
                        "platformIconsPackAuthors": platformIconsPackAuthors,
                        "platformIconsPackName": platformIconsPackName,
                        "platformIconsPackDescription": platformIconsPackDescription,
                        "platformIconsPackIsNSFW": platformIconsPackIsNSFW
                    })
                except Exception as e:
                    print(e)
print("Total " + str(len(index['platformIconsPackList'])) + " entries in the index.")
with open(indexFilename, 'w') as outfile:
    json.dump(index, outfile, indent=2, sort_keys=True)
