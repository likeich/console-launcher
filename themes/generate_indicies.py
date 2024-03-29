import json
import os
import glob

class ThemeConfig:
    def __init__(self, baseUri, themeList):
        self.baseUri = baseUri
        self.themeList = themeList

    def __str__(self):
        return f"ThemeConfig(baseUri={self.baseUri}, themeList={self.themeList})"

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.__dict__, file, indent=4)

class IconPack:
    def __init__(self, name, description, authors, sources, newImageCost, artistContact, previewFilename, iconList, bannerList, posterList):
        self.name = name
        self.description = description
        self.authors = authors
        self.sources = sources
        self.newImageCost = newImageCost
        self.artistContact = artistContact
        self.previewFilename = previewFilename
        self.iconList = iconList
        self.bannerList = bannerList
        self.posterList = posterList

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.__dict__, file, indent=4)

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        return cls(**data)


config = ThemeConfig(
    baseUri="https://github.com/likeich/console-launcher/tree/main/themes",
    themeList=[name for name in os.listdir() if os.path.isdir(name) and name != "platform_icons_packs"]
)
config.save_to_file("themes.json")

valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"]
image_folders = ["icons", "banners", "posters"]
for theme in config.themeList:
    icon_pack = IconPack.load_from_file(f"{theme}/theme.json")

    for folder in image_folders:
        file_list = [os.path.basename(filename) for ext in valid_extensions for filename in glob.glob(f'{theme}/{folder}/*{ext}')]
        if folder == "icons":
            icon_pack.iconList = file_list
        elif folder == "banners":
            icon_pack.bannerList = file_list
        elif folder == "posters":
            icon_pack.posterList = file_list

    icon_pack.save_to_file(f"{theme}/theme.json")
    print(f"Generated {len(icon_pack.iconList)} icons, {len(icon_pack.bannerList)} banners, and {len(icon_pack.posterList)} posters for {theme}.")

print(f"Generated {len(config.themeList)} themes.")
