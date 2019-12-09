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
    args['headers'] = ['.h']
    args['sources'] = ['.c','.S']
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
# import importlib
# import importlib.util
import sys
import uuid 

issues_list = []


def get_app_targets(args):
    targets = None
    if 'app_targets' in args.keys():
        targets = args['app_targets']
    return targets
    

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


def make_cmake_includes_paths_list(filepath, paths, lib_name, addsubdir=True, addlib=True, folder_flags=None,targets=None):
    text_lib_name = """#adding entries for {}\n"""
    text_inc = '\tinclude_directories("${{PROJECT_SOURCE_DIR}}/{}")\n'
    text_sub = '\tsubdirs("${{PROJECT_SOURCE_DIR}}/{}")\n'
    text_add_lib = '#adding new target_lib\n\tadd_library({0} "")\n'
    
    # {0} = name, {1} = flags
    fmt_text_add_compile_defs = '\ttarget_compile_definitions({} \n\t\tPRIVATE {}\n\t)\n'
    fmt_text_compile_lang_generator = ' $<$<COMPILE_LANGUAGE:{}>:' # CXX,C,ASM CSharp etc ...
    fmt_text_add_target_properties = '\tset_target_properties({} PROPERTIES LINKER_LANGUAGE {}})\n'
    #$<$<COMPILE_LANGUAGE:CXX>:
    fmt_text_add_compile_options = '\ttarget_compile_options({} {} {}\n\t)\n'
    
    paths = list(map(normalise_path_to_unix, paths))
    with open(filepath, "a") as f:
        f.write(text_lib_name.format(lib_name))
        for path in paths:
            f.write(text_inc.format(path))
        if True is addlib:
            if len(targets) is 0:
                f.write(text_add_lib.format(lib_name))
                f.write(fmt_text_add_target_properties.format(lib_name))
                if folder_flags is not None:
                    f.write(fmt_text_add_compile_defs.format(lib_name, folder_flags))
            else:    
                for target in targets:
                    lib_target = "{}.{}".format(lib_name,target)
                    f.write(text_add_lib.format(lib_target))
                    for option_dict in targets[target]:
                        option_type = option_dict['TYPE']
                        flags_lines = map(lambda x: "\n\t\t{} {}".format(option_type,x), option_dict['FLAGS'])
                        flags_lines = ''.join(flags_lines)
                        text_compile_lang_generator = ''
                        if 'LANG' in option_dict:
                            for lang in option_dict['LANG']:
                                text_compile_lang_generator = fmt_text_compile_lang_generator.format(lang)
                                f.write(fmt_text_add_compile_options.format(lib_target,text_compile_lang_generator,flags_lines))
                    
                    # text_add_target_properties = fmt_text_add_target_properties.format(lang)
                    # f.write(text_add_target_properties.format(lib_target))
                    if folder_flags is not None:
                        f.write(fmt_text_add_compile_defs.format(lib_target, folder_flags))
            
        if True is addsubdir:
            for path in paths:
                f.write(text_sub.format(path))

def update_cmake_c_flags(filepath, flag):
    c_flags_update_string = '\n#adding c-flags({0}) from arguments\n\tset(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -D{0}")\n'
    with open(filepath, "a") as f:
        f.write(c_flags_update_string.format(flag))

def make_cmake_includes_for_cflags(args):
    cflags_list = []
    includes_file_name = os.path.join(args['root'], args['CmakeIncludes'])
    if 'c-flags' in args.keys():
        cflags_list = args['c-flags']
    for flag in cflags_list:
        update_cmake_c_flags(
            includes_file_name, flag)


def make_cmake_includes_for_third_party_libs(args):
    libnames = args['application_libs']
    includes_file_name = os.path.join(args['root'], args['CmakeIncludes'])
    for lib_name in libnames.keys():
        paths = libnames[lib_name]
        make_cmake_includes_paths_list(
            includes_file_name, paths, lib_name, addsubdir=False, addlib=False,targets=None)


def populate_target_sources_lang(prefix, suffix, filepath, files_list,source_exts,targets,uid,visibility="PUBLIC",lang="C"):
    text = """
target_sources({0}
                {3}
{2}
            )
"""
    src_visibility = visibility
    src_list_name_uid = "{}_src_list_{}".format(lang,uid).replace('-','')
    src_list_var_cmake = "${{{}}}".format(src_list_name_uid)
    text_source_list = "set({} {}\n)\n"
    file_entry_text = '\n' + 20 * ' ' + '"${{CMAKE_CURRENT_SOURCE_DIR}}/{}"'
    src_files_list = []
    for x in files_list:
        for source_ext in source_exts:
            if x.endswith(source_ext):
                src_files_list.append(x)

    if len(src_files_list) > 0:
        files_list_to_write = list(
            map(lambda x: file_entry_text.format(x), src_files_list))
        lines = reduce((lambda x, y: x + y), files_list_to_write)
        set_src_list = text_source_list.format(src_list_name_uid,lines)
        with open(filepath, "a+") as f:
            f.write(set_src_list)
            if targets is None:
                f.write(text.format(prefix, suffix, src_list_var_cmake,visibility))
            else:
                for target in targets:
                    prefix_target = "{}.{}".format(prefix,target)
                    f.write(text.format(prefix_target, suffix, src_list_var_cmake,src_visibility))
                    
def populate_target_sources(prefix, suffix, filepath, files_list, args):
    source_exts=args['sources']
    visibility=args["CMAKE_SOURCE_PROPERTY"]
    targets = get_app_targets(args)
    uid = uuid.uuid1().replace('-','')
    lang = "C"
    for ext in source_exts:
        if ext in args['sources_asm']:
            lang = 'ASM'
        populate_target_sources_lang(prefix, suffix, filepath, files_list,ext,targets,uid,visibility,lang)

    

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
        includes_file_name = get_cmake_includes_file_names(args)
        paths = list(map(lambda x: x.replace(root, ''), files_list.keys()))
        paths = list(map(lambda x: x.replace('\\', '/'), paths))
        targets = get_app_targets(args)
        make_cmake_includes_paths_list(
            includes_file_name, paths, pre, folder_flags=folder_flags,targets=targets)
        for path in files_list.keys():  # prepare CmakeLists for the library
            file_path = os.path.join(path, 'CMakeLists.txt')
            try:
                os.remove(file_path)
            except:
                """file doesnt exist"""
                pass
            make_cmake_lists_for_lib(
                pre, suf, file_path, files_list[path], args)

    except Exception as e:
        traceback.print_exc()
    finally:
        pass
    return includes_file_name

def get_cmake_includes_file_names(args):
    return os.path.join(args['root'], args['CmakeIncludes'])

def make_generate_target_execs(args):
    targets = get_app_targets(args)
    includes_file_name = get_cmake_includes_file_names(args)

    with open(includes_file_name, "a+") as f:
        print('Adding the following targets as exectuables into {}'.format(includes_file_name))
        if targets is None:
            print('Single Target\n')
            text_add_exec = """\n\tadd_executable(${{PROJECT_NAME}}.${{BUILD_EXT}} "")"""
            f.write(text_add_exec)
        else:
            targets_count = 0 
            text_add_exec = """\n#Adding targetExec #{}\n\tadd_executable(${{PROJECT_NAME}}.{}.${{BUILD_EXT}} "")\n"""
            for target in targets:
                print('Add Target:[{}]\n'.format(target))
                f.write(text_add_exec.format(targets_count,target))
                targets_count += 1



def make_generate_target_link_libs(args):
    targets = get_app_targets(args)
    includes_file_name = get_cmake_includes_file_names(args)
    libs_dep_list = args['lib_dep_list']
    with open(includes_file_name, "a+") as f:
        if targets is None:
            text_lib_dependencies = """\ntarget_link_libraries (${{PROJECT_NAME}}.${{BUILD_EXT}}\n\t{}\n)"""
            print('Adding the following libs as dependencies -->\n\n{}\n\n\tinto {}\n\nThis Should link all your sources specified.\nEnjoy\n--<Abhinav Tripathi>"mr.a.tripathi@gmail.com"'.format(libs_dep_list, includes_file_name))
            f.write(text_lib_dependencies.format(libs_dep_list))
        else:
            text_lib_dependencies = """\ntarget_link_libraries (${{PROJECT_NAME}}.{}.${{BUILD_EXT}}\n\t{}\n)"""
            for target in targets:
                libs_target_list =  ["{}.{}".format(element,target) for element in libs_dep_list.strip().split('\n')]
                libs_target = '\n\t'.join(libs_target_list)
                print('Adding the following libs as dependencies -->\n\n{}\n\n\tinto {}\n\nThis Should link all your sources specified.\nEnjoy\n--<Abhinav Tripathi>"mr.a.tripathi@gmail.com"'.format(libs_target , includes_file_name))
                f.write(text_lib_dependencies.format(target,libs_target))

def make_generate_cmake_project_includes(default_args):
    args = default_args
    targets = get_app_targets(args)
    target_add_source_default = "PUBLIC" 
    includes_file_name = get_cmake_includes_file_names(args)
    with open(includes_file_name, "w") as f:
        f.write("")
    make_generate_target_execs(args)
    make_cmake_includes_for_cflags(args)
    make_cmake_includes_for_third_party_libs(args)
    libs_dep_list = " "
    for sub_list in args['subfolders']:
        if len(sub_list) > 0:
            sub = sub_list[0]
            if len(sub_list) > 1:
                sub = sub_list[0]
                args["current_folder_flags"] = ""
                for token in sub_list:
                    if "-D" in token:
                        args["current_folder_flags"] += token
                    if "CMAKE_SOURCE_PROPERTY" in token:
                        try:
                            flag  = token.split(":")[1]
                            if flag in ["PUBLIC","PRIVATE"]:
                                args["CMAKE_SOURCE_PROPERTY"] = flag
                            else:
                                args["CMAKE_SOURCE_PROPERTY"] = "PUBLIC"
                                issue = "{} : token {} is not in format CMAKE_SOURCE_PROPERTY:PUBLIC/PRIVATE, setting to PUBLIC".format(sub,token)
                                issues_list.append(issue)
                                print(issue)
                        except Exception as e:
                            print("token {} is not in format CMAKE_SOURCE_PROPERTY:PUBLIC/PRIVATE")
                            raise e
                
            else:
                sub = sub_list[0]
                args["current_folder_flags"] = None
            # Failsafes
            if "current_folder_flags" not in args.keys():
                args["current_folder_flags"] = None
            if "CMAKE_SOURCE_PROPERTY" not in args.keys():
                if 'target_add_source_default' in args.keys():
                    target_add_source_default = args['target_add_source_default']
                if target_add_source_default in ["PUBLIC","PRIVATE"]:
                    args["CMAKE_SOURCE_PROPERTY"] = target_add_source_default
                else:
                    print("token {} is not in format CMAKE_SOURCE_PROPERTY:PUBLIC/PRIVATE, setting to PUBLIC",target_add_source_default)
                    target_add_source_default = "PUBLIC"
            
            args['prefix'] = sub.replace('\\', '/').replace('/', '_')
            libs_dep_list = libs_dep_list + '\n\t' + (args['prefix'])
            args['lib_dep_list'] = libs_dep_list
            args['current_folder'] = os.path.join(args['root'], sub)
            make_cmake_lists_forfolder(args)
        
    
    

    make_generate_target_link_libs(args)
    if len(issues_list) > 0:
        print('{} Issue(s) / Warning(s) Found\n--<Listed Below>--\n'.format(len(issues_list)))
        issue_no = 1
        for issue in issues_list:
            print('\t{}: {}'.format(issue_no,issue))


def main(args_file_name, subfolders=None, path=None):
    args_file_name = normalise_path_to_unix(args_file_name)
    file_path, module_name = os.path.split(args_file_name)
    sys.path.append(file_path)
    print("Importing {} from {}".format(module_name, file_path))
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
        run(parse_args_file_name)
        print("Done")
    except SystemExit as e:
        pass
else:
    print("listfiles.py: Included as a module. The ideal way!")
