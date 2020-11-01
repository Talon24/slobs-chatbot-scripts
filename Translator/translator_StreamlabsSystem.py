# -*- coding: utf8 -*-
"""Script for the streamlabs chatbot to select a random Overwatch hero.

It can select from all heroes, from a specific class or from favourites."""
# pylint: disable=invalid-name

import os
import re
import json
import codecs
import datetime
import collections

from urllib import urlencode  # pylint: disable=no-name-in-module

# pylint: disable=invalid-name
ScriptName = "Translator"
Website = "https://github.com/Talon24"
Description = "Translator using the Wiktionary."
Creator = "Talon24"
Version = "0.9.0"

# Have pylint know the parent variable
if False:  # pylint: disable=using-constant-test
    Parent = Parent  # pylint:disable=undefined-variable, self-assigning-variable
# pylint: enable=invalid-name


def requests_get(url, headers=None):
    """Similar api to requests.get."""
    if not headers:
        headers = {}
    result = Parent.GetRequest(url, headers)
    text = json.loads(result).get("response")
    # log(json.loads(result).keys())
    # log(json.loads(result).get("status"))
    return text


def Init():
    """Called on start of bot. Named by API."""
    # pylint: disable=invalid-name, global-variable-undefined
    global settings
    settings = getjson("settings.json")

    # wikitext = wikimedia_api("bird", "en")
    # # log(text)
    # translations = parse_wikipedia_en(wikitext)
    # text = " --- ".join(["%s: %s" % (key, ", ".join(val))
    #                      for key, val in translations.items()])
    # if len(text) > 510:
    #     position = text[:513].rfind("---")
    #     text = text[:position]
    # log(text)



def Execute(data):
    """Executed on every message received. Named by API."""
    # pylint: disable=invalid-name
    message = data.Message
    if data.IsChatMessage() and not data.IsWhisper() and has_command(message):
        selection = strip_command(message)
        if not selection:
            send_message("Command: {} <source language> <target language> <text>"
                         "".format(settings["command"]))
            return
        source, target, data = selection.split(" ", maxsplit=2)
        if source == "de":
            message = from_de(data, lang=target)
        elif source == "en":
            message = from_en(data, lang=target)
        else:
            return
        if message:
            send_message(message)


def Tick():
    """Executed in a time interval. Named by API."""
    # pylint: disable=invalid-name
    return


def ReloadSettings(_jsonData):
    """Called when "Save Settings" in UI is clicked."""
    # pylint: disable=invalid-name
    Init()


def remove_dups(list_):
    """Get new list without duplicates, order-preserving."""
    seen = set()
    seen_add = seen.add
    return [x for x in list_ if not (x in seen or seen_add(x))]


def wikimedia_api(search, lang="de"):
    """main."""
    # url = r"https://en.wikipedia.org/w/api.php
    url = r"https://{}.wiktionary.org/w/api.php?{}"
    firstmatch = closest_match(search, lang=lang)
    # log(firstmatch)
    params = {
        "action": "query",
        "format": "json",
        "titles": firstmatch,
        "prop": "revisions",
        "rvslots": "main",
        "rvprop": "content",
    }
    paramstring = urlencode(params)
    finished_url = url.format(lang, paramstring)
    req = requests_get(finished_url)
    # print(json.dumps(req.json()["query"]["pages"], indent=4))
    pages = json.loads(req)["query"]["pages"]
    if len(pages) == 1:
        page = pages.keys()[0]
        # log(json.dumps(json.loads(req, encoding="utf8"), indent=4, ensure_ascii=False))
        text = pages[page]["revisions"][0]["slots"]["main"]["*"]
        return text, finished_url
    else:
        raise KeyError("Url had multiple pages??")


def closest_match(search, lang="de"):
    """Query the search function"""
    # url = ("https://{}.wiktionary.org/w/api.php?action=opensearch&"
    #        "format=json&formatversion=2&search={}&namespace=0&limit=1")
    url = "https://{}.wiktionary.org/w/api.php?".format(lang)
    params = urlencode({
        "action": "opensearch",
        "format": "json",
        "version": 2,
        # "search": quote(search.encode("utf8")),
        "search": search,
        # "search": "Wärmflasche".encode("utf8"),
        "namespace": 0,
        "limit": 1
    })
    url = url + params
    req = requests_get(url)
    # real_url = json.loads(req)[3][0]  # Wiki page url
    # log(json.dumps(json.loads(req), indent=4, ensure_ascii=False))
    firstmatch = json.loads(req)[1][0]
    return firstmatch


def from_de(search, lang="en"):
    """Translate with german as source language."""
    # url = r"https://de.wiktionary.org/wiki/"
    wikitext, _url = wikimedia_api(search, "de")
    translations = parse_wikipedia_de(wikitext, lang)
    text = " --- ".join([", ".join(x) for x in translations])
    if len(text) > 450:
        position = text[:453].rfind("---")
        text = text[:position]

    return text


def from_en(search, lang="de"):
    """Translate with english as source language."""
    wikitext, url = wikimedia_api(search, "en")
    # log(wikitext)
    translations = parse_wikipedia_en(wikitext, url, lang=lang)
    text = " --- ".join(["%s: %s" % (key, ", ".join(val))
                         for key, val in translations.items()])
    if len(text) > 450:
        position = text[:453].rfind("---")
        text = text[:position]
    return text


def parse_wikipedia_en(page, url, lang="de"):
    """Parse the translation tables from wikipedia."""
    page = re.sub(r"\\u00([0-0a-f]{2})", r"\\x\1", page)
    sections = re.findall(r"={4,5}Translations={4,5}\n([\w\W]*?)(?:(?:==)|$)", page)
    out = collections.OrderedDict()
    for section in sections:
        if not "see translation subpage" in section:
            trans_tables = re.findall(r"(\{\{trans-top[\w\W]*?\{\{trans-bottom\}\})", section)
            for trans in trans_tables:
                category = re.search(r"\{\{trans-top\|(.*?)\}\}", trans).group(1)
                # {{t+|de|Vogel|m}}
                translations = re.findall(r"\{\{(?:t.*?\|)?%s\|([^|}]*).*?\}\}" % (lang), trans)
                if translations:
                    out[category] = translations
        else:
            reference = re.search(r"\{\{see translation subpage\|(.+?)\}\}",
                                  section).group(1)
            subpage_data = parse_translation_subpage_en(url, reference, lang)
            out.update(subpage_data)
    # log(out)
    return out


def parse_translation_subpage_en(url, reference, lang="de"):
    """Read data from the translation subpage."""
    out = collections.OrderedDict()
    injected_url = re.sub(r"titles=(.*?)(?=&|$)",
                          r"titles=\1/translations",
                          url)
    req = requests_get(injected_url)
    # log(injected_url)
    pages = json.loads(req)["query"]["pages"]
    page = pages.keys()[0]
    subpage = pages[page]["revisions"][0]["slots"]["main"]["*"]
    # log(subpage)
    log(reference)
    section = re.search(r"===%s===[^=]([\w\W]*?)(?:[^=]===[^=]|$)" % reference, subpage).group(1)
    trans_tables = re.findall(r"(\{\{trans-top[\w\W]*?\{\{trans-bottom\}\})", section)
    for trans in trans_tables:
        category = re.search(r"\{\{trans-top\|(.*?)\}\}", trans).group(1)
        # {{t+|de|Vogel|m}}
        translations = re.findall(r"\{\{(?:t.*?\|)?%s\|([^|}]*).*?\}\}" % (lang), trans)
        if translations:
            out[category] = translations
    return out



def parse_wikipedia_de(page, lang="en"):
    """Parse the translation tables from wikipedia."""
    page = re.sub(r"\\u00([0-0a-f]{2})", r"\\x\1", page)
    # translations = re.findall(r"==== \{\{Übersetzungen\}\} ====\n([\w\W]*?)\n(?:(?:==)|$)", page)
    translations = re.findall(r"==== \{\{Übersetzungen\}\} ====([\w\W]*?)(?:(?:==)|$)", page)
    out = []
    # log(page)
    log("Translations: {}".format(translations))
    for trans in translations:
        # {{Ü|en|lorry}}
        translations = re.findall(r"\{\{Ü\|%s\|(.*?)\}\}" % (lang), trans)
        if translations:
            out.append(translations)
    # log(out)
    return out


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
