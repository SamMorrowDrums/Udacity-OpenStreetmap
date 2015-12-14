#!/usr/bin/env python

import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^(([a-z]|_)*):(([a-z]|_)*)$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
non_number = re.compile(r'\D')
# UK government regex for Postcode Validation
postcode = re.compile(r'^(GIR ?0AA|[A-PR-UWYZ]([0-9]{1,2}|([A-HK-Y][0-9]([0-9ABEHMNPRV-Y])?)|[0-9][A-HJKPS-UW]) ?[0-9][ABD-HJLNP-UW-Z]{2})$')
# Missing Space Post Code
missingSpace = re.compile(r'^BT\d\d?(\d[A-Z]+)$')

CREATED = ["version", "changeset", "timestamp", "user", "uid"]

def floatOrNone(n):
    return float(n) if n else None

def validPostcode(code):
    # Ensure all postcodes are uppercase and no extra whitespace
    code = code.upper().strip()
    # Fix BTT instead of BT Postcodes
    code = code.replace("BTT", "BT")
    # Add Missing Space
    missing = re.match(missingSpace, code)
    if missing:
        code = code.replace(missing.group(1), " " + missing.group(1))
    m = re.search(postcode, code)
    if not m:
        print "Invalid / Incomplete Post Code " + code
    return code

def cleanHouseNumber(d):
    if (re.search(non_number, d)):
        return d
    else:
        return int(d)

def parseChildElement(node, child):
    key = child.get("k")
    ref = child.get("ref")
    if key and not re.search(problemchars, key):
        m = re.match(lower_colon, key)
        if m and m.group(1) == "addr":
            node["address"] = node["address"] if node.get("address") else {}
            if m.group(3) == "postcode":
                node["address"]["postcode"] = validPostcode(child.get("v"))
            else:
                node["address"][m.group(3)] = child.get("v")
        else:
            node[key] = child.get("v")
    elif ref:
        node["node_refs"] = node["node_refs"] if node.get("node_refs") else []
        node["node_refs"].append(ref)

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way":
        node["id"] = element.get("id")
        node["type"] = element.tag
        node["visible"] = element.get("visible")
        node["pos"] = [floatOrNone(element.get("lat")), floatOrNone(element.get("lon"))]
        node["created"] = {}
        for key in CREATED:
            node["created"][key] = element.get(key)
        for child in element.getchildren():
            parseChildElement(node, child)
        return node

    else:
        return None

def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


data = process_map("BelfastAndSurrounding.osm", False)

