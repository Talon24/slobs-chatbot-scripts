"""Chatbot script"""
# pylint: disable=invalid-name

import os
import re
import ast
import sys
import json
import math
import codecs
import decimal
import datetime
import operator
import fractions

# Subprocess must know this is a win32 system.
sys.platform = "win32"
import subprocess  # pylint: disable=wrong-import-position

try:
    import simpleeval
    EVALUATOR = simpleeval.SimpleEval()
except ImportError:
    simpleeval = ImportError

# pylint: disable=invalid-name
ScriptName = "Calculator"
Website = "https://github.com/Talon24"
Description = "Allow the bot to solve calculations. Requires simpleeval."
Creator = "Talon24"
Version = "1.0.6"

# Have pylint know the parent variable
if False:  # pylint: disable=using-constant-test
    Parent = Parent  # pylint:disable=undefined-variable, self-assigning-variable
# pylint: enable=invalid-name


def Init():
    """Called on start of bot. Named by API."""
    # pylint: disable=invalid-name, global-variable-undefined
    global settings
    settings = get_json("settings.json")
    if simpleeval == ImportError:
        log("Simlpeeval not installed. Install it via settings!")
        return
    settings["last_call"] = 0
    if settings["^-behaviour"] == "Bitwise XOR":
        EVALUATOR.operators[ast.BitXor] = operator.xor
    elif settings["^-behaviour"] == "Power":
        EVALUATOR.operators[ast.BitXor] = operator.pow
    elif settings["^-behaviour"] == "Nothing":
        EVALUATOR.operators[ast.BitXor] = no_power
    EVALUATOR.operators[ast.LShift] = safe_lshift
    EVALUATOR.operators[ast.RShift] = operator.rshift
    EVALUATOR.operators[ast.BitAnd] = operator.and_
    EVALUATOR.operators[ast.BitOr] = operator.or_
    EVALUATOR.operators[ast.Invert] = operator.invert
    EVALUATOR.functions["decimal"] = decimal.Decimal
    EVALUATOR.functions["fraction"] = fractions.Fraction
    EVALUATOR.functions["frac"] = fractions.Fraction
    EVALUATOR.functions["bin"] = bin
    EVALUATOR.functions["hex"] = hex
    EVALUATOR.functions["oct"] = oct
    EVALUATOR.functions["round"] = round
    EVALUATOR.functions["deg"] = math.degrees
    EVALUATOR.functions["rad"] = math.radians
    EVALUATOR.functions["sin"] = math.sin
    EVALUATOR.functions["cos"] = math.cos
    EVALUATOR.functions["tan"] = math.tan
    EVALUATOR.functions["log"] = math.log
    EVALUATOR.functions["xor"] = operator.xor
    EVALUATOR.names["pi"] = math.pi


def Execute(data):
    """Executed on every message received. Named by API."""
    # pylint: disable=invalid-name
    username = data.UserName
    message = data.Message
    if data.IsChatMessage() and not data.IsWhisper() and has_command(message):
        calculation = strip_command(message)
        if on_cooldown(username):
            return
        set_cooldown(username)
        log("{} asked for calculation: {}".format(username, calculation))
        # Pretty spacing in the calculation
        pretty_calc = re.sub(r" *(\(\)) *", r"\1", calculation)
        pretty_calc = re.sub(r" *(?<=\b|[()])"  # Start border or bracket
                             r"([\+\-\*\/<>%\^|&]|\*\*|\/\/|==|>=|<=|in|<<|>>)"
                             r"(?=\b|[()]) *",  # End border or bracket
                             r" \1 ", pretty_calc)
        # Previous fixing breaks scientific notation from 5e+2 to 5e + 2
        # Revert this if it happens
        pretty_calc = re.sub(r" *(\de) ([\+\-]) (\d)",
                             r"\1\2\3", pretty_calc)
        try:
            result = EVALUATOR.eval(calculation)
        except ZeroDivisionError:
            result = "Division by zero!"
        except SyntaxError:
            result = "Invalid expression!"
        except simpleeval.NumberTooHigh:
            send_message("Number too large to calculate!")
            return
        # pylint: disable=broad-except
        except Exception as exc:
            send_message(exc)
            return
        else:
            try:
                result = format_result(result)
            except ValueError:
                return
        reply = "{} = {}".format(pretty_calc, result)
        send_message(reply)


def Tick():
    """Executed in a time interval. Named by API."""
    # pylint: disable=invalid-name
    return


def ReloadSettings(_jsonData):
    """Called when "Save Settings" in UI is clicked."""
    # pylint: disable=invalid-name
    Init()


def format_result(result):
    """Formatting on the result of the calculation."""
    if result is not True and result is not False:
        # Python2 appears to not format corrent with its, Decimal fixes this
        decimal.getcontext().prec = int(settings["max_precision"])
        decimal.getcontext().capitals = 0
        if isinstance(result, complex):
            real = ndecimal(result.real)
            imag = ndecimal(result.imag)
            result = '({:,} + {:,}i)'.format(real, imag)
        elif isinstance(result, fractions.Fraction):
            num, denom = result.numerator, result.denominator
            result = '({:,} / {:,})'.format(num, denom)
        elif isinstance(result, str):
            if len(result) > settings["max_string_len"]:
                raise ValueError
        else:
            result = format(ndecimal(result), ",")
    return result


def ndecimal(number):
    """Normalized Decimal of given number that avoids scientific notation."""
    try:
        normalized = decimal.Decimal(number).normalize()
    except TypeError:
        raise SyntaxError("Phython 2.7.13 is being sheet and can't normalize"+
                          " Maybe max_precision is set as a float?")
    sign, digits, exponent = normalized.as_tuple()
    if exponent < 0:
        cutoff = len(digits) - len("".join([str(i) for i in digits]).rstrip("0"))
        if cutoff == 0:
            return decimal.Decimal((sign, digits, exponent))
        else:
            return decimal.Decimal((sign, digits[:-cutoff], exponent-cutoff))
    elif 0 <= exponent < decimal.getcontext().prec:
        return decimal.Decimal((sign, digits + (0,) * exponent, 0))
    else:
        return normalized


class AmbiguouityError(Exception):
    """Raised if Operation is defines as nothing."""


def no_power(*_):
    """^ is ambiguous and settings set to discard it."""
    raise AmbiguouityError("The ^ is ambiguous. Use the ** operator for "
                           "power and xor() for bitwise xor.")


def safe_lshift(self, other):
    """lshift that avoids too large numbers."""
    if other <= 2000:
        return self << other
    else:
        raise simpleeval.NumberTooHigh


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


def has_command(message):
    """Check if the message begins with a command as its own word."""
    return re.search(r"^{}\b".format(re.escape(settings.get("command"))), message)


def strip_command(message):
    """Retrieve message content without the command."""
    return message.replace(settings.get("command"), "", 1).strip()


def install_simpleeval():
    """Execute getpip and then use it to install simpleeval.

    Subprocess uses module that is only on linux, so fallback to os.
    """

    # Build paths
    pippath = os.path.join(os.path.dirname(__file__), "getpip.py")
    os_path = os.__file__
    python_path = os_path.replace(os.path.join("Lib", "os.py"), "python.exe")

    # Check if pip is in installation or has to be installed
    try:
        import pip  # pylint: disable=import-outside-toplevel, unused-import
        log("Pip is installed.")
    except ImportError:
        req = Parent.GetRequest("https://bootstrap.pypa.io/get-pip.py", {})
        getpip = json.loads(req)["response"]
        with open(pippath, "w") as file:
            file.write(getpip)
        output = call([python_path, pippath])
        log("getpip output: {}\n{}\n{}".format(
            not bool(output[2]), output[0], output[1]))
    # Call pip to install simpleeval
    command = [python_path, "-m", "pip", "install", "simpleeval"]
    log("call: {}".format(" ".join(command)))
    output = call(command)
    log("simpleeval install output: {}\n{}\n{}".format(
        not bool(output[2]), output[0], output[1]))


def call(command):
    """Make a commandline call."""
    pipe = subprocess.PIPE
    term = subprocess.Popen(command, stdin=pipe, stdout=pipe, stderr=pipe)
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


def on_cooldown(user):
    """Shortcut: Get remaining cooldown of a user."""
    return Parent.GetUserCooldownDuration(ScriptName, settings["command"], user)


def set_cooldown(user):
    """Shortcut: Set the cooldown of a user."""
    Parent.AddUserCooldown(ScriptName, settings["command"], user, int(settings["timeout"]))
