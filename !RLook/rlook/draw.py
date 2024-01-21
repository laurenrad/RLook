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

# This module contains a set of routines for drawing and plotting.
# It's a bit quick and dirty as I have ambitions of turning this into a standalone later.
import swi
import struct

from rlook.reporter import Reporter # noqa

# Constants for GCOL actions
GCOL_STORE = 0x0  # Store the colour on the screen
GCOL_OR = 0x1  # OR the colour on the screen
GCOL_AND = 0x2  # AND the colour on the screen
GCOL_EOR = 0x3  # EOR the colour on the screen
GCOL_INVERT = 0x4  # Invert the colour on the screen
GCOL_NONE = 0x5  # Leave colour unchanged
GCOL_ANDNOT = 0x6  # AND the colour on the screen with NOT c
GCOL_ORNOT = 0x7  # OR the colour on the screen with NOT c

# Colour constants
COLOUR_WHITE = 0x0
COLOUR_GREY1 = 0x1
COLOUR_GREY2 = 0x2
COLOUR_GREY3 = 0x3
COLOUR_GREY4 = 0x4
COLOUR_GREY5 = 0x5
COLOUR_GREY6 = 0x6
COLOUR_BLACK = 0x7
COLOUR_DARKBLUE = 0x8
COLOUR_YELLOW = 0x9
COLOUR_GREEN = 0xA
COLOUR_RED = 0xB
COLOUR_CREAM = 0xC
COLOUR_ARMYGREEN = 0xD
COLOUR_ORANGE = 0xE
COLOUR_LIGHTBLUE = 0xF

# Constants for command offsets
RELATIVE_MOVE = 0
RELATIVE_FG = 1
RELATIVE_INVERSE = 2
RELATIVE_BG = 3
ABSOLUTE_MOVE = 4
ABSOLUTE_FG = 5
ABSOLUTE_INVERSE = 6
ABSOLUTE_BG = 7


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def sign(n):
    if n != 0:
        return n // abs(n)
    else:
        return 0


def set_fg_colour(colour, mode=GCOL_STORE):
    """Set the foreground drawing colour."""
    command = colour | (mode << 4)
    swi.swi("Wimp_SetColour", "i", command)


def set_bg_colour(colour, mode=GCOL_STORE):
    """Set the background drawing colour."""
    command = 0x80 | colour | (mode << 4)
    swi.swi("Wimp_SetColour", "i", command)


def move(a):
    """Move the cursor to an absolute position."""
    swi.swi("OS_Plot", "III", ABSOLUTE_MOVE, a.x, a.y)


def line(point, colour="fg", dash=None):
    """Draw a line from the current cursor position."""
    line_base = 0x00

    if colour == "bg":
        swi.swi("OS_Plot", "III", line_base+ABSOLUTE_BG, point.x, point.y)
    elif colour == "inverse":
        swi.swi("OS_Plot", "III", line_base+ABSOLUTE_INVERSE, point.x, point.y)
    else:
        swi.swi("OS_Plot", "III", line_base+ABSOLUTE_FG, point.x, point.y)


def dotted_line(a, colour="fg", pattern=None):
    """
    Draw a dotted line, with greatly simplified options.
    Pattern is 00-FF and represents dash width.
    Will use foreground colour unless specified as 'bg' or 'inverse'.
    """
    line_base = 0x10

    # Set up dotted line
    if pattern is not None:
        swi.swi("OS_WriteC", "I", 23)
        swi.swi("OS_WriteC", "I", 6)
        for i in range(0, 8):
            swi.swi("OS_WriteC", "I", pattern)

    if colour == "bg":
        swi.swi("OS_Plot", "III", line_base+ABSOLUTE_BG, a.x, a.y)
    elif colour == "inverse":
        swi.swi("OS_Plot", "III", line_base+ABSOLUTE_INVERSE, a.x, a.y)
    else:
        swi.swi("OS_Plot", "III", line_base+ABSOLUTE_FG, a.x, a.y)


def point(a, colour="fg"):
    """
    Plot a point at the absolute coordinates (x,y).
    Will use foreground colour unless specified as 'bg' or 'inverse'.
    """
    point_base = 0x40
    if colour == "bg":
        swi.swi("OS_Plot", "III", point_base+ABSOLUTE_BG, a.x, a.y)
    elif colour == "inverse":
        swi.swi("OS_Plot", "III", point_base+ABSOLUTE_INVERSE, a.x, a.y)
    else:
        swi.swi("OS_Plot", "III", point_base+ABSOLUTE_FG, a.x, a.y)


def rectangle(a, b, colour="fg"):
    """
    Plot a filled rectangle with absolute coordinates from point1 to point2.
    Will use foreground colour unless specified as 'bg' or 'inverse'.
    """
    rect_base = 0x60  # Base command num for rectangle fill
    swi.swi("OS_Plot", "iii", rect_base+ABSOLUTE_MOVE, a.x, a.y)  # Move cursor to (x1,y1)
    if colour == "bg":
        swi.swi("OS_Plot", "III", rect_base+ABSOLUTE_BG, b.x, b.y)
    elif colour == "inverse":
        swi.swi("OS_Plot", "III", rect_base+ABSOLUTE_INVERSE, b.x, b.y)
    else:
        swi.swi("OS_Plot", "III", rect_base+ABSOLUTE_FG, b.x, b.y)


class WaveformPlot():
    def __init__(self, width, height, pos):
        self.width = width
        self.height = height
        self.pos = pos  # Point
        self.centre = self.pos.y + (self.height // 2)

    # Set a new position
    def move(self, pos):
        """Set a new position."""
        self.pos = pos
        self.centre = self.pos.y + (self.height // 2)

    def resize(self, width, height):
        """Set a new width and height."""
        self.width = width
        self.height = height
        self.centre = self.pos.y + (self.height // 2)

    def plot_waveform2(self, samples):
        """Plot a PCM waveform (alternate algorithm)."""
        xscale = round(len(samples) / 2 / self.width)  # scale sample display to width

        max_samp = 0
        for samp in struct.iter_unpack("<h", samples):
            if abs(samp[0]) > max_samp:
                max_samp = abs(samp[0])
        yscale = self.height / 2 / max_samp

        move(Point(self.pos.x, self.centre))
        x = self.pos.x  # Current x position of plot
        samp_count = 0  # number of samples processed

        for samp in struct.iter_unpack("<h", samples):
            if samp_count % xscale == 0:
                scaled = samp[0] * yscale
                line(Point(x, self.centre+int(scaled)))
                x += 1
            samp_count += 1

    def plot_waveform(self, samples):
        # For test, this should be 16-bit unsigned pcm
        xscale = round(len(samples) / 2 / self.width)  # scale sample display to width

        max_samp = 0
        for samp in struct.iter_unpack("<h", samples):
            if abs(samp[0]) > max_samp:
                max_samp = abs(samp[0])
        yscale = self.height / 2 / max_samp

        move(Point(self.pos.x, self.centre))
        x = self.pos.x  # Current x position of plot
        samp_count = 0  # number of samples processed
        sum = 0  # Running sum of samples to average

        for samp in struct.iter_unpack("<h", samples):
            sum += samp[0]
            if samp_count % xscale == 0:
                avg = sum / xscale
                scaled = avg * yscale
                line(Point(x, self.centre+int(scaled)))
                sum = 0
                x += 1
            samp_count += 1

    def plot_border(self):
        move(Point(self.pos.x, self.pos.y))
        line(Point(self.pos.x+self.width, self.pos.y))
        line(Point(self.pos.x+self.width, self.pos.y+self.height))
        line(Point(self.pos.x, self.pos.y+self.height))
        line(Point(self.pos.x, self.pos.y))

    def plot_marker(self, x, len, thickness, colour, pattern):
        """Plot a vertical marker on the graph."""
        # len is the length of the data set to scale to
        xscale = self.width / (len / 2)

        set_fg_colour(colour)
        x = round((x*xscale) + self.pos.x)
        thickness = thickness // 2
        for i in range(thickness*-1, thickness):
            move(Point(x+i, self.pos.y))
            dotted_line(Point(x+i, self.pos.y+self.height), "fg", pattern)
        set_fg_colour(COLOUR_BLACK)

    def plot_start(self, start, len):
        """Plot the start point marker."""
        self.plot_marker(start, len, 8, COLOUR_ARMYGREEN, 0xFF)

    def plot_end(self, end, len):
        """Plot the end point marker."""
        self.plot_marker(end, len, 8, COLOUR_RED, 0xF0)

    def plot_loop(self, loop, len):
        """Plot the loop point marker."""
        self.plot_marker(loop, len, 8, COLOUR_LIGHTBLUE, 0xA5)
