"""
mbed SDK
Copyright (c) 2016 ARM Limited

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

import sys
from os.path import join, abspath, dirname, exists

LAYOUT_FILE = "layout.txt"

def patch_tools():
    CUSTOM = abspath(join(dirname(__file__), "custom"))
    sys.path.insert(0, CUSTOM)
    ROOT = abspath(join(dirname(__file__), "tools"))
    sys.path.insert(0, ROOT)
    import argparse
    parse_args_old = argparse.ArgumentParser.parse_args
    def parse_args(*args, **kwargs):
        global old_prepare
        import tools.build_api as build_api
        if build_api.prepare_toolchain is not prepare_toolchain:
            old_prepare = build_api.prepare_toolchain
            build_api.prepare_toolchain = prepare_toolchain
        return parse_args_old(*args, **kwargs)
    argparse.ArgumentParser.parse_args = parse_args
    def prepare_toolchain(src_paths, build_dir, target, toolchain_name, *args, **kwargs):
        global old_prepare
        from app_layout import extract_layouts
        build_profile = kwargs.get('build_profile', [])
        if exists(LAYOUT_FILE):
            build_profile = extract_layouts(toolchain_name, target, LAYOUT_FILE, build_profile)
        kwargs['build_profile'] = build_profile
        toolchain = old_prepare(src_paths, build_dir, target, toolchain_name, *args, **kwargs)
        return toolchain


patch_tools()

##############################################################################
# Build System Settings
##############################################################################
#BUILD_DIR = abspath(join(ROOT, "build"))

# ARM
#ARM_PATH = "C:/Program Files/ARM"

# GCC ARM
#GCC_ARM_PATH = ""

# GCC CodeRed
#GCC_CR_PATH = "C:/code_red/RedSuite_4.2.0_349/redsuite/Tools/bin"

# IAR
#IAR_PATH = "C:/Program Files (x86)/IAR Systems/Embedded Workbench 7.0/arm"

# Goanna static analyser. Please overload it in private_settings.py
#GOANNA_PATH = "c:/Program Files (x86)/RedLizards/Goanna Central 3.2.3/bin"

#BUILD_OPTIONS = []

# mbed.org username
#MBED_ORG_USER = ""
