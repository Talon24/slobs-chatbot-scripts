"""Chatbot script"""
# pylint: disable=invalid-name

import os
import sys
import json
import time
import codecs
import datetime

# Subprocess must know this is a win32 system.
sys.platform = "win32"
import subprocess  # pylint: disable=wrong-import-position

# pylint: disable=invalid-name
ScriptName = "Viewbot Hunter"
Website = "https://github.com/Talon24"
Description = "Check for bots and block them"
Creator = "Talon24"
Version = "0.9.2"

# Have pylint know the parent variable
if False:  # pylint: disable=using-constant-test
    Parent = Parent  # pylint:disable=undefined-variable, self-assigning-variable
# pylint: enable=invalid-name


SETTINGS = {}
BOTS = set()
BANNED = set()


def Init():
    """Called on start of bot. Named by API."""
    # pylint: disable=invalid-name
    SETTINGS.update(get_json("settings.json"))
    SETTINGS["allowlist"] = SETTINGS["allowlist"].split(", ")
    deserialize_botlist()
    deserialize_bannedlist()


def Execute(_data):
    """Executed on every message received. Named by API."""
    # pylint: disable=invalid-name
    return


def Tick():
    """Executed in a time interval. Named by API."""
    # pylint: disable=invalid-name
    if not on_cooldown("update botlist") and SETTINGS["automatic_update"]:
        set_cooldown("update botlist", SETTINGS["cooldown_update"])
        update_botlist()

    if not on_cooldown("search bots"):
        viewers = Parent.GetViewerList()
        # log("Viewers: {}".format(viewers))
        set_cooldown("search bots", SETTINGS["cooldown_botcheck"])
        viewers = set(viewers)
        non_allowlisted = viewers.difference(SETTINGS["allowlist"])
        bots = BOTS.intersection(non_allowlisted)
        # Don't consider bots that are already banned, probably viewerlist
        # did not refresh yet
        # bots.add("NotARealUserOnlyForTestingPurposes")
        bots = bots.difference(BANNED)
        if bots:
            log(bots)
            templates = get_templates()
            for bot in bots:
                BANNED.add(bot)
                if SETTINGS["write_message"]:
                    selected = random_choice(templates)
                    send_message(selected.format(bot))
                if not SETTINGS["safe_mode"]:
                    send_message("/ban {}".format(bot))
        serialize_bannedlist()


def update_botlist():
    """Manual update button starts this."""
    command = [add_absname("get_botlist.py"), SETTINGS["browser"].lower()]
    result = call_python(command, hidden=True)
    stdout, stderr, code = result
    if stderr:
        if "IOError: Required webdriver" in stderr:
            message = stderr.splitlines()[-1]
            log(message)
        else:
            log("Error when getting botlist!\n"
                "stdout {}, stderr {}, code {}".format(stdout, stderr, code))
        return False
    else:
        BOTS.update(json.loads(stdout))
        serialize_botlist()
        return True


def ReloadSettings(_jsonData):
    """Called when "Save Settings" in UI is clicked."""
    # pylint: disable=invalid-name
    Init()


def Unload():
    """Called when script is disabled."""
    # pylint: disable=invalid-name
    serialize_botlist()
    serialize_bannedlist()


def send_message(message):
    """Shortcut for twitch message sender."""
    message = str(message)
    if len(message) < 510:
        Parent.SendStreamMessage(message)


def log(message):
    """Shortcut for logging."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Parent.Log(ScriptName, "[{}] {}".format(now, message))


def get_json(filename):
    """Read a json file."""
    work_dir = os.path.dirname(__file__)
    with codecs.open(os.path.join(work_dir, filename), encoding="utf-8-sig") as file:
        result = json.load(file, encoding="utf-8-sig")
    return result


def deserialize_botlist():
    """Load the list of previously known bots."""
    work_dir = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(work_dir, "bots.json"), encoding="utf-8-sig") as file:
            result = json.load(file, encoding="utf-8-sig")
        BOTS.update(result)
    except IOError:
        pass


def serialize_botlist():
    """Save the known bots to a file."""
    work_dir = os.path.dirname(__file__)
    with codecs.open(os.path.join(work_dir, "bots.json"), "w", encoding="utf-8-sig") as file:
        json.dump(list(BOTS), file, encoding="utf-8-sig", indent=4)


def deserialize_bannedlist():
    """Read a json file."""
    work_dir = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(work_dir, "banned.json"), encoding="utf-8-sig") as file:
            result = json.load(file, encoding="utf-8-sig")
        BANNED.update(result)
    except IOError:
        pass


def serialize_bannedlist():
    """Read a json file."""
    work_dir = os.path.dirname(__file__)
    with codecs.open(os.path.join(work_dir, "banned.json"), "w", encoding="utf-8-sig") as file:
        json.dump(list(BANNED), file, encoding="utf-8-sig", indent=4)


def get_templates():
    """Open The file of message templates."""
    default_line = ["That's a suspicious name, {}... Begone, bot!"]
    work_dir = os.path.dirname(__file__)
    try:
        with codecs.open(os.path.join(work_dir, "message_templates.txt"),
                         encoding="utf-8-sig") as file:
            data = file.read()
    except IOError:
        return default_line
    lines = data.splitlines()
    lines = [line.strip() for line in lines
             if not line.startswith("#") and line.strip()]
    if lines:
        return lines
    else:
        return default_line


def add_absname(file):
    """Prefix a file name with the working directory."""
    work_dir = os.path.dirname(__file__)
    return os.path.join(work_dir, file)


def install_selenium():
    """Execute getpip and then use it to install simpleeval.

    Subprocess uses module that is only on linux, so fallback to os.
    """

    # Check if pip is in installation or has to be installed
    try:
        import pip  # pylint: disable=import-outside-toplevel, unused-import
        log("Pip is installed.")
    except ImportError:
        pippath = os.path.join(os.path.dirname(__file__), "getpip.py")
        req = Parent.GetRequest("https://bootstrap.pypa.io/get-pip.py", {})
        getpip = json.loads(req)["response"]
        with open(pippath, "w") as file:
            file.write(getpip)
        output = call_python([pippath])
        status = "Success" if not output[2] else "Failure"
        log("getpip output: {}\n{}\n{}".format(status, output[0], output[1]))
    except NameError:
        # pip is installed, but due to ironPython it will raise this error.
        # Not an issue as it's called outside of it.
        log("Pip is installed.")
    # Call pip to install selenium
    command = ["-m", "pip", "install", "--upgrade", "selenium"]
    # log("call: {}".format(" ".join(command)))
    output = call_python(command)
    if bool(output[2]):
        log("Selenium install output: {}\n{}\n{}".format(
            not bool(output[2]), output[0], output[1]))
    else:
        log("Selenium is installed.")


def self_check():
    """Check if everything works, and log status."""
    # pylint: disable=too-many-branches
    status = {}
    try:
        import pip  # pylint: disable=import-outside-toplevel, unused-import
    except ImportError:
        status["Pip"] = "Failure"
    except NameError:
        status["Pip"] = "Success"
    else:
        status["Pip"] = "Success"
    try:
        import selenium  # pylint: disable=import-outside-toplevel, unused-import
    except ImportError:
        status["Selenium"] = "Failure"
    else:
        status["Selenium"] = "Success"
    if not update_botlist():
        status["Botlist Updater"] = "Failure"
    else:
        status["Botlist Updater"] = "Success"
    messages = ["Status report:"]
    for key, value in status.items():
        messages.append("{}: {}".format(key, value))
    messages.append("Known bots: {}".format(len(BOTS)))
    messages.append("Banned bots: {}".format(len(BANNED)))
    templates = get_templates()
    messages.append("Message templates: {}".format(len(templates)))
    missing_placeholders = [template for template in templates
                            if "{}" not in template]
    for template in missing_placeholders:
        messages.append("The message >>{}<< is missing the paceholder {{}}, "
                        "so the bot name will not appear.".format(template))
    if missing_placeholders:
        status["Message Templates"] = "Failure"
    else:
        status["Message Templates"] = "Success"
    if all([stat == "Success" for stat in status.values()]):
        messages.append("Everything is set up correctly!")
    log("\n".join(messages))
    if status["Selenium"] == "Failure":
        log("Required Module not installed, please click the "
            "\"Install Selenium\" button.")
    elif status["Botlist Updater"] == "Failure":
        log("The webdriver is missing! Please refer to the table at "
            "https://github.com/Talon24/slobs-chatbot-scripts")


def open_explorer():
    """Open the windows explorer at the scripts directory."""
    workdir = os.path.dirname(__file__)
    call(["explorer.exe", workdir], hidden=True)


def open_templates():
    """Open the windows explorer at the scripts directory."""
    file = os.path.join(os.path.dirname(__file__), "message_templates.txt")
    call([r"notepad.exe", file], hidden=True, waiting=False)


def call_python(command, hidden=False):
    """Make a commandline call to python."""
    os_path = os.__file__
    python_path = os_path.replace(os.path.join("Lib", "os.py"), "python.exe")
    command.insert(0, python_path)
    stdout, stderr, code = call(command, hidden=hidden)
    return stdout, stderr, code


def call(command, hidden=False, waiting=True):
    """Make a commandline call."""
    pipe = subprocess.PIPE
    flags = 0
    if hidden:
        flags |= 0x00000008  # detached process flag, hides terminal
    term = subprocess.Popen(command, stdin=pipe, stdout=pipe, stderr=pipe,
                            creationflags=flags)
    if not waiting:
        return None, None, None
    stdout, stderr = term.communicate(b"")
    code = term.returncode
    try:
        stdout = stdout.decode("utf8")
        stderr = stderr.decode("utf8")
    except UnicodeDecodeError:
        raise UnicodeDecodeError("Can't decode {} or {}".format(stdout, stderr))
    return stdout, stderr, code


def removesuffix(string_, suffix):
    """As i ran into https://www.python.org/dev/peps/pep-0616/ ."""
    if suffix and string_.endswith(suffix):
        return string_[:-len(suffix)]
    else:
        return string_


def random_choice(iterable):
    """Alternative to random.choice, as the random module is apparently broken."""
    max_ = len(iterable)
    if max_ == 0:
        raise IndexError("Cannot select from empty list.")
    return iterable[Parent.GetRandom(0, max_)]


def get_viewers():
    """Interface to get the viewer list from Parent."""
    return Parent.GetViewerList()


def on_cooldown(command):
    """Shortcut: Get remaining cooldown of a user."""
    return Parent.GetCooldownDuration(ScriptName, command)


def set_cooldown(command, seconds):
    """Shortcut: Set the cooldown of a user."""
    if seconds <= 0:
        return
    Parent.AddCooldown(ScriptName, command, int(seconds))
    index = 0
    while not on_cooldown(command):
        # Cooldown wasn't flushed, wait until it is
        time.sleep(0.01)
        if index > 500:  # stop waiting after 5 seconds
            log("Timer of {} seconds was set, but never got flushed.".format(seconds))
            break
