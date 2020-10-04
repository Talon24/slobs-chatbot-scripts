"""Chatbot script"""
#pylint: disable=invalid-name

import os
import re
import json
import datetime
import codecs

#pylint: disable=invalid-name
ScriptName = "Multicounter"
Website = "https://github.com/Talon24"
Description = "Additional Counters."
Creator = "Talon24"
Version = "1.0.0"

# Have pylint know the parent variable
# Parent = Parent  # pylint:disable=undefined-variable, self-assigning-variable
#pylint: enable=invalid-name


COUNTERFILE = "counters.json"
TRUST = {"admin": 10,
         "mod": 5,
         "viewer": 1}


def Init():
    """Called on start of bot. Named by API."""
    #pylint: disable=invalid-name, global-variable-undefined
    global settings
    settings = get_json("settings.json")
    settings["admins"] = settings["admins"].split(", ")
    settings["mods"] = settings["mods"].split(", ")


def Execute(data):
    """Executed on every message received. Named by API."""
    #pylint: disable=invalid-name
    username = data.UserName
    message = data.Message
    if data.IsChatMessage() and has_command(message):
        log("{} has made a request: {}".format(username, message))
        counters = getcounters()
        trust = get_trust(username)
        arguments = message.replace(settings["command"], "", 1).strip().split()
        if len(arguments) == 0:
            send_message("Available counters: {}".format(", ".join(counters.keys())))
        elif len(arguments) == 1:
            key = arguments[0]
            if key in counters:
                send_message("{}: {}".format(key, counters.get(key)))
            else:
                send_message("No such counter.")
        elif len(arguments) >= 2:
            update_counters(counters, arguments, trust)
            savecounters(counters)


def Tick():
    """Executed in a time interval. Named by API."""
    #pylint: disable=invalid-name
    return


def get_trust(username):
    """Look up the trust level for a user."""
    if username in settings["admins"]:
        trust = TRUST["admin"]
    elif username in settings["mods"]:
        trust = TRUST["mod"]
    else:
        trust = TRUST["viewer"]
    return trust


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
    Parent.SendStreamMessage(message)


def log(message):
    """Shortcut for logging."""
    # Parent.Log("Counter-script", message)
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
