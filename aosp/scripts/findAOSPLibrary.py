#!/usr/bin/python
import os 
os.system('find ./*  -iname "*.mk" > .directory')
with open(".directory") as f:
    mkfs = f.readlines()
    for mkf in mkfs:
        mkfn = mkf.strip()
        with open(mkfn) as f1:
        # print "analyse file:%s" % f1.name
            s = f1.read()
            if s.find("E := lib") > 0:
                libname = s[s.index("E := lib"):][3:s[s.index("E := lib"):].index("\n")]
                print "lib: {:<50} \tmk: {:<}" .format(libname,f1.name)

os.remove(".directory")