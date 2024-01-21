# MIT License

# Copyright (c) 2023 Lauren Rad

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
RLook: choices.py
Module for storing and loading choices for RLook.
"""

import pickle
import os

from .reporter import Reporter


def save(choices):
    # Save a choices object to a file. Returns True on success or False on failure.
    choices_write = os.getenv("Choices$Write")
    if choices_write is None:
        Reporter.print("RLook: Choices$Write not set.")
        return False

    if not os.path.exists(choices_write):
        Reporter.print("RLook: Unable to find Choices directory.")

    choices_write = choices_write + ".RLook"
    Reporter.print(f"RLook: choices_write is: {choices_write}", debug=True)

    try:
        with open(choices_write, 'wb') as f:
            pickle.dump(choices, f)
    except Exception as e:
        Reporter.print(f"RLook: An error occurred while trying to save choices: {e}.")
        return False

    return True


def load():
    """
    Load choices fromt he choices file. Returns a Choices object or None on error.
    Choices$Path can contain multiple locations; the style guide isn't fully
    clear on how to handle this so it will just use the first one.
    """
    # Choices$Path also ends in a '.' unlike Choices$Write
    choices_path = os.getenv("Choices$Path")
    if choices_path is None:
        Reporter.print("RLook: Choices$Path not set.")
        return None

    choices_path = choices_path.split(',')[0] + "RLook"  # use only first item
    Reporter.print(f"RLook: Choices path is: {choices_path}", debug=True)
    if not os.path.exists(choices_path):
        Reporter.print("RLook: Choices file not found.")
        return None

    try:
        with open(choices_path, 'rb') as f:
            c = pickle.load(f)
    except Exception as e:  # noqa
        Reporter.print("RLook: Unable to read choices file: {e}")
        return None

    return c


class Choices:
    # Default values for choices
    VERSION = 1.0  # Version of choices format.
    DEFAULT_STARTEND_PLAY = False
    DEFAULT_STARTEND_EXPORT = False
    DEFAULT_AUTOPLAY = True

    def __init__(self):
        # New objects start with defaults
        self._version = Choices.VERSION
        self._startend_playback = Choices.DEFAULT_STARTEND_PLAY  # Use Start/End points for play
        self._startend_export = Choices.DEFAULT_STARTEND_EXPORT  # Use Start/End points for export
        self._autoplay = Choices.DEFAULT_AUTOPLAY  # Automatically play tones when browsing

    @property
    def startend_playback(self):
        return self._startend_playback

    @startend_playback.setter
    def startend_playback(self, value):
        self._startend_playback = bool(value)

    @property
    def startend_export(self):
        return self._startend_export

    @startend_export.setter
    def startend_export(self, value):
        self._startend_export = bool(value)

    @property
    def autoplay(self):
        return self._autoplay

    @autoplay.setter
    def autoplay(self, value):
        self._autoplay = bool(value)

    # Reset choices to default.
    def reset(self):
        self.__init__()

    # Set choices from a list of values
    def set(self, choices):
        self.startend_playback, self.startend_export, self.autoplay = choices

    def __repr__(self):
        return f"Choice: 1:{self.startend_playback} 2:{self.startend_export} 3:{self.autoplay}"
