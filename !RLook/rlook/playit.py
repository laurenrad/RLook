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

# Quick and dirty backend module for PlayIt. 
# Needs proper error handling, among other things.

import swi
import os

# SWI definitions
PlayIt_Version     = 0x4D140
PlayIt_Config      = 0x4D141
PlayIt_LoadDriver  = 0x4D142
PlayIt_DriverInfo  = 0x4D143
PlayIt_SampleInfo  = 0x4D144
PlayIt_Status      = 0x4D145
PlayIt_Volume      = 0x4D146
PlayIt_Open        = 0x4D147
PlayIt_BeginEnd    = 0x4D148
PlayIt_SetPtr      = 0x4D149
PlayIt_Play        = 0x4D14A
PlayIt_Stop        = 0x4D14B
PlayIt_Pause       = 0x4D14C
PlayIt_Balance     = 0x4D14D
PlayIt_PauseAt     = 0x4D14E
PlayIt_VU          = 0x4D14F
PlayIt_ListDrivers = 0x4D150
PlayIt_Identify    = 0x4D151
PlayIt_Queue       = 0x4D152
PlayIt_SetLoop     = 0x4D153
PlayIt_FileInfo    = 0x4D154
PlayIt_ClientOp    = 0x4D155


# Perform any needed module setup first
# Returns True on presumed success, False otherwise
def _playit_setup():
    playit_dir = os.getenv("PlayIt$Path")    # Get the module path
    if playit_dir == None:
        return False

    # Ensure module is loaded
    try:
        swi.swi("OS_Module","is;..i",18,"PlayIt")
    except swi.error as e:
        print("Module Not Loaded "+repr(e)) # Specifically errnum should be 258
    
    try:    
        swi.swi("OS_Module","is",1,playit_dir+"PlayIt")    
    except swi.error as e:
        print("Unable to load module "+repr(e)) # Specific errnum should be 214
        return # TBD: Raise a more useful error
        
    # Check version
    ver = swi.swi(PlayIt_Version,";i")
    if ver < 148:
        print("PlayIt Version too low, 1.48 or greater required")
        return False
    
    # Make sure a driver is loaded
    swi.swi(PlayIt_LoadDriver,"s",playit_dir) # Let PlayIt scan for the best driver
    
    return True
    
# Print some debug information
def debug():
    ver = swi.swi(PlayIt_Version,";i")
    
    print(f"PlayIt module version {ver}")
    

# Attempt to stop all playback
def panic():
    swi.swi(PlayIt_Stop,"")

def play(filename):
    if not _playit_setup(): # set up module if needed
        return # setup failed, quit without playing
    
    try:
        swi.swi(PlayIt_Open,"si;i",filename,0) # auto-detect
    except swi.error as e:
        print("An error occurred trying to open the file: "+repr(e))
        return
    
    swi.swi(PlayIt_Play,"")
    