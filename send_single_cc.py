import time
import os
import sys
import mido

if len(sys.argv) < 3:
    sys.exit("Please provide arguments: send_single_cc.py <control> <value>")

try:
    ALL_FI_TARGET_PORT = os.environ["ALL_FI_TARGET_PORT"]
except KeyError:
    sys.exit("Set the ALL_FI_TARGET_PORT env var first")

if !(ALL_FI_TARGET_PORT in mido.get_output_names()):
    sys.exit(f"MIDI port {ALL_FI_TARGET_PORT} not found")


control = int(sys.argv[1])
value = int(sys.argv[2])

outport = mido.open_output(ALL_FI_TARGET_PORT)

print(f"MIDI CC: {control} => {value})
message = mido.Message("control_change", control=control, value=value)
outport.send(message)

outport.close()
