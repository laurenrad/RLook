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

import swi

from rlook.reporter import Reporter
import rlook.disk.diskread as diskread
import rlook.exceptions as exceptions
import rlook.tbox as tbox
from rlook.disk.formatting import format_value

import riscos_toolbox as toolbox
from riscos_toolbox.objects.window import Window
from riscos_toolbox.gadgets.button import Button
from riscos_toolbox.gadgets.displayfield import DisplayField
from riscos_toolbox.gadgets.textarea import TextArea

class FuncPane(tbox.WindowNestedMixin,Window):
    template = "FuncTab" # Toolbox object template
    
    # Gadget component IDs for this window
    G_DISKLABEL  = 0x2D
    G_MASTERTUNE = 0x01 
    G_VOICEMODE  = 0x02 
    G_KEYDISP    = 0x03 
    G_EXTCTRL    = 0x04 
    G_RX         = [0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x29]
    G_PATCHNUM   = [0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x2A]
    G_LEVEL      = [0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x2B]
    G_SYSTEM     = 0x2F
    
    # Create a set of displayfields. Takes in a tuple of Component IDs
    # and returns a list of DisplayField objects.
    def _create_displayfields(self, components):
        gadgets = []
        for component in components:
            gadgets.append(DisplayField(self, component))
            
        return gadgets
    
    def __init__(self, *args):
        super().__init__(*args)
        # Create gadget objects
        self.g_disklabel = TextArea(self, FuncPane.G_DISKLABEL)
        self.g_disklabel.text = "" # Needed to work around a Toolbox bug
        self.g_mastertune = DisplayField(self, FuncPane.G_MASTERTUNE)
        self.g_voicemode = DisplayField(self, FuncPane.G_VOICEMODE)
        self.g_keydisp = DisplayField(self, FuncPane.G_KEYDISP)
        self.g_extctrl = DisplayField(self, FuncPane.G_EXTCTRL)
        self.g_rx = self._create_displayfields(FuncPane.G_RX)
        self.g_patchnum = self._create_displayfields(FuncPane.G_PATCHNUM)
        self.g_level = self._create_displayfields(FuncPane.G_LEVEL)
        self.g_system = DisplayField(self, FuncPane.G_SYSTEM)
        Reporter.print(f"RLook: FuncPane created. id={hex(self.id)}",debug=True)
        
    # Update the UI for this pane with the new disk's info.
    def load_disk(self, disk):
        Reporter.print("RLook: Function pane is loading disk.",debug=True)
        fmt = disk.format
        
        # Disk Label
        val = disk.function.lookup("DISK LABEL")
        if val != None:
            formatted = format_value("DISK LABEL",val,fmt)
            self.g_disklabel.text = formatted
            
        # Master Tune
        val = disk.function.lookup("MASTER TUNE")
        if val != None:
            self.g_mastertune.value = format_value("MASTER TUNE",val,fmt)
        
        # Voice Mode
        val = disk.function.lookup("VOICE MODE")
        if val != None:
            self.g_voicemode.value = format_value("VOICE MODE",val,fmt)
        
        # Keyboard Display
        val = disk.function.lookup("KEYBOARD DISPLAY")
        if val != None:
            self.g_keydisp.value = format_value("KEYBOARD DISPLAY",val,fmt)
                    
        # Ext. Ctrl
        val = disk.function.lookup("EXTERNAL CONTROLLER")
        if val != None:
            self.g_extctrl.value = format_value("EXTERNAL CONTROLLER",val,fmt)
        
        # RX-CH
        vals = disk.function.lookup("MULTI MIDI RX-CH")
        if vals != None and len(vals) == 8:
            formatted = format_value("MULTI MIDI RX-CH",vals,fmt)
            for i in range(0,8):
                self.g_rx[i].value = formatted[i]
                
        # Multi patch number
        vals = disk.function.lookup("MULTI PATCH NUMBER")
        if vals != None and len(vals) == 8:
            formatted = format_value("MULTI PATCH NUMBER",vals,fmt)
            for i in range(0,8):
                self.g_patchnum[i].value = formatted[i]
                
        # Level
        vals = disk.function.lookup("MULTI LEVEL")
        if vals != None and len(vals) == 8:
            formatted = format_value("MULTI LEVEL",vals,fmt)
            for i in range(0,8):
                self.g_level[i].value = formatted[i]
                
        # System version
        self.g_system.value = disk.os_ver
