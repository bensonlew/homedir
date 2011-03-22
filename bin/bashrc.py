#!/usr/bin/env python
# ~/bin/bashrc.py

import os
import re
import sys

# This script generates configuration files from the machine independent files
# in the ~/etc directory and machine-specific files in ~/local/$HOSTNAME/etc
# NOTE: this script doesn't source the local .bashrc file; that is done in ~/.bashrc

WARNING = [
    "WARNING: DO NOT EDIT THIS FILE. IT IS AUTOMATICALLY GENERATED BY ~/.bashrc.py",
    "  EDIT FILES IN ~/etc FOR MACHINE-INDEPENDENT CONFIGURATION OR",
    "  FILES IN ~/local/$HOSTNAME/etc FOR MACHINE-SPECIFIC CONFIGURATION",
]
HOSTNAME = os.environ['HOSTNAME']
HOME = os.environ['HOME']
ETCPATH = "%s/etc" % HOME
LOCALETCPATH = "%s/local/%s/etc" % (HOME, HOSTNAME)
COMMENT_CHAR = ["", "#", "!", "//", ";;", "%"]
# don't include wmiirc because it needs the shebang on the first line
PATTERN = r"""
    (^\.hgrc|\.sh|^\.conkyrc|^\.inputrc|^\.screenrc)$|
    (^\.Xdefaults|^\.Xmodmap)$|
    (^\.conkerorrc)$|
    (^\.emacs|\.el)$|
    (^\.mostrc)$
"""
FILELIST_TO_GENERATE = [
    '.Xdefaults',
    '.Xmodmap',
    '.bashrc',
    '.emacs',
    ]

###############################################################################
def main():

    print2stderr("running ~/.bashrc.py...")
    print2stderr("  you are on host %s" % HOSTNAME)
    comment_regex = re.compile(PATTERN, re.VERBOSE)

    # walk through the ~/etc directory and the ~/etc/$HOSTNAME/etc directory,
    # and create a list of files to generate
    filelist = []
    filelist = append_filelist(ETCPATH, filelist)
    filelist = append_filelist(LOCALETCPATH, filelist)

    # generate new files in the home directory
    for filename in filelist:
        if filename not in FILELIST_TO_GENERATE:
            continue
        print2stderr("  generating ~/%s..." % filename)
        homefile = "%s/%s" % (HOME, filename)
        basefile = "%s/%s" % (ETCPATH, filename)
        localfile = "%s/%s" % (LOCALETCPATH, filename)
        folderpath = os.path.dirname(homefile)

        # backup home file, if it exists
        if os.path.isfile(homefile):
            os.rename(homefile, homefile+".bak")

        # create folder path if it doesn't exist
        if not os.path.exists(folderpath):
            print2stderr("  creating directory %s..." % folderpath)
            os.system("mkdir -p %s" % folderpath)

        # create new file and insert the warning header if it is a recognized type
        fh = open(homefile, "w")
        match = comment_regex.search(filename)
        if match:
            comment_char = COMMENT_CHAR[match.lastindex]
            fh.write("%s ~/%s\n" % (comment_char, filename))
            fh.write("\n")
            for line in WARNING:
                fh.write("%s %s\n" % (comment_char, line))
            fh.write("\n")
            fh.close()

        # append base file, if it exists
        if os.path.isfile(basefile):
            os.system("cat %s >> %s" % (basefile, homefile))

        # append local file, if it exists
        if os.path.isfile(localfile):
            os.system("cat %s >> %s" % (localfile, homefile))

        # make it executable
        os.system("chmod +x %s" % homefile)

###############################################################################
def print2stderr(string):
    sys.stderr.write(string+'\n')

###############################################################################
def append_filelist(startpath, filelist):
    """ Walks the path, startpath, and appends files to the list, filelist """
    os.chdir(startpath)
    for (path, dirs, files) in os.walk(startpath):
        path += "/"
        path = path.lstrip(startpath+"/")
        for filename in files:
            if not re.search(r"(^\.bashrc|(^|/)\#.*\#|~|\.bak|\.orig)$", filename):
                filepath = "%s%s" % (path, filename)
                if filepath not in filelist:
                    filelist.append(filepath)
    return filelist

###############################################################################
if __name__ == "__main__":
    main()
