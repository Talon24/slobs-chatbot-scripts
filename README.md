# slabs-chatbot-scripts

Various streamlabs custom scripts

The trigger command on all scripts is customizable.

## Calculator

Performing calculations within the twitch chat.

Some additional functions from the math module are added, as well as decimals and fractions.
The handling of the `^`-operator can be configured.

### Requirement

The calculator requires the `simpleeval` module to be installed. This can be done
in the Script settings under `Maintenance` using the `Install simpleeval` button.

## Multicounter

Create different individual counters.

    !counter[ <countername>[ +|-|create|delete|set <Number to set>]]

Command for the Multicounter must precede the counter name, thus avoiding command conflicts.
The streamer can select which trust level is required to access functionality of the counters.

### Examples

| Command                | Explanation                       |
| ---------------------- | --------------------------------- |
| `!counter`             | Lists available counters          |
| `!counter name`        | Show value of name counter        |
| `!counter name create` | Create name counter if not exists |
| `!counter name +`      | Increase counter                  |
| `!counter name -`      | Decrease counter                  |
| `!counter name set 20` | Sets the counter to 20            |
| `!counter name delete` | Removes the counter               |

## Random Hero

Draw a random hero from the pool of heroes. Can select out of all heroes or of
a certain category or from favourites.

The Hero lists and favourites can be defined by the streamer.
Items in the Lists are separated by `", "` (a comma followed by a space _without_ the quotation marks)

### Categories

-   Overwatch
    -   Tank
    -   DPS
    -   Support
    -   Favourite (if specified)
-   Heroes of the Storm
    -   Tank
    -   DPS
    -   Support
    -   Bruiser
    -   Favourite (if specified)

### Examples

| Command              | Explanation                              |
| -------------------- | ---------------------------------------- |
| `!randomhero hots`   | Draw a hero from all HotS heros          |
| `!randomhero ow dps` | Draw a dps hero from Overwatch           |
| `!randomhero ow fav` | Draw a hero from the Overwatchfavourites |

## Music License Displayer

### License managing

Watches your music player and writes the license corresponding to that song
to a file which streamlabs/obs can read and display as textbox layer.

Assemble your incompetech/filmmusic.io licenses in a single file and create an empty text file
which you can link in your streaming software, then put the path for
both of these files into the script settings. The script will look for
the title in that file and write the corresponding three lines to the out file.

### Command

This script can also read the currently played song from the supported
audio players so that viewers can ask for the song title.

| Command  | Answer                                                |
| -------- | ----------------------------------------------------- |
| `!music` | Current song is «Night in Venice» by «Kevin MacLeod». |

### Supported formats

Supports the license format for incompetech, multiple licenses
assembled in a single text file. Example:

    Night In Venice by Kevin MacLeod
    Link: https://incompetech.filmmusic.io/song/5763-night-in-venice
    License: http://creativecommons.org/licenses/by/4.0/

    Study And Relax by Kevin MacLeod
    Link: https://incompetech.filmmusic.io/song/5764-study-and-relax
    License: http://creativecommons.org/licenses/by/4.0/

Supported Music players: `Winamp` and `Foobar2000`

### Notes

-   The license angreement on filmmusic.io states that you
    [MUST NOT](https://tools.ietf.org/html/rfc2119) change the license text.
    If your music file cannot be matched to a license, you could edit
    the metadata on the file to match the license text.
-   To be save, check the [hints on streaming](https://filmmusic.io/faq/67)
    for yourself. As the music watcher script needs your licenses assembled in
    one file anyway, you can copy-and-paste it as additional references easily
    and you're on the safe side even if the name mismatches.
-   It is recommended to run through newly added songs and check if they
    work corrently. If the program couldn't match a song, it is shown in the
    `Logs`-Page (The (i)-Button in the top-right corner) in the `Scripts`-tab.
-   I observed that it can sometimes take up to 10 seconds until an Update
    from Winamp is recognized.

## Translator

This script checks the Wiktionary page for a word to retrieve translations.

Syntax:

    !translate <from_language> <to_language> <Word>

Example:

    User: !translate en de lamppost
    Bot: pole that holds up a light: Laternenpfahl

Supported source languages:

-   English
-   German

Source languages may work even if not supported, as the wiktionary often
has pages for words in other languages.

Language codes as used on the wiktionary are used to identify languages.

This relies on the search function of wiktionary, so it may not always be correct.
Also be aware that a user might ask for a translation of a banned word in a different language.
You can specify bad words, if the output contains one of these, it won't send the message.
The banned words specified in the Mod Tools tab of the Chatbot will be included.

## Viewbot Hunter

Gets the list of known Stream-watching bots from [Twitch Insights](https://twitchinsights.net/bots).
Requires a webdriver for your corresponding Browser. Supported are Firefox, Chrome and PhantomJS.
The Webdriver file (ending with `.exe`) must be saved to the directory of the Viewbot Hunter.
There's a button to open the directory in the script settings under Maintenance.

Downloads:

| Browser   | Webdriver Download                                           | Comment                                                                   |
| --------- | ------------------------------------------------------------ | ------------------------------------------------------------------------- |
| Firefox   | [Download](https://github.com/mozilla/geckodriver/releases/) |                                                                           |
| Chrome    | [Download](https://chromedriver.chromium.org/downloads)      |                                                                           |
| PhantomJS | [Download](https://phantomjs.org/download.html)              | PhantomJS can work without having a browser installed, but is less stable |


This script can give information and can update its botlist with a chat command, but the users that are allowed have to be listed explicitly.
Allowed commands:

- `!viewbothunter info` -- Amount of banned, known bots, and update times.
- `!viewbothunter update` -- Update the botlist.
- `!viewbothunter lookup [username]` -- check whether a user is a known bot and already banned.

Custom ban message templates can be added in the file `message_templates.txt`.
This file will be generated from `message_templates_example.txt`.
**DO NOT** edit this file, as it will be overwritten by script updates.
