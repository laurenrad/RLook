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

# Copyright 2023 Lauren Rad
# Quick n Dirty module for using Reporter from Python3.

import swi
import rlook

# Constants for Reporter's SWI numbers.
SWIs = {'Text0': 0x54C80, 'TextS': 0x54C81, 'Regs': 0x54C83, 'Where': 0x54C84, 'Poll': 0x54C85, 'Dump': 0x54C86, 'GetSwiRet': 0x54C87, 'ErrBlk': 0x54C88, 'Quit': 0x54C8A, 'Clear': 0x54C8B, 'Open': 0x54C8C, 'Close': 0x54C8D, 'On': 0x54C8E, 'Off': 0x54C8F, 'CmdOn': 0x54C90, 'CmdOff': 0x54C91, 'Hide': 0x54C92, 'Show': 0x54C93, 'ErrOn': 0x54C94, 'ErrOff': 0x54C95, 'TaskOn': 0x54C96, 'TaskOff': 0x54C97, 'Vdu4On': 0x54C98, 'Vdu4Off': 0x54C99, 'RmaOn': 0x54C9A, 'RmaOff': 0x54C9B, 'TimeOn': 0x54C9C, 'TimeOff': 0x54C9D, 'SrceOn': 0x54C9E, 'SrceOff': 0x54C9F, 'ObeyOn': 0x54CA0, 'ObeyOff': 0x54CA1, 'Push': 0x54CA2, 'Pull': 0x54CA3, 'Pause': 0x54CA4, 'Scroll': 0x54CA5, 'SaveOn': 0x54CA6, 'SaveOff': 0x54CA7, 'LogOn': 0x54CA8, 'LogOff': 0x54CA9}


# internal - very simple error handler for errors from SWI mod.
def _handle_swierr(e):
    if e.errnum == 486:
        pass # silently ignore when Reporter isn't running
    else:
        raise e # raise again to be handled later possibly

class Reporter:


    # print a string to reporter by calling the SWI Text0 (0x054C80).
    # if debug is True, will only print if debug global is set.
    def print(s, debug=False):
        if (not debug) or rlook.debug_enabled:
            try:
                swi.swi(SWIs['Text0'],"s",s)
            except swi.error as swi_err:
                _handle_swierr(swi_err)

    # editor's note: This is where TextS would go, but it's not useful
    # in this context, so it's not implemented.

    # print out the registers 0-9, pc, flags, etc by calling SWI Regs (0x054C82).
    def regs():
        try:
            swi.swi(SWIs['Regs'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # SWI Registers (0x054C83) - not implemented.

    # display the address of the last abort and module info if relevant.
    # SWI "Where", number 0x054C84
    def where():
        try:
            swi.swi(SWIs['Where'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # SWI "Poll", number 0x054C85
    def poll():
        try:
            swi.swi(SWIs['Poll'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # SWI "Dump", number 0x054C86
    def dump(addr,length,width,text):
        try:
            swi.swi(SWIs['Dump'],"iiis",addr,length,width,text)
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # SWI ErrBlk, number 0x054C88 is also not implemented.
    # I may provide a replacement for this later that prints a
    # swi.error pretty.

    # Quit Reporter.
    # SWI "Quit", number 0x054C8A
    def quit():
        try:
            swi.swi(SWIs['Quit'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Clear the Reporter window.
    # SWI "Clear", number 0x054C8B
    def clear():
        try:
            swi.swi(SWIs['Clear'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Open the Reporter window if it has been closed (but not hidden).
    # SWI "Open", number 0x054C8C
    def open_win():
        try:
            swi.swi(SWIs['Open'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Close the Reporter window.
    # SWI "Close", number 0x054C8D
    def close_win():
        try:
            swi.swi(SWIs['Close'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Turn most reporting on / off.
    # I wasn't sure what to call this one...
    # SWIs "On" (0x054C8E) and "Off" (0x054C8F)
    def opt_gen(value):
        try:
            if value == True:
                swi.swi(SWIs['On'],".")
            else:
                swi.swi(SWIs['Off'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Turn on/off reporting for ALL commands.
    # SWIs "CmdOn" (0x054C90) and "CmdOff" (0x054C91)
    def opt_cmd(value):
        try:
            if value == True:
                swi.swi(SWIs['CmdOn'],".")
            else:
                swi.swi(SWIs['CmdOff'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Hide the Reporter window until the Show SWI is called.
    # SWI "Hide", number 0x054C92
    def hide():
        try:
            swi.swi(SWIs['Hide'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Show a previously hidden Reporter window.
    # SWI "Show", number 0x054C93
    def show():
        try:
            swi.swi(SWIs['Show'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Turns reporting on/off for errors.
    # SWIs "ErrOn" (0x054C94) and "ErrOff" (0x054C95)
    def opt_err(value):
        try:
            if value == True:
                swi.swi(SWIs['ErrOn'],".")
            else:
                swi.swi(SWIs['ErrOff'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)


    # Turns reporting on/off for Wimp Task init/closedown.
    # SWIs "TaskOn" (0x054C96) and "TaskOff" (0x054C97)
    def opt_tasks(value):
        try:
            if value == True:
                swi.swi(SWIs['TaskOn'],".")
            else:
                swi.swi(SWIs['TaskOff'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Turns reporting on/off for VDU 4 output.
    # SWIs "Vdu4On" (0x054C98) and "Vdu4Off" (0x054C99)
    def opt_vdu4(value):
        try:
            if value == True:
                swi.swi(SWIs['Vdu4On'],".")
            else:
                swi.swi(SWIs['Vdu4Off'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Turns reporting on/off for RMA Storage events.
    # SWIs "RmaOn" (0x054C9A) and "RmaOff" (0x054C9B)
    def opt_rma(value):
        try:
            if value == True:
                swi.swi(SWIs['RmaOn'],".")
            else:
                swi.swi(SWIs['RmaOff'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Turns timestamps on/off for output.
    # SWIs "TimeOn" (0x054C9C) and "TimeOff" (0x054C9D)
    def opt_timestamps(value):
        try:
            if value == True:
                swi.swi(SWIs['TimeOn'],".")
            else:
                swi.swi(SWIs['TimeOff'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Source on/off option. I don't know what this actually does?
    # SWIs "SrceOn" (0x054C9E) and "SrceOff" (0x054C9F)
    def opt_srce(value):
        try:
            if value == True:
                swi.swi(SWIs['SrceOn'],".")
            else:
                swi.swi(SWIs['SrceOff'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # If this option is enabled, reporting of OS commands is restricted to
    # Obey commands only.
    # SWIs "ObeyOn" (0x054CA0) and "ObeyOff" (0x054CA1)
    def opt_obey(value):
        try:
            if value == True:
                swi.swi(SWIs['ObeyOn'],".")
            else:
                swi.swi(SWIs['ObeyOff'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Store the state of Reporter options.
    # SWI "Push" (0x054CA2)
    def push():
        try:
            swi.swi(SWIs['Push'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Restore state of Reporter options from the state stack.
    # SWI "Pull" (0x054CA3)
    def pull():
        try:
            swi.swi(SWIs['Pull'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Pause / unpause the Reporter log.
    # SWIs "Pause" (0x054CA4) and "Scroll" (0x054CA5)
    def opt_pause(value):
        try:
            if value == True:
                swi.swi(SWIs['Pause'],".")
            else:
                swi.swi(SWIs['Scroll'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Turn automatic saving in certain circumstances on/off.
    # SWIs "SaveOn" (0x054CA6) and "SaveOff (0x054CA7)
    def opt_save(value):
        try:
            if value == True:
                swi.swi(SWIs['SaveOn'],".")
            else:
                swi.swi(SWIs['SaveOff'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Turn logging to disc on/off.
    # SWIs "LogOn" (0x054CA8) and "LogOff" (0x054CA9)
    def opt_log(value):
        try:
            if value == True:
                swi.swi(SWIs['LogOn'],".")
            else:
                swi.swi(SWIs['LogOff'],".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)


if __name__ == '__main__':
    regs()
    text0("Hello world")
