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

import copy

from rlook.reporter import Reporter
import rlook.disk.diskread as diskread
import rlook.exceptions as exceptions
import rlook.disk.formatting as formatting
from rlook.disk.formatting import format_value
import rlook.tbox as tbox
from rlook.tbox import ScrollListPlus


import riscos_toolbox as toolbox
from riscos_toolbox.events import toolbox_handler
from riscos_toolbox.objects.window import Window
from riscos_toolbox.gadgets.displayfield import DisplayField
from riscos_toolbox.gadgets.slider import Slider, SliderValueChangedEvent
from riscos_toolbox.gadgets.scrolllist import ScrollListSelectionEvent
class PatchPane(tbox.WindowNestedMixin,Window):
    template = "PatchTab"
    
    # Gadget component IDs for this window
    G_PATCHLIST   = 0x00 # ScrollList for patch selection
    G_TONESLIDER  = 0x19 # Slider to select note for tone assignment
    G_TONE1       = 0x1A # DisplayField for 1st assigned tone
    G_TONE2       = 0x1F # DisplayField for 2nd assigned tone
    G_NOTENAME    = 0x20 # DisplayField for selected note name
    G_LINKEDTONES = 0x1B # ScrollList containing linked tones
    G_NAME        = 0x18 # DisplayField for tone name
    G_BENDRANGE   = 0x17 # DisplayField for bend range
    G_ATSENSE     = 0x16 # DisplayField for aftertouch sense
    G_KEYMODE     = 0x15 # DisplayField for key moode
    G_VSWTHRESH   = 0x14 # DisplayField for velocity switch threshold
    G_OCTSHIFT    = 0x13 # DisplayField for octave shift
    G_LEVEL       = 0x12 # DisplayField for level
    G_DETUNE      = 0x11 # DisplayField for unison detune
    G_VMIXRATIO   = 0x03 # DisplayField for v-mix ratio
    G_ATASSIGN    = 0x0E # DisplayField for aftertouch assign
    G_KEYASSIGN   = 0x0F # DisplayField for key assign
    G_OUTASSIGN   = 0x10 # DisplayField for output assign
    
    def __init__(self, template, id, diskwin):
        super().__init__(template, id) # Will call Object constructor
        self.diskwin = diskwin # Keep reference to document window
        Reporter.print(f"RLook: PatchPane created. id={hex(self.id)}",debug=True)
        self.disk = None
        
        # Set up gadgets
        self.g_patchlist = ScrollListPlus(self, PatchPane.G_PATCHLIST)
        self.g_toneslider = Slider(self, PatchPane.G_TONESLIDER)
        self.g_tone1 = DisplayField(self, PatchPane.G_TONE1)
        self.g_tone2 = DisplayField(self, PatchPane.G_TONE2)
        self.g_notename = DisplayField(self, PatchPane.G_NOTENAME)
        self.g_linkedtones = ScrollListPlus(self, PatchPane.G_LINKEDTONES)
        self.g_name = DisplayField(self, PatchPane.G_NAME)
        self.g_bendrange = DisplayField(self, PatchPane.G_BENDRANGE)
        self.g_atsense = DisplayField(self, PatchPane.G_ATSENSE)
        self.g_keymode = DisplayField(self, PatchPane.G_KEYMODE)
        self.g_vswthresh = DisplayField(self, PatchPane.G_VSWTHRESH)
        self.g_octshift = DisplayField(self, PatchPane.G_OCTSHIFT)
        self.g_level = DisplayField(self, PatchPane.G_LEVEL)
        self.g_detune = DisplayField(self, PatchPane.G_DETUNE)
        self.g_vmixratio = DisplayField(self, PatchPane.G_VMIXRATIO)
        self.g_atassign = DisplayField(self, PatchPane.G_ATASSIGN)
        self.g_keyassign = DisplayField(self, PatchPane.G_KEYASSIGN)
        self.g_outassign = DisplayField(self, PatchPane.G_OUTASSIGN)
        
    def unload_disk(self):
        self.disk = None
    
    # When a disk is loaded, add all patches to the list and select the first one    
    def load_disk(self, disk):
        Reporter.print("RLook: Patch pane is loading disk.",debug=True)
        self.fmt = disk.format
        self.disk = disk
        
        # Populate patch list
        for patch in self.disk.patches:
            self.g_patchlist.add_item(patch.get_name(),-1)
            
        # Select first patch and show its params
        self.g_patchlist.select_item(0)
        self.view_patch(0)
        
    
    # This updates the gadgets with data for the given patch.
    def view_patch(self,index):
        patch = self.disk.patches[index]
        
        ## Populate regular display fields
        
        # Name
        val = patch.lookup("NAME")
        if val != None:
            self.g_name.value = format_value("NAME",val,self.fmt)
        
        # Patch bend range !
        val = patch.lookup("BEND RANGE")
        if val != None:
            self.g_bendrange.value = format_value("BEND RANGE",val,self.fmt)
        
        # Aftertouch sense !
        val = patch.lookup("AFTER TOUCH SENSE")
        if val != None:
            self.g_atsense.value = format_value("AFTER TOUCH SENSE",val,self.fmt)
            
        # Key mode !
        val = patch.lookup("KEY MODE")
        if val != None:
            self.g_keymode.value = format_value("KEY MODE",val,self.fmt)
            
        # Velocity switch threshold !
        val = patch.lookup("VELOCITY SW THRESHOLD")
        if val != None:
            self.g_vswthresh.value = format_value("VELOCITY SW THRESHOLD",val,self.fmt)
            
        # Octave Shift !
        val = patch.lookup("OCTAVE SHIFT")
        if val != None:
            self.g_octshift.value = format_value("OCTAVE SHIFT",val,self.fmt)
            
        # Level !
        val = patch.lookup("OUTPUT LEVEL")
        if val != None:
            self.g_level.value = format_value("OUTPUT LEVEL",val,self.fmt)
            
        # Unison Detune !
        val = patch.lookup("DETUNE")
        if val != None:
            self.g_detune.value = format_value("DETUNE",val,self.fmt)
            
        # V-Mix ratio !
        val = patch.lookup("VELOCITY MIX RATIO")
        if val != None:
            self.g_vmixratio.value = format_value("VELOCITY MIX RATIO",val,self.fmt)
            
        # Aftertouch assign !
        val = patch.lookup("AFTER TOUCH ASSIGN")
        if val != None:
            self.g_atassign.value = format_value("AFTER TOUCH ASSIGN",val,self.fmt)
            
        # Key assign !
        val = patch.lookup("KEY ASSIGN")
        if val != None:
            self.g_keyassign.value = format_value("KEY ASSIGN",val,self.fmt)
            
        # Output assign !
        val = patch.lookup("OUTPUT ASSIGN")
        if val != None:
            self.g_outassign.value = format_value("OUTPUT ASSIGN",val,self.fmt)
            
        ## Now the rest of it
        
        # Linked tones
        self.g_linkedtones.delete_items(0,-1) # first clear ScrollList
        for tone in patch.tone_list():
            tname = formatting.roland_number(tone) + " "
            tname += self.disk.tones[tone].lookup("NAME")
            if tname != None:
                self.g_linkedtones.add_item(tname,-1)
                
        # Tone assignment
        selected = self.g_patchlist.get_selected()
        note = self.g_toneslider.value
        self.set_tone_assign(selected,note)
    
    # Update the tone assignment display.
    # The params TONE TO KEY 1 and TONE TO KEY 2 will give us a list of
    # note assignments over the whole range.    
    def set_tone_assign(self, selected, note):
        self.g_notename.value = formatting.int_to_note(note)
        tone1_num = self.disk.patches[selected].lookup("TONE TO KEY 1")[note-12]
        tone1_name = self.disk.tones[tone1_num].lookup("NAME")
        tone2_num = self.disk.patches[selected].lookup("TONE TO KEY 2")[note-12]
        tone2_name = self.disk.tones[tone2_num].lookup("NAME")
        self.g_tone1.value = formatting.roland_number(tone1_num) + " " + tone1_name
        self.g_tone2.value = formatting.roland_number(tone2_num) + " " + tone2_name
        
            
    # When the user selects a patch, call view_patch to update everything
    @toolbox_handler(ScrollListSelectionEvent)
    def patch_selected(self, event, id_block, poll_block):
        if id_block.self.id != self.id or id_block.self.component != PatchPane.G_PATCHLIST:
            return False # pass event on

        self.view_patch(poll_block.item)
        return True
        
    # Handler for the tone assignment slider.
    @toolbox_handler(SliderValueChangedEvent)
    def tone_assign_changed(self, event, id_block, poll_block):
        # Set up note name display
        note_num = poll_block.new_value
        selected = self.g_patchlist.get_selected()    
        self.set_tone_assign(selected, note_num)    
