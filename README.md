# slabs-chatbot-scripts
Various streamlabs custom scripts

The trigger command on all scripts is customizable.

## Calculator
Performing calculations within the twitch chat.

Some additional functions from the math module are added, as well as decimals and fractions.
The handling of the `^`-operator can be configured.

### Requirement
The calculator requires the `simpleeval` module to be installed, It can be downloaded via `pip`.

Step-by-Step-guide to do so:
- Navigate to the python installation folder (Check the script settings in your chatbot, you should have specified it as `Python 2.7.13 Directory`).
- Navigate to the `Scripts` folder
- Click on the address bar in your explorer, clear it and type in the following command
```
pip.exe install simpleeval
```

## Multicounter
Create different individual counters.

```
!counters[ <countername>[ +|-|<crate>|<delete>|<set <Number to set>>]]
```

Command for the Multicounter must precede the counter name, thus avoiding command conflicts.
The streamer can select which trust level is required to access functionality of the counters.

### Examples

| Command               | Explanation                       |
|-----------------------|-----------------------------------|
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
Items in the Lists are separated by `", "` (a comma followed by a space *without* the quotation marks)

### Categories
- Overwatch
  - Tank
  - DPS
  - Support
- Heroes of the Storm
  - Tank
  - DPS
  - Support
  - Bruiser

### Examples

| Command               | Explanation                               |
|-----------------------|-------------------------------------------|
| !randomhero hots      | Draw a hero from all HotS heros           |
| !randomhero ow dps    | Draw a dps hero from Overwatch            |
| !randomhero ow fav    | Draw a hero from the Overwatchfavourites  |
