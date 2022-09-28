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

import os
import time
import mido

GETFEEDBACK_API_KEY = os.environ["GETFEEDBACK_API_KEY"]
GETFEEDBACK_SURVEY_ID = os.environ["GETFEEDBACK_SURVEY_ID"]
ALL_FI_TARGET_PORT = os.environ["ALL_FI_TARGET_PORT"]

def first(items):
    for i in items:
        return i

def get_target_port():
    for n in mido.get_output_names():
        if TARGET_PORT in n:
            return n

# test getting GFP API responses

import requests

api_base_url = "https://api.getfeedback.com"
responses_url = f"/surveys/{GETFEEDBACK_SURVEY_ID}/responses"

headers = {"authorization": f"Bearer {GETFEEDBACK_API_KEY}"}
payload = {"per_page": 100}

r = requests.get(api_base_url + responses_url,
                 headers=headers, params=payload)

responses = r.json()["active_models"]

len(responses) # 10, cool

responses[0]["answers"][0]

def answer_value(answer):
    # allowing multiselect because it'll be handy for instrument mixes
    if answer["type"] == "MultipleChoice":
        return [choice["text"] for choice in answer["choices"]]
    elif answer["type"] == "Slider":
        return answer["number"]
    else:
        # TODO: more if needed!
        return None



answer_value(responses[0]["answers"][1])



# params: page, per_page, status=completed, since, until




# example
note_on_msg = mido.Message("note_on", note=60, velocity=127, channel=10)
note_off_msg = mido.Message("note_off", note=60, velocity=127, channel=10)

# open port
if outport:
    outport.close()

outport = mido.open_output(get_target_port())

outport.send(note_on_msg)

time.sleep(2)
outport.send(note_on_msg)

cc_msg = mido.Message("control_change", control=0, value=127)

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
