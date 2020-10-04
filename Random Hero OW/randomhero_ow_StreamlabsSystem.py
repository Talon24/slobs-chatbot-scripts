"""Script for the streamlabs chatbot to select a random Overwatch hero.

It can select from all heroes, from a specific class or from favourites."""
#pylint: disable=invalid-name

import os
import re
import json
import codecs
import datetime

#pylint: disable=invalid-name
ScriptName = "Random Hero Selector - Overwatch"
Website = "https://github.com/Talon24"
Description = "Draw a random Overwatch hero from all or from a certain Role."
Creator = "Talon24"
Version = "1.0.2"

# Have pylint know the parent variable
Parent = Parent  # pylint:disable=undefined-variable, self-assigning-variable
#pylint: enable=invalid-name


def Init():
    """Called on start of bot. Named by API."""
    #pylint: disable=invalid-name, global-variable-undefined
    global settings
    settings = getjson("settings.json")
    settings["dps"] = settings["dps"].split(", ")
    settings["support"] = settings["support"].split(", ")
    settings["tank"] = settings["tank"].split(", ")
    settings["fav"] = settings["fav"].split(", ")
    # send_message(str(settings))


def Execute(data):
    """Executed on every message received. Named by API."""
    #pylint: disable=invalid-name
    # username = data.UserName
    message = data.Message
    valid = data.IsChatMessage()
    if valid and has_command(message):
        if message.strip() == settings["command"]:
            all_heroes = settings["tank"] + settings["support"] + settings["dps"]
            send_message(mychoice(all_heroes))
        else:
            selection = message.replace(settings["command"], "", 1).strip()
            if selection in ("tank",):
                send_message(mychoice(settings["tank"]))
            elif selection in ("dps", "damage"):
                send_message(mychoice(settings["dps"]))
            elif selection in ("sup", "support"):
                send_message(mychoice(settings["support"]))
            elif selection in ("fav",) and settings["fav"]:
                send_message(mychoice(settings["fav"]))
            else:
                send_message("Not a valid selection! Please choose tank, dps or support")


def Tick():
    """Executed in a time interval. Named by API."""
    #pylint: disable=invalid-name
    return


def send_message(message):
    """Shortcut for twitch message sender."""
    Parent.SendStreamMessage(message)


def log(message):
    """Shortcut for logging."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Parent.Log(ScriptName, "[{}] {}".format(now, message))


def getjson(filename):
    """Read a json file."""
    work_dir = os.path.dirname(__file__)
    with codecs.open(os.path.join(work_dir, filename), encoding="utf-8-sig") as file:
        result = json.load(file, encoding="utf-8-sig")
    return result


def mychoice(iterable):
    """Alternative to random.choice, in case Parent's random is different."""
    max_ = len(iterable) -1
    return iterable[Parent.GetRandom(0, max_)]


def has_command(message):
    """Check if the message begins with a command as its own word."""
    return re.search(r"^{}\b".format(re.escape(settings.get("command"))), message)
