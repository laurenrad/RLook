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
Module for the Choices window in RLook.
"""

import pickle
import swi

import rlook
from rlook.reporter import Reporter
import rlook.exceptions as exceptions
import rlook.choices as choices

import riscos_toolbox as toolbox
from riscos_toolbox.events import toolbox_handler
from riscos_toolbox.objects.window import Window
from riscos_toolbox.gadgets.actionbutton import ActionButtonSelectedEvent
from riscos_toolbox.gadgets.optionbutton import OptionButton
    
class ChoicesWin(Window):
    template = "Choices"
    
    # Gadget constants
    G_OPT_PLAYPOINTS = 0x04 # Option: Use start/end points for play
    G_OPT_XPORTPOINTS = 0x05 # Option: Use start/end points for export
    G_OPT_AUTOPLAY = 0x06 # Option: Autoplay tones
    G_DEFAULT = 0x00 # Button: default
    G_SAVE = 0x01 # Button: save
    G_CANCEL = 0x02 # Button: cancel
    G_SET = 0x03 # Buttton: set

    def __init__(self, *args):
        super().__init__(*args)
        # Gadget setup
        self.g_opt_playpoints = OptionButton(self, ChoicesWin.G_OPT_PLAYPOINTS)
        self.g_opt_xportpoints = OptionButton(self, ChoicesWin.G_OPT_XPORTPOINTS)
        self.g_opt_autoplay = OptionButton(self, ChoicesWin.G_OPT_AUTOPLAY)
        self.refresh_gadgets()
        Reporter.print("RLook: ChoicesWin created.",debug=True)
        
    # Update gadgets to reflect global choices
    def refresh_gadgets(self):
        self.g_opt_playpoints.state = int(rlook.opts.startend_playback)
        self.g_opt_xportpoints.state = int(rlook.opts.startend_export)
        self.g_opt_autoplay.state = int(rlook.opts.autoplay)
        
    # Stores gadget states in global choices. This does NOT save to disk.
    def store_choices(self):
        rlook.opts.set([self.g_opt_playpoints.state,\
                        self.g_opt_xportpoints.state,\
                        self.g_opt_autoplay.state])
                        
    # Take any immediate action on setting choices. This is
    # not needed at the moment, so does nothing, but is here for expansion.
    def action_choices(self):
        pass
        
    @toolbox_handler(ActionButtonSelectedEvent)
    def button_selected(self, event, id_block, poll_block):
        if id_block.self.id != self.id:
            return False # Pass along if this is for a different window
                        
        if id_block.self.component == ChoicesWin.G_DEFAULT:
            # On default, reset choices and refresh gadgets
            rlook.opts.reset()
            self.refresh_gadgets()
        elif id_block.self.component == ChoicesWin.G_SAVE:
            self.store_choices()
            self.action_choices()
            if choices.save(rlook.opts) == False:
                e = exceptions.WimpCustomError("Unable to save choices.")
                toolbox.report_exception(e)
        elif id_block.self.component == ChoicesWin.G_CANCEL:
            # On cancel, refresh gadgets from the set choices. That should be all.
            self.refresh_gadgets()
        elif id_block.self.component == ChoicesWin.G_SET:
            # On set, store gadgets in choices and take any needed actions.
            # None of these choices currently need immediate actions on setting;
            # This could change in the future so this will call a stub method
            # called action_choices.
            self.store_choices()
            self.action_choices()
        else:
            return False
            
        return True
            