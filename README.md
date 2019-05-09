#c_source_tools  
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

~~~python
#  Example Arguments dict:
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
~~~
