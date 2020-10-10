import argparse
import re
import json
import sys
from os import path, mkdir, remove, listdir
from shutil import copyfile, rmtree
from PIL import Image

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

args = None
log_switch = False

post_file_name = "index.md"
post_file_backup_name = "~index.md"
post_file_archetype = path.join("..", "archetypes", "post.md")
settings_path = ".settings"


def execute_info():

    if not path.exists(settings_path):
        print("No actual post.")
        return

    print(f"Actual post is: '{settings_get_date()}'")

    exit_invalid_initialization()


def execute_update():
    exit_invalid_initialization()

    yml = yaml.load(get_frontmatters(), Loader=Loader)

    previous_images = settings_get_images()

    convert(get_image_path(yml))

    remove_previous_images(previous_images, yml)

    yml = cleanup_zombies(yml)

    yml = merge_images(yml)

    update_frontmatters(yml)

    print("Done.")


def remove_previous_images(previous_images, yml):
    converted_images = settings_get_images()

    for image in [i for i in previous_images if i not in converted_images]:
        image_path = path.join(get_image_path(yml), image)
        log(f"Removing previous image '{image}'")
        remove(image_path)


def init_date():

    yml = yaml.load(get_frontmatters(), Loader=Loader)

    yml = set_date(yml)

    lines = get_frontmatters()

    lines = update_date(yml, lines)

    content = get_content()
    with open(get_post_file_path(), "w") as f:
        f.write("---\n")
        f.write(lines)
        f.write("---\n")
        f.write(content)


def init_title():

    yml = yaml.load(get_frontmatters(), Loader=Loader)

    yml = set_title(yml)

    lines = get_frontmatters()

    lines = update_title(yml, lines)

    content = get_content()
    with open(get_post_file_path(), "w") as f:
        f.write("---\n")
        f.write(lines)
        f.write("---\n")
        f.write(content)


def update_frontmatters(yml):
    copyfile(get_post_file_path(), get_post_backup_file_path())

    lines = get_frontmatters()

    lines = update_title(yml, lines)
    lines = update_date(yml, lines)
    lines = update_header_image(yml, lines)
    lines = update_featured_image(yml, lines)
    lines = update_captions(yml, lines)

    content = get_content()
    with open(get_post_file_path(), "w") as f:
        f.write("---\n")
        f.write(lines)
        f.write("---\n")
        f.write(content)


def set_title(yml):
    yml['title'] = "Tour " + settings_get_date()[0:4] + "-" + settings_get_date()[4:6] + "-" + settings_get_date()[6:8]

    return yml


def set_date(yml):
    yml['date'] = settings_get_date()[0:4] + "-" + settings_get_date()[4:6] + "-" + settings_get_date()[6:8]

    return yml


def get_image_path(yml):
    return path.join(get_out_path(), get_image_resource_path(yml))


def get_image_resource_path(yml):
    items = [i for i in yml['resources'] if 'src' in i]

    ret = ""

    if len(items) > 0:
        path = items[0]['src']
    # Should never happens
    else:
        path = ''


    reg = re.match("(.*)/\*\*", path)
    if reg is not None and len(reg.groups()) >= 1:
        ret = reg.group(1)

    # log(f"get_image_path={ret}")

    return ret


def merge_images(yml):
    files = get_image_resources(yml)

    if len(files) == 0:
        return yml

    key = 'header_image'
    if key in yml and yml[key] is None:
        yml[key] = files[0]

    key = 'featured_image'
    if key in yml and yml[key] is None:
        yml[key] = files[0]

    # log(f"merge_images {yml}")

    key = 'captions'
    key2 = 'name'
    if key in yml:
        if yml[key] is None:
            yml[key] = []
        for file in files:
            hit = False
            for item in yml[key]:
                if key2 in item and item[key2] == file:
                    hit = True
                    break
            if not hit:
                # log(f"merge_images added {file}")
                yml[key].append(dict(name=file, text=""))

    yml[key] = sorted(yml[key], key=lambda k: k['name'])

    # log(f"merge_images {yml}")
    return yml


def cleanup_zombies(yml):
    files = get_image_resources(yml)

    key = 'header_image'
    if key in yml:
        if yml[key] is not None and not yml[key] in files:
            yml[key] = ""
    else:
        yml[key] = ""

    key = 'featured_image'
    if key in yml:
        if yml[key] is not None and not yml[key] in files:
            yml[key] = ""
    else:
        yml[key] = ""

    # log(f"cleanup_zombies={yml}")

    key = 'captions'
    if key in yml:
        if yml[key] is not None:
            key2 = 'name'
            # log(f"cleanup_zombies={yml[key]}")
            items = yml[key].copy()
            for item in items:
                if not item[key2] in files:
                    # log(f"cleanup_zombies remove item {item[key2]} ")
                    yml[key].remove(item)
    else:
        yml[key] = []

    # log(f"cleanup_zombies ret = {yml}")
    return yml


def get_image_resources(yml):
    files = get_images(get_image_path(yml))
    sub = get_image_resource_path(yml)

    ret = []
    for name in files:
        ret.append(path.join(sub, name))

    return ret


def get_images(dir):
    ret = [f for f in listdir(dir) if f.lower().endswith(".jpg")
           or f.lower().endswith(".jpeg") or f.lower().endswith(".png")]

    ret.sort()

    return ret


def convert(image_path):
    names = []
    for f in get_images(get_in_path()):

        in_path = path.join(get_in_path(), f)
        out_path = path.join(image_path, f)

        log(f"Converting '{in_path}' to '{out_path}'")

        im = Image.open(in_path)

        if im.width <= 1200 and im.height <= 1200:
            copyfile(in_path, out_path)
            continue

        if im.width > im.height:
            new_image = im.resize((1200, round(1200*im.height/im.width)))
        else:
            new_image = im.resize((round(1200*im.width/im.height), 1200))

        new_image.save(out_path, exif=im.info['exif'], quality=80)
        names.append(f)

    settings_save_images(names)


def update_date(yml, lines):
    return re.sub("\ndate:.*\n", f"\ndate: {yml['date']}\n",lines)


def update_featured_image(yml, lines):
    return re.sub("\nfeatured_image:.*\n", f"\nfeatured_image: {yml['featured_image']}\n",lines)


def update_header_image(yml, lines):
    return re.sub("\nheader_image:.*\n", f"\nheader_image: {yml['header_image']}\n",lines)


def update_captions(yml, lines):
    data = yml['captions']

    lines = clear_captions(lines)
    # log(f"update_captions lines={lines}")

    if data is None:
        output = ""
    else:
        output = yaml.dump(data, Dumper=Dumper)

    # log(f"update_captions output={output}")
    lines = re.sub("\ncaptions:.*\n", f"\ncaptions:\n{output}", lines)

    # log(f"update_captions {lines}")
    return lines


def clear_captions(lines):
    arr = lines.split('\n')
    captions = False
    arr2 = []

    for item in arr:
        if item.startswith("captions:"):
            captions = True
            arr2.append(item)
            continue

        if captions:
            if len(item.strip()) == 0:
                captions = False
                arr2.append(item)

        else:
            arr2.append(item)

    ret = ""
    for item in arr2:
        if len(ret) == 0:
            ret = item
        else:
            ret = ret + '\n' + item

    return ret


def update_title(yml, lines):
    return re.sub("\ntitle:.*\n", f"\ntitle: \"{yml['title']}\"\n",lines)


def get_content():
    lines = ""

    # log(f"get_content get_post_file_path={get_post_file_path()}")
    pattern = re.compile("^---$")
    cnt = 0

    with open(get_post_file_path(), "r") as f:
        # log(f"get_content with f={f}")

        for line in f:
            # log(f"get_content {line}")

            if pattern.match(line):
                cnt += 1
                continue

            if cnt < 2:
                continue

            lines = lines + line

    # log(f"get_content return={lines}")
    return lines


def get_frontmatters():
    lines = ""
    with open(get_post_file_path(), "r") as f:
        # log("open")
        pattern = re.compile("^---$")
        cnt = 0

        for line in f:
            # log(line)
            if pattern.match(line):
                cnt += 1
                # log(f"a: {cnt}")
                continue

            if cnt == 0:
                # log(f"b: {cnt}")
                continue

            if cnt == 2:
                # log(f"c: {cnt}")
                break

            # log(line)
            lines = lines + line

    return lines


def execute_cleanup():

    if path.exists(settings_path):
        date = settings_get_date()
    else:
        print("Not initialized: nothing to do.")
        return

    if path.exists(get_in_path()):
        rmtree(get_in_path())
        print(f"Removed '{get_in_path()}'")

    remove(settings_path)

    print(f"{date} closed.")


def settings_get_date():
    with open(settings_path) as f:
        settings = json.load(f)
        return settings['date']


def settings_get_images():
    with open(settings_path) as f:
        settings = json.load(f)
        return settings['images']


def settings_init(date):
    with open(settings_path, 'w') as f:
        json.dump(dict(date=date, images=[]), f)


def settings_save_images(images):

    date = settings_get_date()

    with open(settings_path, 'w') as f:
        json.dump(dict(date=date, images=images), f)


def execute_init():

    # date must match YYYYMMDD pattern
    pattern = re.compile("^\d{8}$")

    if not pattern.match(args.date):
        exit_on_error("Wrong date format, must be <YYYYMMDD>")

    settings_init(args.date)

    # ### in ####
    if path.exists(get_in_path()):
        print(f"Existing in path found. Put your original images here: '{get_in_path()}'")
    else:
        mkdir(get_in_path())
        print(f"Post directory created. Put your original images here: '{get_in_path()}'")

    # ### post dir ####
    if path.exists(get_out_path()):
        if args.clean:
            rmtree(get_out_path())
            mkdir(get_out_path())
            print(f"Existing post directory cleaned: '{get_out_path()}'")
        else:
            print(f"Existing post directory found: '{get_out_path()}'")
    else:
        mkdir(get_out_path())
        print(f"Post' directory created: '{get_out_path()}' ")

    # ### post file ####
    if path.exists(get_post_file_path()):
        print(f"Existing post file found: '{get_post_file_path()}'")
    else:
        copyfile(post_file_archetype, get_post_file_path())
        init_title()
        print(f"New post file created: '{get_post_file_path()}'")

    yml = yaml.load(get_frontmatters(), Loader=Loader)
    image_path = get_image_path(yml)
    if not path.exists(image_path):
        mkdir(image_path)
        print(f"Image directory created: '{get_image_resource_path(yml)}' ")

    init_date()

    print(f"The next step would be to add your images into the '{get_in_path()}' directory. "
          f"After that you can update the post directory '{get_out_path()}' and the post file '{post_file_name}': "
          f"call 'update'.")


def get_post_file_path():
    return path.join(get_out_path(), post_file_name)


def get_post_backup_file_path():
    return path.join(get_out_path(), post_file_backup_name)


def get_in_path():
    with open('.settings') as f:
        settings = json.load(f)
        return path.join("in", "posts", settings['date'])


def log(message):
    """
        Only switched on for development
    """
    if log_switch:
        print(message)


def exit_invalid_initialization():
    if not path.exists(settings_path):
        exit_on_error("Editorial seems not to be initialized.")

    if not path.exists(get_in_path()):
        exit_on_error(f"Invalid in path: '{get_in_path()}'.")

    if not path.exists(get_out_path()):
        exit_on_error(f"Invalid post path: '{get_out_path()}'.")

    if not path.exists(get_post_file_path()):
        exit_on_error(f"No post file found: '{get_post_file_path()}'.")


def get_out_path():
    with open(settings_path) as f:
        settings = json.load(f)
        return path.join("..", "content", "posts", settings['date'])


def parse_args():

    global args

    parser = argparse.ArgumentParser(description='Bring your content into the Hugo blog')

    parser.add_argument("-v", "--verbose",
                        action='store_true',
                        help="Print more info")

    sub_parsers = parser.add_subparsers()

    # ######### init #########
    init_parser = sub_parsers.add_parser('init',
                                         help="Setup a new post or edit an existing one",
                                         description=""
                                         )
    init_parser.add_argument('date', metavar='DATE', type=str,
                             help="Date of the post as <YYYYMMDD>, example: 'init 20201231'")

    init_parser.add_argument('--clean', action="store_true",
                             help="Removes existing post content, if exists."
                                  "Be careful with this option! Particularly, if there are multiple editors working "
                                  "on this blog."
                             )

    init_parser.set_defaults(func=execute_init)

    # ######### update #########
    update_parser = sub_parsers.add_parser('update',
                                           help="Converts images into a proper size and update the post file",
                                           description="Images must be in in/post/<DDDDYYMM>"
                                           )

    update_parser.set_defaults(func=execute_update)

    # ######### cleanup #########
    cleanup_parser = sub_parsers.add_parser('cleanup',
                                            help=f"cleanup editorial by clean up the in directory",
                                            description=f"Removes in directory (with your original images). "
                                            )

    cleanup_parser.set_defaults(func=execute_cleanup)

    args = parser.parse_args()

    if args.verbose:
        set_log_switch(True)

    if len(sys.argv) > 1:
        args.func()
    else:
        execute_info()

def set_log_switch(value):
    global log_switch
    log_switch = value


def exit_on_error(message):
    print(message)
    exit(1)


if __name__ == '__main__':
    parse_args()