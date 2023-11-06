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

# This is the module for globals, common utility functions, etc

import tempfile
import swi

from .disk import formatting
from . import choices

# Set up tempdir
# Style guide says this should only be created "when needed", but this
# doesn't seem practical right now.
# ignore_cleanup_errors would be nice to use here, but I believe 3.8 is
# the most recent Python version on RISC OS.
tempdir = tempfile.TemporaryDirectory(prefix="rlook")

# Global choices instance
opts = choices.Choices()

# Flag for debug output / UI stuff
debug_enabled = False

# Custom event numbers - gather them all here to avoid clashes.
E_MENU_QUIT = 0x100 # Quit from the iconbar menu
E_WINDOW_CLOSE = 0x201 # Window closed
E_HELP = 0x202 # Icon bar - Help...

# This takes the name of a tone and its number (unformatted) and returns
# something usable as a filename.
# This will attempt to sanitize the name to remove
# prohibited chars, but is untested and probably will
# have some issues. TODO
# Also, spaces seem to result in filename truncation; it looks like
# usually when I see a space in a filename added through the filer,
# it's actually an NBSP. I'm choosing the safer option for now of
# replacing spaces with underscores.
def tone_filename(num, name):
    num = formatting.roland_number(num)
    return num+"_"+\
            name.rstrip().translate({ord(c):None for c in '$&%@\\^:.#*"|'}).replace(' ','_') \
            +"/wav"
