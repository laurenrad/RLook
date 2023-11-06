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
RLook: formatting.py
Module for functions which format parameter data for display in the interface.
"""
import struct

from rlook.reporter import Reporter
from . import formats

def format_value(key:str, value, disk_fmt) -> str:
    """
    If there is a formatting binding set for the parameter specified by 'key',
    then apply it to value, otherwise return raw value.
    """
    
    if isinstance(disk_fmt,formats.S50):
        bindings = Fields50.bindings
    elif isinstance(disk_fmt,formats.S550):
        bindings = Fields550.bindings
    else:
        raise RuntimeError(f"No bindings available for format {type(disk_fmt)}")
    
    if key in bindings:
        try:
            # use formatting if available
            return bindings[key](value)
        except Exception as E:
            Reporter.print(f"Exception '{E}' trying to format value '{value}' for '{key}'")
            return str(value)
    else:
        Reporter.print(f"RLook: ERR: No binding for key {key}")
        return str(value)

def midi_multi_ch_parse(vals: tuple) -> tuple:
    """Parse a tuple of MIDI channel values and return as a tuple of strings."""
    # 0-16, where 0-15 are channels 1-16 and 16=OFF
    result = []
    for v in vals:
        if v == 16:
            result.append("Off")
        else:
            result.append(str(v+1))
    return tuple(result)
         

def readable_disk_label(raw: bytes) -> str:
    """Rearrange the disk label into a readable format and return it as a string."""
    # for some reason the first line of the disk label is stored normally, and then
    # every other line is stored in columns. i have no idea why.
    result = raw[:12].decode('ascii') + '\n' # store first line
    
    # unpack the rest into a tuple of 12 columns of 4 rows, then
    # unscramble with zip and convert back from int before decoding and appending
    for line in zip(*struct.unpack('4s'*12,raw[12:])):
        result += bytearray(line).decode('ascii') + '\n'
    
    return result[:-1] # don't return the final newline   

def int_to_note(n: int) -> str:
    """
    Convert a MIDI note number to a printable string.
    Note that the manual lists the possible range for orig. key
    as 11-120 but the lowest value that can be selected is C0 = 12
    """
    scale = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    degree = n%12 # scale degree
    octave = (n//12)-1 # octave
    return f'{scale[degree]} {octave}' # return result string

def note_to_int(n: str) -> int:
    """
    Reverse of int_to_note. A temporary solution for the tone to key interface.
    """
    scale = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    note, octave = n.split() # split into note and octave
    octave_start = (int(octave)+1)*12 # get start index of octave
    degree = scale.index(note) # get scale degree
    return octave_start + degree

def roland_number(num: int) -> str:
    """
    Converts between decimal 0-31 patch/tone number and a string
    representing a Roland number (a shifted octal).
    """
    octdec = int(oct(num)[2:]) #get octal but chop off the prefix to interpret as if it were decimal
    octdec += 11 # roland number starts from 1 instead of 0
    return 'I' + str(octdec) # the roland number will be preceded by an 'I' for set 1

# MIDI
def multi_on_off(vals: tuple) -> tuple:
    """Parse a tuple of on/off values (0/1) and return a tuple of strings"""
    result = []
    for v in vals:
        if v == 0:
            result.append("Off")
        else:
            result.append("On")
    return tuple(result)
    
# The envelope views for TVF and TVA are packed in a really annoying way
# on the 550 where it's interleaved as level1, rate1, leve2, rate 2, etc.
# This will untangle them into a tuple containing two tuples, one representing
# the rate values, and one containing the level values.
def envelope_unpack(vals: list) -> tuple:
    rate = []; level = []
    for i in range(0,len(vals),2):
        level.append(str(vals[i]))
        rate.append(str(vals[i+1]))
    
    return (tuple(rate),tuple(level))

class Fields550:
    """
    This contains parameter formatting information for the S-550 parameters.
    This is called Fields550 for historical reasons, because it used to contain
    list of fields to display in the GUI, but these have been moved into the
    view code since then.
    """

    
    # Some lookup dicts for parameters where integers represent different options
    # This sort of thing is getting a little hard to manage so it might be time to use an ext
    # file for this
    lookup_values = {'KEY MODE':
                     {0:'Normal', 1:'V-Sw', 2:'X-Fade', 3:'V-Mix', 4:'Unison'},
                     'AFTER TOUCH ASSIGN':
                     {0:'P. Modulation', 1:'Volume', 2:'Bend+', 3:'Bend-', 4:'Filter'},
                     'KEY ASSIGN':
                     {0:'Rotary',1:'Fix'}
                     }
    
    def patch_output_renum(val: int) -> str:
        """Parse the output assign value and return as a string."""
        # 0-8, where 8=tone and 0-7 are outs 1-8
        if val == 8:
            return "Tone"
        else:
            return str(val+1)
        

    # FUNCTION
    # Some notes: keyboard display only applies if 'Split Disp' is selected
    # on the play screen, so this could be confusing.
    # Also EXTERNAL CONTROLLER is translating correctly but not reflecting what's
    # on disk, so this should be looked into.
    def parse_voice_mode(val: int) -> str:
        """Parse the VOICE MODE parameter and return as a string."""
        # 0 = Auto: Last Note Priority (VAL),
        # 1 = Auto: First Note Priority (VAF), 2-23=Fix Mode 1-22
        if val == 0:
            return "Last Note (VAL)"
        elif val == 1:
            return "First Note (VAF)"
        else:
            return 'V ' + str(val-1)
        
    def multi_roland_number(vals: tuple) -> list:
        """Run a tuple of patch numbers through roland_number"""
        # could probably use a comprehension or something for this
        result = []
        for v in vals:
            result.append(roland_number(v))
        return result
    
    # TONE - TBD This would need to be rewritten to be usable so it has been
    # Replaced with a placeholder that returns an empty string
    def parse_source_tone(val: int) -> str:
        return ""
    #def parse_source_tone(val:int) -> str:
    #    """
    #    Parse the 'SOURCE TONE' parameter and return a printable string.
    #    This value is not relevant unless 'ORIG/SUB TONE' is 1.
    #    """
    #    return (roland_number(val) +
    #            ' ' +
    #            app.get_disk().tones[val].get_name()).rstrip()
        
    #            Tone
    
    # Some of the following is being reworked as part of having everything return str
    bindings = { 'NAME': lambda val: val.rstrip(),
                 'TONE OUTPUT ASSIGN': lambda val: str(val+1),
                 'SOURCE TONE': parse_source_tone,
                 'FREQUENCY': lambda val: str(val//1000) + ' kHz',
                 'ORIG KEY NUMBER': int_to_note,
                 'LEVEL':lambda val:str(val),
                 'FINE TUNE':lambda val:str(val),
                 # It's not documented in the manual, but if a tone is empty WAVE BANK is 2
                 'WAVE BANK': lambda val: ['A','B','None'][val],
                 'WAVE SEGMENT TOP': lambda val: str(val+1),
                 'WAVE SEGMENT LENGTH':lambda val:str(val),
                 'TVF SWITCH': lambda val: ['Off','On'][val],
                 'WAVE SEGMENT LENGTH':lambda val:str(val),
                 'OSC LFO DEPTH':lambda val:str(val),
                 'TRANSPOSE':lambda val:str(val), # Or 'Shift' in the interface
                 'BENDER SWITCH': lambda val: ['Off','On'][val],
                 'PITCH FOLLOW': lambda val: ['Off','On'][val],
                 'AFTER TOUCH SWITCH': lambda val: ['Off','On'][val],
                 #     TVF tab.
                 'TVF CUT OFF': lambda val: str(val),
                 'TVF RESONANCE': lambda val: str(val),
                 'TVF KEY FOLLOW': lambda val: str(val),
                 'TVF LFO DEPTH': lambda val: str(val),
                 'TVF LEVEL CURVE': lambda val: str(val),
                 'TVF EG DEPTH': lambda val: str(val),
                 'TVF EG POLARITY': lambda val: ['+','-'][val],
                 'TVF KEY RATE FOLLOW': lambda val: str(val),
                 'TVF VELOCITY RATE FOLLOW': lambda val: str(val),
                 'TVF ENV SUSTAIN POINT': lambda val: str(val+1),
                 'TVF ENV END POINT': lambda val: str(val+1),
                 'TVF ENV': envelope_unpack,
                 #     TVA tab.
                 'TVA LFO DEPTH':lambda val:str(val),
                 'TVA LEVEL CURVE':lambda val:str(val),
                 'ENV VEL-RATE':lambda val:str(val),
                 'TVA ENV KEY-RATE':lambda val:str(val),
                 'TVA ENV SUSTAIN POINT': lambda val: str(val+1),
                 'TVA ENV END POINT': lambda val: str(val+1),
                 'TVA ENV': envelope_unpack,
                 #     Loop tab
                 'LOOP MODE': lambda val: ['Fwd','Alt','1Shot','Reverse'][val],
                 'LOOP TUNE': lambda val : str(val),
                 'START POINT': lambda val : str(val),
                 'LOOP LENGTH': lambda val : str(val),
                 'LOOP POINT': lambda val : str(val),
                 'END POINT': lambda val : str(val),
                 #     LFO tab. There's an error in the manual with values on LFO MODE and POLARITY
                 'LFO RATE': lambda val : str(val),
                 'LFO SYNC': lambda val: ['Off','On'][val],
                 'LFO MODE': lambda val: ['Sin','Peak Hold'][val],
                 'LFO DELAY': lambda val : str(val),
                 'LFO OFFSET': lambda val : str(val),
                 'LFO POLARITY': lambda val: ['+','-'][val],
                 # Patch
                 'BEND RANGE': lambda val : str(val),
                 'AFTER TOUCH SENSE': lambda val : str(val),
                 'VELOCITY SW THRESHOLD': lambda val : str(val),
                 'OCTAVE SHIFT': lambda val : str(val),
                 'KEY MODE': lambda val : Fields550.lookup_values['KEY MODE'][val],
                 'OUTPUT LEVEL': lambda val : str(val),
                 'DETUNE':lambda val:str(val),
                 'VELOCITY MIX RATIO':lambda val:str(val),
                 'AFTER TOUCH ASSIGN':lambda val:Fields550.lookup_values['AFTER TOUCH ASSIGN'][val],
                 'KEY ASSIGN': lambda val : Fields550.lookup_values['KEY ASSIGN'][val],
                 'OUTPUT ASSIGN': patch_output_renum,
                 # Function
                 'DISK LABEL': readable_disk_label,
                 'MASTER TUNE': str,
                 'VOICE MODE': parse_voice_mode,
                 'MULTI MIDI RX-CH': midi_multi_ch_parse,
                 'MULTI PATCH NUMBER': multi_roland_number,
                 'MULTI LEVEL': lambda val: tuple([str(v) for v in list(val)]),
                 'KEYBOARD DISPLAY': lambda val: FunctionFields.lookup_keyboard_disp[val],
                 'KEYBOARD DISPLAY': lambda val: ['A','B','C','D','E','F','G','H','ALL'][val],
                 'EXTERNAL CONTROLLER': lambda val: ['OFF','MOUSE','RC-100'][val],
                 # MIDI
                 'RX CHANNEL': midi_multi_ch_parse,
                 'RX PROGRAM CHANGE': multi_on_off,
                 'RX BENDER': multi_on_off,
                 'RX MODULATION': multi_on_off,
                 'RX HOLD': multi_on_off,
                 'RX AFTER TOUCH': multi_on_off,
                 'RX VOLUME': multi_on_off,
                 'RX BEND RANGE': multi_on_off,
                 'SYSTEM EXCLUSIVE': lambda val: ['Off','On'][val],
                 'DEVICE ID': lambda val : str(val+1),
                 'RX PROGRAM CHANGE NUMBER': lambda val: tuple([str(v + 1) for v in list(val)])
                 }
    
class Fields50:
    """
    This contains parameter formatting information for the S-50 parameters.
    This is a placeholder that needs to be filled out later.
    """
    #             Function
    bindings = { 'CONTROLLER ASSIGN': lambda val: ['Mod Depth','Bend Range','Cntrl Change'][val],
                 'DP-2 ASSIGN': lambda val: ['Trig Play','Patch Shift'][val],
                 'AUDIO TRIG': lambda val: ['Off','On'][val],
                 'DT-100': lambda val: ['Off','On'][val],
                 'KEYBOARD ASSIGN':lambda val: ['A','B','C','D','Off'][val],
                 # MIDI
                 'RX CHANNEL': midi_multi_ch_parse,
                 'RX PROGRAM CHANGE': multi_on_off,
                 'RX BENDER': multi_on_off,
                 'RX MODULATION': multi_on_off,
                 'RX HOLD': multi_on_off,
                 'RX AFTER TOUCH': multi_on_off,
                 'RX VOLUME': multi_on_off,
                 'RX BEND RANGE': multi_on_off,
                 'TX CHANNEL': lambda val: val+1,
                 'TX PROGRAM CHANGE': lambda val: ['Off','On'][val],
                 'TX BENDER': lambda val: ['Off','On'][val],
                 'TX MODULATION': lambda val: ['Off','On'][val],
                 'TX HOLD': lambda val: ['Off','On'][val],
                 'TX AFTER TOUCH': lambda val: ['Off','On'][val],
                 'TX VOLUME': lambda val: ['Off','On'][val],
                 'TX BEND RANGE': lambda val: ['Off','On'][val],
                 'DEVICE ID': lambda val : val+1,
                 'SYSTEM EXCLUSIVE': lambda val: ['Off','On'][val],
                 # Tones
                 # Main
                 #'SOURCE TONE': parse_source_tone,
                 'ORIG KEY NUMBER': int_to_note,
                 'PITCH FOLLOW': lambda val: ['Off','On'][val],
                 'WAVE SEGMENT TOP': lambda val: val+1,
                 'FREQUENCY': lambda val: str(val//1000) + ' kHz',
                 'WAVE BANK': lambda val: ['A','B','None'][val],
                 #  Loop
                 'LOOP MODE': lambda val: ['Fwd','Alt','1Shot','Reverse'][val]
                 }
        
# Display names of parameters. The plan for now is to just match the interface.
#??? means check that this is correct
display_names = { 'NAME':'Name', # name shared between patch and tone
                  'OUTPUT ASSIGN':'Output Assign',
                  'TONE OUTPUT ASSIGN':'Output Assign',
                  'SOURCE TONE':'Original Tone',
                  # ORIG/SUB TONE not displayed
                  'FREQUENCY':'Frequency', # displayed, but not in sampler
                  'ORIG KEY NUMBER':'Original Key',
                  'WAVE BANK':'Wave Bank', # displayed, but not in sampler
                  'WAVE SEGMENT TOP':'Start Segment', # displayed, but not in sampler
                  'WAVE SEGMENT LENGTH':'Length (Segments)', # displayed, but not in sampler
                  'START POINT':'Start Point',
                  'END POINT':'End Point',
                  'LOOP POINT':'Loop Point',
                  'LOOP MODE':'Loop Mode',
                  'TVA LFO DEPTH':'LFO Depth', # A lot are shortened because of tab context
                  'LFO RATE':'Rate',
                  'LFO SYNC':'Sync',
                  'LFO DELAY':'Delay',
                  'LFO MODE':'Mode',
                  'OSC LFO DEPTH':'P.LFO Depth',
                  'LFO POLARITY':'Polarity',
                  'LFO OFFSET':'Offset',
                  'TRANSPOSE':'Shift',
                  'FINE TUNE':'Fine Tune',
                  'TVF CUT OFF':'Cut-off',
                  'TVF RESONANCE':'Resonance',
                  'TVF KEY FOLLOW':'Key Follow',
                  'TVF LFO DEPTH':'LFO Depth',
                  'TVF EG DEPTH':'EG Depth',
                  'TVF EG POLARITY':'EG Pol.',
                  'TVF LEVEL CURVE':'L.Curve',
                  'TVF KEY RATE FOLLOW':'Key-Rate',
                  'TVF VELOCITY RATE FOLLOW':'Vel-Rate',
                  'TVF SWITCH':'TVF',
                  'BENDER SWITCH':'Pitch Bender',
                  'TVA ENV SUSTAIN POINT':'Sus',
                  'TVA ENV END POINT':'End',
                  # TVA Env not displayed directly
                  'TVA ENV KEY-RATE':'Key-Rate',
                  'LEVEL':'Level',
                  'ENV VEL-RATE':'Vel-Rate',
                  # Recording params not displayed
                  # Zoom T not displayed
                  # Zoom L not displayed
                  # Copy source not displayed
                  'LOOP TUNE':'Loop Tune',
                  'TVA LEVEL CURVE':'L.Curve',
                  'LOOP LENGTH':'Loop Length',
                  'PITCH FOLLOW':'Pitch Follow',
                  # ENV ZOOM not displayed
                  'TVF ENV SUSTAIN POINT':'Sus',
                  'TVF ENV END POINT':'End',
                  # TVF ENV not displayed directly
                  'AFTER TOUCH SWITCH':'After Touch',
                  #   ***Patch***
                  'BEND RANGE':'P.Bend Range',
                  'AFTER TOUCH SENSE':'A.T. Sense',
                  'KEY MODE':'Key Mode',
                  'VELOCITY SW THRESHOLD':'V-Sw Thresh.',
                  # Tone to Key 1 and 2 not displayed directly
                  # Copy source not displayed
                  'OCTAVE SHIFT':'Oct.Shift',
                  'OUTPUT LEVEL':'Level',
                  'DETUNE':'Unison Detune',
                  'VELOCITY MIX RATIO':'V-Mix Ratio',
                  'AFTER TOUCH ASSIGN':'A.T. Assign',
                  'KEY ASSIGN':'Key Assign',
                  # Func - some of these don't have a real name in the interface
                  # so they've just been assigned something sensible
                  'MASTER TUNE':'Master Tune',
                  'VOICE MODE':'Voice Mode',
                  'MULTI MIDI RX-CH':'RX Channel',
                  'MULTI PATCH NUMBER':'Multi Patch Number',
                  'KEYBOARD DISPLAY':'Keyboard Display',
                  'MULTI LEVEL':'Level',
                  'DISK LABEL':'Disk Label',
                  'EXTERNAL CONTROLLER':'Ext. Ctrl',
                  # MIDI
                  'RX CHANNEL':'RX-CH',
                  'RX PROGRAM CHANGE':'P.Chg',
                  'RX BENDER':'Bend',
                  'RX MODULATION':'Mod',
                  'RX HOLD':'Hold',
                  'RX AFTER TOUCH':'A.T',
                  'RX VOLUME':'Vol',
                  'RX BEND RANGE':'B.Rng',
                  'SYSTEM EXCLUSIVE':'Exclusive',
                  'DEVICE ID':'Device ID',
                  'RX PROGRAM CHANGE NUMBER':'Prog #',
                  # S-50 Specific Entries - Function
                  'CONTROLLER ASSIGN':'Controller Assign',
                  'DP-2 ASSIGN':'DP-2 Assign',
                  'AUDIO TRIG':'Audio Trig',
                  'MIDI CONTROL CHANGE NUMBER':'MIDI Control Change Number',
                  # DT-100 doesn't need formatting
                  'MULTI TONE NUMBER':'Multi Tone Number',
                  'KEYBOARD ASSIGN':'Keyboard Assign',
                  # S-50 Specific Entries - MIDI
                  'RX PROGRAM NUMBER':'RX Program Number',
                  'TX PROGRAM NUMBER':'TX Program Number',
                  'TX CHANNEL':'TX Channel',
                  'TX PROGRAM CHANGE':'TX Program Change',
                  'TX BENDER':'TX Bender',
                  'TX MODULATION':'TX Modulation',
                  'TX HOLD':'TX Hold',
                  'TX AFTER TOUCH':'TX After Touch',
                  'TX VOLUME':'TX Volume',
                  'TX BEND RANGE':'TX Bend Range',
                  # Patches
                  'MODULATION DEPTH':'Mod. Depth',
                  # Tones
                  'LFO DEPTH':'LFO Depth',
                  'LEVEL CURVE':'Level Curve',
                  'ENV KEY-RATE':'Env Key-Rate'
                }

# Bold font for parameter displays
param_font = 'TkDefaultFont 10 bold'
font_bold = 'TkDefaultFont 10 bold'
