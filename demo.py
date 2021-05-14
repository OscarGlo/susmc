import sys
import shutil
from math import ceil, floor

from PIL import Image
from main import unzip_files, amogus

if __name__ == "__main__":
    files = [
        "brown_dye",
        "green_dye",
        "lime_dye",
        "light_blue_dye",
        "pink_dye",
        "red_dye",
        "orange_dye",
        "light_gray_dye",
    ]
    item_path = "assets/minecraft/textures/item/"
    out_files = list(map(lambda f: "out/" + f + ".png", files))
    files = list(map(lambda f: item_path + f + ".png", files))
    unzip_files(sys.argv[1], files=files)

    amogus(item_path, "out")

    # Composition settings
    scaling = 64
    border = 100
    comp_spacing = 50
    item_spacing = 100
    count_row = 4


    def get_img(path):
        return Image.open(path).resize((16 * scaling, 16 * scaling), Image.NEAREST)


    comp_size = 2 * 16 * scaling + comp_spacing
    width = 2 * border + count_row * comp_size + (count_row - 1) * item_spacing
    rows = ceil(len(files) / count_row)
    height = 2 * border + rows * 16 * scaling + (rows - 1) * item_spacing

    # Generate composite img
    img = Image.new("RGBA", (width, height))
    for i in range(len(files)):
        x = border + (i % count_row) * (comp_size + item_spacing)
        y = border + floor(i / count_row) * (16 * scaling + item_spacing)
        original = get_img(files[i])
        img.paste(original, (x, y))

        result = get_img(out_files[i])
        img.paste(result, (x + 16 * scaling + comp_spacing, y))
    img.save("demo.png")

    shutil.rmtree("assets")
    shutil.rmtree("out")
