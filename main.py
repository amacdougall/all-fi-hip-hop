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
try:
    import mido
except ModuleNotFoundError:
    import MockedMido
    print("Can't find mido so outputting to file")
    mido = MockedMido.MockedMido()

try:
    GETFEEDBACK_API_KEY = os.environ["GETFEEDBACK_API_KEY"]
except KeyError:
    GETFEEDBACK_API_KEY = ''

try:
    GETFEEDBACK_SURVEY_ID = os.environ["GETFEEDBACK_SURVEY_ID"]
except KeyError:
    GETFEEDBACK_SURVEY_ID = ''

try:
    ALL_FI_TARGET_PORT = os.environ["ALL_FI_TARGET_PORT"]
except KeyError:
    ALL_FI_TARGET_PORT = ''

def get_target_port():
    for n in mido.get_output_names():
        if ALL_FI_TARGET_PORT in n:
            return n
    sys.exit(f"MIDI port '{ALL_FI_TARGET_PORT}' not found")

# test getting GFP API responses

import requests

api_base_url = "https://api.getfeedback.com"
responses_url = f"/surveys/{GETFEEDBACK_SURVEY_ID}/responses"
survey_url = f"/surveys/{GETFEEDBACK_SURVEY_ID}"

headers = {"authorization": f"Bearer {GETFEEDBACK_API_KEY}"}
payload = {"per_page": 100}

r = requests.get(api_base_url + responses_url,
                 headers=headers, params=payload)
responses = r.json()["active_models"]

def answer_value(answer):
    # allowing multiselect because it'll be handy for instrument mixes
    if answer["type"] == "MultipleChoice":
        return [choice["text"] for choice in answer["choices"]]
    elif answer["type"] == "Slider":
        return answer["number"]
    else:
        # TODO: more if needed!
        return None

# get survey data so we can find the question for each answer
r = requests.get(api_base_url + survey_url, headers=headers)
survey = r.json()["survey"]
questions = survey["ordered_components"]

def find_question_by_answer(a):
    for q in questions:
        if q["id"] == a["component_id"]:
            return q

# create a set of desired values first, but then blend against the most recent
# five values. Try to weight the most recent response more strongly, though,
# because why not?
#
# Anyway, this is the master list of values. A value won't be counted if it's
# None.
#
def build_value_set():
    return {
        "chord_pattern_type": {
            "control": 0,
            "value": None # 0.5 Sustained; 1.0 Rhythmic
        },
        "chord_piano_amount": {
            "control": 5,
            "value": None # 0.0 - 0.8
        },
        "chord_strings_amount": {
            "control": 10,
            "value": None # 0.0 - 0.8
        },
        "chord_guitar_amount": {
            "control": 15,
            "value": None # 0.0 - 0.5
        },
    }

values = build_value_set()

# debug: just do one response

response = responses[1]

for answer in response["answers"]:
    question = find_question_by_answer(answer)
    print("handling question " + question["title"])
    match question["title"]:
        case "Chords: overall style":
            match answer["choices"][0]["text"]:
                case "Lo-fi hip-hop":
                    values["chord_pattern_type"]["value"] = 0.5
                    values["chord_piano_amount"]["value"] = 0.8
                    values["chord_strings_amount"]["value"] = 0.8
                    values["chord_guitar_amount"]["value"] = 0.0
                case "Classic hip-hop":
                    values["chord_pattern_type"]["value"] = 1.0
                    values["chord_piano_amount"]["value"] = 0.8
                    values["chord_strings_amount"]["value"] = 0.0
                    values["chord_guitar_amount"]["value"] = 0.0
                case "Rap-rock":
                    values["chord_pattern_type"]["value"] = 0.0
                    values["chord_piano_amount"]["value"] = 0.0
                    values["chord_strings_amount"]["value"] = 0.0
                    values["chord_guitar_amount"]["value"] = 0.5
        case "Chords: sustained or rhythmic?":
            match answer["choices"][0]["text"]:
                case "Sustained":
                    values["chord_pattern_type"]["value"] = 0.5
                case "Rhythmic":
                    values["chord_pattern_type"]["value"] = 1.0
        case "Chords: what instruments?":
            choices = [choice["text"] for choice in answer["choices"]]
            if "Piano" in choices:
                values["chord_piano_amount"]["value"] = 0.8
            else:
                values["chord_piano_amount"]["value"] = 0.0
            if "Strings" in choices:
                values["chord_strings_amount"]["value"] = 0.8
            else:
                values["chord_strings_amount"]["value"] = 0.0
            if "Electric guitar" in choices:
                values["chord_guitar_amount"]["value"] = 0.5
            else:
                values["chord_guitar_amount"]["value"] = 0.0

# for starters, just set these values directly on the song

# open port
outport = False

if outport:
    outport.close()

outport = mido.open_output(get_target_port())

for k in values:
    if values[k]["value"] != None:
        print(f"{k} => MIDI CC:")
        print(f"{values[k]['control']} => {values[k]['value']}")
        message = mido.Message(
            "control_change",
            control=values[k]["control"],
            value=int(127 * values[k]["value"]) # to byte value
        )
        outport.send(message)
        time.sleep(1)

# This works! Be sure to thank the creator of the loopMidi tool and the author
# of the blog post.

# To the east, false dawn
# A light reaches through the sky
# Azure sky now falls
