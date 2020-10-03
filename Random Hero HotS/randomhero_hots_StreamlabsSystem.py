"""Chatbot script"""

import os
import codecs
import json

ScriptName = "Random Hero Selector - HotS"
Website = "https://github.com/Talon24"
Description = "Draw a random Hero of the Storm from all or from a certain Role."
Creator = "Talon24"
Version = "1.0.0"

# Field:
# GetParam
# GetParamCount
# IsChatMessage
# IsFromDiscord
# IsFromMixer
# IsFromTwitch
# IsFromYoutube
# IsRawData
# IsWhisper
# Message
# RawData
# Service
# User
# UserName


def Init():
    # send_message("On-Line!")
    global settings
    # with codecs.open(os.path.join(work_dir, "settings.json"), encoding="utf-8-sig") as file:
    #     settings = json.load(file, encoding="utf-8-sig")
    settings = getjson("settings.json")
    settings["dps"] = settings["dps"].split(", ")
    settings["support"] = settings["support"].split(", ")
    settings["tank"] = settings["tank"].split(", ")
    settings["bruiser"] = settings["bruiser"].split(", ")
    settings["fav"] = settings["fav"].split(", ")
    # send_message(str(settings))
    return


def Execute(data):
    username = data.UserName
    message = data.Message
    words = message.split()
    valid = data.IsChatMessage()
    if valid and message.startswith(settings.get("command")):
        # Parent.Log("!randomhero", "Random hero started, input: %s" % message)
        # send_message("You're %s and your message is %s. Is this a chat message? %s. Service: %s." % (username, message, valid, data.Service))
        # send_message("Selector started! words: %s" % str(words))
        # return
        if message.strip() == settings["command"]:
            all_heroes = (settings["tank"] + settings["support"] +
                          settings["dps"] + settings["bruiser"])
            send_message(mychoice(all_heroes))
        else:
            selection = message.replace(settings["command"], "", 1).strip()
            if selection in ("tank", "t"):
                send_message(mychoice(settings["tank"]))
            elif selection in ("dps", "damage", "d"):
                send_message(mychoice(settings["dps"]))
            elif selection in ("sup", "support", "s"):
                send_message(mychoice(settings["support"]))
            elif selection in ("bruiser", "b"):
                send_message(mychoice(settings["bruiser"]))
            elif selection in ("fav",) and settings["fav"]:
                send_message(mychoice(settings["fav"]))
            else:
                send_message("Not a valid selection! Please choose tank, dps, support or bruiser")
    return


def Tick():
    return


def send_message(message):
    Parent.SendStreamMessage(message)


def getjson(filename):
    work_dir = os.path.dirname(__file__)
    with codecs.open(os.path.join(work_dir, filename), encoding="utf-8-sig") as file:
        result = json.load(file, encoding="utf-8-sig")
    return result


def mychoice(iterable):
    max_ = len(iterable) -1
    return iterable[Parent.GetRandom(0, max_)]
