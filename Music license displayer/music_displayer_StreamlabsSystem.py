"""Write currently played track to a file. Only Winamp so far."""
# pylint: disable=invalid-name

import os
import re
import sys
import json
import ctypes
import codecs
import datetime

# Subprocess must know this is a win32 system.
sys.platform = "win32"
import subprocess  # pylint: disable=wrong-import-position

# pylint: disable=invalid-name
ScriptName = "Music License Displayer"
Website = "https://github.com/Talon24"
Description = "Edits a file with the license of a currently played incompetech music file."
Creator = "Talon24"
Version = "1.0.1"

# Have pylint know the parent variable
if False:  # pylint: disable=using-constant-test
    Parent = Parent  # pylint:disable=undefined-variable, self-assigning-variable
# pylint: enable=invalid-name


def Init():
    """Called on start of bot. Named by API."""
    # pylint: disable=invalid-name, global-variable-undefined
    global settings
    settings = get_json("settings.json")
    settings["last_tick"] = datetime.datetime(2000, 1, 1)
    global PLAYER  # pylint: disable=global-statement
    if settings["player"] == "Winamp":
        PLAYER = Winamp()
    elif settings["player"] == "Foobar":
        PLAYER = Foobar2000(settings["foobar_title"])
    if os.path.isfile(settings["license_file"]) and os.path.isfile(settings["out_file"]):
        settings["ready"] = True
    else:
        settings["ready"] = False
        if not os.path.isfile(settings["license_file"]):
            log("License file not found!")
        if not os.path.isfile(settings["out_file"]):
            log("Output file not found!")


def ReloadSettings(_jsonData):
    """Called when "Save Settings" in UI is clicked."""
    # pylint: disable=invalid-name
    Init()


def Execute(data):
    """Executed on every message received. Named by API."""
    # pylint: disable=invalid-name
    username = data.UserName
    message = data.Message
    if (data.IsChatMessage() and has_command(message) and not data.IsWhisper()
            and settings["ask_song_enabled"] and settings["ready"]):
        author, title, status = PLAYER.song_attributes()
        log("{} requested current song".format(username))
        if status not in ["Stopped", "Paused"] and PLAYER.window_title is not None:
            send_message(settings["message_template"].format(title=title, author=author))


def Tick():
    """Executed in a time interval. Named by API."""
    # pylint: disable=invalid-name
    if not settings["ready"]:
        return
    if datetime.datetime.now() - settings["last_tick"] >= datetime.timedelta(seconds=1):
        settings["last_tick"] = datetime.datetime.now()
        PLAYER.refresh()
        if not settings["license_watching_enabled"]:
            return
        if PLAYER.changed():
            author, title, status = PLAYER.song_attributes()
            text = ""
            if status not in ["Stopped", "Paused"] and PLAYER.window_title is not None:
                text = find_license(title)
                if settings["verbose"]:
                    log("Now displaying {} by {}.".format(title, author))
                if text == "" and settings["warnings"]:
                    log("=" * 20 + " No license found for song {} by {} !".format(
                        title, author
                    ))
            else:
                if settings["verbose"]:
                    log("Paused or stopped, removing text.")
            edit_file(text)


def get_title(application="winamp"):
    """Get title of an executable.

    This is an alternative to the ctypes function which uses EnumWindows.
    If it was working, that should be preferred. Unfortuantely, that
    seems to not work from within the chatbot. If there is a way to make that
    work, this can and probably should be removed.
    """
    filters = {"winamp": "imagename eq winamp.exe",
               "foobar": "imagename eq foobar2000.exe"}
    command = ["tasklist", "/fi", filters[application],
               "/v", "/fo", "list"]
    # result = os.popen(command).read()
    pipe = subprocess.PIPE
    # This flag stops the subprocess terminal to pop up
    detached_process = 0x00000008
    # no_window_flag = 0x08000000
    term = subprocess.Popen(command, stdin=pipe, stdout=pipe, stderr=pipe,
                            creationflags=detached_process)
    result, _ = term.communicate(b"")
    try:
        lines = result.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return None
    if len(lines) == 1:
        return None
    windowtitle = re.search(r"[^:]+:\s*(.*)", lines[-1]).group(1)
    return windowtitle


def get_titles_ctypes():
    """List of all window names that are currently open."""
    enum_windows = ctypes.windll.user32.EnumWindows
    enum_windows_proc = ctypes.WINFUNCTYPE(ctypes.c_bool,
                                           ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int))
    get_window_text = ctypes.windll.user32.GetWindowTextW
    get_window_text_length = ctypes.windll.user32.GetWindowTextLengthW
    is_window_visible = ctypes.windll.user32.IsWindowVisible

    titles = []

    def foreach_window(hwnd, _l_param):
        if is_window_visible(hwnd):
            length = get_window_text_length(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            get_window_text(hwnd, buff, length + 1)
            titles.append(buff.value)
        return True
    enum_windows(enum_windows_proc(foreach_window), 0)

    return titles


class Winamp():
    """Reader for winamp."""

    def __init__(self):
        self.song = None
        self.attributes = None
        self.window_title = None
        self.previous_title = None

    def read_window_title(self):
        """Find the winamp window title."""
        # window_titles = get_titles_ctypes()
        # try:
        #     winamp = [title for title in window_titles
        #               if re.match(r".* Winamp(?: \[.+\])?", title)][0]
        # except IndexError:
        #     # Winamp did not write the title back
        #     winamp = None
        winamp = get_title("winamp")
        self.previous_title = self.window_title
        if not winamp == "Notifier":
            # Window name is "Notifier" if it didn't refresh yet
            self.window_title = winamp

    def song_attributes(self):
        """Parse the song information / status from the winamp title."""
        try:
            match = re.match(r"^(\d)+\. (.+) - (.+) - Winamp(?: \[(.+)\])?$",
                             self.window_title)
            author = match.group(2)
            title = match.group(3)
            status = match.group(4)
            return author, title, status
        except TypeError:
            return None, None, None

    def refresh(self):
        """Update the view."""
        self.read_window_title()

    def changed(self):
        """Whether the song has changed."""
        return self.previous_title != self.window_title


class Foobar2000():
    """Reader for Foobar2000."""

    def __init__(self, title_template):
        self.song = None
        self.attributes = None
        self.window_title = None
        self.previous_title = None
        self.build_pattern(title_template)

    def read_window_title(self):
        """Find the foobar window title."""
        # window_titles = get_titles_ctypes()
        # try:
        #     foobar = [title for title in window_titles
        #               if title.endswith("[foobar2000]")
        #               or title.startswith("foobar2000")][0]
        # except IndexError:
        #     foobar = None
        foobar = get_title("foobar")
        self.previous_title = self.window_title
        self.window_title = foobar

    def build_pattern(self, pattern):
        """Pattern tanslation.

        Converts the foobar title build string into a regex that extracts
        the relevant fields from the built title.
        """
        # Place capture groups for watched tags, just match others.
        for tag in re.findall("%.+?%", pattern):
            if tag == r"%title%":
                pattern = pattern.replace(tag, r"(?P<title>.+?)")
                # pattern = pattern.replace(tag, r"(.+?)")
            elif tag == r"%album artist%":
                pattern = pattern.replace(tag, r"(?P<artist>.+?)")
                # pattern = pattern.replace(tag, r"(.+?)")
            else:
                pattern = pattern.replace(tag, ".+?")

        # Replace text-brackets with hex-escape code so they won't be
        # considered in the following
        pattern = re.sub(r"'\['", r"\\x5b", pattern)
        pattern = re.sub(r"'\]'", r"\\x5d", pattern)

        # Remove the quotes around literal strings
        pattern = re.sub(r"'([^']+?)'", r"\1", pattern)

        # Translate foobar optionals to regex optionals
        prev = None
        while pattern != prev:
            prev = pattern
            pattern = re.sub(r"\[([^\[\]]+)\]", r"(?:\1)?", pattern)

        # Escape forwardslashes
        pattern = re.sub(r"([\/])", r"\\\1", pattern)

        # Append foobar name to the end of the title
        pattern += r"  \[foobar2000\]"

        # Force the pattern to match from the beginning to the end
        pattern = "^" + pattern + "$"
        self.pattern = pattern

    def song_attributes(self):
        """Parse the song information from the foobar title."""
        try:
            match = re.match(self.pattern, self.window_title)
            if match is None:
                return None, None, "Stopped"
            author = match.group("artist")
            title = match.group("title")
            status = None  # Need an if in minilanguage to get status
            return author, title, status
        except TypeError:
            return None, None, None

    def refresh(self):
        """Update the view."""
        self.read_window_title()

    def changed(self):
        """Whether the song has changed."""
        return self.previous_title != self.window_title


def find_license(title):
    """Get the Lines in the license file applicable for the given title."""
    output = ""
    with open(settings["license_file"], "r") as file:
        for line in file:
            if line.lower().startswith(title.lower()):
                output += line
                output += file.readline()
                output += file.readline()
                break
    return output


def edit_file(text):
    """Write a text into the file that Streamlabs watches."""
    with open(settings["out_file"], "w") as file:
        file.write(text)


def get_json(filename):
    """Read a json file."""
    work_dir = os.path.dirname(__file__)
    with codecs.open(os.path.join(work_dir, filename), encoding="utf-8-sig") as file:
        result = json.load(file, encoding="utf-8-sig")
    return result


def log(message):
    """Shortcut for logging."""
    # Parent.Log("Counter-script", message)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Parent.Log(ScriptName, "[{}] {}".format(now, message))


def send_message(message):
    """Shortcut for twitch message sender."""
    message = str(message)
    if len(message) < 510:
        Parent.SendStreamMessage(message)


def has_command(message):
    """Check if the message begins with a command as its own word."""
    return re.search(r"^{}\b".format(re.escape(settings.get("command"))), message)
