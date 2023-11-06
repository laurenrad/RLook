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

# Stuff for playing and handling wave samples using disksample

import tempfile
import os
import swi
import time

from .reporter import Reporter

# SWI Constants
XBIT                = 0x20000
DISKSAMPLE_VERSION         = 0x52EC0 | XBIT
DISKSAMPLE_CONFIGURE         = 0x52EC1 | XBIT       
DISKSAMPLE_FILEOPEN         = 0x52EC2 | XBIT
DISKSAMPLE_STREAMCLOSE      = 0x52EC3 | XBIT
DISKSAMPLE_STREAMCREATE     = 0x52EC4 | XBIT
DISKSAMPLE_STREAMSOURCE     = 0x52EC5 | XBIT
DISKSAMPLE_STREAMRECEIVER       = 0x52EC6 | XBIT
DISKSAMPLE_DECODING        = 0x52EC7 | XBIT
DISKSAMPLE_STREAMPLAY        = 0x52EC8 | XBIT
DISKSAMPLE_STREAMPAUSE        = 0x52EC9 | XBIT
DISKSAMPLE_STREAMSTOP        = 0x52ECA | XBIT
DISKSAMPLE_STREAMPOSITION    = 0x52ECB | XBIT
DISKSAMPLE_STREAMVOLUME        = 0x52ECC | XBIT
DISKSAMPLE_STREAMISREADY    = 0x52ECD | XBIT
DISKSAMPLE_STREAMSTATUS        = 0x52ECE | XBIT
DISKSAMPLE_STREAMCHAIN        = 0x52ECF | XBIT
DISKSAMPLE_STREAMINFO        = 0x52ED0 | XBIT
DISKSAMPLE_STREAMTEXTS        = 0x52ED1 | XBIT
DISKSAMPLE_STREAMPARAM        = 0x52ED2 | XBIT
DISKSAMPLE_STREAMDECODING    = 0x52ED3 | XBIT
DISKSAMPLE_CHANNELPARAMS    = 0x52ED4 | XBIT
DISKSAMPLE_CHANNELSTATUS    = 0x52ED5 | XBIT
XBIT                = 0x20000

# Other DiskSample constants
ERROR_STREAM_UNSUPPORTED    = 0x81B000

# TBD
def play(disk):
    tempdir = tempfile.TemporaryDirectory(prefix='TestApp_')
    
    # TBD


# Close all open files to allow RMKill of dsplay
def panic():
    try:
        swi.swi(DISKSAMPLE_CONFIGURE,"i",-1)
    except swi.error as e:
        Reporter.print("An error occurred")
        Reporter.print(repr(e))
        print(repr(e))        

# Play a file using DiskSample
# This works except it doesn't close the file when it's done!    
def playfile(filename):
    try:
        # Create stream and open file
        stream_handle = swi.swi(DISKSAMPLE_STREAMCREATE,"ii;i",0,64)
        Reporter.print("stream created")
        swi.swi(DISKSAMPLE_STREAMRECEIVER,"iii",stream_handle,0,0) # internal player
        swi.swi(DISKSAMPLE_STREAMSOURCE,"iis",stream_handle,1,filename)
        
        #swi.swi(DISKSAMPLE_STREAMSTATUS,"iii",stream_handle,0x8,0x8) # no loop
        # Open stream from file
        #stream_handle = swi.swi(DISKSAMPLE_FILEOPEN,"s;i","orchhit8")
        
        Reporter.print(f"After opening, stream handle is {stream_handle}")
    
        
        # Wait up to 1 second for stream to be ready (worst case scenario)
        #stream_ready = swi.swi(DISKSAMPLE_STREAMISREADY,"i;i",stream_handle)
        status = swi.swi(0x52ECE,"iii;i",stream_handle,0,0) # 0x52ECE = stream status
        
        start = time.time() 
        while (time.time() - start < 1) and (status & 1):
            #stream_ready = swi.swi(DISKSAMPLE_STREAMISREADY,"i;i",stream_handle)
            status = swi.swi(0x52ECE,"iii;i",stream_handle,0,0)
        print(f"stream_ready {status}") # THIS IS JUST RETURNING STREAM HANDLE??? WHY????    
        if not (status & 1):
            Reporter.print("Stream timed out")
            return # Quit if the stream isn't ready TBD real error handling
        Reporter.print("Ready to play")
        swi.swi(DISKSAMPLE_STREAMSTATUS,"iii",stream_handle,0x8,0x8) # no loop        
        
        swi.swi(DISKSAMPLE_STREAMPLAY,"i",stream_handle) # begin playback
        
        Reporter.print("Playback started")
        
        # Wait for stream to finish
        status = 2
        start = time.time() # timeout for debug
        while (status & 2) and (time.time() - start < 3):
            status = swi.swi(DISKSAMPLE_STREAMSTATUS,"iii;i",stream_handle,0,0)
            Reporter.print(f"status: {status}")
            
        
        #start = time.time()
        #stream_status = swi.swi(DISKSAMPLE_STREAMSTATUS,"iii;i",stream_handle,0,0)
        #Reporter.print("first stream status is "+repr(stream_status))
        #stream_status = 2
        #while (stream_status & 2) != 0:
        #    stream_status = swi.swi(DISKSAMPLE_STREAMSTATUS,"iii;i",stream_handle,0,0)
        #    Reporter.print("stream status: "+repr(stream_status))
        #    if time.time() - start > 5:
        #        break # DEBUG: time out if this fails to stop
        #Reporter.print("Stream finished")
        
        # Close the stream (and the file)
        if stream_handle != -1:
            swi.swi(DISKSAMPLE_STREAMCLOSE,"i",stream_handle)
        
    except swi.error as e:
        Reporter.print("An error occurred")
        Reporter.print(repr(e))
        print(repr(e))
        return # just fail silently other than reporter output for now
        
    
