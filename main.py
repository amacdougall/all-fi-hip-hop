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
import sys
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

def answer_value(answer):
    # allowing multiselect because it'll be handy for instrument mixes
    if answer["type"] == "MultipleChoice":
        return [choice["text"] for choice in answer["choices"]]
    elif answer["type"] == "Slider":
        return answer["number"]
    else:
        # TODO: more if needed!
        return None

def is_completed(response):
    if response["completed_at"] == None:
        return False
    else:
        return True

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
        # bass
        "bass_pattern_type": {
            "control": 20,
            "value": None # 0.5 Chill; 1.0 Lively
        },
        "bass_synth_amount": {
            "control": 25,
            "value": None # 0.0 - 0.50
        },
        "bass_electric_amount": {
            "control": 30,
            "value": None # 0.0 - 0.8
        },
        # TODO: more instruments?
        # accent
        "accent_pattern_type": {
            "control": 35,
            "value": None # 0.5 Chill; 1.0 Lively
        },
        "accent_gfunk_amount": {
            "control": 40,
            "value": None # 0.0 - 0.50
        },
        "accent_bell_amount": {
            "control": 45,
            "value": None # 0.0 - 0.8
        },
        # TODO: more instruments?
        # pad
        "pad_dark_amount": {
            "control": 50,
            "value": None # 0.0 - 0.50
        },
        "pad_moon_amount": {
            "control": 55,
            "value": None # 0.0 - 0.8
        },
        "pad_soundtrack_amount": {
            "control": 60,
            "value": None # 0.0 - 0.8
        },
        # lead (no pattern choice)
        "lead_glimmer_amount": {
            "control": 65,
            "value": None # 0.0 - 0.4
        },
        "lead_acoustic_amount": {
            "control": 70,
            "value": None # 0.0 - 0.8
        },
        # TODO: more instruments?
        # TODO: lead Gross Beat?
        # drums
        "drum_pattern_type": {
            "control": 75,
            "value": None # 0.5 Boom Bap; 1.0 Other
        },
        "drum_snare_crossfade": {
            "control": 80,
            "value": None # 0.0 - 1.0
        },
        "drum_ny": {
            "control": 82,
            "value": None # 0.0 - 0.5
        },
        # vocal
        "vocal_echo": {
            "control": 85,
            "value": None # 0.0 none, 0.25 some, 1.0 a lot
        },
        # TODO: verse Gross Beat?
    }

def apply_general_vibe(values, answer):
    match answer["choices"][0]["text"]:
        case "Classic lyrical hip-hop":
            values["chord_pattern_type"]["value"] = 1.0
            values["chord_piano_amount"]["value"] = 0.8
            values["chord_strings_amount"]["value"] = 0.0
            values["chord_guitar_amount"]["value"] = 0.0
            values["bass_pattern_type"]["value"] = 0.5
            values["bass_synth_amount"]["value"] = 0.0
            values["bass_electric_amount"]["value"] = 0.8
            values["accent_pattern_type"]["value"] = 0.5
            values["accent_gfunk_amount"]["value"] = 0.8
            values["accent_bell_amount"]["value"] = 0.0
            values["lead_acoustic_amount"]["value"] = 0.0
            values["lead_glimmer_amount"]["value"] = 0.0
            values["drum_pattern_type"]["value"] = 0.5
            values["drum_snare_crossfade"]["value"] = 0.0
            values["drum_ny"]["value"] = 0.35
            values["vocal_echo"]["value"] = 0.0
        case "Lo-fi art soundscape":
            values["chord_pattern_type"]["value"] = 0.5
            values["chord_piano_amount"]["value"] = 0.8
            values["chord_strings_amount"]["value"] = 0.8
            values["chord_guitar_amount"]["value"] = 0.0
            values["bass_pattern_type"]["value"] = 0.5
            values["bass_synth_amount"]["value"] = 0.0
            values["bass_electric_amount"]["value"] = 0.8
            values["accent_pattern_type"]["value"] = 0.5
            values["accent_gfunk_amount"]["value"] = 0.0
            values["accent_bell_amount"]["value"] = 0.8
            values["pad_soundtrack_amount"]["value"] = 0.8
            values["pad_moon_amount"]["value"] = 0.0
            values["pad_dark_amount"]["value"] = 0.0
            values["lead_acoustic_amount"]["value"] = 0.8
            values["lead_glimmer_amount"]["value"] = 0.0
            values["drum_pattern_type"]["value"] = 0.5
            values["drum_snare_crossfade"]["value"] = 0.5
            values["drum_ny"]["value"] = 0.0
            values["vocal_echo"]["value"] = 1.0
        case "In your face synths and guitars":
            values["chord_pattern_type"]["value"] = 0.5
            values["chord_piano_amount"]["value"] = 0.0
            values["chord_strings_amount"]["value"] = 0.0
            values["chord_guitar_amount"]["value"] = 0.5
            values["bass_pattern_type"]["value"] = 0.5
            values["bass_synth_amount"]["value"] = 0.0
            values["bass_electric_amount"]["value"] = 0.8
            values["lead_glimmer_amount"]["value"] = 0.4
            values["lead_acoustic_amount"]["value"] = 0.0
            values["vocal_echo"]["value"] = 0.25
    return values

def apply_chord_preset(values, answer):
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
            values["chord_pattern_type"]["value"] = 0.5
            values["chord_piano_amount"]["value"] = 0.0
            values["chord_strings_amount"]["value"] = 0.0
            values["chord_guitar_amount"]["value"] = 0.5
    return values

def apply_chord_pattern(values, answer):
    match answer["choices"][0]["text"]:
        case "Sustained":
            values["chord_pattern_type"]["value"] = 0.5
        case "Rhythmic":
            values["chord_pattern_type"]["value"] = 1.0
    return values

def apply_chord_instruments(values, answer):
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
    return values

def apply_bass_preset(values, answer):
    match answer["choices"][0]["text"]:
        case "Classic hip-hop":
            values["bass_pattern_type"]["value"] = 0.5
            values["bass_synth_amount"]["value"] = 0.0
            values["bass_electric_amount"]["value"] = 0.8
        case "Analog synth":
            values["bass_pattern_type"]["value"] = 0.5
            values["bass_synth_amount"]["value"] = 0.5
            values["bass_electric_amount"]["value"] = 0.0
        case "Groovy funk":
            values["bass_pattern_type"]["value"] = 1.0
            values["bass_synth_amount"]["value"] = 0.3
            values["bass_electric_amount"]["value"] = 0.8
    return values

def apply_bass_pattern(values, answer):
    match answer["choices"][0]["text"]:
        case "Chill":
            values["bass_pattern_type"]["value"] = 0.5
        case "Groovy":
            values["bass_pattern_type"]["value"] = 1.0
    return values

def apply_bass_instruments(values, answer):
    choices = [choice["text"] for choice in answer["choices"]]
    if "Synth" in choices:
        values["bass_synth_amount"]["value"] = 0.5
    else:
        values["bass_synth_amount"]["value"] = 0.0
    if "Electric" in choices:
        values["bass_electric_amount"]["value"] = 0.8
    else:
        values["bass_electric_amount"]["value"] = 0.0
    return values

def apply_accent_preset(values, answer):
    match answer["choices"][0]["text"]:
        case "G-Funk":
            values["accent_pattern_type"]["value"] = 1.0
            values["accent_gfunk_amount"]["value"] = 0.8
            values["accent_bell_amount"]["value"] = 0.0
        case "Tiny bell":
            values["accent_pattern_type"]["value"] = 0.5
            values["accent_gfunk_amount"]["value"] = 0.0
            values["accent_bell_amount"]["value"] = 0.8
        case "Synth bell":
            values["accent_pattern_type"]["value"] = 0.5
            values["accent_gfunk_amount"]["value"] = 0.8
            values["accent_bell_amount"]["value"] = 0.5
    return values

def apply_accent_pattern(values, answer):
    match answer["choices"][0]["text"]:
        case "Dense":
            values["accent_pattern_type"]["value"] = 0.5
        case "Sparse":
            values["accent_pattern_type"]["value"] = 1.0
    return values

def apply_accent_instruments(values, answer):
    choices = [choice["text"] for choice in answer["choices"]]
    if "G-Funk Sine Wave" in choices:
        values["accent_gfunk_amount"]["value"] = 0.5
    else:
        values["accent_gfunk_amount"]["value"] = 0.0
    if "Bell" in choices:
        values["accent_bell_amount"]["value"] = 0.8
    else:
        values["accent_bell_amount"]["value"] = 0.0
    return values

def apply_pad_instruments(values, answer):
    choices = [choice["text"] for choice in answer["choices"]]
    if "Dark Synth" in choices:
        values["pad_dark_amount"]["value"] = 0.5
    else:
        values["pad_dark_amount"]["value"] = 0.0
    if "Sci-Fi Moon Noises" in choices:
        values["pad_moon_amount"]["value"] = 0.8
    else:
        values["pad_moon_amount"]["value"] = 0.0
    if "Lo-Fi Strings" in choices:
        values["pad_soundtrack_amount"]["value"] = 0.8
    else:
        values["pad_soundtrack_amount"]["value"] = 0.0
    return values

def apply_drum_preset(values, answer):
    match answer["choices"][0]["text"]:
        case "Classic hip-hop":
            values["drum_pattern_type"]["value"] = 0.5
            values["drum_snare_crossfade"]["value"] = 0.0
        case "Experimental":
            values["drum_pattern_type"]["value"] = 0.5
            values["drum_snare_crossfade"]["value"] = 0.6
    return values

def apply_drum_pattern(values, answer):
    match answer["choices"][0]["text"]:
        case "Classic hip-hop":
            values["drum_pattern_type"]["value"] = 0.5
        case "Experimental":
            values["drum_pattern_type"]["value"] = 1.0
    return values

def apply_drum_snare_fade(values, answer):
    values["drum_snare_crossfade"]["value"] = int(answer["number"]) / 100
    return values

def apply_drum_ny(values, answer):
    values["drum_ny"]["value"] = int(answer["number"]) / 100 * 0.8
    return values

def apply_vocal_echo(values, answer):
    match answer["choices"][0]["text"]:
        case "Clear":
            values["vocal_echo"]["value"] = 0.0
        case "A little echo":
            values["vocal_echo"]["value"] = 0.25
        case "Weird cascading echo on the backbeat":
            values["vocal_echo"]["value"] = 1.0
    return values

def apply_lead_instruments(values, answer):
    choices = [choice["text"] for choice in answer["choices"]]
    if "Synth Electric Guitar" in choices:
        values["lead_glimmer_amount"]["value"] = 0.4
    else:
        values["lead_glimmer_amount"]["value"] = 0.0
    if "Acoustic Guitar" in choices:
        values["lead_acoustic_amount"]["value"] = 0.8
    else:
        values["lead_acoustic_amount"]["value"] = 0.0
    return values

# open port
outport = False

if outport:
    outport.close()

outport = mido.open_output(get_target_port())

headers = {"authorization": f"Bearer {GETFEEDBACK_API_KEY}"}


# get survey data so we can find the question for each answer
r = requests.get(api_base_url + survey_url, headers=headers)
survey = r.json()["survey"]
questions = survey["ordered_components"]

while True:
    payload = {"per_page": 100,
               "since_field": "completed_at"}
    r = requests.get(api_base_url + responses_url,
                     headers=headers, params=payload)
    responses = r.json()["active_models"]

    responses = filter(is_completed, responses)

    # Simplest Thing That Could Possibly Work™: just do latest response
    response = next(responses)

    values = build_value_set()

    for answer in response["answers"]:
        question = find_question_by_answer(answer)
        if question == None:
            breakpoint()
        print("handling question " + question["title"])
        match question["title"]:
            case "General vibe":
                values = apply_general_vibe(values, answer)
            case "Chords: overall style":
                values = apply_chord_preset(values, answer)
            case "Chords: sustained or rhythmic?":
                values = apply_chord_pattern(values, answer)
            case "Chords: what instruments?":
                values = apply_chord_instruments(values, answer)
            case "Bass: overall style":
                values = apply_bass_preset(values, answer)
            case "Bass: chill or groovy?":
                values = apply_bass_pattern(values, answer)
            case "Bass: what instruments?":
                values = apply_bass_instruments(values, answer)
            case "Accent: overall style":
                values = apply_accent_preset(values, answer)
            case "Accent: sparse or dense?":
                values = apply_accent_pattern(values, answer)
            case "Accent: what instruments?":
                values = apply_accent_instruments(values, answer)
            case "Pad: what instruments?":
                values = apply_pad_instruments(values, answer)
            case "Drums: overall style":
                values = apply_drum_preset(values, answer)
            case "Drums: what kinds of patterns?":
                values = apply_drum_pattern(values, answer)
            case "Drums: snare or clap?":
                values = apply_drum_snare_fade(values, answer)
            case "Drums: how hard do they hit?":
                values = apply_drum_ny(values, answer)
            case "Vocals: clear or echoing?":
                values = apply_vocal_echo(values, answer)
            case "Lead: what instruments?":
                values = apply_lead_instruments(values, answer)

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

    if len(sys.argv) > 1 and sys.argv[1] == 'oneshot':
        sys.exit()
    else:
        # sleep 30 seconds before repeating
        time.sleep(30)
