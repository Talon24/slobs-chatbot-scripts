"""Script for the streamlabs chatbot to select a random HotS hero.

It can select from all heroes, from a specific class or from favourites."""
# pylint: disable=invalid-name

import os
import re
import json
import codecs
import datetime


# pylint: disable=invalid-name
ScriptName = "Random Hero Selector - HotS"
Website = "https://github.com/Talon24"
Description = "Draw a random Hero of the Storm from all or from a certain Role."
Creator = "Talon24"
Version = "1.0.2"

# Have pylint know the parent variable
if False:  # pylint: disable=using-constant-test
    Parent = Parent  # pylint:disable=undefined-variable, self-assigning-variable
# pylint: enable=invalid-name


def Init():
    """Called on start of bot. Named by API."""
    # pylint: disable=invalid-name, global-variable-undefined
    global settings
    settings = getjson("settings.json")
    settings["dps"] = settings["dps"].split(", ")
    settings["support"] = settings["support"].split(", ")
    settings["tank"] = settings["tank"].split(", ")
    settings["bruiser"] = settings["bruiser"].split(", ")
    settings["fav"] = settings["fav"].split(", ")


def Execute(data):
    """Executed on every message received. Named by API."""
    # pylint: disable=invalid-name
    message = data.Message
    if data.IsChatMessage() and has_command(message):
        selection = strip_command(message)
        if not selection:
            all_heroes = (settings["tank"] + settings["support"] +
                          settings["dps"] + settings["bruiser"])
            send_message(mychoice(all_heroes))
            return
        if selection in ("tank", "t"):
            key = "tank"
        elif selection in ("dps", "damage", "d"):
            key = "dps"
        elif selection in ("sup", "support", "s"):
            key = "support"
        elif selection in ("bruiser", "b"):
            key = "bruiser"
        elif selection in ("fav",) and settings["fav"]:
            key = "fav"
        else:
            send_message("Not a valid selection! Please choose tank, dps, support or bruiser")
            return
        send_message(mychoice(settings[key]))


def Tick():
    """Executed in a time interval. Named by API."""
    # pylint: disable=invalid-name
    return


def send_message(message):
    """Shortcut for twitch message sender."""
    message = str(message)
    if len(message) < 510:
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
    max_ = len(iterable)
    if max_ == 0:
        raise IndexError("Cannot select from empty list.")
    return iterable[Parent.GetRandom(0, max_)]


def has_command(message):
    """Check if the message begins with a command as its own word."""
    return re.search(r"^{}\b".format(re.escape(settings.get("command"))), message)


def strip_command(message):
    """Retrieve message content without the command."""
    return message.replace(settings.get("command"), "", 1).strip()
