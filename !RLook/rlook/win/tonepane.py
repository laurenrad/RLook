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
import os
import wave
import ctypes
import copy

import rlook
from rlook.reporter import Reporter
import rlook.exceptions as exceptions
import rlook.disk.diskread as diskread
import rlook.disk.formatting as formatting
from rlook.disk.formatting import format_value
import rlook.tbox as tbox
from rlook.tbox import ScrollListPlus
import rlook.draw as draw
import rlook.playit as playit

import riscos_toolbox as toolbox
from riscos_toolbox.objects.window import Window
from riscos_toolbox.gadgets.displayfield import DisplayField
from riscos_toolbox.gadgets.scrolllist import ScrollListSelectionEvent
from riscos_toolbox.gadgets.radiobutton import RadioButton, RadioButtonStateChangedEvent
from riscos_toolbox.objects.saveas import SaveAs, SaveToFileEvent, SaveCompletedEvent
from riscos_toolbox.events import toolbox_handler, wimp_handler
from riscos_toolbox.mixins.window import UserRedrawMixin

class ToneNav(Window):
    template = "ToneNav"

class ToneMain(tbox.WindowNestedMixin,Window):
    template = "ToneMain"
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # Set up gadgets
        self.g_name = DisplayField(self,0x01)
        self.g_orig_tone = DisplayField(self,0x03)
        self.g_orig_key = DisplayField(self,0x04)
        self.g_level = DisplayField(self,0x08)
        self.g_fine_tune = DisplayField(self,0x0A)
        self.g_pitch_follow = DisplayField(self,0x0B)
        self.g_start_segment = DisplayField(self,0x0E)
        self.g_length = DisplayField(self,0x10)
        self.g_frequency = DisplayField(self,0x16)
        self.g_wave_bank = DisplayField(self,0x17)
        self.g_p_lfo_depth = DisplayField(self,0x18)
        self.g_output_assign = DisplayField(self,0x19)
        self.g_tvf = DisplayField(self,0x1A)
        self.g_after_touch = DisplayField(self,0x1C)
        self.g_shift = DisplayField(self,0x1E)
        self.g_pitch_bender = DisplayField(self,0x20)
        Reporter.print(f"RLook: Created ToneMain. id={hex(self.id)}",debug=True)
        
    def load_tone(self, tone, fmt):
        val = tone.lookup("NAME")
        if val != None:
            self.g_name.value = format_value("NAME",val,fmt)
            
        Reporter.print(f"RLook: Fix ORIG/SUB TONE!")
        val = tone.lookup("ORIG/SUB TONE") #TBD THIS DOESN'T WORK
        if val != None:
            self.g_orig_tone.value = format_value("ORIG/SUB TONE",val,fmt)
            
        val = tone.lookup("ORIG KEY NUMBER")
        if val != None:
            self.g_orig_key.value = format_value("ORIG KEY NUMBER",val,fmt)
            
        val = tone.lookup("LEVEL")
        if val != None:
            self.g_level.value = format_value("LEVEL",val,fmt)
            
        val = tone.lookup("FINE TUNE")
        if val != None:
            self.g_fine_tune.value = format_value("FINE TUNE",val,fmt)
            
        val = tone.lookup("PITCH FOLLOW")
        if val != None:
            self.g_pitch_follow.value = format_value("PITCH FOLLOW",val,fmt)
            
        val = tone.lookup("WAVE SEGMENT TOP")
        if val != None:
            self.g_start_segment.value = format_value("WAVE SEGMENT TOP",val,fmt)
        
        val = tone.lookup("WAVE SEGMENT LENGTH")
        if val != None:
            self.g_length.value = format_value("WAVE SEGMENT LENGTH",val,fmt)
        
        val = tone.lookup("FREQUENCY")
        if val != None:
            self.g_frequency.value = format_value("FREQUENCY",val,fmt)
            
        val = tone.lookup("WAVE BANK")
        if val != None:
            self.g_wave_bank.value = format_value("WAVE BANK",val,fmt)
            
        val = tone.lookup("OSC LFO DEPTH")
        if val != None:
            self.g_p_lfo_depth.value = format_value("OSC LFO DEPTH",val,fmt)
            
        val = tone.lookup("TONE OUTPUT ASSIGN")
        if val != None:
            self.g_output_assign.value = format_value("TONE OUTPUT ASSIGN", val,fmt)
            
        val = tone.lookup("TVF SWITCH")
        if val != None:
            self.g_tvf.value = format_value("TVF SWITCH",val,fmt)
            
        val = tone.lookup("AFTER TOUCH SWITCH")
        if val != None:
            self.g_after_touch.value = format_value("AFTER TOUCH SWITCH",val,fmt)
            
        val = tone.lookup("TRANSPOSE")
        if val != None:
            self.g_shift.value = format_value("TRANSPOSE",val,fmt)
            
        val = tone.lookup("BENDER SWITCH")
        if val != None:
            self.g_pitch_bender.value = format_value("BENDER SWITCH",val,fmt)
    
class ToneLoop(tbox.WindowNestedMixin,Window):
    template = "ToneLoop"
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # Set up gadgets
        self.g_mode = DisplayField(self,0x01)
        self.g_tune = DisplayField(self,0x03)
        self.g_start = DisplayField(self,0x05)
        self.g_length = DisplayField(self,0x07)
        self.g_loop = DisplayField(self,0x09)
        self.g_end = DisplayField(self,0x0B)
        
        Reporter.print(f"RLook: Created ToneLoop. id={hex(self.id)}",debug=True)
        
    def load_tone(self, tone, fmt):
        val = tone.lookup("LOOP MODE")
        if val != None:
            self.g_mode.value = format_value("LOOP MODE",val,fmt)
            
        val = tone.lookup("LOOP TUNE")
        if val != None:
            self.g_tune.value = format_value("LOOP TUNE",val,fmt)
            
        val = tone.lookup("START POINT")
        if val != None:
            self.g_start.value = format_value("START POINT",val,fmt)
            
        val = tone.lookup("LOOP LENGTH")
        if val != None:
            self.g_length.value = format_value("LOOP LENGTH",val,fmt)
    
        val = tone.lookup("LOOP POINT")
        if val != None:
            self.g_loop.value = format_value("LOOP POINT",val,fmt)
            
        val = tone.lookup("END POINT")
        if val != None:
            self.g_end.value = format_value("END POINT",val,fmt)
    
class ToneLFO(tbox.WindowNestedMixin,Window):
    template = "ToneLFO"
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # Set up gadgets
        self.g_rate = DisplayField(self,0x01)
        self.g_sync = DisplayField(self,0x03)
        self.g_mode = DisplayField(self,0x04)
        self.g_delay = DisplayField(self,0x06)
        self.g_offset = DisplayField(self,0x08)
        self.g_polarity = DisplayField(self,0x0A)
        Reporter.print(f"RLook: Created ToneLFO. id={hex(self.id)}",debug=True)
        
    def load_tone(self, tone, fmt):        

        val = tone.lookup("LFO RATE")
        if val != None:
            self.g_rate.value = format_value("LFO RATE",val,fmt)
            
        val = tone.lookup("LFO SYNC")
        if val != None:
            self.g_sync.value = format_value("LFO SYNC",val,fmt)
            
        val = tone.lookup("LFO MODE")
        if val != None:
            self.g_mode.value = format_value("LFO MODE",val,fmt)
            
        val = tone.lookup("LFO DELAY")
        if val != None:
            self.g_delay.value = format_value("LFO DELAY",val,fmt)
            
        val = tone.lookup("LFO OFFSET")
        if val != None:
            self.g_offset.value = format_value("LFO OFFSET",val,fmt)
            
        val = tone.lookup("LFO POLARITY")
        if val != None:
            self.g_polarity.value = format_value("LFO POLARITY",val,fmt)
    
class ToneTVF(tbox.WindowNestedMixin,Window):
    template = "ToneTVF"
    
    # Create multiple DisplayFields at once from a list of components. Return a list
    def _create_displayfields(self, components):
        gadgets = []
        for component in components:
            gadgets.append(DisplayField(self,component))
            
        return gadgets
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # Set up gadgets
        self.g_cutoff = DisplayField(self,0x01)
        self.g_resonance = DisplayField(self,0x03)
        self.g_keyfollow = DisplayField(self,0x04)
        self.g_lfodepth = DisplayField(self,0x07)
        self.g_lcurve = DisplayField(self,0x08)
        self.g_eg_depth = DisplayField(self,0x0A)
        self.g_eg_pol = DisplayField(self,0x0D)
        self.g_keyrate = DisplayField(self,0x0F)
        self.g_velrate = DisplayField(self,0x11)
        self.g_sus = DisplayField(self,0x14)
        self.g_end = DisplayField(self,0x16)
        self.g_rate = self._create_displayfields([0x17,0x18,0x19,0x1A,0x1B,0x1C,0x1D,0x1E])
        self.g_level = self._create_displayfields([0x1F,0x20,0x21,0x22,0x23,0x24,0x25,0x26])
        Reporter.print(f"RLook: Created ToneTVF. id={hex(self.id)}",debug=True)
         
    def load_tone(self, tone, fmt):
        val = tone.lookup("TVF CUT OFF")
        if val != None:
            self.g_cutoff.value = format_value("TVF CUT OFF",val,fmt)
        
        val = tone.lookup("TVF RESONANCE")
        if val != None:
            self.g_resonance.value = format_value("TVF RESONANCE",val,fmt)
            
        val = tone.lookup("TVF KEY FOLLOW")
        if val != None:
            self.g_keyfollow.value = format_value("TVF KEY FOLLOW",val,fmt)
            
        val = tone.lookup("TVF LFO DEPTH")
        if val != None:
            self.g_lfodepth.value = format_value("TVF LFO DEPTH",val,fmt)
            
        val = tone.lookup("TVF LEVEL CURVE")
        if val != None:
            self.g_lcurve.value = format_value("TVF LEVEL CURVE",val,fmt)
            
        val = tone.lookup("TVF EG DEPTH")
        if val != None:
            self.g_eg_depth.value = format_value("TVF EG DEPTH",val,fmt)
            
        val = tone.lookup("TVF EG POLARITY")
        if val != None:
            self.g_eg_pol.value = format_value("TVF EG POLARITY",val,fmt)
            
        val = tone.lookup("TVF KEY RATE FOLLOW")
        if val != None:
            self.g_keyrate.value = format_value("TVF KEY RATE FOLLOW",val,fmt)
            
        val = tone.lookup("TVF VELOCITY RATE FOLLOW")
        if val != None:
            self.g_velrate.value = format_value("TVF VELOCITY RATE FOLLOW",val,fmt)
            
        val = tone.lookup("TVF ENV SUSTAIN POINT")
        if val != None:
            self.g_sus.value = format_value("TVF ENV SUSTAIN POINT",val,fmt)
            
        val = tone.lookup("TVF ENV END POINT")
        if val != None:
            self.g_end.value = format_value("TVF ENV END POINT",val,fmt)
        
        # TVF ENV rate and level need to be unpacked into separate sets first.
        # The formatting function should unpack these into a tuple containing the rate
        # tuple and the level tuple.
        vals = tone.lookup("TVF ENV")
        if vals != None:
            vals = format_value("TVF ENV",vals,fmt)
        for i in range(0,8):
            self.g_rate[i].value = vals[0][i]
            
        for i in range(0,8):
            self.g_level[i].value = vals[1][i]
    
class ToneTVA(tbox.WindowNestedMixin,Window):
    template = "ToneTVA"
    
    # Create multiple DisplayFields at once from a list of components. Return a list
    def _create_displayfields(self, components):
        gadgets = []
        for component in components:
            gadgets.append(DisplayField(self,component))
            
        return gadgets
    
    def __init__(self, *args):
        super().__init__(*args)
        
        # Set up gadgets
        self.g_lfo_depth = DisplayField(self,0x35)
        self.g_level_curve = DisplayField(self,0x36)
        self.g_vel_rate = DisplayField(self,0x37)
        self.g_key_rate = DisplayField(self,0x38)
        self.g_sus = DisplayField(self,0x14)
        self.g_end = DisplayField(self,0x16)
        self.g_rate = self._create_displayfields([0x17,0x18,0x19,0x1A,0x1B,0x1C,0x1D,0x1E])
        self.g_level = self._create_displayfields([0x1F,0x20,0x21,0x22,0x23,0x24,0x25,0x26])
        Reporter.print(f"RLook: Created ToneTVA. id={hex(self.id)}")
        
    def load_tone(self, tone, fmt):
        val = tone.lookup("TVA LFO DEPTH")
        if val != None:
            self.g_lfo_depth.value = format_value("TVA LFO DEPTH",val,fmt)
            
        val = tone.lookup("TVA LEVEL CURVE")
        if val != None:
            self.g_level_curve.value = format_value("TVA LEVEL CURVE",val,fmt)
                                                               
        val = tone.lookup("ENV VEL-RATE")
        if val != None:
            self.g_vel_rate.value = format_value("ENV VEL-RATE",val,fmt)
            
        val = tone.lookup("TVA ENV KEY-RATE")
        if val != None:
            self.g_key_rate.value = format_value("TVA ENV KEY-RATE",val,fmt)
            
        val = tone.lookup("TVA ENV SUSTAIN POINT")
        if val != None:
            self.g_sus.value = format_value("TVA ENV SUSTAIN POINT",val,fmt)
            
        val = tone.lookup("TVA ENV END POINT")
        if val != None:
            self.g_end.value = format_value("TVA ENV END POINT",val,fmt)
            
        # TVA ENV rate and level need to be unpacked into separate sets first.
        # The formatting function should unpack these into a tuple containing the rate
        # tuple and the level tuple.
        vals = tone.lookup("TVA ENV")
        if vals != None:
            vals = format_value("TVA ENV",vals,fmt)
        for i in range(0,8):
            self.g_rate[i].value = vals[0][i]
            
        for i in range(0,8):
            self.g_level[i].value = vals[1][i]
          
# This class is for the display showing the waveform of the selected tone and its
# associated loop points. This is perhaps the most subject to change.  
class WaveformView(UserRedrawMixin, tbox.WindowNestedMixin, Window):
    template = "Waveform"
    
    def __init__(self, *args):
        super().__init__(*args)
        self.disk = None
        self.wave = None
        self.start = 0 # Start sample
        self.end = 0 # End sample
        self.loop = 0 # Loop sample
        self.plotter = draw.WaveformPlot(948,300,draw.Point(0,0))
        
    # Called whenever the window is to be redrawn. This is very stupid and inefficient right now.
    def redraw_window(self, visible, scroll, redraw, offset):
        swi.swi("Wimp_SetColour","I",0x80)
        #swi.swi(0x100,"") # CLG
        if (self.disk != None and self.wave != None):
            self.plotter.move(draw.Point(visible.min.x+50,visible.min.y+400))
            self.plotter.plot_border()
            self.plotter.plot_waveform(self.wave)
            self.plotter.plot_start(self.start,len(self.wave))
            self.plotter.plot_end(self.end,len(self.wave))
            self.plotter.plot_loop(self.loop,len(self.wave))
    
    def unload_disk(self):
        self.disk = None    
    
    def load_disk(self, disk):
        self.disk = disk
        self.load_tone(self.disk.tones[0])
        
    def load_tone(self, tone):
        if self.disk != None:
            self.wave = self.disk.convert_wave(tone.number,
                                               use_loop_points=True).tobytes()
            self.start = tone.lookup("START POINT")
            self.end = tone.lookup("END POINT")
            self.loop = tone.lookup("LOOP POINT")
            self.force_redraw()
            
    def set_func(self, func):
        if func == 0:
            self.func = draw.plot_waveform
        elif func == 1:
            self.func = draw.plot_waveform2
        self.force_redraw()

# Main tone pane. This is marked as an ancestor object so SaveAs can get info from it.
class TonePane(tbox.WindowNestedMixin,Window):
    template = "ToneTab"
    
    # Gadget component IDs for this window
    # This will work on the assumption that component IDs are contiguous.
    #G_TONE_START = 0x00 # Start component - tone I11
    G_TONE_LIST = 0x00
    G_MAIN = 0x04
    G_LOOP = 0x05
    G_LFO = 0x06
    G_TVF = 0x07
    G_TVA = 0x08
    G_WAVE = 0x09
    
    def __init__(self, *args):
        super().__init__(*args)
        self.disk = None
        
        Reporter.print(f"RLook: TonePane Created. id={hex(self.id)}")
        
        # Set up gadgets and child objects
        self.g_tonelist = ScrollListPlus(self,TonePane.G_TONE_LIST)
        self.tone_lfo = toolbox.create_object(ToneLFO.template,ToneLFO)
        self.tone_loop = toolbox.create_object(ToneLoop.template,ToneLoop)
        self.tone_main = toolbox.create_object(ToneMain.template,ToneMain)
        self.tone_tva = toolbox.create_object(ToneTVA.template,ToneTVA)
        self.tone_tvf = toolbox.create_object(ToneTVF.template,ToneTVF)
        self.tone_saveas = toolbox.create_object(SaveSample.template,SaveSample)
        self.waveform = toolbox.create_object(WaveformView.template,WaveformView)
            
        # Set multisel on the ScrollList, but the behavior here isn't super coherent yet.
        self.g_tonelist.multisel = 1

    # Remove reference to disk object.    
    # This would also remove child windows, but as mentioned elsewhere,
    # this is broken in the library currently.    
    def unload_disk(self):
        self.waveform.unload_disk()
        self.disk = None
        #toolbox.delete_object(self.tone_lfo.id)
        #toolbox.delete_object(self.tone_loop.id)
        #toolbox.delete_object(self.tone_main.id)
        #toolbox.delete_object(self.tone_tva.id)
        #toolbox.delete_object(self.tone_tvf.id)
        #toolbox.delete_object(self.tone_saveas.id)
        #toolbox.delete_object(self.waveform.id)
        
    def load_disk(self, disk):
        self.disk = disk
        fmt = disk.format
        Reporter.print("RLook: Tone pane is loading disk.",debug=True)
        # Show the main pane by default
        pane_bounds = self._get_pane_bounds()
        self.tone_main.show_nested(*pane_bounds,0,0,self,0x800000)
        
        for i in range(0,32):
            tname = disk.tones[i].lookup("NAME")
            tnum = formatting.roland_number(i)
            self.g_tonelist.add_item(tnum+" "+tname,-1)
            
        # Select the first tone and load the panes with it.
        self.g_tonelist.select_item(0)
        self.load_tone(self.disk.tones[0],self.disk.format)
        self.waveform.load_disk(self.disk)
            
    # Play the selected tone. For now, only one tone can be selected,
    # so just figure out which one it is         
    def play_tone(self):
        selected = self.g_tonelist.get_selected()
        
        if self.disk != None:
            os.path.exists
            tmpfile = rlook.tempdir.name+"."+str(self.id)+str(selected)+"/wav"
            # if the wav file isn't already created, create it
            if not os.path.exists(tmpfile):
                self.disk.export_wav(selected,tmpfile,False)
            playit.play(tmpfile)

      # Get the placement of the main window and return an offset for showing the tone panes.
    def _get_pane_bounds(self):
        b = swi.block(32)
        b[0] = self.wimp_handle
        swi.swi("Wimp_GetWindowState",".bi",b,0x4B534154)
        return [b[1]+400,b[2],b[3],b[4]-80]
            
    # The next set of functions are to be used by the parent window to show the child panes
    def show_main(self):
        pane_bounds = self._get_pane_bounds()
        self.tone_main.show_nested(*pane_bounds,0,0,self,0x8000000)
        
    def show_loop(self):
        pane_bounds = self._get_pane_bounds()
        self.tone_loop.show_nested(*pane_bounds,0,0,self,0x800000)
        
    def show_lfo(self):
        pane_bounds = self._get_pane_bounds()
        self.tone_lfo.show_nested(*pane_bounds,0,0,self,0x800000)
        
    def show_tvf(self):
        pane_bounds = self._get_pane_bounds()
        self.tone_tvf.show_nested(*pane_bounds,0,0,self,0x800000)
        
    def show_tva(self):
        pane_bounds = self._get_pane_bounds()
        self.tone_tva.show_nested(*pane_bounds,0,0,self,0x800000)
        
    def show_wave(self):
        pane_bounds = self._get_pane_bounds()
        self.waveform.show_nested(*pane_bounds,0,0,self,0x800000)
        self.waveform.force_redraw()
        
    # Return selected tone.
    def selected_tone(self):
        return self.g_tonelist.get_selected()
            
    # Update all child panes when a new tone is selected.
    def load_tone(self, tone, format):
        self.tone_lfo.load_tone(tone,format)
        self.tone_loop.load_tone(tone,format)
        self.tone_main.load_tone(tone,format)
        self.tone_tva.load_tone(tone,format)
        self.tone_tvf.load_tone(tone,format)
        self.waveform.load_tone(tone)
        
    # Handler for tone selection ScrollList.
    @toolbox_handler(ScrollListSelectionEvent)
    def tone_selected(self, event, id_block, poll_block):
        self.load_tone(self.disk.tones[poll_block.item],self.disk.format)
    
class SaveSample(SaveAs):
    template = "SaveSample"
    
    def __init__(self, *args):
        super().__init__(*args)
        Reporter.print(f"RLook: Created SaveSample. id={hex(self.id)}",debug=True)
        
        
    # SaveAs_AboutToBeShownEvent - not implemented in riscos_toolbox
    # When the SaveAs window is shown, generate a buffer with the wave file
    # and set the address.
    @toolbox_handler(tbox.SaveAsAboutToBeShownEvent)
    def about_to_show(self, event, id_block, poll_block):
    
        if self.id != id_block.self.id:
            return False
    
        # First, get the ancestor tone pane. It has the disk.
        tonepane = toolbox.get_object(id_block.ancestor.id)
        selected = tonepane.selected_tone()
        
        # Set default filename to the tone name, formatted and sanitized
        tone_name = tonepane.disk.tones[selected].lookup("NAME")
        self.file_name = rlook.tone_filename(selected, tone_name)
        
        # Get a buffer containing the wave file, and do some
        # ctypes gymnastics to get the actual start address
        # of the data as an int, which is needed to pass to 
        # set_data_address.
        wav_out = tonepane.disk.get_wav(selected)
        dataptr = ctypes.c_char_p(wav_out)
        addr = ctypes.cast(dataptr,ctypes.c_void_p).value
        
        # sic, future-proof for when typo fixed
        try: 
            self.set_data_addresss(addr,len(wav_out),0,0)
        except AttributeError:
            self.set_data_address(addr,len(wav_out),0,0)
            
        return True
            
            