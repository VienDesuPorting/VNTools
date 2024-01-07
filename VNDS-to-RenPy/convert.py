# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Automatically converts VNDS to Ren'Py.

import os
import zipfile
from io import open

# Sets of variables found in the game.
global_variables = set()
game_variables = set()

def unjp(s):
    print(s)
    white = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890"
    for a in s:
        if a not in white:
            s = s.replace(a, str(ord(a)))
    if s[0].isdigit():
        s = "var" + s
    print(s)
    return s

def scan_gsetvar(l):
    l = l.split()[0]
    l = unjp(l)
    global_variables.add(l)

def scan_setvar(l):
    if l[0] == "~":
        return

    l = l.split()[0]
    l = unjp(l)
    game_variables.add(l)

with zipfile.ZipFile("script.zip", 'r') as zip_ref:
    zip_ref.extractall()
    
def scan_script(infn):
    inf = open("script/" + infn, encoding="utf-8")
    
    for l in inf:
        l = l.replace("\xef\xbb\xbf", "")
        l = l.strip()

        if not l:
            continue

        if " " in l:
            command, l = l.split(' ', 1)
        else:
            command = l
            l = ""
            
        if "scan_" + command in globals():
            globals()["scan_" + command](l)

    inf.close()


class ConvertState(object):

    def __init__(self, outf, shortfn=""):
        self.outf = outf
        self.depth = 0
        self.shortfn = shortfn
        self.textbuffer = ""
        self.empty_block = False
        self.imindex = 0
        
    def write(self, s, *args):

        
        self.outf.write("    " * self.depth + "\n")

        line = "    " * self.depth + s % args + "\n"

        if isinstance(line, str):
            line = line.encode("utf-8")

        self.outf.write(line.decode("utf-8"))
        
        self.empty_block = False
        
    def indent(self):
        self.depth += 1

    def outdent(self):
        self.depth -= 1

def convert_endscript(cs, l):
    cs.write("return")

def convert_label(cs, l):
    l = l.replace("*", "_star_")
    l = l.replace("-", "_")
    l = cs.shortfn + "_" + l

    cs.outdent()
    cs.write("label %s:", l)
    cs.indent()

def convert_goto(cs, l):
    l = l.replace("*", "_star_")
    l = cs.shortfn +  "_" + l
    l = l.replace("-", "_")

    cs.write("jump %s", l)
    
def convert_choice(cs, l):
    choices = l.split("|")
    
    cs.write("menu:")
    cs.indent()

    for i, c in enumerate(choices):
        cs.write("%r:", c)
        cs.indent()
        cs.write("$ selected = %d", i + 1)
        cs.outdent()

    cs.outdent()

def convert_setvar(cs, l):
    if l[0] == "~":
        return

    print(f"l = {l}")
    if l == 'chain = "main.scr start"':
        var, op, val = "chain", "=",  "main.scr start"
    else:
        var, op, val = l.split()
    var = unjp(var)
    
    if op == "=":
        cs.write("$ %s = %s", var, val)
    elif op == "+":
        cs.write("$ %s += %s", var, val)
    elif op == "-":
        cs.write("$ %s -= %s", var, val)
    else:
        raise Exception("Unknown operation " + op)

def convert_gsetvar(cs, l):
    if l[0] == "~":
        return

    var, op, val = l.split()
    var = unjp(var)
    
    if op == "=":
        cs.write("$ persistent.%s = %s", var, val)
    elif op == "+":
        cs.write("$ persistent.%s += %s", var, val)
    elif op == "-":
        cs.write("$ persistent.%s -= %s", var, val)
    else:
        raise Exception("Unknown operation " + op)
    
def convert_if(cs, l):
    var, rest = l.strip().split(' ', 1)
    var = unjp(var)

    if var in global_variables:
        var = "persistent." + var

    cs.write("if %s %s:", var, rest)
    cs.indent()

    cs.empty_block = True
    
def convert_fi(cs, l):
    if cs.empty_block:
        cs.write("pass")
    
    cs.outdent()

def convert_sound(cs, l):
    if l == "~":
        cs.write("stop sound")
    else:
        l = "sound/" + l
        cs.write("play sound \"%s\"", l)

def convert_setimg(cs, l):
    fn, x, y = l.split()
    x = int(x)
    y = int(y)
    fn = "foreground/" + fn

    cs.write("show expression %r as i%d at fgpos(%d, %d)", fn, cs.imindex, x, y)
    cs.imindex += 1
    
def convert_delay(cs, l):
    try:
        t = int(l) / 60.0
        cs.write("pause %f", t)
    except:
        pass
    
    
        
def convert_bgload(cs, fn):

    if " " in fn:
        fn, delay = fn.split(" ", 1)
        delay = int(delay) / 60.0
    else:
        delay = 0.5
        
    assert " " not in fn

    cs.write("nvl clear")
    fn = "background/" + fn
    cs.write("scene expression %r", fn)
    cs.imindex = 0

    if delay:
        cs.write("with Dissolve(%f)", delay)
    
def convert_jump(cs, fn):
    if " " in fn:
        fn, l = fn.split(" ", 1)
        l = l.replace("*", "_star_")
        l = l.replace("-", "_")
        fn = fn.replace(".scr", "").replace("-", "_")
        cs.write("jump %s_%s", fn, l)
        return

    fn = fn.replace(".scr", "").replace("-", "_")
    cs.write("jump %s", fn)
        
def convert_music(cs, fn):
    if " " in fn:
        fn, loops = fn.split(" ", 1)
    else:
        loops = 0

    if int(loops) > 0:
        noloop = " noloop"
    else:
        noloop = ""
        
    if fn == "~":
        cs.write("stop music")
    else:
        fn = "sound/" + fn
        cs.write("play music %r%s", fn, noloop)
        
def convert_text(cs, text):

    while text and (text[0] == "~" or text[0] == "!"):
        text = text[1:]

    if not text:
        return

    if text[0] == "@":
        cs.textbuffer += text[1:] + "\n"
        return

    text = cs.textbuffer + text
    text = text.replace("\\", "\\\\")
    text = text.replace("\"", "\\\"")
    text = text.replace("\n", "\\n")
    
    cs.write('"%s"', text) 
    cs.textbuffer = ""

def convert_script(infn):
    dir_rp = "rpy/"
    if not os.path.exists(dir_rp):
        os.mkdir(dir_rp)

    if os.path.exists(dir_rp):
        shortfn = infn.replace(".scr", "")
        shortfn = shortfn.replace("-", "_")
        inf = open("script/" + infn, encoding="utf-8")
        outf = open (dir_rp + shortfn + ".rpy", "w", encoding = "utf-8")
        cs = ConvertState(outf, shortfn)
        cs.write("label %s:", shortfn)
        cs.indent()

    for l in inf:
        l = l.replace("\xef\xbb\xbf", "")
        l = l.strip()

        if not l:
            continue

        if l[0] == "#":
            continue

        if " " in l:
            command, l = l.split(' ', 1)
        else:
            command = l
            l = ""

        if "convert_" + command in globals():
            globals()["convert_" + command](cs, l)
        else:
            print("Unknown command", repr(command), repr(l), repr(infn))

    outf.close()

def main():
    for i in os.listdir("script"):
        if not i.endswith(".scr"):
            continue

        scan_script(i)

    for i in os.listdir("script"):
        if not i.endswith(".scr"):
            continue

        convert_script(i)

    outf = open("rpy/_start.rpy", "w", encoding="utf-8")
    cs = ConvertState(outf)
    cs.write("init python:")
    cs.indent()
    
    for i in global_variables:
        i = unjp(i)
        cs.write("if persistent.%s is None:", i)
        cs.indent()
        cs.write("persistent.%s = 0", i)
        cs.outdent()

    # prevent non-empty block.
    cs.write("pass")
        
    cs.outdent()
    cs.write("label start:")
    cs.indent()

    for i in game_variables:
        i = unjp(i)
        cs.write("$ %s = 0", i)

    cs.write("window show")
    cs.write("jump main")
        
    cs.outdent()        
    outf.close()

if __name__ == "__main__":
    main()
