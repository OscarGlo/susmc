import glob
import json
import os
import shutil
import sys
import zipfile

import click
from PIL import Image
from colorthief import ColorThief
from progress.bar import IncrementalBar
from progress.spinner import Spinner

try:
    from sklearn.cluster import KMeans
except KeyboardInterrupt:
    print("Cancelling execution.")
    exit(1)


def color_filter(img: Image, color: tuple[int, int, int]):
    pixels = img.load()

    # Changes all non fully transparent pixels to the given color
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            a = pixels[i, j][3]
            if a > 0:
                pixels[i, j] = (color[0], color[1], color[2], a)


def get_palette(path):
    palette = ColorThief(path).get_palette(5, 1)

    # Cluster similar colors in 2 groups
    km = KMeans(n_clusters=2, random_state=0).fit(palette)
    color_labels = dict(zip(palette, km.labels_))

    if sum(km.labels_) > 2:
        for c in color_labels.keys():
            color_labels[c] = 1 - color_labels[c]

    # Order colors according to group and general lightness
    palette.sort(key=lambda c: (c[0] + c[1] + c[2]) / (3 * 255) + color_labels[c])
    return palette


def transform(source, dest):
    palette = get_palette(source)

    res = Image.new("RGBA", (16, 16), (0, 0, 0, 0))

    # Base bundle path
    base_path = __file__[:__file__.rindex(os.sep)]

    # Color and stack all layers according to palette
    for i in range(5):
        layer = Image.open(os.path.join(base_path, f"layers/{i}.png"))
        pi = min(i, len(palette) - 1)
        color_filter(layer, palette[pi])
        res = Image.alpha_composite(res, layer)

    res.save(dest)


def amogus(source_folder, dest_folder, debug=True):
    os.makedirs(dest_folder, exist_ok=True)

    files = glob.glob(os.path.join(source_folder, "*.png"))

    bar = None
    if debug:
        bar = IncrementalBar("Processing images...", max=len(files), suffix='%(index)d/%(max)d files')

    for file in files:
        name = file.split(os.path.sep)[-1]
        # Skip overlay files for more colorful amogus
        if not name.endswith("_overlay.png"):
            out = os.path.join(dest_folder, name)
            try:
                transform(file, out)
            except Exception as e:
                print(f"\nError on {name}: {e}")
        if bar:
            bar.next()
    if bar:
        bar.finish()


def sus(lang_path):
    data = None
    # Read
    with open(lang_path) as f:
        data = json.load(f)
        for k in list(data):
            if k.startswith("block.") or k.startswith("item."):
                data[k] = f"Sus {data[k]}"
            else:
                del data[k]
    # Write
    with open(lang_path, "w") as f:
        json.dump(data, f)


@click.command()
@click.option("-f", "--format", "pack_format", default=6, type=click.INT, help="Format id for the pack (6 by default)")
@click.argument("jar_path", type=click.Path(exists=True))
@click.argument("dest_folder", default=".", type=click.Path())
def make_ressourcepack(jar_path, dest_folder, pack_format):
    """
    Creates an amogusified resourcepack from the jar at JAR_PATH,
    and writes it in DEST_FOLDER or the current directory if not specified.
    If DEST_FOLDER does not exist, it will be created.
    """
    name = jar_path.split(os.sep)[-1][:-4]
    contents = zipfile.ZipFile(jar_path)

    # Unzip files from jar
    spin = Spinner("Unzipping files...")
    item = "assets/minecraft/textures/item"
    lang = "assets/minecraft/lang"
    for f in contents.namelist():
        spin.next()
        if f.startswith(item):
            contents.extract(f)
        elif f.startswith(lang):
            contents.extract(f)
    spin.finish()

    # Sussify lang files
    for file in glob.glob(f"{lang}/*.json"):
        sus(file)
    # Amogus item textures
    amogus(item, item)

    # Write pack mcmeta
    with open("pack.mcmeta", "w") as f:
        json.dump({"pack": {"pack_format": pack_format, "description": f"When {name} is sus"}}, f)

    # Write zip folder
    rp_path = os.path.join(dest_folder, f"sus_{name}.zip")
    rp = zipfile.ZipFile(rp_path, "w")
    for root, dirs, files in os.walk("assets"):
        for file in files:
            rp.write(os.path.join(root, file),
                     os.path.relpath(os.path.join(root, file)))
    rp.write("pack.mcmeta")
    rp.close()

    # Remove temp files
    shutil.rmtree("assets")
    os.unlink("pack.mcmeta")

    print(f"Resource pack exported in {rp_path}.")


# Run CLI
if __name__ == '__main__':
    try:
        make_ressourcepack.main(sys.argv[1:], standalone_mode=False)
    except click.exceptions.Abort:
        print("Stopping process...")
        # Remove temp files if any
        assets = os.path.exists("assets")
        pack = os.path.exists("pack.mcmeta")
        if assets or pack:
            if assets:
                shutil.rmtree("assets")
            if pack:
                os.unlink("pack.mcmeta")
            print("Temp files deleted.")
        else:
            print("Nothing to delete.")
    except click.exceptions.ClickException as e:
        # Print command line exceptions
        print(e)
