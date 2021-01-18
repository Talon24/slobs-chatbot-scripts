"""Check the list currently online bots."""

import os
import time
import json
import argparse
import functools
import subprocess

from selenium import webdriver
from selenium.webdriver.support.ui import Select

URL = "https://twitchinsights.net/bots"


def get_executable_path(browser):
    """Absolute path of the webdriver."""
    drivernames = {
        "firefox": "geckodriver.exe",
        "chrome": "chromedriver.exe",
        "phantomjs": "phantomjs.exe"
    }
    return os.path.join(os.path.dirname(__file__), drivernames[browser])


def get_driver(browser="phantomjs", browser_executable=None):
    """Get the best fitting webdriver."""
    # Have selenium start without launching the webdriver with a console
    flag = 0x00000008  # detached process flag, hides terminal
    webdriver.common.service.subprocess.Popen = functools.partial(
        subprocess.Popen, creationflags=flag)

    executable_path = get_executable_path(browser)
    if not os.path.exists(executable_path):
        abspath = os.path.abspath(executable_path)
        raise IOError("Required webdriver {} not found".format(abspath))
    if browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.headless = True
        options.binary = browser_executable
        options.add_argument('--disable-gpu')
        options.hide_command_prompt_window = True
        driver = functools.partial(webdriver.Firefox,
                                   executable_path=executable_path,
                                   options=options)
    elif browser == "chrome":
        options = webdriver.ChromeOptions()
        options.headless = True
        options.binary = browser_executable
        options.add_argument('--disable-gpu')
        driver = functools.partial(webdriver.Chrome,
                                   executable_path=executable_path,
                                   options=options)
    elif browser == "phantomjs":
        driver = functools.partial(webdriver.PhantomJS,
                                   executable_path=executable_path)
    else:
        raise FileNotFoundError
    return driver


def cli():
    """Command Line Interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("browser", choices=["firefox", "chrome", "phantomjs"],
                        default="phantomjs",
                        help="Browser driver. Firefox/Chrome need to be "
                        "installed, phantomjs works self-contianed.")
    parser.add_argument("--browser-executable", "-b", help="Location of the "
                        "Browser executable. Supply if system can't find it.")
    return parser.parse_args()


def get_bots(browser, browser_executable=None):
    """Look up list of bots."""
    starter = get_driver(browser, browser_executable)
    with starter() as driver:
        driver.get(URL)
        time.sleep(3)  # Let page load
        by_selector = driver.find_element_by_css_selector
        select = Select(by_selector("#tonline_length > label > select"))
        select.select_by_visible_text("All")
        table = by_selector("#tonline > tbody")
        users = table.find_elements_by_css_selector("a")
        names = [name.text for name in users]
    return names


def main():
    """Main."""
    arguments = cli()
    bots = get_bots(arguments.browser, arguments.browser_executable)
    print(json.dumps(bots, indent=4))


if __name__ == '__main__':
    main()
