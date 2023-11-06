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

# Application: RLook
# File: diskwin.py
# Description: Module for the window associated with disk images.


import traceback
import swi
import os
import ctypes
import io
import gc

import rlook
import rlook.exceptions as exceptions
import rlook.playit as playit
import rlook.tbox as tbox
import rlook.disk.diskread as diskread
from rlook.reporter import Reporter

from .midipane import MIDIPane
from .funcpane import FuncPane
from .tonepane import TonePane, ToneNav
from .patchpane import PatchPane
from .choiceswin import ChoicesWin

import riscos_toolbox as toolbox
from riscos_toolbox.objects.menu import Menu, SelectionEvent
from riscos_toolbox.objects.window import Window
from riscos_toolbox.objects.proginfo import ProgInfo
from riscos_toolbox.objects.fileinfo import FileInfo
from riscos_toolbox.objects.saveas import SaveAs, SaveToFileEvent, SaveCompletedEvent
from riscos_toolbox.gadgets.button import Button
from riscos_toolbox.gadgets.scrolllist import ScrollList
from riscos_toolbox.gadgets.textarea import TextArea
from riscos_toolbox.gadgets.displayfield import DisplayField
from riscos_toolbox.gadgets.radiobutton import RadioButton, RadioButtonStateChangedEvent
from riscos_toolbox.events import toolbox_handler, wimp_handler, message_handler

# Debug func for tracking objects for memory management
def obj_log(comment, filename):
    with open(filename,'a') as log:
        log.write(comment+":"+f"objs: {len(toolbox.base._objects)}\n")
        log.write("\t"+f"{toolbox.base._objects}\n")

# The navigation toolbar for a disk window.
# Currently this exists mainly to set the Function radio button by default.
class DiskToolbar(Window):
    template = "Navigation"
    	
    def __init__(self, *args):
        super().__init__(*args)		
        self.g_func = RadioButton(self,0x00)
        self.g_func.state = 1
        Reporter.print("RLook: Created DiskToolbar. id={hex(self.id)}",debug=True)			

class DiskWindow(Window):
    template = "DiskWindow"
	
    # Constants
    G_FUNC   = 0x00 
    G_MIDI   = 0x01
    G_PATCH  = 0x02
    G_TONE   = 0x03
    G_TEST   = 0x04
    PANE_BOUNDS = [0, 0, 1500, 1024, 0, 0]
	
    # The library's version of set_toolbar_id doesn't work, so here's one
    TBAR_IBL = 1<<0 # Internal bottom left toolbar
    TBAR_ITL = 1<<1 # Internal top left toolbar
    TBAR_EBL = 1<<2 # External bottom left toolbar
    TBAR_ETL = 1<<3 # External top left toolbar	
    def set_toolbar_id(self, type, id):
        if type & DiskWindow.TBAR_IBL:
            swi.swi("Toolbox_ObjectMiscOp","iiii",DiskWindow.TBAR_IBL,self.id,18,id)
        if type & DiskWindow.TBAR_ITL:
            swi.swi("Toolbox_ObjectMiscOp","iii.i",DiskWindow.TBAR_ITL,self.id,18,id)
        if type & DiskWindow.TBAR_EBL:
            swi.swi("Toolbox_ObjectMiscOp","iii..i",DiskWindow.TBAR_EBL,self.id,18,id)
        if type & DiskWindow.TBAR_ETL:
            swi.swi("Toolbox_ObjectMiscOp","iii...i",DiskWindow.TBAR_ETL,self.id,18,id)
	
    def __init__(self, *args):
        super().__init__(*args)
        self.filename = ""
        try:
            self.funcpane = toolbox.create_object(FuncPane.template,FuncPane)
            self.midipane = toolbox.create_object(MIDIPane.template,MIDIPane)
            self.patchpane = toolbox.create_object(PatchPane.template,PatchPane)
            self.tonepane = toolbox.create_object(TonePane.template,TonePane)
            self.tonebar = toolbox.create_object(ToneNav.template, ToneNav)
            Reporter.print(f"Created DiskWindow. id={hex(self.id)}")
        except Exception as e:
            Reporter.print(repr(e))	
			
    # On loading a disk file, update the interface accordingly. 
    # (And for now, load a test file for this)
    def disk_load(self,filename):
        self.disk = diskread.Disk(filename)
        self.filename = filename.decode('utf-8')
		
        # Update window title - check style guide later. this is just to differentiate
        # files during testing.
        self.title = os.path.basename(self.filename)[:49]
		
        # Now update the toolbar panes as well
        self.funcpane.load_disk(self.disk)
        self.midipane.load_disk(self.disk)
        self.patchpane.load_disk(self.disk)
        self.tonepane.load_disk(self.disk)
		
        # Show function pane by default
        self.funcpane.show_nested(*DiskWindow.PANE_BOUNDS,self,0x800000)
		
    # When radio buttons from the toolbar change, show the appropriate pane.
    @toolbox_handler(RadioButtonStateChangedEvent)
    def radiobutton_changed(self, event, id_block, poll_block):
        if poll_block.state == 1:
            if id_block.self.component == DiskWindow.G_FUNC: # func
                self.funcpane.show_nested(*DiskWindow.PANE_BOUNDS,self,0x800000)
                self.set_toolbar_id(DiskWindow.TBAR_ITL,0)
            elif id_block.self.component == DiskWindow.G_MIDI: # midi pane
                self.midipane.show_nested(*DiskWindow.PANE_BOUNDS,self,0x800000)
                self.set_toolbar_id(DiskWindow.TBAR_ITL,0)
            elif id_block.self.component == DiskWindow.G_PATCH: # patch pane
                self.patchpane.show_nested(*DiskWindow.PANE_BOUNDS,self,0x800000)
                self.set_toolbar_id(DiskWindow.TBAR_ITL,0)
            elif id_block.self.component == DiskWindow.G_TONE: # tone pane
                self.tonepane.show_nested(*DiskWindow.PANE_BOUNDS,self,0x800000)
                self.set_toolbar_id(DiskWindow.TBAR_ITL,self.tonebar.id)
            elif id_block.self.component == TonePane.G_MAIN:
                self.tonepane.show_main()
            elif id_block.self.component == TonePane.G_LOOP:
                self.tonepane.show_loop()
            elif id_block.self.component == TonePane.G_LFO:
                self.tonepane.show_lfo()
            elif id_block.self.component == TonePane.G_TVF:
                self.tonepane.show_tvf()
            elif id_block.self.component == TonePane.G_TVA:
                self.tonepane.show_tva()
            elif id_block.self.component == TonePane.G_WAVE:
                self.tonepane.show_wave()
                
    # When the window closes, delete any manually created objects.
    # This is so ObjectDeleted is triggered, which causes riscos-toolbox to remove its
    # reference to the corresponding Python object.
    # Unfortunately, there is a bug in riscos-toolbox which causes a crash when
    # this event is raised.
    # For now, just remove the disk objects at least.
    @toolbox_handler(rlook.E_WINDOW_CLOSE)
    def window_close(self, event, id_block, poll_block):
        Reporter.print("RLook: Disk window hidden.",debug=True)
        self.disk = None
        self.patchpane.unload_disk()
        self.tonepane.unload_disk()
        #toolbox.delete_object(self.funcpane.id)
        #toolbox.delete_object(self.midipane.id)
        #toolbox.delete_object(self.patchpane.id)
        #toolbox.delete_object(self.tonepane.id)
        #toolbox.delete_object(self.tonebar.id)
        #toolbox.delete_object(self.id)        
	
class DiskMenu(Menu):
    template = "DiskMenu"
	
    # Constants for menu entry component ids
    ENTRY_PLAY = 0x00
    ENTRY_TEST = 0x01
    ENTRY_FILE_SELECTED = 0x02
	
    def __init__(self, *args):
        super().__init__(*args)
        self.filemenu = toolbox.create_object(DiskMenu.FileMenu.template,DiskMenu.FileMenu)
        Reporter.print(f"RLook: Created DiskMenu. id={hex(self.id)}",debug=True)
        # Remove test entry if debug is off
        if rlook.debug_enabled == False:
            self.remove(DiskMenu.ENTRY_TEST)
		
    @toolbox_handler(tbox.MenuAboutToBeShownEvent)
    def menu_show(self,event,id_block,poll_block):
        
        parent_class = type(toolbox.get_object(id_block.parent.id))
        
        # Depending on what pane this was opened on, fade/unfade
        # menu entries as needed.
        if parent_class == FuncPane:
            # This is how it should be done in the library, but
            # I can't get it to work for some reason:
            #self.__getitem__(ENTRY_PLAY).fade(1)
            # In the meantime, I will call Toolbox_ObjectMiscOp directly.			
            # Fade play entry
            swi.swi("Toolbox_ObjectMiscOp","0iiii",self.id,2,DiskMenu.ENTRY_PLAY,1)
            swi.swi("Toolbox_ObjectMiscOp","0iiii",self.filemenu.id,2,
                    DiskMenu.ENTRY_FILE_SELECTED,1)
        elif parent_class == MIDIPane:
            swi.swi("Toolbox_ObjectMiscOp","0iiii",self.id,2,DiskMenu.ENTRY_PLAY,1)
            swi.swi("Toolbox_ObjectMiscOp","0iiii",self.filemenu.id,2,
                    DiskMenu.ENTRY_FILE_SELECTED,1)
        elif parent_class == PatchPane:
            swi.swi("Toolbox_ObjectMiscOp","0iiii",self.id,2,DiskMenu.ENTRY_PLAY,1)
            swi.swi("Toolbox_ObjectMiscOp","0iiii",self.filemenu.id,2,
                    DiskMenu.ENTRY_FILE_SELECTED,1)
        elif parent_class == TonePane:
            swi.swi("Toolbox_ObjectMiscOp","0iiii",self.id,2,DiskMenu.ENTRY_PLAY,0)
            swi.swi("Toolbox_ObjectMiscOp","0iiii",self.filemenu.id,2,
                    DiskMenu.ENTRY_FILE_SELECTED,0)
		
    # Here's the selection handler. As mentioned elsewhere, going around the
    # toolbox on opening the nested windows means the links between objects
    # are broken, but by getting the parent's class type it should be possible to know
    # what the menu was opened on.
    @toolbox_handler(SelectionEvent)
    def menu_select(self,event,id_block,poll_block):
        # Some constants for menu entries
        ENTRY_PLAY = 0x00
		
        Reporter.print("RLook: Menu select: "+repr(id_block.parent.id)+" ",debug=True)
        Reporter.print(f"Parent type: {type(toolbox.get_object(id_block.parent.id))}",debug=True)
        Reporter.print("Component was: "+repr(id_block.self.component),debug=True)
        Reporter.print(f"ID Block: {id_block}",debug=True)
        id, comp = swi.swi("Toolbox_GetParent","0I;ii",self.id)
        Reporter.print(f"id={hex(id)} comp={comp}",debug=True)
		
        if id_block.self.component == DiskMenu.ENTRY_PLAY:
            # Play the selected tone. If this entry is selected,
            # the ancestor should be the tone pane.
            Reporter.print("RLook: Playing tone.",debug=True)
            pane = toolbox.base.get_object(id_block.ancestor.id)
            pane.play_tone()
        elif id_block.self.component == DiskMenu.ENTRY_TEST:
            Reporter.print("RLook: Test menu selected.",debug=True)
	
    class FileMenu(Menu):
        template = "FileMenu"
		
        def __init__(self, *args):
            super().__init__(*args)

# Class for the Save All dialogue       
# TBD This doesn't work on Tone pane due to id relationships     
class SaveAll(SaveAs):
    template = "SaveAll"
    
    def __init__(self, *args):
        super().__init__(*args)
        Reporter.print("RLook: Created SaveAll. id={hex(self.id)}",debug=True)
        
    @toolbox_handler(tbox.SaveAsAboutToBeShownEvent)
    def about_to_show(self, event, id_block, poll_block):
         
        if self.id != id_block.self.id:
             return False # pass on event to next handler
        
        self.file_name = os.path.basename(toolbox.get_object(id_block.ancestor.id).filename)\
                         +"_Export"
     
    @toolbox_handler(SaveToFileEvent)
    def save_to_file(self, event, id_block, poll_block):
        # This should be the only one to use this event but check anyway
        if self.id != id_block.self.id:
            return False # pass on event to next handler

        parent_win = toolbox.get_object(id_block.ancestor.id)     
        
        save_temp = poll_block.filename.decode('utf-8')
        try:
            os.mkdir(save_temp)
            parent_win.disk.export_disk_report(save_temp+".Report/txt")
            # This takes several seconds during which the system appears to freeze.
            # This needs to be dealt with.
            for i in range(0,32):
                newfile = save_temp+"."+\
                          rlook.tone_filename(i,parent_win.disk.tones[i].lookup("NAME"))
                parent_win.disk.export_wav(i,newfile)
                swi.swi("OS_File","isI",18,newfile,0xfb1) # Set file type
        except Exception as e:
            Reporter.print(f"RLook: Something went wrong trying to save files: {e}")
            self.file_save_completed(save_temp, False) # TODO may not be clear enough
            return True # bail
            
        self.file_save_completed(save_temp, True)
            
        return True
        
    # This is called after save is reported complete. This is unused for now.
    @toolbox_handler(SaveCompletedEvent)
    def save_completed(self, event, id_block, poll_block):
        if self.id != id_block.self.id:
            return False
        
        return True
			
# Class for the Save Report dialogue
class SaveReport(SaveAs):
    template = "SaveReport"
	
    def __init__(self, *args):
        super().__init__(*args)
        Reporter.print("RLook: Created SaveReport. id={hex(self.id)}",debug=True)
		
    @toolbox_handler(tbox.SaveAsAboutToBeShownEvent)
    def about_to_show(self, event, id_block, poll_block):        
        if self.id != id_block.self.id:
            return False # pass on event to next handler
		
        disk = toolbox.get_object(id_block.ancestor.id).disk
        buf = io.BytesIO()
        for key,value in disk.function.values.items():
            buf.write(bytes(f"{key}: {value}\n","utf-8"))
        for key,value in disk.midi.values.items():
            buf.write(bytes(f"{key}: {value}\n","utf-8"))
        for patch in disk.patches:
            for key,value in patch.values.items():
                buf.write(bytes(f"{key} {value}\n","utf-8"))
        for tone in disk.tones:
            for key,value in tone.values.items():
                buf.write(bytes(f"{key} {value}\n","utf-8"))
					
        # Do some ctypes gymnastics to get the star address of
        # the data for passing to set_data_address.
        dataptr = ctypes.c_char_p(buf.getvalue())
        addr = ctypes.cast(dataptr,ctypes.c_void_p).value
        size = len(buf.getvalue())
			
        # sic, future-proof
        # I think I can remove this now that it's patched upstream? Double check.
        try:
            self.set_data_addresss(addr,size,0,0)
        except AttributeError:
            self.set_data_address(addr,size,0,0)
			
        buf.close()
        
        return True
