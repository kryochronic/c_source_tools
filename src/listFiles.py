#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Following ignore list for PEP8 for Formatting "--ignore=E501,E126,E241,E221"

"""
MIT License

Copyright (c) [2019] [Abhinav Tripathi] "mr dot a dot tripathi at gmail dot com"

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Cmake Generator Source Core in Python.
This software can be used to generate a Cmake Make include file(*args['CmakeIncludes']*) suitable for importing into the main(root)
'CmakeLists.txt' with the following features:
    # Exclude file / folders as per exclude list paths
    # install header search paths as configured in arguments (application_libraries)
    # add 'add_library' directive as configured in the arguments for each subfolder,
        # recursively add each (sub)-subfolder via 'subdirs' if it contains Source
          files as specified by *args['pattern']*
        # Automatically generate the Library name & add all files in (sub)-subfolder
          to the subfolder named library name basis path
        # add a 'CmakeLists.txt' into the folder for each listed (sub)-subfolder
        # ignores files / paths as specified in argument via *args['exclude']*
    # add 'target_compile_definitions' for directory specific files
    # Link all the included 'subfolders' via 'target_link_libraries' directives

    Example Arguments dict:

def make_args(root=none):
    if root is None:
        root = os.getcwd()
    args['application_libs'] = {
                                        'lwip':             [
                                                                'amazon-freertos/lib/third_party/lwip',
                                                            ],
                                        'ti_starterware':   [
                                                                'ti_starterware/include',
                                                            ],
                                        'application':      [
                                                                'src',
                                                            ],
                                        'aws':              [
                                                                'amazon-freertos/lib/include',
                                                                'amazon-freertos/lib/include/private',
                                                            ],
                                    }
    args['suf']     = ''
    args['pattern'] = ['*.c', '*.h', '*.S']
    args['exclude'] =   [
                        #path to exclude
                        'binary',
                        'fatfs/port',
                        # File names to ignore
                        'some_specific_c_file.c',
                        ]

    args['root']           = root
    args['CmakeIncludes']  = "ProjectIncludes.cmake" # the name of the CMAKE INCLUDE FILE to generate
    if subfolders is None:
        args['subfolders'] = [ # a list in the form of [['path/to/traverse','FLAGS NEEDED'],]
                            ['some/thirdparty/lib/drivers', '-DBOOT=MMCSD -DCONSOLE=UARTCONSOLE'],
                            ['src', '-DBOOT=MMCSD -DCONSOLE=UARTCONSOLE'],
                            ['another/thirdparty/lib/bufferpool'],
                            ['yet/another/lib/OSetc'],
                            ['yet/another/lib/some/subfolder'],
                        ]
    return args

"""


import os
import traceback
from fnmatch import fnmatch
from time import sleep
from functools import reduce
import importlib
import importlib.util
import sys







def normalise_path_to_unix(path):
    path = path.replace('\\', '/')
    if path.find('/') == 0:
        path = path[1:]
        pass
    return path


def list_files(root=os.getcwd(), exclude=[], pattern=['*.c', '*.h', '*.s']):
    files_list = {}
    excluded_folders = []
    for path, subdirs, files in os.walk(root):
        base = path.replace('\\', '/')
        include_folder = True
        for x in exclude:
            if x in base and x not in root:
                include_folder = False
                excluded_folders.append(base)
                break
        if include_folder:
            for name in files:
                for filetype in pattern:
                    if fnmatch(name, filetype):
                        if path not in files_list.keys():
                            files_list[path] = []
                        if name not in exclude:
                            files_list[path].append(name)
    return files_list


def make_cmake_includes_paths_list(filepath, paths, lib_name, addsubdir=True, addlib=True, folder_flags=None):
    text_lib_name = """#adding entries for {}\n"""
    text_inc = '\tinclude_directories("${{PROJECT_SOURCE_DIR}}/{}")\n'
    text_sub = '\tsubdirs("${{PROJECT_SOURCE_DIR}}/{}")\n'
    text_add_lib = '\tadd_library({} "")\n'
    text_add_lib_flags = '\ttarget_compile_definitions({} \n\t\tPRIVATE {}\n\t)\n' #{0} = name, {1} = flags

    paths = list(map(normalise_path_to_unix, paths))
    with open(filepath, "a") as f:
        f.write(text_lib_name.format(lib_name))
        for path in paths:
            f.write(text_inc.format(path))
        if True is addlib:
            f.write(text_add_lib.format(lib_name))
            if folder_flags is not None:
                f.write(text_add_lib_flags.format(lib_name, folder_flags))
        if True is addsubdir:
            for path in paths:
                f.write(text_sub.format(path))


def make_cmake_includes_for_third_party_libs(args):
    libnames = args['application_libs']
    includes_file_name = os.path.join(args['root'], args['CmakeIncludes'])
    for lib_name in libnames.keys():
        paths = libnames[lib_name]
        make_cmake_includes_paths_list(includes_file_name, paths, lib_name, addsubdir=False, addlib=False)


def make_cmake_lists_for_lib(prefix, suffix, filepath, files_list):
    text = """
target_sources({0}
                PUBLIC
{2}
            )
"""
    file_entry_text = ' ' * 20 + '"${{CMAKE_CURRENT_SOURCE_DIR}}/{}"\n'
    c_files_list = []
    for x in files_list:
        if '.h' not in x:
            c_files_list.append(x)

    if len(c_files_list) > 0:
        files_list_to_write = list(map(lambda x: file_entry_text.format(x), c_files_list))
        lines = reduce((lambda x, y: x + y), files_list_to_write)

        with open(filepath, "w") as f:
            f.write(text.format(prefix, suffix, lines))


def make_cmake_lists_forfolder(args):
    pre = args['prefix']
    suf = args['suf']
    pattern = args['pattern']
    exclude = args['exclude']
    root = args['root']
    current_folder = args["current_folder"]
    target_path = os.path.join(root, current_folder)
    folder_flags = args["current_folder_flags"]
    try:
        files_list = list_files(target_path, exclude=exclude, pattern=pattern)
        for key in files_list.keys():
            print('{}'.format(normalise_path_to_unix(key.replace(root, ''))))
            for filename in files_list[key]:
                print('\t{}'.format(filename))
        includes_file_name = os.path.join(root, args['CmakeIncludes'])
        paths = list(map(lambda x: x.replace(root, ''), files_list.keys()))
        paths = list(map(lambda x: x.replace('\\', '/'), paths))
        make_cmake_includes_paths_list(includes_file_name, paths, pre, folder_flags=folder_flags)
        for path in files_list.keys():  # prepare CmakeLists for the library
            file_path = os.path.join(path, 'CmakeLists.txt')
            make_cmake_lists_for_lib(pre, suf, file_path, files_list[path])

    except Exception as e:
        traceback.print_exc()
    finally:
        pass
    return includes_file_name


def make_generate_cmake_project_includes(default_args):
    args = default_args
    includes_file_name = os.path.join(args['root'], args['CmakeIncludes'])
    with open(includes_file_name, "w") as f:
        f.write("")
    make_cmake_includes_for_third_party_libs(args)
    libs_dep_list = " "
    for sub_list in args['subfolders']:
        sub = sub_list[0]
        if len(sub_list) > 1:
            args["current_folder_flags"] = sub_list[1]
        else:
            args["current_folder_flags"] = None
        args['prefix']            = sub.replace('\\', '/').replace('/', '_')
        libs_dep_list             = libs_dep_list + '\n\t' + (args['prefix'])
        args['current_folder']    = os.path.join(args['root'], sub)
        make_cmake_lists_forfolder(args)
    
    text_lib_dependencies = """\ntarget_link_libraries (${{PROJECT_NAME}}.elf\n\t{}\n)"""
    print('Adding the following libs as dependencies -->\n\n{}\n\n\tinto {}\n\nThis Should link all your sources specified.\nEnjoy\n--<Abhinav Tripathi>"mr.a.tripathi@gmail.com"'.format(libs_dep_list,includes_file_name))
    with open(includes_file_name, "a+") as f:
        f.write(text_lib_dependencies.format(libs_dep_list))


def main(args_file_name, subfolders=None, path=None):
    args_file_name = normalise_path_to_unix(args_file_name)
    file_path, module_name = os.path.split(args_file_name)
    sys.path.append(file_path)
    print("Importing {} from ".format(module_name, file_path))
    module = __import__(module_name.replace('.py', ''))
    default_args = module.cmake_list_file_args(subfolders=None, path=None).args
    make_generate_cmake_project_includes(default_args)

def parse_args_file_name(args_file=None):
    """Looks for arguments file in the cli arguments.

    :param args_file: Need this file for making Cmake makefiles.
    """
    if args_file:
        main(args_file_name=args_file, path=os.getcwd())
        return 'Parsed {} and wrote the Cmake files'.format(args_file)
    else:
        print("No args file supplied. Please supply args_file")
        return 'Phat Gaya'

if __name__ == '__main__':
    try:
        from clize import run
        rv = run(parse_args_file_name)
        print(rv)
    except SystemExit as e:
        pass
else:
    print("listfiles.py: Included as a module. The ideal way!")