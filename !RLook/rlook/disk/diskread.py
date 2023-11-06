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
RLook: diskread.py
This module contains classes representing the data on a 12-bit sample disk
and associated methods for reading and exporting this data.
This module serves as the primary backend for RLook. (This is the standalone version).
If ran as __main__, this module will read the example disk image into Disk d.
"""

import struct
import wave
import audioop # Warning: deprecated
import os
import io # For convert_wave
from rlook.reporter import Reporter
from .exceptions import *
from . import formats

# Globals
# Maximum filesize to prevent loading excessively large files into memory.
# This is set to 2MB to give some leeway to check the format
MAX_FILE_SIZE = 2000000

# Set up a quick function for debug output to console/reporter/log
def tee(s):
    REPORTER_ON = True
    CONSOLE_ON = False
    if REPORTER_ON:
        Reporter.print(s)
    if CONSOLE_ON:
        print(s)    
    
class ParamBlock:
    """
    Parent class for a block of parameters on disk.
    What these blocks currently all have in common is essentially a block
    format, a dict containing values, and a starting address.
    """
    def __init__(self,block_fmt,block_addr):
        self.values = {}
        self.block_fmt = block_fmt
        self.addr = block_addr

    def read(self, img):
        """
        Read block data from disk. This will be overridden by subclasses
        which have multiple instances, like tones and patches.
        """
        b = DiskBytes(img,self.addr) # Create buffer at starting address to read from

        # Read the parameter data in according to the format definition
        b.read_params(self.values, self.block_fmt)

    def get_name(self) -> str:
        """
        Return the block's name, for use by named subclasses (Tone and Patch).
        This will result in a KeyError exception if called on a ParamBlock
        object without a name.
        """
        return self.values['NAME']

    def lookup(self, key:str):
        """
        Returns the value of a parameter specified by key, or None if not found.
        """
        return self.values.get(key)

    def print(self):
        """DEBUG: Dump all values stored from disk."""
        for k in self.values.keys():
            tee(f'{k}:\t\t\t{self.values[k]}')

class Tone(ParamBlock):
    """
    This class represents parameter data for a single tone.
    For now at least, this does not store wave data, because all wave data is
    stored together at the end of the disk and storing it per tone would
    increase complexity a great deal. Instead, wave data is stored in a disk
    object.
    """
    def read(self, img, number:int, size:int):
        """
        Read a single tone from disk.
        """
        self.number = number
        self.addr = self.addr + size*self.number # calculate tone addr and update field
        ParamBlock.read(self,img) # call parent read function now that addr is updated

        # The sample rate / sampling frequency parameter is actually used by
        # the backend, so it will be converted and stored as a usable value.
        # 0 = 30KHz, 1 = 15KHz
        self.values['FREQUENCY'] = 15000 if self.values['FREQUENCY'] else 30000

    def length(self):
        """Return the length of the tone in wave segments (0-18)."""
        return self.values['WAVE SEGMENT LENGTH']

class Patch(ParamBlock):
    """
    This class represents parameter data for a single patch.
    """
    def read(self, img, number:int, size:int):
        self.number = number
        self.addr = self.addr + size*self.number # calculate patch addr and update field
        ParamBlock.read(self,img) # call parent read function now that addr is updated

    def tone_list(self) -> set:
        """
        Return a set of linked tones, defined as all unique entries in the
        Tone to Key parameters.
        """
        return set(self.values['TONE TO KEY 1'] + self.values['TONE TO KEY 2'])


class DiskBytes:
    """
    This is a class to provide a buffer to a bytes object representing
    a sample disk image.

    This class implements a pop function, making it easy to read through a
    disk image stored in a bytes object and interpret one parameter at a time
    without having to open the file again or keep track of the offset.

    Additional methods relevant to reading bytes off disk can be implemented
    as needed.
    """

    def __init__(self,bytesobject,offset_start=0,offset_end=None):
        """Constructor takes a bytes object and an optional start offset."""
        self._view = memoryview(bytesobject[offset_start:offset_end])

    def pop(self,n: int) -> bytes:
        """Pop n bytes from contents and return them."""
        # store the bytes to be popped off and advance the view n bytes
        result, self._view = (self._view[:n].tobytes(),
                              self._view[n:])
        return result # return the popped bytes

    def skip(self,n: int):
        """Skip ahead n bytes in the buffer."""
        self._view = self._view[n:] # advance the view n bytes

    def contents(self) -> bytes:
        """Return all remaining buffer contents as a bytes object."""
        return self._view.tobytes()

    def read_params(self, values: dict, fmt: tuple):
        """
        Reads parameter data in according to the format definition provided
        and places it in the passed in values dict.
        """

        for param in fmt:
            pname = param['name']
            if param['type'] == 'int':
                values[pname] = int.from_bytes(self.pop(param['size']),byteorder='big',signed=False)
            elif param['type'] == 'signed_int':
                values[pname] = int.from_bytes(self.pop(param['size']),byteorder='big',signed=True)
            elif param['type'] == 'multi':
                fmt = str(param['size']) + 'b' # format string for struct.unpack
                values[pname] = struct.unpack(fmt,self.pop(param['size']))
            elif param['type'] == 'ascii':
                values[pname] = self.pop(param['size']).decode('ascii')
            elif param['type'] == 'raw':
                # for values that need to be unprocessed for formatting
                values[pname] = self.pop(param['size'])
            elif param['type'] == 'dummy':
                self.skip(param['size'])
            else:
                pass # TODO error handling

class Disk:
    """
    This class represents a 12-bit sample disk and provides method(s) to
    extract its wave data.
    """
    # some constants
    SEGMENT_SIZE = 18432 # number of bytes in a segment
    BANK_SIZE = 331776  # number of bytes in a wave bank

    def __init__(self, filename):
        """
        Create a Disk object from an image file specified in a given filename.
        This will also create associated Tone, Patch, MidiParams, and
        FunctionParams objects.
        """
        self.patches = [] # list of patches
        self.tones = [] # list of tones
        self.filename = filename # name of disk image file

        # Check for excessively large file first
        if os.path.getsize(filename) > MAX_FILE_SIZE:
            raise FileSizeError()

        with open(filename,'rb') as disk:
            # read in the full image for params, but it's easier to get wave
            # and system data from the file while it's open here
            img = disk.read() # full image

            # an exception will be raised here if this fails
            self.format = formats.check(img) # check disk format

            if len(img) != 737280:
                tee(f'Bad disk image size: {len(img)} bytes.')

            # system data - read in raw
            disk.seek(0) # back to the start to get system
            self.sys = disk.read(64512) # at start of disk
            tee(f'Read {len(self.sys)} bytes system data.')

            # get disk system ver string
            # This is 32 bytes, starting at offset 32. but the last byte
            # seems to be an end of string marker (0xFE) so it will be omitted
            try:
                self.os_ver = self.sys[32:63].decode('ascii')
                self.os_ver = " ".join(self.os_ver.split()) # Remove duplicate whitespace
                tee(f'System version: {self.os_ver}')
            except Exception as E:
                tee(f'Unable to decode version string! ({E})')

            # wave data - read in raw
            disk.seek(73728) #  wave data starts here
            self.wave = disk.read(663552)
            tee(f'Read {len(self.wave)} bytes wave data.')

        # Function data
        #self.function = FunctionParams(self.img,self.format) # function parameters
        self.function = ParamBlock(self.format.func_fmt,68608) # function parameters
        self.function.read(img) # read from image
        tee(f'Read function parameters from disk.')

        # MIDI data
        #self.midi = MidiParams(self.img,self.format) # midi parameters
        self.midi = ParamBlock(self.format.midi_fmt,68832) # MIDI parameters
        self.midi.read(img) # read from image
        tee(f'Read MIDI parameters from disk.')

        # Patches
        for i in range(0,self.format.PATCH_COUNT):
            # create a patch object and read the data into it
            p = Patch(self.format.patch_fmt,self.format.PATCHES_OFFSET)
            p.read(img,i,self.format.PATCH_SIZE)
            self.patches.append(p)
        tee(f'Read {len(self.patches)} patches from disk.')

        # Tones
        for i in range(0,self.format.TONE_COUNT):
            # create a tone object and read the data into it
            t = Tone(self.format.tone_fmt,self.format.TONES_OFFSET)
            t.read(img,i,self.format.TONE_SIZE)
            self.tones.append(t)
        tee(f'Read {len(self.tones)} tones from disk.')
        tee('Done reading disk.')

    def __del__(self):
        pass # placeholder

    def get_wave_count(self) -> int:
        """
        Return the number of samples (non-empty tones) on a disk.
        """
        total = 0
        for tone in self.tones:
            if tone.length() != 0:
                total += 1
        return total

    def get_wave_start(self, num:int) -> int:
        """
        Return the start address of a given tone's wave sample.
        """
        tone_bank = self.tones[num].values['WAVE BANK']
        tone_seg = self.tones[num].values['WAVE SEGMENT TOP']

        tone_addr = 0 # base address of wave data
        if tone_bank == 1: #if bank B, add size of bank A (330156 bytes)
            tone_addr += self.BANK_SIZE

        tone_addr += (self.SEGMENT_SIZE * tone_seg) # 18342 bytes per segment, 18 segments per bank
        return tone_addr

    def get_wave_end(self, num:int) -> int:
        """
        Return the end address of a given tone's wave sample.
        """
        tone_addr = self.get_wave_start(num)
        tone_length = self.tones[num].length()
        end_addr = tone_addr + (self.SEGMENT_SIZE * tone_length) # address of next segment after tone
        return end_addr

    def export_disk_report(self, filename:str):
        """
        Export a report containing unformatted parameter info to a text
        file. This will not export dummy data which is not read in.
        """
        with open(filename, 'w') as outfile:
            outfile.write("Function Data:\n")
            for key,value in self.function.values.items():
                outfile.write(f"{key}:  {value}\n")

            outfile.write("\nMIDI Data:\n")
            for key,value in self.midi.values.items():
                outfile.write(f"{key}:  {value}\n")

            outfile.write("\nPatch Data:\n")
            for patch in self.patches:
                for key,value in patch.values.items():
                    outfile.write(f"{key}:  {value}\n")
                outfile.write("\n")

            outfile.write("\nTone Data:\n")
            for tone in self.tones:
                for key,value in tone.values.items():
                    outfile.write(f"{key}:  {value}\n")
                outfile.write("\n")

    def convert_wave(self, num:int, use_loop_points:bool=False) -> bytes:
        """
        Convert wave sample of a tone to 16-bit PCM, 44.1KHz.
        Returns a bytes buffer of the result.
        If use_loop_points is true, use the start and end points of
        the Tone.
        """
        # Constants
        FRAMERATE_OUT = 44100 # output sample rate
        WIDTH_OUT = 2 # 16-bit (2 bytes)
        CHANNELS_OUT = 1 # mono

        tone_bank = self.tones[num].values['WAVE BANK']
        tone_seg = self.tones[num].values['WAVE SEGMENT TOP']
        tone_length = self.tones[num].length()
        tone_freq = self.tones[num].values['FREQUENCY']
        loop_start = self.tones[num].values['START POINT']
        loop_end = self.tones[num].values['END POINT']

        # calculate location of tone's wave data on disk
        tone_addr = 0 # base address of wave data

        if tone_bank == 1: #if bank B, add size of bank A (330156 bytes)
            tone_addr += self.BANK_SIZE

        tone_addr += (self.SEGMENT_SIZE * tone_seg) # 18342 bytes per segment, 18 segments per bank
        end_addr = tone_addr + (self.SEGMENT_SIZE * tone_length) # addr of next segment after tone

        wave_view = DiskBytes(self.wave,tone_addr,end_addr) # memoryview access to wave data

        result = io.BytesIO(b'') # Create a buffer to write the results to

        frag_state = None # fragment state for audioop.ratecv to pass to next call
        samples_read = 0
        while tone_addr < end_addr:
            # wave data is stored as 3-byte chunks, each containing two 12-bit samples
            # in format: A1 A2 A3 B3 B1 B2
            # samples will be shifted left 4 places so 16-bit values are output.

            rawbytes = wave_view.pop(3) # get a chunk
            # make sure we are not getting a partial chunk as this would throw things off
            if len(rawbytes) != 3:
                tee(f'DEBUG: bad chunk size, got chunk of size {len(rawbytes)} at address {tone_addr}')
                break # fail out

            chunk = int.from_bytes(rawbytes, byteorder='big', signed=False)
            # ...
            # for first sample, just mask off lower 12 bits and shift down
            sample_a = (chunk & 0xfff000) >> 8

            # for second, mask off all but lower 12 bits...
            chunk &= 0xfff
            # and move upper 8 bits into position, and set rest to 0
            sample_b = chunk << 8 & 0xff00
            # finally, move lower 4 bits into position in original variable and set rest to 0
            # then, logical 'or' it with the upper 8 to put everything together
            sample_b |= (chunk >> 4 & 0xf0)
            samples_read += 2

            if use_loop_points and (samples_read >= loop_end):
                break # stop processing if end point is reached and use_loop_points is enabled
            else:
                result.write(struct.pack('H',sample_a)) # Write A to buffer
                result.write(struct.pack('H',sample_b)) # Write B to buffer


            tone_addr += 3 # just to keep track of where we are

        #tee(f'Read {samples_read} samples.')
        return result.getbuffer() # Return buffer view

    def resample(self, wavedata, tone_freq):
        """
        Resample wave to 44.1KHz.
        TODO: Rewrite to use buffer.
        """
        # Constants
        FRAMERATE_OUT = 44100 # output sample rate
        WIDTH_OUT = 2 # 16-bit (2 bytes)
        CHANNELS_OUT = 1 # mono
        frag_state = None
        (result,frag_state) = audioop.ratecv(wavedata,WIDTH_OUT,CHANNELS_OUT,
                                       tone_freq,FRAMERATE_OUT,frag_state)
        return result

    def export_wav(self, num:int, filename:str='tmp/wav', use_loop_points:bool=False):
        """
        Encode a wav file from a tone's wave data, and export to a file.
        Outputs to tmp.wav if optional filename is not specified.
        This replaces the previous create_wav method to use the new conversion
        methood, convert_wave.
        If use_loop_points=False
        """
        FRAMERATE_OUT = 44100 # output sample rate
        WIDTH_OUT = 2 # 16-bit (2 bytes)
        CHANNELS_OUT = 1 # mono

        freq = self.tones[num].values['FREQUENCY']
        raw = self.resample(self.convert_wave(num,use_loop_points),freq) # Get resampled PCM
         
        with wave.open(filename,'wb') as wav:
            wav.setnchannels(CHANNELS_OUT) # set number of output channels
            wav.setsampwidth(WIDTH_OUT) # set output sample width
            wav.setframerate(FRAMERATE_OUT) # set output sample rate
            wav.writeframes(raw)
        
    def get_wav(self, num:int, use_loop_points:bool=False):
        """
        Encode a wav file from a tone's wave data, and return it as a bytes object.
        Outputs to tmp.wav if optional filename is not specified.
        This replaces the previous create_wav method to use the new conversion
        methood, convert_wave.
        If use_loop_points=False
        """
        FRAMERATE_OUT = 44100 # output sample rate
        WIDTH_OUT = 2 # 16-bit (2 bytes)
        CHANNELS_OUT = 1 # mono

        freq = self.tones[num].values['FREQUENCY']
        raw = self.resample(self.convert_wave(num,use_loop_points),freq) # Get resampled PCM
        
        buf = io.BytesIO(b'')
        with wave.open(buf,'w') as wavwrite:
            wavwrite.setnchannels(CHANNELS_OUT) # set number of output channels
            wavwrite.setsampwidth(WIDTH_OUT) # set output sample width
            wavwrite.setframerate(FRAMERATE_OUT) # set output sample rate
            wavwrite.writeframes(raw)
            
        buf.flush()
        return buf.getvalue()


if __name__ == '__main__':
    d = Disk('DEV/OUT') # create a test disk
