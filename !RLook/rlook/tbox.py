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
import riscos_toolbox as toolbox
from riscos_toolbox.gadgets.scrolllist import ScrollList
from riscos_toolbox.objects.saveas import SaveAs
from riscos_toolbox.objects.menu import Menu
from riscos_toolbox.events import ToolboxEvent

# Constants
TASK = 0x4B534154 # everyone's favorite Wimp constant

# This module is for filling in anything missing in riscos_toolbox.

# Some nested windowing stuff
# Some nesting value constants
NEST_WORKAREA = 0x00 # Nesting linked to work area of parent window
NEST_LOWERBOUND = 0x01 # Nesting linked to lower bound of parent (left or bottom)
NEST_UPPERBOUND = 0x02 # Nesting linked to upper bound of parent (top or right)
NEST_LEFT = 16 # Nesting values for left side of window
NEST_BOTTOM = 18 # Nesting values for bottom side of window
NEST_RIGHT = 20 # Nesting values for right side of window
NEST_TOP = 22 # Nesting values for top side of window
NEST_X = 24 # X scroll offset of window
NEST_Y = 26 # Y scroll offset of window

# Put nesting flags together 
def nest_flags(left,bottom,right,top,x,y):
    result = 0
    result |= (left << NEST_LEFT)
    result |= (bottom << NEST_BOTTOM)
    result |= (right << NEST_RIGHT)
    result |= (top << NEST_TOP)
    result |= (x << NEST_X)
    result |= (y << NEST_Y)
    return result

# This class extends ScrollList with some missing features.
# Probably will make a PR from these in the future
class ScrollListPlus(ScrollList):
    _type = 0x401A
    
    # Methods
    GetState     = _type + 0
    SetState     = _type + 1
    AddItem      = _type + 2
    DeleteItems  = _type + 3
    SelectItem   = _type + 4
    DeselectItem = _type + 5
    GetSelected  = _type + 6
    MakeVisible  = _type + 7
    SetColour    = _type + 8
    GetColour    = _type + 9
    SetFont      = _type + 10
    GetItemText  = _type + 11
    CountItems   = _type + 12
    SetItemText  = _type + 13
    
    # Flags
    ScrollList_SelectionChangingMethod_OnAll = 2
    
    def select_item(self, index):
        swi.swi('Toolbox_ObjectMiscOp','0iiii',self.window.id,
                ScrollListPlus.SelectItem,self.id,index)
    
    # This is just select item with a flag set    
    def select_all(self):
        swi.swi('Toolbox_ObjectMiscOp','Iiiii',
                ScrollListPlus.ScrollList_SelectionChangingMethod_OnAll,
                self.window.id,self.ScrollListPlus.SelectItem,self.id,0)
        
    def deselect_item(self, index):
        pass
        
    @property
    def colour(self):
        pass
    
    @colour.setter
    def colour(self, colour):
        pass
        
    def set_colour(self, fg, bg):
        pass
        
    def set_font(self, name, width, height):
        pass
        
    def get_item_text(self, index):
        pass
        
    def count_items(self):
        pass
        
    def set_item_text(self, index, text):
        pass
        
# Placeholder for SaveAs AboutToBeShownEvent
class SaveAsAboutToBeShownEvent(ToolboxEvent):
    event_id = SaveAs.AboutToBeShown
    
# Menu_AboutToBeShown Placeholder
class MenuAboutToBeShownEvent(ToolboxEvent):
    event_id = Menu.AboutToBeShown
    
# The end goal with this one is to create a show method for window objects that can accommodate
# the different options; the existing one only allows the default.
class WindowNestedMixin():
    # Show a nested window.
    def show_nested(self, min_x, min_y, max_x, max_y, scroll_x, scroll_y, parent, flags):        
        b = swi.block(10,[min_x,min_y,max_x,max_y,scroll_x,scroll_y,-1,0,
                      parent.wimp_handle,flags])
        swi.swi("Toolbox_ShowObject","4i1bi0",self.id,b,parent.id)
        
# Delete a toolbox object.
# Unfortunately, this will trigger broken code in riscos-toolbox, so it can't be used
# right now and may be incorporated into future versions anyway. It's here for posterity.
def delete_object(id, recursive=True):
    flags = int(not recursive)
    swi.swi("Toolbox_DeleteObject","Ii",flags,id)
        
        