#!/usr/bin/env python
"""For demonstrating the usage of Newton's Method (Newton Raphson Method)
to solve DC operating point of a circuit with non-linear components.
The only supported non-linear device here is a certain kind model of diode.
All the derivative linear DC analysis jobs of the Newton's iterations are
passed to another demo program iccad_mna.py.
"""

import sys
import numpy as np
import math
import os
import re

# The theory of linear companion model of diode is based on,
# http://ecircuitcenter.com/SpiceTopics/Non-Linear%20Analysis/Non-Linear%20Analysis.htm
# choose Is and Vt of the certain diode model the two values below:
Is_dmodel = 1e-14  # i.e. 10fA
Vt_dmodel = 0.026  # i.e. 26mV

# 4 diode formula functions defined below
def I_d(V_d):
    return Is_dmodel * (math.exp(V_d / Vt_dmodel) - 1)

def G_eq(V_d):
    return Is_dmodel / Vt_dmodel * math.exp(V_d / Vt_dmodel)

def R_eq(V_d):
    return 1.0 / G_eq(V_d)

def I_eq(V_d):
    return I_d(V_d) - G_eq(V_d) * V_d


class Newton:
    inputFileName = ""  # circuit file name
    parseReady = False
    found_diodes = []  # diode cards in the circuit
    non_diode_lines = []  # all other cards in the circuit
    equ_diode_lines = []  # linearly equivalent Geq and Ieq for diodes

    # initially guess all Vd = 1V
    # also try like Vd = 0, and compare the converging speeds
    init_diode_Vd = 1

    # set absolute voltage tolerance = 1uV to stop iteration; neither
    # current tolerance nor relative tolerance being considered here
    volt_tolerance = 1e-6

    # node_volt_iter0 and node_volt_iter1 each saves the 1st and 2nd
    # DC analysis node voltage result for any two consecutive iterations
    node_volt_iter0 = {"0": 0,
                       "GND": 0}
    node_volt_iter1 = {"0": 0,
                       "GND": 0}

    def __init__(self, fileName=""):
        self.parseReady = False
        if fileName:
            self.inputFileName = fileName
            self.parseFile()

    def inputFile(self):
        if len(sys.argv) > 1:  # use file name in command line
            self.inputFileName = sys.argv[1]
            print("Input circuit file name for analyzing is: %s"
                  % (self.inputFileName))
        else:
            # use raw_input() in Python 2, but input() in Python 3
            self.inputFileName = input(
                "Input circuit file name for analyzing: ")

    def parseFile(self):
        with open(self.inputFileName) as netlist:
            self.found_diodes = []
            for line in netlist.readlines():
                # parse the line into a word list
                wl = line.upper().strip().split()
                # ignore all lines except those beginning with 'd/D'
                # and having at least 3 fields
                if len(wl) >= 3 and wl[0].startswith('D'):
                    self.found_diodes.append((wl[0], wl[1], wl[2]))
                else:  # Just pass all other lines to non-diode card list
                    self.non_diode_lines.append(line.replace("\n", ""))
            self.parseReady = True

    def reportStatus(self):
        if self.parseReady == True:
            print(self.found_diodes)
            print(self.non_diode_lines)
            print(self.equ_diode_lines)
            print(self.node_volt_iter0)
            print(self.node_volt_iter1)

    def initGuess(self):
        if self.parseReady != True:
            return
        # guess all diodes working on a predefined initial value
        self.equ_diode_lines = []
        for (dname, dnode1, dnode2) in self.found_diodes:
            self.equ_diode_lines.append("Requ_%s %s %s %e"
                                        % (dname, dnode1, dnode2,
                                           R_eq(self.init_diode_Vd)))
            self.equ_diode_lines.append("Iequ_%s %s %s %e"
                                        % (dname, dnode1, dnode2,
                                           I_eq(self.init_diode_Vd)))

    def createLinearFile(self, fName):
        # create a linearized netlist for DC simulation
        with open(fName, "w") as f:
            print(*self.non_diode_lines, sep="\n", file=f)
            print(*self.equ_diode_lines, sep="\n", file=f)

    def runMNAnalysis(self, finName, foutName):
        return os.system("python iccad_mna.py %s > %s" % (finName, foutName))

    def readbackNodeResult(self, fName, node_volt_dic):
        with open(fName) as fout:
            for line in fout.readlines():
                if re.match("^node .+", line):
                    node_args = re.split(" ", line.replace("\n", ""))
                    n_name = re.sub(":$", "", node_args[1])
                    n_volt = re.sub("V$", "", node_args[2])
                    node_volt_dic[n_name] = float(n_volt)  # save voltage

    def continueGuess(self):
        if self.parseReady != True:
            return
        # apply all diodes's Vd from Iter0 dictionary
        self.equ_diode_lines = []
        for (dname, dnode1, dnode2) in self.found_diodes:
            v1 = self.node_volt_iter0[dnode1]
            v2 = self.node_volt_iter0[dnode2]
            vd = v1 - v2
            print(dname, ": guessed Vd = ", vd)
            self.equ_diode_lines.append("Requ_%s %s %s %e"
                                        % (dname, dnode1, dnode2, R_eq(vd)))
            self.equ_diode_lines.append("Iequ_%s %s %s %e"
                                        % (dname, dnode1, dnode2, I_eq(vd)))

    def judgeConverged(self):
        for node in self.node_volt_iter0.keys():
            if abs(self.node_volt_iter0[node]
                    - self.node_volt_iter1[node]) > self.volt_tolerance:
                return False
        return True


# define the file names used for initial guess
SPICE_net0 = "./newton.iter.0.spice"
SPICE_out0 = "./newton.iter.0.out"

# define the file names used for continued guess
SPICE_net1 = "./newton.iter.1.spice"
SPICE_out1 = "./newton.iter.1.out"


littleNewton = Newton()
littleNewton.inputFile()
littleNewton.parseFile()

# Give an initial guess first, and then enter Newton Iteration
littleNewton.initGuess()
littleNewton.createLinearFile(SPICE_net0)
ret_code = littleNewton.runMNAnalysis(SPICE_net0, SPICE_out0)
if ret_code != 0:
    exit(ret_code)
littleNewton.readbackNodeResult(SPICE_out0, littleNewton.node_volt_iter0)
# End of initial guess

iterNum = 0
while (True):
    littleNewton.continueGuess()
    littleNewton.createLinearFile(SPICE_net1)
    ret_code = littleNewton.runMNAnalysis(SPICE_net1, SPICE_out1)
    if ret_code != 0:
        exit(ret_code)
    littleNewton.readbackNodeResult(SPICE_out1, littleNewton.node_volt_iter1)
    iterNum += 1
    if littleNewton.judgeConverged():
        print("Converged after", iterNum, "times. See result in", SPICE_out1)
        break
    elif iterNum > 100:
        print("Not converged after too many iterations!")
        exit(False)

    # save this iteration's node voltage dictionary for next comparison
    littleNewton.node_volt_iter0 = littleNewton.node_volt_iter1.copy()
    littleNewton.node_volt_iter1 = {"0": 0,
                                    "GND": 0}
