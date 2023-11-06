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

from rlook.reporter import Reporter
import rlook.disk.diskread as diskread
import rlook.exceptions as exceptions
import rlook.tbox as tbox
from rlook.disk.formatting import format_value

import riscos_toolbox as toolbox
from riscos_toolbox.objects.window import Window
from riscos_toolbox.gadgets.displayfield import DisplayField

class MIDIPane(tbox.WindowNestedMixin,Window):
    template = "MIDITab"
	
    # Gadget component IDs for this window
    G_RXCH    = [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18] # RX Channel
    G_BEND    = [0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x20] # RX Bender
    G_PCHG    = [0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28] # RX Program Change
    G_BRNG    = [0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30] # RX Bend Range
    G_MOD     = [0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38] # RX Modulation
    G_HOLD    = [0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40] # RX Hold
    G_AT      = [0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48] # RX Aftertouch
    G_VOL     = [0x49, 0x4A, 0x4B, 0x4C, 0x4D, 0x4E, 0x4F, 0x50] # RX Volume
    G_PROGNUM = [0x5E, 0x5F, 0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 
                 0x66, 0x67, 0x68, 0x69, 0x6A, 0x6B, 0x6C, 0x6D,
                 0x6E, 0x6F, 0x70, 0x71, 0x72, 0x73, 0x74, 0x75,
                 0x76, 0x77, 0x78, 0x79, 0x7A, 0x7B, 0x7C, 0x7D] # Program change num
    G_EXCLUSIVE = 0x7F # System Exclusive on/off
    G_DEVICEID  = 0x81 # Device ID
	
    # Create a set of displayfields. Takes in a tuple of Component IDs
    # and returns a list of DisplayField objects.
    def _create_displayfields(self, components):
        gadgets = []
        for component in components:
            gadgets.append(DisplayField(self, component))
			
        return gadgets
	
    def __init__(self, *args):
        super().__init__(*args)
        Reporter.print(f"RLook: Created MIDIPane. id={hex(self.id)}",debug=True)
		
        # Set up gadgets
        self.g_row_rxch    = self._create_displayfields(MIDIPane.G_RXCH)
        self.g_row_bend    = self._create_displayfields(MIDIPane.G_BEND)
        self.g_row_pchg    = self._create_displayfields(MIDIPane.G_PCHG)
        self.g_row_brng    = self._create_displayfields(MIDIPane.G_BRNG)
        self.g_row_mod     = self._create_displayfields(MIDIPane.G_MOD)
        self.g_row_hold    = self._create_displayfields(MIDIPane.G_HOLD)
        self.g_row_at      = self._create_displayfields(MIDIPane.G_AT)
        self.g_row_vol     = self._create_displayfields(MIDIPane.G_VOL)
        self.g_prognum     = self._create_displayfields(MIDIPane.G_PROGNUM)
        self.g_exclusive   = DisplayField(self, MIDIPane.G_EXCLUSIVE)
        self.g_deviceid    = DisplayField(self, MIDIPane.G_DEVICEID)
        
    def load_disk(self, disk):
        Reporter.print(f"RLook: MIDI pane is loading disk.",debug=True)		
        fmt = disk.format

        # Here we introduce the somewhat wonky formatting module.
        # it could probably use some work to be more robust.
        vals = disk.midi.lookup("RX CHANNEL")
        if vals != None and len(vals) == 8:
            formatted = format_value("RX CHANNEL",vals,fmt)
            for i in range(0, 8):
                self.g_row_rxch[i].value = formatted[i]
		
        vals = disk.midi.lookup("RX PROGRAM CHANGE")
        if vals != None and len(vals) == 8:
            formatted = format_value("RX PROGRAM CHANGE",vals,fmt)
            for i in range(0, 8):
                self.g_row_bend[i].value = formatted[i]
		
        vals = disk.midi.lookup("RX BENDER")
        if vals != None and len(vals) == 8:
            formatted = format_value("RX BENDER",vals,fmt)
            for i in range(0, 8):
                self.g_row_pchg[i].value = formatted[i]
		
        vals = disk.midi.lookup("RX BEND RANGE")
        if vals != None and len(vals) == 8:
            formatted = format_value("RX BEND RANGE",vals,fmt)
            for i in range(0, 8):
                self.g_row_brng[i].value = formatted[i]
		
        vals = disk.midi.lookup("RX MODULATION")
        if vals != None and len(vals) == 8:
            formatted = format_value("RX MODULATION",vals,fmt)
            for i in range(0, 8):
                self.g_row_mod[i].value = formatted[i]
		
        vals = disk.midi.lookup("RX HOLD")
        if vals != None and len(vals) == 8:
            formatted = format_value("RX HOLD",vals,fmt)
            for i in range(0, 8):
                self.g_row_hold[i].value = formatted[i]
		
        vals = disk.midi.lookup("RX AFTER TOUCH")
        if vals != None and len(vals) == 8:
            formatted = format_value("RX AFTER TOUCH",vals,fmt)
            for i in range(0, 8):
                self.g_row_at[i].value = formatted[i]
		
        vals = disk.midi.lookup("RX VOLUME")
        if vals != None and len(vals) == 8:
            formatted = format_value("RX VOLUME",vals,fmt)
            for i in range(0, 8):
                self.g_row_vol[i].value = formatted[i]
		
        vals = disk.midi.lookup("RX PROGRAM CHANGE NUMBER")
        if vals != None and len(vals) == 32:
            formatted = format_value("RX PROGRAM CHANGE NUMBER",vals,fmt)
            for i in range(0, 32):
                self.g_prognum[i].value = formatted[i]
		
        val = disk.midi.lookup("SYSTEM EXCLUSIVE")
        if val != None:
            formatted = format_value("SYSTEM EXCLUSIVE",val,fmt)
            self.g_exclusive.value = formatted
		
        val = disk.midi.lookup("DEVICE ID")		
        if val != None:
            formatted = format_value("DEVICE ID",val,fmt)
            self.g_deviceid.value = formatted
		
		