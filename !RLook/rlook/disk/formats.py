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
RLook: formats.py
This module contains:
    * Classes representing different 12-bit disk formats and their constants
    * Structures defining how to organize and format parameters for display in the GUI
"""
from .exceptions import FormatError


class S550:
    # This class also applies to S-330
    FORMAT_STRING = "S550"  # format string
    SYSTEM_SIZE = 64512  # size of system data in bytes
    PATCH_SIZE = 256  # size of a patch definition in bytes
    TONE_SIZE = 128  # size of a tone definition in bytes
    WAVE_SIZE = 660312  # size of wave data in bytes
    TONES_OFFSET = 69120  # offset of Tone block
    PATCHES_OFFSET = 64512  # offset of Patch block
    # system is always at beginning of disk
    FUNCTION_OFFSET = 68608  # offset of Function block
    MIDI_OFFSET = 68832  # offset of MIDI block
    WAVE_OFFSET = 73728  # offset of Wave Data block
    PATCH_COUNT = 16  # number of patches on disk, depends on disk format. 16 for S-550
    TONE_COUNT = 32  # number of tones on disk, 32 for S-550

    # Tone parameters definition. All params will have a name, type, and size;
    # types: int, signed_int, ascii, multi, raw, dummy
    # This will be kept as literal to the disk spec as possible so it's going
    # to be a little hard to read, but see the disk format spec for more info.
    # OUTPUT ASSIGN is renamed TONE OUTPUT ASSIGN to avoid conflict with the
    # patch parameter of the same name
    tone_fmt = ({'name': 'NAME', 'type': 'ascii', 'size': 8},
                {'name': 'TONE OUTPUT ASSIGN', 'type': 'int', 'size': 1},
                {'name': 'SOURCE TONE', 'type': 'int', 'size': 1},
                {'name': 'ORIG/SUB TONE', 'type': 'int', 'size': 1},
                {'name': 'FREQUENCY', 'type': 'int', 'size': 1},
                {'name': 'ORIG KEY NUMBER', 'type': 'int', 'size': 1},
                {'name': 'WAVE BANK', 'type': 'int', 'size': 1},
                {'name': 'WAVE SEGMENT TOP', 'type': 'int', 'size': 1},
                {'name': 'WAVE SEGMENT LENGTH', 'type': 'int', 'size': 1},
                {'name': 'START POINT', 'type': 'int', 'size': 3},
                {'name': 'END POINT', 'type': 'int', 'size': 3},
                {'name': 'LOOP POINT', 'type': 'int', 'size': 3},
                {'name': 'LOOP MODE', 'type': 'int', 'size': 1},
                {'name': 'TVA LFO DEPTH', 'type': 'int', 'size': 1},
                {'name': 'dummy1', 'type': 'dummy', 'size': 1},
                {'name': 'LFO RATE', 'type': 'int', 'size': 1},
                {'name': 'LFO SYNC', 'type': 'int', 'size': 1},
                {'name': 'LFO DELAY', 'type': 'int', 'size': 1},
                {'name': 'dummy2', 'type': 'dummy', 'size': 1},
                {'name': 'LFO MODE', 'type': 'int', 'size': 1},
                {'name': 'OSC LFO DEPTH', 'type': 'int', 'size': 1},
                {'name': 'LFO POLARITY', 'type': 'int', 'size': 1},
                {'name': 'LFO OFFSET', 'type': 'int', 'size': 1},
                {'name': 'TRANSPOSE', 'type': 'signed_int', 'size': 1},
                {'name': 'FINE TUNE', 'type': 'signed_int', 'size': 1},
                {'name': 'TVF CUT OFF', 'type': 'int', 'size': 1},
                {'name': 'TVF RESONANCE', 'type': 'int', 'size': 1},
                {'name': 'TVF KEY FOLLOW', 'type': 'int', 'size': 1},
                {'name': 'dummy3', 'type': 'dummy', 'size': 1},
                {'name': 'TVF LFO DEPTH', 'type': 'int', 'size': 1},
                {'name': 'TVF EG DEPTH', 'type': 'int', 'size': 1},
                {'name': 'TVF EG POLARITY', 'type': 'int', 'size': 1},
                {'name': 'TVF LEVEL CURVE', 'type': 'int', 'size': 1},
                {'name': 'TVF KEY RATE FOLLOW', 'type': 'int', 'size': 1},
                {'name': 'TVF VELOCITY RATE FOLLOW', 'type': 'int', 'size': 1},
                {'name': 'dummy4', 'type': 'dummy', 'size': 1},
                {'name': 'TVF SWITCH', 'type': 'int', 'size': 1},
                {'name': 'BENDER SWITCH', 'type': 'int', 'size': 1},
                {'name': 'TVA ENV SUSTAIN POINT', 'type': 'int', 'size': 1},
                {'name': 'TVA ENV END POINT', 'type': 'int', 'size': 1},
                {'name': 'TVA ENV', 'type': 'multi', 'size': 16},  # Manual has this as two params
                {'name': 'dummy5', 'type': 'dummy', 'size': 1},
                {'name': 'TVA ENV KEY-RATE', 'type': 'int', 'size': 1},
                {'name': 'LEVEL', 'type': 'int', 'size': 1},
                {'name': 'ENV VEL-RATE', 'type': 'int', 'size': 1},
                {'name': 'Recording Params', 'type': 'multi', 'size': 12},
                {'name': 'ZOOM T', 'type': 'int', 'size': 1},
                {'name': 'ZOOM L', 'type': 'int', 'size': 1},
                {'name': 'COPY SOURCE', 'type': 'int', 'size': 1},
                {'name': 'LOOP TUNE', 'type': 'signed_int', 'size': 1},
                {'name': 'TVA LEVEL CURVE', 'type': 'int', 'size': 1},
                {'name': 'dummy6', 'type': 'dummy', 'size': 12},
                {'name': 'LOOP LENGTH', 'type': 'int', 'size': 3},
                {'name': 'PITCH FOLLOW', 'type': 'int', 'size': 1},
                {'name': 'ENV ZOOM', 'type': 'int', 'size': 1},
                {'name': 'TVF ENV SUSTAIN POINT', 'type': 'int', 'size': 1},
                {'name': 'TVF ENV END POINT', 'type': 'int', 'size': 1},
                {'name': 'TVF ENV', 'type': 'multi', 'size': 16},
                {'name': 'AFTER TOUCH SWITCH', 'type': 'int', 'size': 1},
                {'name': 'dummy7', 'type': 'dummy', 'size': 2})

    # Patch parameters definition. Same as above.
    patch_fmt = ({'name': 'NAME', 'type': 'ascii', 'size': 12},
                 {'name': 'BEND RANGE', 'type': 'int', 'size': 1},
                 {'name': 'dummy1', 'type': 'dummy', 'size': 1},
                 {'name': 'AFTER TOUCH SENSE', 'type': 'int', 'size': 1},
                 {'name': 'KEY MODE', 'type': 'int', 'size': 1},
                 {'name': 'VELOCITY SW THRESHOLD', 'type': 'int', 'size': 1},
                 {'name': 'TONE TO KEY 1', 'type': 'multi', 'size': 109},
                 {'name': 'TONE TO KEY 2', 'type': 'multi', 'size': 109},
                 {'name': 'COPY SOURCE', 'type': 'int', 'size': 1},
                 {'name': 'OCTAVE SHIFT', 'type': 'signed_int', 'size': 1},
                 {'name': 'OUTPUT LEVEL', 'type': 'int', 'size': 1},
                 {'name': 'dummy2', 'type': 'dummy', 'size': 1},
                 {'name': 'DETUNE', 'type': 'signed_int', 'size': 1},
                 {'name': 'VELOCITY MIX RATIO', 'type': 'int', 'size': 1},
                 {'name': 'AFTER TOUCH ASSIGN', 'type': 'int', 'size': 1},
                 {'name': 'KEY ASSIGN', 'type': 'int', 'size': 1},
                 {'name': 'OUTPUT ASSIGN', 'type': 'int', 'size': 1},
                 {'name': 'dummy3', 'type': 'dummy', 'size': 12})

    # Function parameters definition.
    # Notes:
    # - The disk label is text, but is stored as type 'raw' because the
    #   unscrambler function was easier to write to take a bytes value.
    # - As per the disk spec, the second disk label in the MIDI spec
    #   is not stored, as a disk represents 1 'Block'.
    func_fmt = ({'name': 'MASTER TUNE', 'type': 'signed_int', 'size': 1},
                {'name': 'dummy1', 'type': 'dummy', 'size': 13},
                {'name': 'dummy2', 'type': 'dummy', 'size': 1},
                {'name': 'dummy3', 'type': 'dummy', 'size': 1},
                {'name': 'VOICE MODE', 'type': 'int', 'size': 1},
                {'name': 'MULTI MIDI RX-CH', 'type': 'multi', 'size': 8},
                {'name': 'MULTI PATCH NUMBER', 'type': 'multi', 'size': 8},
                {'name': 'dummy4', 'type': 'dummy', 'size': 9},
                {'name': 'KEYBOARD DISPLAY', 'type': 'int', 'size': 1},
                {'name': 'MULTI LEVEL', 'type': 'multi', 'size': 8},
                {'name': 'DISK LABEL', 'type': 'raw', 'size': 60},
                {'name': 'dummy5', 'type': 'dummy', 'size': 4},
                {'name': 'EXTERNAL CONTROLLER', 'type': 'int', 'size': 1},
                {'name': 'dummy6', 'type': 'dummy', 'size': 108})

    # MIDI parameters definition.
    # Notes:
    # - RX CHANNEL may or may not be the same thing as MULTI MIDI RX-CH in function
    midi_fmt = ({'name': 'dummy1', 'type': 'dummy', 'size': 64},
                {'name': 'RX CHANNEL', 'type': 'multi', 'size': 8},
                {'name': 'RX PROGRAM CHANGE', 'type': 'multi', 'size': 8},
                {'name': 'RX BENDER', 'type': 'multi', 'size': 8},
                {'name': 'RX MODULATION', 'type': 'multi', 'size': 8},
                {'name': 'RX HOLD', 'type': 'multi', 'size': 8},
                {'name': 'RX AFTER TOUCH', 'type': 'multi', 'size': 8},
                {'name': 'RX VOLUME', 'type': 'multi', 'size': 8},
                {'name': 'RX BEND RANGE', 'type': 'multi', 'size': 8},
                {'name': 'dummy2', 'type': 'dummy', 'size': 1},
                {'name': 'SYSTEM EXCLUSIVE', 'type': 'int', 'size': 1},
                {'name': 'DEVICE ID', 'type': 'int', 'size': 1},
                {'name': 'RX PROGRAM CHANGE NUMBER', 'type': 'multi', 'size': 32},
                {'name': 'dummy3', 'type': 'dummy', 'size': 125})


class S50:
    """Format definition for S-50 disks. Work in progress."""
    FORMAT_STRING = "S-50"  # format string
    SYSTEM_SIZE = 64512  # size of system data in bytes
    PATCH_SIZE = 512  # size of a patch definition in bytes - larger on S-50 due to garbage data
    TONE_SIZE = 128  # size of a tone definition in bytes
    WAVE_SIZE = 660312  # size of wave data in bytes
    TONES_OFFSET = 69120  # offset of Tone block
    PATCHES_OFFSET = 64512  # offset of Patch block
    # system is always at beginning of disk
    FUNCTION_OFFSET = 68608  # offset of Function block
    MIDI_OFFSET = 68832  # offset of MIDI block
    WAVE_OFFSET = 73728  # offset of Wave Data block - not confirmed but appears to be correct
    PATCH_COUNT = 8  # number of patches on disk, depends on disk format. 16 for S-550
    TONE_COUNT = 32  # number of tones on disk, 32 for S-550

    # A few parameters, including name, frequency, wave bank, start segment, and length
    # temporarily have names that match ones hardcoded in elsewhere until this is changed.
    # Also, as with S-550 envelopes are stored together in 1 multi.
    # TVA ENV parameters are just listed as ENV since there is no TVA; but since these
    # are functionally similar, these are stored here under the S-550 names.
    tone_fmt = ({'name': 'NAME', 'type': 'ascii', 'size': 8},
                {'name': 'dummy1', 'type': 'dummy', 'size': 1},
                {'name': 'SOURCE TONE', 'type': 'int', 'size': 1},
                {'name': 'ORIG/SUB TONE', 'type': 'int', 'size': 1},
                {'name': 'FREQUENCY', 'type': 'int', 'size': 1},
                {'name': 'ORIG KEY NUMBER', 'type': 'int', 'size': 1},
                {'name': 'WAVE BANK', 'type': 'int', 'size': 1},
                {'name': 'WAVE SEGMENT TOP', 'type': 'int', 'size': 1},
                {'name': 'WAVE SEGMENT LENGTH', 'type': 'int', 'size': 1},
                {'name': 'START POINT', 'type': 'int', 'size': 3},
                {'name': 'END POINT', 'type': 'int', 'size': 3},
                {'name': 'LOOP POINT', 'type': 'int', 'size': 3},
                {'name': 'LOOP MODE', 'type': 'int', 'size': 1},
                {'name': 'dummy2', 'type': 'dummy', 'size': 2},
                {'name': 'LFO RATE', 'type': 'int', 'size': 1},
                {'name': 'dummy3', 'type': 'dummy', 'size': 1},
                {'name': 'LFO DELAY', 'type': 'int', 'size': 1},
                {'name': 'dummy4', 'type': 'dummy', 'size': 2},
                {'name': 'LFO DEPTH', 'type': 'int', 'size': 1},
                {'name': 'dummy5', 'type': 'dummy', 'size': 3},
                {'name': 'FINE TUNE', 'type': 'int', 'size': 1},
                {'name': 'dummy6', 'type': 'dummy', 'size': 13},
                {'name': 'TVA ENV SUSTAIN POINT', 'type': 'int', 'size': 1},
                {'name': 'TVA ENV END POINT', 'type': 'int', 'size': 1},
                {'name': 'TVA ENV', 'type': 'multi', 'size': 16},
                {'name': 'dummy7', 'type': 'dummy', 'size': 1},
                {'name': 'ENV KEY-RATE', 'type': 'int', 'size': 1},
                {'name': 'LEVEL', 'type': 'int', 'size': 1},
                {'name': 'ENV VEL-RATE', 'type': 'int', 'size': 1},
                {'name': 'ENV THRESHOLD', 'type': 'int', 'size': 1},
                {'name': 'REC PRE-TRIGER', 'type': 'int', 'size': 1},  # sic
                {'name': 'REC SAMPLING FREQUENCY', 'type': 'int', 'size': 1},
                {'name': 'REC START POINT', 'type': 'int', 'size': 3},
                {'name': 'REC END POINT', 'type': 'int', 'size': 3},
                {'name': 'REC LOOP POINT', 'type': 'int', 'size': 3},
                {'name': 'ZOOM T', 'type': 'int', 'size': 1},
                {'name': 'ZOOM L', 'type': 'int', 'size': 1},
                {'name': 'COPY SOURCE', 'type': 'int', 'size': 1},
                {'name': 'LOOP TUNE', 'type': 'signed_int', 'size': 1},
                {'name': 'LEVEL CURVE', 'type': 'int', 'size': 1},
                {'name': 'dummy8', 'type': 'dummy', 'size': 12},
                {'name': 'LOOP LENGTH', 'type': 'int', 'size': 3},
                {'name': 'PITCH FOLLOW', 'type': 'int', 'size': 1},
                {'name': 'ENV ZOOM', 'type': 'int', 'size': 1},
                {'name': 'dummy9', 'type': 'dummy', 'size': 21})

    patch_fmt = ({'name': 'NAME', 'type': 'ascii', 'size': 12},
                 {'name': 'BEND RANGE', 'type': 'int', 'size': 1},
                 {'name': 'dummy1', 'type': 'dummy', 'size': 1},
                 {'name': 'AFTER TOUCH SENSE', 'type': 'int', 'size': 1},
                 {'name': 'dummy2', 'type': 'dummy', 'size': 4},
                 {'name': 'KEY MODE', 'type': 'int', 'size': 1},
                 {'name': 'VELOCITY SW THRESHOLD', 'type': 'int', 'size': 1},
                 {'name': 'dummy3', 'type': 'dummy', 'size': 19},
                 {'name': 'TONE TO KEY 1', 'type': 'multi', 'size': 128},
                 {'name': 'TONE TO KEY 2', 'type': 'multi', 'size': 128},
                 {'name': 'COPY SOURCE', 'type': 'int', 'size': 1},
                 {'name': 'OCTAVE SHIFT', 'type': 'int', 'size': 1},
                 {'name': 'OUTPUT LEVEL', 'type': 'int', 'size': 1},
                 {'name': 'MODULATION DEPTH', 'type': 'int', 'size': 1},
                 {'name': 'DETUNE', 'type': 'dummy', 'size': 1},
                 {'name': 'VELOCITY MIX RATIO', 'type': 'int', 'size': 1},
                 {'name': 'AFTER TOUCH ASSIGN', 'type': 'int', 'size': 1},
                 {'name': 'dummy4', 'type': 'dummy', 'size': 209})

    # For compatibility, 'DISK LABEL' and 'NOTE' are stored together as
    # 'DISK LABEL' together these are equivalent to the S-550 field.
    func_fmt = ({'name': 'MASTER TUNE', 'type': 'signed_int', 'size': 1},
                {'name': 'dummy1', 'type': 'dummy', 'size': 3},
                {'name': 'CONTROLLER ASSIGN', 'type': 'int', 'size': 1},
                {'name': 'DP-2 ASSIGN', 'type': 'int', 'size': 1},
                {'name': 'dummy2', 'type': 'dummy', 'size': 8},
                {'name': 'AUDIO TRIG', 'type': 'int', 'size': 1},
                {'name': 'SYSTEM MODE', 'type': 'int', 'size': 1},
                {'name': 'VOICE MODE', 'type': 'int', 'size': 1},
                {'name': 'MULTI MIDI RX-CH', 'type': 'multi', 'size': 8},
                {'name': 'MULTI PATCH NUMBER', 'type': 'multi', 'size': 8},
                {'name': 'MULTI TONE NUMBER', 'type': 'multi', 'size': 8},
                {'name': 'dummy3', 'type': 'dummy', 'size': 1},
                {'name': 'KEYBOARD ASSIGN', 'type': 'int', 'size': 1},
                {'name': 'MULTI LEVEL', 'type': 'multi', 'size': 8},
                {'name': 'DISK LABEL', 'type': 'raw', 'size': 60},
                {'name': 'MIDI CONTROL CHANGE NUMBER', 'type': 'int', 'size': 1},
                {'name': 'PARAMETER INITIALIZE', 'type': 'int', 'size': 1},
                {'name': 'DT-100', 'type': 'int', 'size': 1},
                {'name': 'dummy4', 'type': 'dummy', 'size': 270})

    midi_fmt = ({'name': 'dummy1', 'type': 'dummy', 'size': 8},
                {'name': 'TX CHANNEL', 'type': 'int', 'size': 1},
                {'name': 'TX PROGRAM CHANGE', 'type': 'int', 'size': 1},
                {'name': 'TX BENDER', 'type': 'int', 'size': 1},
                {'name': 'TX MODULATION', 'type': 'int', 'size': 1},
                {'name': 'TX HOLD', 'type': 'int', 'size': 1},
                {'name': 'TX AFTER TOUCH', 'type': 'int', 'size': 1},
                {'name': 'TX VOLUME', 'type': 'int', 'size': 1},
                {'name': 'dummy2', 'type': 'dummy', 'size': 1},
                {'name': 'RX PROGRAM NUMBER', 'type': 'multi', 'size': 8},
                {'name': 'TX PROGRAM NUMBER', 'type': 'multi', 'size': 8},
                {'name': 'RX CHANNEL', 'type': 'multi', 'size': 8},
                {'name': 'RX PROGRAM CHANGE', 'type': 'multi', 'size': 8},
                {'name': 'RX BENDER', 'type': 'multi', 'size': 8},
                {'name': 'RX MODULATION', 'type': 'multi', 'size': 8},
                {'name': 'RX HOLD', 'type': 'multi', 'size': 8},
                {'name': 'RX AFTER TOUCH', 'type': 'multi', 'size': 8},
                {'name': 'RX VOLUME', 'type': 'multi', 'size': 8},
                {'name': 'RX BEND RANGE', 'type': 'multi', 'size': 8},
                {'name': 'TX BEND RANGE', 'type': 'int', 'size': 1},
                {'name': 'SYSTEM EXCLUSIVE', 'type': 'int', 'size': 1},
                {'name': 'DEVICE ID', 'type': 'int', 'size': 1},
                {'name': 'dummy3', 'type': 'dummy', 'size': 285})


def check(img: bytes):
    """
    Check disk image and return the class associated with its format.
    Currently, this is only intended to check if this is an S-550 disk
    and raise an exception if not.
    """
    # Format should be in these 4 bytes, at least for S-50 and S-550.
    # If this is not a Roland disk image, this decoding will fail so
    # if we get a UnicodeDecodeError it's definitely invalid
    try:
        format_str = img[4:8].decode('ascii')
    except UnicodeDecodeError:
        raise FormatError('Format error: Unknown file format')
        return None  # None for no valid format

    # otherwise, check the string for a format
    if format_str == 'S550' or format_str == 'S330':
        # There seems to be no significant difference between these two.
        # There are a couple remaining questions which I have noted to investigate
        # later.
        return S550()
    elif format_str == format_str == 'W-30':
        # experimental; this seems largely compatible but a couple test disks acted weird
        return S550()
    elif format_str == 'S-50' or format_str == 'S-51':
        # S-51 indicates an S-550 disk converted to S-50 (and possibly S-330 to
        # S-50, but this isn't confirmed.) The reverse is not true, an S-50 disk
        # converted to S-550 will still have the format string 'S550'.
        return S50()  # limited features
    else:
        raise FormatError(f"Format error: Invalid disk format '{format_str}'")
        return None
