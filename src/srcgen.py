import time
import os
modules = {
    "app_utils": "Miscellaneous Utilities for the Application",
}

nav_modules = {
    "mdio_interrupt": "MDIO Interrupts",
}
listSectionCommon = [
    "INCLUDE FILES",
    "CONFIGURATIONS",
    "MACROS",
    "LITERALS",
    "DATA TYPES",
    "FUNCTION PROTOTYPES",
    "GLOBAL VARIABLES",
    "LUTS",
]
listSectionCSource = []
for i in listSectionCommon:
    listSectionCSource.append(i)
listSectionCSource.append("CODE")
moduledesc = """/* 
 * \\file   {}
 *
 * \\brief  {}
*/
"""
header = """/*
    Author: {} <{}> 

    THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
    WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
    SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
    OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
    IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
    OF SUCH DAMAGE.

    Copyright (c) {} {}.
    All Rights Reserved.
*/
"""
configDict = {
    "modules": modules,
    "moduledesc": moduledesc,
    "author": "XX YY",
    "org": "None",
    "email": "none@none.com",
    "copyright": "XX YY",
    "header": header,
    "disclaimer": "",
    "license": "MIT",
    "lastColumn": 120,
    "listSectionCSource": listSectionCSource,
    "listSectionsCHeader": listSectionCommon,
    "path_prefix": './autogen/',
}


def createHeader():
    pass


def createSource():
    pass


def createFilesWithSections(generate_path, fileName, desc, sectionsList, configDict=configDict):

    ifdefgaurd = fileName.split(".")[0].upper()
    if ".h" in fileName:
        ifdefgaurd = ifdefgaurd + "_H"
    else:
        ifdefgaurd = ifdefgaurd + "_C"

    copy_right_year = time.strftime("%Y", time.localtime())
    with open(generate_path + fileName, "w") as f:
        f.write(configDict["moduledesc"].format(fileName, desc))
        f.write(configDict["header"].format(
            configDict["author"], configDict["email"], copy_right_year,configDict["copyright"]))
        if ".h" in fileName:
            f.write("#ifndef {0}\n#define {0}\n".format(ifdefgaurd))
        else:
            f.write("#ifndef {0}\n#define {0}\n#define __FILENAME_WO_PATH__ \"{1}\"\n".format(ifdefgaurd,fileName))
            
        for sectionName in sectionsList:
            section = sectionName
            sectionLength = len(section)
            offCenter = sectionLength % 2
            sectionLinePadLen = int((configDict["lastColumn"] - sectionLength)/2)
            f.write("/*{}*/\n".format("*"*configDict["lastColumn"]))
            f.write("/*{}*/\n".format(" "*sectionLinePadLen +
                                      section.upper() + " "*(sectionLinePadLen + offCenter)))
            f.write("/*{}*/\n\n\n".format("*"*configDict["lastColumn"]))
        f.write("#endif /* #ifndef {0} */\n".format(ifdefgaurd))

def main(configDict=configDict):
    path_prefix = configDict["path_prefix"]
    try:
        os.mkdir(path_prefix)
    except:
        pass
    print(configDict["modules"])
    for name, desc in configDict["modules"].items():
        print("Generate h file: Sections -->")
        print(listSectionCommon)
        createFilesWithSections(
            path_prefix, name+".h", desc, configDict["listSectionsCHeader"], configDict)
        print("Generate c file: Sections --> ")
        print(configDict["listSectionCSource"])
        createFilesWithSections(
            path_prefix, name + ".c", desc, configDict["listSectionCSource"], configDict)


if __name__ == "__main__":
    main()
