# Open your $EDITOR to compose a message in weechat
#
# Usage:
# /edit [extension]
# /fenced [extension]
#
# Optional settings:
# /set plugins.var.python.edit.editor "vim -f"
# /set plugins.var.python.edit.terminal "xterm"
# /set plugins.var.python.edit.run_externally "false"
#
# History:
# 2022-05-18
# Version 1.1.0: Use XDG Base Dir, support extension and fences, make editor
#                and terminal options more flexible, and small fixes
# 2015-10-18
# Version 1.0.2: Add the ability to run the editor in a external terminal
# Version 1.0.1: Add configurable editor key
# Version 1.0.0: initial release

import os
import os.path
import shlex
import subprocess
import weechat

# script options
SETTINGS = {
    "editor": (
        "",
        "The editor command. You can customize by inserting the {} "
        "placeholder in place of the filename.",
    ),
    "terminal": (
        "",
        "The terminal command. You can customize by inserting the {} "
        "placeholder in place of the editor command.",
    ),
    "run_externally": (
        "off",
        "Run the editor externallly (using the terminal command).",
    ),
}

FILE = ""
FENCED = False


def xdg_cache_dir():
    return os.path.expanduser(os.environ.get("XDG_CACHE_HOME", "~/.cache/"))


def weechat_cache_dir():
    cache_dir = os.path.join(xdg_cache_dir(), "weechat")
    if os.path.exists(cache_dir):
        return cache_dir
    return os.path.expanduser(os.environ.get("WEECHAT_HOME", "~/.weechat/"))


def editor_process_cb(data, command, return_code, out, err):
    buf = data

    if return_code != 0:
        cleanup(buf)
        weechat.prnt("", "{}: {}".format(err.strip(), return_code))
        return weechat.WEECHAT_RC_ERROR

    if return_code == 0:
        read_file(buf)
        cleanup(buf)

    return weechat.WEECHAT_RC_OK


def cleanup(buf):
    try:
        os.remove(FILE)
    except (OSError, IOError):
        pass

    weechat.command(buf, "/window refresh")


def read_file(buf):
    try:
        with open(FILE) as f:
            text = f.read()

        if text and text[-1] == "\n":
            text = text[:-1]  # remove trailing newline if exists.
        if FENCED:
            text = "```\n" + text + "\n```"

        weechat.buffer_set(buf, "input", text)
        weechat.buffer_set(buf, "input_pos", str(len(text)))

    except (OSError, IOError):
        pass

    weechat.command(buf, "/window refresh")


def hook_editor_process(terminal, editor, buf):
    if "{}" in editor:
        editor_cmd = editor.format(FILE)
    else:
        editor_cmd = "{} {}".format(editor, FILE)
    if "{}" in terminal:
        command = terminal.format(editor_cmd)
    else:
        command = '{} -e "{}"'.format(terminal, editor_cmd)
    weechat.hook_process(command, 0, "editor_process_cb", buf)


def run_blocking(editor, buf):
    cmd = shlex.split(editor) + [FILE]
    code = subprocess.Popen(cmd).wait()

    if code != 0:
        cleanup(buf)

    read_file(buf)


def edit(data, buf, args, fenced=False):
    editor = weechat.config_get_plugin("editor") or os.environ.get(
        "EDITOR", "vim -f"
    )

    terminal = weechat.config_get_plugin("terminal") or os.getenv("TERMCMD")

    terminal = terminal or "xterm"

    run_externally = weechat.config_string_to_boolean(
        weechat.config_get_plugin("run_externally")
    )
    run_externally = bool(run_externally)

    global FILE, FENCED

    FILE = os.path.join(
        weechat_cache_dir(), "message." + ("md" if not args else args)
    )

    FENCED = fenced

    with open(FILE, "w+") as f:
        f.write(weechat.buffer_get_string(buf, "input"))

    if run_externally:
        hook_editor_process(terminal, editor, buf)
    else:
        run_blocking(editor, buf)

    return weechat.WEECHAT_RC_OK


def fenced(data, buf, args):
    return edit(data, buf, args, fenced=True)


def main():
    if not weechat.register(
        "edit",
        "A Farzat",
        "1.1.0",
        "MIT",
        "Open your $EDITOR to compose a message",
        "",
        "",
    ):
        return weechat.WEECHAT_RC_ERROR

    # set default settings
    version = weechat.info_get("version_number", "") or 0
    for option, value in SETTINGS.items():
        if not weechat.config_is_set_plugin(option):
            weechat.config_set_plugin(option, value[0])
        if int(version) >= 0x00030500:
            weechat.config_set_desc_plugin(
                option, '%s (default: "%s")' % (value[1], value[0])
            )

    weechat.hook_command(
        "edit",
        "Open your $EDITOR to compose a message",
        "[extension]",
        "extension: extension for temporary composing file",
        "extension",
        "edit",
        "",
    )
    weechat.hook_command(
        "fenced",
        "Open your $EDITOR to compose a message" " with automatic code fences",
        "[extension]",
        "extension: extension for temporary composing file",
        "extension",
        "fenced",
        "",
    )


if __name__ == "__main__":
    main()
