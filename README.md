# c_source_tools  
===
## MIT License  

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

## Cmake Generator Source Core in Python.  
This software can be used to generate a Cmake Make include file(**args['CmakeIncludes']**)
suitable for importing into the main(root)  
'CmakeLists.txt' with the following features:  
* Exclude file / folders as per exclude list paths  
* install header search paths as configured in arguments **args[application_libraries]**   
  add 'add_library' directive as configured in the arguments for each subfolder,  
  * recursively add each (sub)-subfolder via 'subdirs' if it contains Source  
    files as specified by **args['pattern']**  
  * Automatically generate the Library name & add all files in (sub)-subfolder  
    to the subfolder named library name basis path  
  * add a 'CmakeLists.txt' into the folder for each listed (sub)-subfolder  
  * ignores files / paths as specified in argument via **args['exclude']**  
  * add 'target_compile_definitions' for directory specific files    
  * Link all the included 'subfolders' via 'target_link_libraries' directives    

## c_source_tools in detail
<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

### Arguments Keyword Glossary

|Key word|type|Description|Quick Example|
|---|---|---|---|
|root |path |Root of the Project.<br>All paths are relative to this| `args['c-flags'] = os.cwd()`<br>`args['c-flags'] = /home/me/myself/and/irene`
|c-flags |list|Tokens to be defined with '-D'| `args['c-flags'] = [`<br>`                                 "__IAR_SYSTEMS_ICC__=1",`<br>`                              ] `|
|prefix|string|Unused| NA
|application_libs|dict|Include Paths to include with -I|`{`<br>`'application':   [`<br>`     'src/inc',`<br>`    'src/prt',`<br>`],`<br>`}`
|suf|path|Unused||
|pattern|list|Pattern of files to look for|example `[*.s,*.S,*.c,*.h]`|
|headers|list|Extension of Header files, so as to not add to the Cmake add_sources directive|`[*.h,*.hpp]`
|sources|list|Extension of Header files, so as to add to the Cmake add_sources directive|`[*.c,*.s,*.S]`|
|exclude|list|Patterns to ignore in the path|`[*.c,*.s,*.S]`|   
|CmakeIncludes|string|Name of the file to generate|`'CmakeIncludes.cmake'`
|subfolders|list|Target include folders to parse for files as per 'pattern'<br>Format of sublist:<br>* folder:required<br>* #defines: optional|`[['src','TARGET_HW=AVR],]'`|<br>

## Requirements to be added

|Key word|type|Quick Example|
|---|---|---|
|asm_source_ext|string|`args['asm_source_ext'] = ['*.s']`<br>`args['asm_source_ext'] = ['*.s','*.s90','*.S']`|<br>
|app_targets|list|Under Dev|<br>

### Multiple Targets

For a Project **P1** and a library **L1** and a target '**T1**', c_source_tools will generate a **Target Library** definition with the name '**L1.T1**' for Target '**${PROJECT}.T1**'
Example below:

```CMake
add_library(L1.+3V+LIC+IRR "")
target_compile_options(L1.+3V+LIC+IRR PUBLIC "--preinclude \"${PROJECT_SOURCE_DIR}/+3V-IRR-LIC.txt\"")
add_target(${PROJECT}.+3V+LIC+IRR)
```

Format required in **c_source_tools** args file as below:<br>
|Key word|type|Quick Example|
|---|---|---|
|APP_TARGETS |list of dicts| `{ 'app_targets' : [{ 'T1' : { TYPE:PUBLIC } , { FLAGS:['List','of','Target','Options'] } }]`


An Example in for usage!

```Python
{ 'app_targets' : [{ '+3V+LIC+IRR' : { TYPE:PUBLIC } , { FLAGS:['--preinclude ${PROJECT_SOURCE_DIR}/+3V-IRR-LIC.txt']} }]
```

### Assembler Source Separation

Flags are needed for separating the Assembler files from C Files as the compiler unlike GCC does not invoke the assembler. Let assembler files be compiled into another library all together.

## Arguments in detail

### root - Directory Start Point

Defined by the keyword '**root**'

### c-flags - Application wide Complie Flags

These are global symbols to be defined on the commandline with a '-D'

## Example in use

Have a look around in the [AM335X-FreeRTOS-lwip|https://github.com/kryochronic/AM335X-FreeRTOS-lwip] to use the c\_source\_tools

### Example Arguments dict:

```Python
def make_args(root=None):
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
```
