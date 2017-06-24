#! /usr/bin/env python3

import subprocess
import re

#Get all sources from pulse and return an array of the sources
def get_sources():
    pacmd_output, _ = subprocess.Popen("pacmd list-sources",
                shell=True, stdout=subprocess.PIPE).communicate()
    raw_sources = re.split(r"\s\s(\s|\*)\sindex:\s(\d+)",
            pacmd_output.decode("utf=8"))[1:]
    sources = []
    current_index = None
    is_current_active = False
    for index, item in enumerate(raw_sources):
        if index % 3 == 0:
            is_current_active = item == "*"
            continue
        elif index % 3 == 1:
            current_index = index
            continue
        elif index % 3 == 2:
            #pacmd mixes tabs and spaces in its output. Go figure.
            name = re.match(r"\n\tname:\s(.*)", item).groups()[0]
            if "output" in name:
                source = {}
            device_name_match = re.search(r"\t\tdevice.description\s=\s\"(.*)\"", item)
            device_name = device_name_match.groups()[0]
            source = {"pulse_index": current_index, "device_name": device_name}
            sources.append(source)
    return sources

def is_int(n):
    try:
        int(n)
        return True
    except ValueError:
        return False
