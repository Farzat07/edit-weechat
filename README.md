# weechat-edit

This simple [weechat](https://weechat.org/) plugin allows you to
compose messages in your `$EDITOR`, optionally with a file type.

# Usage

- Markdown message (it's the default, same as `/edit md`)
  ```sh
  /edit
  # Type some stuff
  # Save and quit
  ```
- Plain text message
  ```sh
  /edit txt
  # Type some stuff
  # Save and quit
  ```
- Code message with fences added automatically
  ```sh
  /fenced cpp
  # Type some code
  # Save and quit
  ```

# Configuration

If you'd like to customize the editor you use outside of the `$EDITOR`
environment variable, you can set it in weechat.

```sh
/set plugins.var.python.edit.editor "vim -f"
```

# Installation

Copy the script to `$XDG_DATA_HOME/weechat/python/autoload`,
`~/.local/share/weechat/python/autoload`, or `~/.weechat/python/autoload`

```sh
mkdir -p "$XDG_DATA_HOME/weechat/python/autoload"
wget https://gitlab.farzat.xyz/plugins/weechat/weechat-edit/-/raw/master/edit.py "$XDG_DATA_HOME/weechat/python/autoload"
```
