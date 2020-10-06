"""Chatbot script"""
#pylint: disable=invalid-name

import os
import re
import ast
import json
import math
import time
import codecs
import decimal
import datetime
import operator
import fractions

try:
    import simpleeval
    EVALUATOR = simpleeval.SimpleEval()
except ImportError:
    simpleeval = ImportError

#pylint: disable=invalid-name
ScriptName = "Calculator"
Website = "https://github.com/Talon24"
Description = "Allow the bot to solve calculations. Requires simpleeval."
Creator = "Talon24"
Version = "1.0.1"

# Have pylint know the parent variable
if False:  # pylint: disable=using-constant-test
    Parent = Parent  # pylint:disable=undefined-variable, self-assigning-variable
#pylint: enable=invalid-name


class AmbiguouityError(Exception):
    """Raised if Operation is defines as nothing."""


def no_power(*_):
    """^ is ambiguous and settings set to discard it."""
    raise AmbiguouityError("The ^ is ambiguous. Use the ** operator for "
                           "power and xor() for bitwise xor.")


def Init():
    """Called on start of bot. Named by API."""
    #pylint: disable=invalid-name, global-variable-undefined
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
    #pylint: disable=invalid-name
    username = data.UserName
    message = data.Message
    if data.IsChatMessage() and has_command(message):
        calculation = strip_command(message)
        now = time.time()
        if not calculation or settings["last_call"] > now - settings["timeout"]:
            return
        settings["last_call"] = now
        log("{} asked for calculation: {}".format(username, calculation))
        # Pretty spacing in the calculation
        pretty_calc = re.sub(r" *(\(\)) *", r"\1", calculation)
        pretty_calc = re.sub(r" *\b([\+\-\*\/<>%\^]|\*\*|//|==|>=|<=|in)\b *",
                             r" \1 ", pretty_calc)
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
        #pylint: disable=broad-except
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


def Tick():
    """Executed in a time interval. Named by API."""
    #pylint: disable=invalid-name
    return



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
    # Parent.Log("Counter-script", message)
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
    return message.replace(settings.get("command"), "").strip()


def install_simpleeval():
    """Execute getpip and then use it to install simpleeval.

    Subprocess uses module that is only on linux, so fallback to os.
    """

    # Build paths
    pippath = os.path.join(os.path.dirname(__file__), "getpip.py")
    python_path = settings["pythondir"]
    if not python_path:
        raise ValueError("Python path is not specified!")
    python_path = python_path.rstrip("Lib")
    sep = os.path.sep
    python_path += sep if not python_path.endswith(sep) else ""
    python_path += "python.exe"

    # Check if pip is in installation or has to be installed
    try:
        import pip  # pylint: disable=import-outside-toplevel, unused-import
        log("Pip is installed.")
    except ImportError:
        req = Parent.GetRequest("https://bootstrap.pypa.io/get-pip.py", {})
        getpip = json.loads(req)["response"]
        with open(pippath, "w") as file:
            file.write(getpip)
        output = os.system(" ".join([python_path, pippath]))
        log("getpip output: {}".format(not bool(output)))
        log("call: {}".format(" ".join([python_path, "-m", "pip", "install", "simpleeval"])))
    # Call pip to install simpleeval
    output = os.system(" ".join([python_path, "-m", "pip", "install", "simpleeval"]))
    log("simpleeval install output: {}".format(not bool(output)))
