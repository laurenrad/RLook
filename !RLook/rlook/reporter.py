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
# Functions for using Reporter from Python.

import swi
import rlook

# Constants for Reporter's SWI numbers.
SWIs = {'Text0': 0x54C80, 'TextS': 0x54C81, 'Regs': 0x54C83, 'Where': 0x54C84,
        'Poll': 0x54C85, 'Dump': 0x54C86, 'GetSwiRet': 0x54C87, 'ErrBlk': 0x54C88,
        'Quit': 0x54C8A, 'Clear': 0x54C8B, 'Open': 0x54C8C, 'Close': 0x54C8D,
        'On': 0x54C8E, 'Off': 0x54C8F, 'CmdOn': 0x54C90, 'CmdOff': 0x54C91, 'Hide': 0x54C92,
        'Show': 0x54C93, 'ErrOn': 0x54C94, 'ErrOff': 0x54C95, 'TaskOn': 0x54C96,
        'TaskOff': 0x54C97, 'Vdu4On': 0x54C98, 'Vdu4Off': 0x54C99, 'RmaOn': 0x54C9A,
        'RmaOff': 0x54C9B, 'TimeOn': 0x54C9C, 'TimeOff': 0x54C9D, 'SrceOn': 0x54C9E,
        'SrceOff': 0x54C9F, 'ObeyOn': 0x54CA0, 'ObeyOff': 0x54CA1, 'Push': 0x54CA2,
        'Pull': 0x54CA3, 'Pause': 0x54CA4, 'Scroll': 0x54CA5, 'SaveOn': 0x54CA6,
        'SaveOff': 0x54CA7, 'LogOn': 0x54CA8, 'LogOff': 0x54CA9}


def _handle_swierr(e):
    # internal - very simple error handler for errors from SWI mod.
    if e.errnum == 486:
        pass  # silently ignore when Reporter isn't running
    else:
        raise e  # raise again to be handled later possibly


class Reporter:
    # print a string to reporter by calling the SWI Text0 (0x054C80).
    # if debug is True, will only print if debug global is set.
    def print(s, debug=False):
        """
        Print a string to Reporter by calling the SWI Text0 (0x54C80).
        If debug is True, will only print if debug global is set.
        """
        if (not debug) or rlook.debug_enabled:
            try:
                swi.swi(SWIs['Text0'], "s", s)
            except swi.error as swi_err:
                _handle_swierr(swi_err)

    # editor's note: This is where TextS would go, but it's not useful
    # in this context, so it's not implemented.

    def regs():
        """
        Print out the registers 0-9, pc, flags, etc.
        SWI(s): Regs (0x054C82).
        """
        try:
            swi.swi(SWIs['Regs'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # SWI Registers (0x054C83) - not implemented. (This is different from Regs)

    def where():
        """
        Display the address of the last abort and module info if relevant.
        SWI(s): Where (0x054C84)
        """
        try:
            swi.swi(SWIs['Where'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def poll():
        """
        SWI(s): Poll (0x054C85)
        """
        try:
            swi.swi(SWIs['Poll'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def dump(addr, length, width, text):
        """
        SWI(s): Dump (0x054C86)
        """
        try:
            swi.swi(SWIs['Dump'], "iiis", addr, length, width, text)
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # SWI ErrBlk, number 0x054C88 is also not implemented.
    # I may provide a replacement for this later that prints a
    # swi.error pretty.

    def quit():
        """
        Quit Reporter.
        SWI(s): Quit (0x054C8A)
        """
        try:
            swi.swi(SWIs['Quit'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def clear():
        """
        Clear the Reporter window.
        SWI(s): Clear (0x054C8B)
        """
        try:
            swi.swi(SWIs['Clear'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def open_win():
        """
        Open the Reporter window if it has been closed (but not hidden).
        SWI(s): Open (0x054C8C)
        """
        try:
            swi.swi(SWIs['Open'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def close_win():
        """
        Close the Reporter window.
        SWI(s): Close (0x054C8D)
        """
        try:
            swi.swi(SWIs['Close'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def opt_gen(value):
        """
        Turn most reporting on / off. See Reporter docs for details.
        SWI(s): On (0x054C8E), Off (0x054C8F)
        """
        try:
            if value is True:
                swi.swi(SWIs['On'], ".")
            else:
                swi.swi(SWIs['Off'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def opt_cmd(value):
        """
        Turn on/off reporting for ALL commands.
        SWI(s): CmdOn (0x054C90), CmdOff (0x054C91)
        """
        try:
            if value is True:
                swi.swi(SWIs['CmdOn'], ".")
            else:
                swi.swi(SWIs['CmdOff'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def hide():
        """
        Hide the Reporter window until show is called.
        SWI(s): Hide (0x054C92)
        """
        try:
            swi.swi(SWIs['Hide'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def show():
        """
        Show a previously hidden Reporter window.
        SWI(s): Show (0x054C93)
        """
        try:
            swi.swi(SWIs['Show'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def opt_err(value):
        """
        Turn reporting on/off for errors.
        SWI(s): ErrOn (0x054C94), ErrOff (0x054C95)
        """
        try:
            if value is True:
                swi.swi(SWIs['ErrOn'], ".")
            else:
                swi.swi(SWIs['ErrOff'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def opt_tasks(value):
        """
        Turn reporting on/off for Wimp Task init/closedown.
        SWI(s): TaskOn (0x054C96), TaskOff (0x054C97)
        """
        try:
            if value is True:
                swi.swi(SWIs['TaskOn'], ".")
            else:
                swi.swi(SWIs['TaskOff'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def opt_vdu4(value):
        """
        Turn reporting on/off for VDU 4 output.
        SWI(s): Vdu4On (0x054C98), Vdu4Off (0x054C99)
        """
        try:
            if value is True:
                swi.swi(SWIs['Vdu4On'], ".")
            else:
                swi.swi(SWIs['Vdu4Off'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def opt_rma(value):
        """
        Turn reporting on/off for RMA Storage events.
        SWI(s): RmaOn (0x054C9A), RmaOff (0x054C9B)
        """
        try:
            if value is True:
                swi.swi(SWIs['RmaOn'], ".")
            else:
                swi.swi(SWIs['RmaOff'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    def opt_timestamps(value):
        """
        Turn timestamps on/off for output.
        SWI(s): TimeOn (0x054C9C), TimeOff (0x054C9D)
        """
        try:
            if value is True:
                swi.swi(SWIs['TimeOn'], ".")
            else:
                swi.swi(SWIs['TimeOff'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Source on/off option. I don't know what this actually does?
    # SWIs "SrceOn" (0x054C9E) and "SrceOff" (0x054C9F)
    def opt_srce(value):
        try:
            if value is True:
                swi.swi(SWIs['SrceOn'], ".")
            else:
                swi.swi(SWIs['SrceOff'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # If this option is enabled, reporting of OS commands is restricted to
    # Obey commands only.
    # SWIs "ObeyOn" (0x054CA0) and "ObeyOff" (0x054CA1)
    def opt_obey(value):
        try:
            if value is True:
                swi.swi(SWIs['ObeyOn'], ".")
            else:
                swi.swi(SWIs['ObeyOff'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Store the state of Reporter options.
    # SWI "Push" (0x054CA2)
    def push():
        try:
            swi.swi(SWIs['Push'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Restore state of Reporter options from the state stack.
    # SWI "Pull" (0x054CA3)
    def pull():
        try:
            swi.swi(SWIs['Pull'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Pause / unpause the Reporter log.
    # SWIs "Pause" (0x054CA4) and "Scroll" (0x054CA5)
    def opt_pause(value):
        try:
            if value is True:
                swi.swi(SWIs['Pause'], ".")
            else:
                swi.swi(SWIs['Scroll'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Turn automatic saving in certain circumstances on/off.
    # SWIs "SaveOn" (0x054CA6) and "SaveOff (0x054CA7)
    def opt_save(value):
        try:
            if value is True:
                swi.swi(SWIs['SaveOn'], ".")
            else:
                swi.swi(SWIs['SaveOff'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)

    # Turn logging to disc on/off.
    # SWIs "LogOn" (0x054CA8) and "LogOff" (0x054CA9)
    def opt_log(value):
        try:
            if value is True:
                swi.swi(SWIs['LogOn'], ".")
            else:
                swi.swi(SWIs['LogOff'], ".")
        except swi.error as swi_err:
            _handle_swierr(swi_err)
