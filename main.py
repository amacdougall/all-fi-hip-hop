# Run loopMIDI. Create a port named the same as the LOOPMIDI_PORT_NAME constant.
# In FL Studio, open MIDI settings, select this device in the Input section, and
# click the Enable button to the bottom left of the Input section. I think you
# have to choose a port number too, honestly not sure.
#
# To activate your virtual env:
#
# python -m venv .
#
# installation notes: to get mido installed under Windows, first you gotta
# install python-rtmidi, which requires Windows C++ build tools. It's a big
# download for no really good reason, but... get the Visual Studio build tools
# installer from https://visualstudio.microsoft.com/visual-cpp-build-tools/,
# then run this:
#
# vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools 
#
# Then you should be able to:
#
# pip install python-rtmidi
# pip install mido
#
TARGET_PORT = 'loopMIDI Python'

import mido
import time

def first(items):
    for i in items:
        return i

def get_target_port():
    for n in mido.get_output_names():
        if TARGET_PORT in n:
            return n

# example
note_on_msg = mido.Message('note_on', note=60, velocity=127, channel=10)
note_off_msg = mido.Message('note_off', note=60, velocity=127, channel=10)

# open port
if outport:
    outport.close()

outport = mido.open_output(get_target_port())

outport.send(note_on_msg)

time.sleep(2)
outport.send(note_on_msg)

cc_msg = mido.Message('control_change', control=0, value=127)

time.sleep(2)
cc_msg = cc_msg.copy(value=0)
outport.send(cc_msg)
time.sleep(2)
cc_msg = cc_msg.copy(value=127)
outport.send(cc_msg)

# This works! Be sure to thank the creator of the loopMidi tool and the author
# of the blog post.

# To the east, false dawn
# A light reaches through the sky
# Azure sky now falls
