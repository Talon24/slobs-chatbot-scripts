"""Chatbot script"""
# pylint: disable=invalid-name

import os
import re
import json
import datetime
import codecs

# pylint: disable=invalid-name
ScriptName = "Multicounter"
Website = "https://github.com/Talon24"
Description = "Additional Counters."
Creator = "Talon24"
Version = "1.0.6"

# Have pylint know the parent variable
if False:  # pylint: disable=using-constant-test
    Parent = Parent  # pylint:disable=undefined-variable, self-assigning-variable
# pylint: enable=invalid-name


COUNTERFILE = "counters.json"
TRUST = {"Admin": 10,
         "Mod": 5,
         "Custom Mod": 4,
         "Subscriber": 2,
         "Viewer": 1}


def Init():
    """Called on start of bot. Named by API."""
    # pylint: disable=invalid-name, global-variable-undefined
    global settings
    settings = get_json("settings.json")
    settings["admins"] = settings["admins"].split(", ")
    settings["mods"] = settings["mods"].split(", ")
    if Parent.GetChannelName().lower() == "api error":
        log("Couldn't load name of the channel, is the chatbot up to date?")


def Execute(data):
    """Executed on every message received. Named by API."""
    # pylint: disable=invalid-name
    username = data.UserName
    message = data.Message
    if data.IsChatMessage() and not data.IsWhisper() and has_command(message):
        log("{} has made a request: {}".format(username, message))
        counters = getcounters()
        trust = get_trust(data.User, data.RawData)
        arguments = strip_command(message).split()
        if len(arguments) < 2:
            view_counters(counters, arguments, trust)
        else:
            update_counters(counters, arguments, trust)
            savecounters(counters)


def Tick():
    """Executed in a time interval. Named by API."""
    # pylint: disable=invalid-name
    return


def ReloadSettings(_jsonData):
    """Called when "Save Settings" in UI is clicked."""
    # pylint: disable=invalid-name
    Init()


def get_trust(user, rawdata):
    """Look up the trust level for a user."""
    data_fields = parse_rawdata(rawdata)
    if user in settings["admins"] or user.lower() == Parent.GetChannelName().lower():
        trust = TRUST["Admin"]
    elif user in settings["mods"]:
        trust = TRUST["Custom Mod"]
    elif data_fields["mod"] == "1":
        trust = TRUST["Mod"]
    elif data_fields["subscriber"] == "1":
        trust = TRUST["Subscriber"]
    else:
        trust = TRUST["Viewer"]
    return trust


def parse_rawdata(rawdata):
    """Make a dictionary from the RawData attribute."""
    out = {}
    for entry in rawdata.split(";"):
        key, value = entry.split("=", maxsplit=1)
        out[key] = value
    return out


def view_counters(counters, arguments, trust):
    """Non-intrusive counter requests."""
    if len(arguments) == 0 and trust >= TRUST[settings["list_trust"]]:
        send_message("Available counters: {}".format(", ".join(counters.keys())))
    elif len(arguments) == 1:
        key = arguments[0]
        if key in counters and trust >= TRUST[settings["view_trust"]]:
            send_message("{}: {}".format(key, counters.get(key)))
        else:
            send_message("No such counter.")


def update_counters(counters, arguments, trust):
    """Process counter command."""
    key = arguments[0]
    argument = arguments[1]
    if key in counters:
        if argument == "+" and trust >= TRUST[settings["increment_trust"]]:
            log("Counter {} has been increased from {} to {}".format(
                key, counters[key], counters[key] + 1))
            counters[key] += 1
            send_message("Increased {} to {}!".format(key, counters[key]))
        elif argument == "-" and trust >= TRUST[settings["decrement_trust"]]:
            log("Counter {} has been decreased from {} to {}".format(
                key, counters[key], counters[key] - 1))
            counters[key] -= 1
            send_message("Decreased {} to {}!".format(key, counters[key]))
        elif argument == "delete" and trust >= TRUST[settings["delete_trust"]]:
            log("Counter {} has been deleted, it had a value of {}".format(
                key, counters[key]))
            del counters[key]
            send_message("Deleted counter {}!".format(key))
        elif argument == "set" and trust >= TRUST[settings["set_trust"]]:
            if len(arguments) == 3 and arguments[2].isnumeric():
                value = arguments[2]
                log("Counter {} has been set from {} to {}".format(
                    key, counters[key], value))
                counters[key] = int(value)
                send_message("Set counter {} to {}!".format(key, value))
    else:
        if argument == "create" and trust >= TRUST[settings["create_trust"]]:
            log("Counter {} has been created".format(key))
            counters[key] = 0
            send_message("Created counter {}".format(key))


def send_message(message):
    """Shortcut for twitch message sender."""
    message = str(message)
    if len(message) < 510:
        Parent.SendStreamMessage(message)


def log(message):
    """Shortcut for logging."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Parent.Log(ScriptName, "[{}] {}".format(now, message))


def getcounters():
    """Open the counters file or generate new one."""
    try:
        return get_json(COUNTERFILE)
    except EnvironmentError:
        create_json(COUNTERFILE)
        return {}


def savecounters(dictionary):
    """Shortcut to save the counters file."""
    save_json(dictionary, COUNTERFILE)


def get_json(filename):
    """Read a json file."""
    work_dir = os.path.dirname(__file__)
    with codecs.open(os.path.join(work_dir, filename), encoding="utf-8-sig") as file:
        result = json.load(file, encoding="utf-8-sig")
    return result


def create_json(filename):
    """Create a new json file."""
    work_dir = os.path.dirname(__file__)
    with codecs.open(os.path.join(work_dir, filename), "w", encoding="utf-8-sig") as file:
        json.dump({}, file, encoding="utf-8-sig")


def save_json(dictionary, filename):
    """Save data to json."""
    work_dir = os.path.dirname(__file__)
    with codecs.open(os.path.join(work_dir, filename), "w", encoding="utf-8-sig") as file:
        json.dump(dictionary, file, encoding="utf-8-sig", sort_keys=True, indent=4)


def has_command(message):
    """Check if the message begins with a command as its own word."""
    return re.search(r"^{}\b".format(re.escape(settings.get("command"))), message)


def strip_command(message):
    """Retrieve message content without the command."""
    return message.replace(settings.get("command"), "", 1).strip()
