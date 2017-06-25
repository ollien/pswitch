#! /usr/bin/env python3

import subprocess
import sys
import re

def get_sources():
    pacmd_output, _ = subprocess.Popen("pacmd list-sources",
                shell=True, stdout=subprocess.PIPE).communicate()
    return parse_pacmd_list_output(pacmd_output)

def get_sinks():
    pacmd_output, _ = subprocess.Popen("pacmd list-sinks",
                shell=True, stdout=subprocess.PIPE).communicate()
    return parse_pacmd_list_output(pacmd_output)

#Will parse output from pacmd list-sinks and pacmd list-sources
def parse_pacmd_list_output(pacmd_output):
    raw_sources = re.split(r"\s\s(\s|\*)\sindex:\s(\d+)",
            pacmd_output.decode("utf-8"))[1:]
    sources = []
    current_index = None
    is_current_active = False
    for index, item in enumerate(raw_sources):
        if index % 3 == 0:
            is_current_active = item == "*"
            continue
        elif index % 3 == 1:
            current_index = int(item)
            continue
        elif index % 3 == 2:
            #pacmd mixes tabs and spaces in its output. Go figure.
            device_name_match = re.search(r"\t\tdevice.description\s=\s\"(.*)\"", item)
            device_name = device_name_match.groups()[0]
            source = {"pulse_index": current_index, "device_name": device_name}
            sources.append(source)
    return sources

def get_sink_input_indexes():
    pacmd_output, _ = subprocess.Popen("pacmd list-sink-inputs",
                shell = True, stdout=subprocess.PIPE).communicate()
    return get_indexes_from_pacmd_output(pacmd_output)

def get_source_output_indexes():
    pacmd_output, _ = subprocess.Popen("pacmd list-source-outputs",
                shell = True, stdout=subprocess.PIPE).communicate()
    return get_indexes_from_pacmd_output(pacmd_output)

def get_indexes_from_pacmd_output(pacmd_output):
    index_matches = re.finditer(r"\s{4}index:\s(\d+)", pacmd_output.decode("utf-8"))
    return [int(index.groups()[0]) for index in index_matches]

def set_sink_input(input_index, sink_index):
    if type(input_index) == int:
        input_index = str(input_index)
    if type(sink_index) == int:
        sink_index = str(sink_index)
    subprocess.Popen(["pacmd", "move-sink-input", input_index, sink_index])

def set_source_output(output_index, source_index):
    if type(output_index) == int:
        output_index = str(output_index)
    if type(source_index) == int:
        source_index = str(source_index)
    subprocess.Popen(["pacmd", "move-source-output", output_index, source_index])

def set_default_sink(sink_index):
    if type(sink_index) == int:
        sink_index = str(sink_index)
    subprocess.Popen(["pacmd", "set-default-sink", sink_index])

def set_default_source(source_index):
    if type(source_index) == int:
        source_index = str(source_index)
    subprocess.Popen(["pacmd", "set-default-source", source_index])

def switch_to_sink(sink_index):
    set_default_sink(sink_index)
    inputs = get_sink_input_indexes()
    for input_index in inputs:
        set_sink_input(input_index, sink_index)

def switch_to_source(source_index):
    set_default_source(source_index)
    outputs = get_source_output_indexes()
    for output_index in outputs:
        set_source_output(output_index, source_index)

def print_menu_and_get_index(device_type):
    devices = None
    if device_type == "sink":
        devices = get_sinks()
        print("Available Pulse Audio sinks:")
    elif device_type == "source":
        devices = get_sources()
        print("Available Pulse Audio sources:")
    else:
        raise ValueError("device_type must be either sink or source")
    for index, device in enumerate(devices):
        print("\t{index}: {name}".format(index=index, name=device["device_name"]))
    valid_input = False
    selection = None
    while not valid_input:
        selection = input("? ")
        valid_input = is_int(selection) and 0 <= int(selection) < len(devices)
    selection = int(selection)
    return devices[selection]["pulse_index"]

def is_int(n):
    try:
        int(n)
        return True
    except ValueError:
        return False

#Returns true if arg is "o", "output", "i", or "input"
def check_type_arg_validity(arg):
    return arg.lower() in ("o", "output", "i", "input")

if __name__ == "__main__":
    if len(sys.argv) == 2 and check_type_arg_validity(sys.argv[1]):
        if sys.argv[1].lower() in ("o", "output"):
            sink_index = print_menu_and_get_index("sink")
            switch_to_sink(sink_index)
        elif sys.argv[1].lower() in ("i", "input"):
            source_index = print_menu_and_get_index("source")
            switch_to_source(source_index)
    elif len(sys.argv) == 3 and is_int(sys.argv[2]) and check_type_arg_validity(sys.argv[1]):
        if sys.argv[1].lower() in ("o", "output"):
            switch_to_sink(int(sys.argv[2]))
        elif sys.argv[1].lower() in ("i", "input"):
            switch_to_source(int(sys.argv[2]))
    else:
        print((
        "Usage: pulse-switcher type [index]\n"
        "Where:\n"
        "    type is i[nput] or o[utput]\n"
        "    index is a pulse audio sink index or source index"))
