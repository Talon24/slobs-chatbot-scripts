# slabs-chatbot-scripts

Various streamlabs custom scripts

The trigger command on all scripts is customizable.

## Calculator

Performing calculations within the twitch chat.

Some additional functions from the math module are added, as well as decimals and fractions.
The handling of the `^`-operator can be configured.

### Requirement

The calculator requires the `simpleeval` module to be installed. This can be done
via the Script settings. The python path must be specified within the Maintenance
tab in order for this to work. Simply copy it from the general settings for scripts.
You can simply copypaste the path that ends with `Lib`. Then hit the
`Install simpleeval` button.

## Multicounter

Create different individual counters.

    !counters[ <countername>[ +|-|<crate>|<delete>|<set <Number to set>>]]

Command for the Multicounter must precede the counter name, thus avoiding command conflicts.
The streamer can select which trust level is required to access functionality of the counters.

### Examples

| Command               | Explanation                       |
| --------------------- | --------------------------------- |
| !counters             | Lists available counters          |
| !counters name        | Show value of name counter        |
| !counters name create | Create name counter if not exists |
| !counters name +      | Increase counter                  |
| !counters name -      | Decrease counter                  |
| !counters name set 20 | Sets the counter to 20            |
| !counters name delete | Removes the counter               |

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

| Command            | Explanation                              |
| ------------------ | ---------------------------------------- |
| !randomhero hots   | Draw a hero from all HotS heros          |
| !randomhero ow dps | Draw a dps hero from Overwatch           |
| !randomhero ow fav | Draw a hero from the Overwatchfavourites |

## Music License Displayer

Watches your music player and writes the license corresponding to that song
to a file which streamlabs/obs can read and display as textbox layer.

Assemble your incompetech/filmmusic.io licenses in a single file and create an empty text file
which you can link in your streaming software, then put the path for
both of these files into the script settings. The script will look for
the title in that file and write the corresponding three lines to the out file.

### Supported formats

Supports the license format for incompetech.

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
