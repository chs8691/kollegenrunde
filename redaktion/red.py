import argparse
import re
import json
from os import path, mkdir
from shutil import copyfile

args = None
log_switch = False

post_file_name = "index.md"
post_file_archetype = path.join("..", "archetypes", "post.md")


def execute_convert():
    print("convert: under construction")


def execute_post():
    print("post: under construction")


def execute_close():
    print("close: under construction")


def execute_init():
    pattern = re.compile("^\d{8}$")

    if not pattern.match(args.date):
        exit_on_error("Wrong date format, must be <YYYYMMDD>")

    with open('.settings', 'w') as f:
        json.dump({'date': args.date}, f)

    if path.exists(get_out_path()):
        print(f"Post' directory '{get_out_path()}' already exists.")
    else:
        mkdir(get_out_path())
        print(f"Post' directory '{get_out_path()}' created.")

    if path.exists(get_in_path()):
        print(f"{get_in_path()} already exists. Add/remove your original images here.")
    else:
        mkdir(get_in_path())
        print(f"{get_in_path()} created. Add/remove your original images here.")

    print("After that, the next step would be to convert and copy your images into the post: call 'convert'.")

    # post_file_path = path.join(get_out_path(), post_file_name)
    # if path.exists(post_file_path):
    #     print(f"{post_file_path} already exists. Open it to edit your blog content.")
    # else:
    #     copyfile(post_file_archetype, post_file_path)
    #     print(f"{post_file_path} created. Edit '{post_file_name}' with your blog content.")


def get_in_path():
    with open('.settings') as f:
        settings = json.load(f)
        return path.join("in", "posts", settings['date'])


def get_out_path():
    with open('.settings') as f:
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

    init_parser.set_defaults(func=execute_init)

    # ######### convert #########
    convert_parser = sub_parsers.add_parser('convert',
                                         help="Convert images into a proper size",
                                         description="Images must be in in/post/<DDDDYYMM>"
                                         )
    init_parser.add_argument('--remove', action="store_true",
                             help="Before converting, all existing images in the post will be removed. "
                                  "Be careful with this option! Particularly, if there are multiple editors working "
                                  "on this blog."
                             )

    init_parser.set_defaults(func=execute_convert)

    # ######### post #########
    post_parser = sub_parsers.add_parser('post',
                                         help=f"Generate post file '{post_file_name}'",
                                         description=f"Based on post.md in the archetypes folder, {post_file_name} "
                                                     f"will be created. For converted images, default settings will "
                                                     f"be added."
                                         )
    post_parser.add_argument('--force', action="store_true",
                             help="Overwrites existing post file."
                             )

    post_parser.set_defaults(func=execute_post)

    # ######### close #########
    close_parser = sub_parsers.add_parser('close',
                                         help=f"Close editorial by clean up the in directory",
                                         description=f"Removes in directory (with your original images). "
                                                     f"You can reopen the process with a new 'init'."
                                         )

    close_parser.set_defaults(func=execute_close)

    args = parser.parse_args()

    if args.verbose:
        set_log_switch(True)

    args.func()


def set_log_switch(value):
    global log_switch
    log_switch = value


def exit_on_error(message):
    print(message)
    exit(1)


if __name__ == '__main__':
    parse_args()