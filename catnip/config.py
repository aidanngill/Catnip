""" Process the user's configuration from the `config.json` file. """

import json
import os

NAME = "config.json"
PATH = os.path.join(os.getcwd(), NAME)

data = {}

if os.path.isfile(PATH):
    with open(PATH, "r", encoding="utf-8") as file:
        data: dict = json.load(file)

CAPTURE_PATH = os.path.join(os.getcwd(), data.get("capture_path", "captures"))

if not os.path.isdir(CAPTURE_PATH):
    os.mkdir(CAPTURE_PATH)
