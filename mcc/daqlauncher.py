#!/usr/bin/python

from Tkinter import *
import os
import sys

root = Tk()
root.title("DAQ Launcher")
frame = Frame(root)
frame.pack()

def fs():
    os.system('python finite_scan.py')

def cs():
    os.system('python continuous_scan.py')

def fswt():
    os.system('python finite_scan_with_trigger.py')

def svr():
    os.system('python single_value_read.py')

def tc():
    os.system('python /home/pi/DataBox/thermo/simpletest.py')

bottomframe = Frame(root)
bottomframe.pack( side = BOTTOM )

finitebutton = Button(frame, text="Finite Scan", command=fs)
finitebutton.pack( side = LEFT)

continuousbutton = Button(frame, text="Continuous Scan", command=cs)
continuousbutton.pack( side = LEFT )

fcwtbutton = Button(frame, text="Finite Scan w/Trigger", command=fswt)
fcwtbutton.pack( side = LEFT )

singlevaluebutton = Button(frame, text="Single Value Read", command=svr)
singlevaluebutton.pack( side = LEFT )

utilsbutton = Button(frame, text="Thermocouple Data", command=tc)
utilsbutton.pack( side = BOTTOM )

root.mainloop()