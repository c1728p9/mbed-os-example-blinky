"""
mbed SDK
Copyright (c) 2017-2017 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import csv, sys
from collections import namedtuple
from os.path import join, abspath, dirname
from copy import deepcopy


# Be sure that the tools directory is in the search path
ROOT = abspath(join(dirname(__file__), "..", "tools"))
sys.path.insert(0, ROOT)


from tools.toolchains import TOOLCHAINS, TOOLCHAIN_CLASSES, TOOLCHAIN_PATHS
from tools.arm_pack_manager import Cache
from tools.targets import CUMULATIVE_ATTRIBUTES, TARGET_MAP

class LayoutException(Exception):
    """Wrapper for an exception that allows calling functions to distinguish
    layout problems from other types of problems"""
    pass

_RegionIntermediate = namedtuple("_REGION_INTERMEDIATE", "name size")
Region = namedtuple("Region", "name addr size")

def layout_to_regions(layout_file, rom_start, rom_size):
    """Extract the regions from a layout file

    Each region is a dictionary containing "name", "addr" and "size".

    Positional arguments:
    layout_data - contents of layout.txt
    rom_start - start of the target's rom block
    rom_size - size of the target's rom block
    """
    region_list = list(_csv_to_region_list(layout_file))
    return _regions_to_abs_regions(region_list, rom_start, rom_size)

def _csv_to_region_list(layout_file):
    """Internal helper generator for the regions within a layout file"""
    for linum, row in enumerate(csv.reader(layout_file)):
        try:
            name, size_str = row
            yield _RegionIntermediate(name, _size_str_to_value(size_str))
        except ValueError:
            raise LayoutException("Invalid layout file format. "
                                  "line %d contains %d entries; expected %d"
                                  % (linum, len(row), 2))
        except LayoutException:
            raise LayoutException("Invalid size specified on line %d" % linum)

def _get_wildcard_size(regions, rom_size):
    """Get the size of the wildcard region"""
    allocated_size = sum(region.size for region in regions if
                         region.size is not None)
    return rom_size - allocated_size

def _regions_to_abs_regions(regions, rom_start, rom_size):
    """Take a list of regions with just size and compute absoute address"""
    wildcard_size = _get_wildcard_size(regions, rom_size)
    offset = rom_start
    seen_wildcards = 0
    for region in regions:
        if region.size is None:
            seen_wildcards += 1
            size = wildcard_size
        else:
            size = region.size
        if seen_wildcards > 1:
            raise LayoutException("Multiple wild card regions found. "
                                  "Only one wild card region allowed.")
        yield Region(region.name, offset, size)
        offset += size


def _size_str_to_value(size_str):
    """Convert a size string to a value or None if wildcard"""
    try:
        if size_str == "*":
            return None
        if size_str[0:2] == "0x":
            return int(size_str[2:], 16)
        else:
            return int(size_str)
    except:
        raise LayoutException("")


def regions_to_common_pairs(regions):
    """Return name, value pairs to be used as defines in the 'common' group

    Positional arguments:
    regions - a list of regions each of with have a name, addr and size
    """
    for region in regions:
        name = region.name.upper()
        yield ("%s_ADDR" % name, region.addr)
        yield ("%s_SIZE" % name, region.addr)


def region_to_ld_pairs(region, rom_start):
    """Return name, value pairs to be used as defines in the 'ld' group

    Positional arguments:
    regions - region to use
    rom_start - address of the starting block of rom
    """
    return [
        ("MBED_APP_START", region.addr),
        ("MBED_APP_SIZE", region.size)
    ]


def regions_with_entry(regions):
    """Get a list of all regions that must be built during a build"""
    return (region for region in regions if region.name.startswith("main"))

def extract_layouts(toolchain, target, layout, base_profile):
    """Extract a profile for the given toolchain

    Positional arguments:
    parser - parser used to parse the command line arguments
    toolchain - the toolchain that the profile should be extracted for
    target - target to extract the layout for
    """
    tc_class = TOOLCHAIN_CLASSES[toolchain]
    common_flags = []
    rom_start, rom_size = _get_target_rom_start_size(target)
    regions = list(layout_to_regions(open(layout, "r"), rom_start, rom_size))
    for name, val in regions_to_common_pairs(regions):
        common_flags.append("-D%s=0x%x" % (name, val))

    for region in regions_with_entry(regions):
        linker_flags = []
        for name, val in region_to_ld_pairs(region, rom_start):
            linker_flags.append(tc_class.make_ld_define(name, val))

        profile_entry = {toolchain: {'c': [], 'cxx': [],
                                     'common': common_flags,
                                     'asm': [], 'ld': linker_flags}}
        new_profile = deepcopy(base_profile)
        new_profile.append(profile_entry)
        return new_profile

def _get_target_rom_start_size(name):
    """Return start and size of first rom region of the target"""
    cache = Cache(True, False)
    device_name = TARGET_MAP[name].device_name #TODO - handle no device name
    target_info = cache.index[device_name]

    roms = [(_str_to_int(info["start"]), _str_to_int(info["size"]))
            for mem, info in target_info["memory"].items() if "ROM" in mem]
    roms.sort(key=lambda entry:entry[0])
    return roms[0]

def _str_to_int(val_str):
    return int(val_str[2:], 16) if val_str[0:2] == "0x" else int(val_str)


