
# *Standard Cell Characterization* for timing and power library preparation
Characterization of a simple two-input AND gate (AND2) cell is demonstrated. The cell timings are characterized and stored in a few NLDM (Non-Linear Delay Model) style 2-D look-up tables (LUTs) for later off-grid indexing based on linear interpolation. Test circuits are provided to evaluate the application of the characterized results.

## 2-input AND Gate (AND2) Cell Characterization Demo Files
iccad_cellchar.py:
    The command line entry to all cell characterization tasks

and2_sckt.spice:
    Transistor-level SPICE deck of AND2 gate in a sub-circuit

and2_weakB_sckt.spice:
    Almost the same as and2_sckt.spice, but pin-B is set to be weak

and2_incap.spice:
    SPICE deck for measuring gate input pins' capacitances

and2_trial_char.spice:
    Doing the cell characterization on only one condition point

and2_batch_char.spice:
    Doing cell characterization on all conditions in one automatic batch run

and2_gentab.bash:
    Generating BASH commands for generating Python format timing data arrays from the SPICE output text of earlier batch run

and2_lut_calc.py:
    Looking up AND2 cell timing values given a certain signal slew and a load capacitance, by interpolations on stored 2-D timing LUTs. Drawing 2 graphs of cell timings if independently called.

chain_test.py:
    Test run on a 100 instances AND2 gate chain to check its timings which is called by iccad_cellchar.py

and2_chain.spice:
    SPICE deck file of a 100 instances AND2 gate chain for comparing timings with LUT-based method

and2_chain_sckt.spice:
    Sub-circuit description file for AND2 gate chains of 10/100 gates and pinA/B linked versions

### Derivative Files (generated by another program)
working_and2_lut_array.py:
    Defining Python arrays containing 11 tables for AND2 cell characterization, among which 8 LUTs are the timing results, 2 tables describe input signal slews in the characterization, 1 table describes the output load capacitances in the characterization; input pin capacitances are described in the first 4 lines.

and2_gentab.second.bash:
    BASH program generated by running the and2_gentab.bash program for generating Python format timing data arrays

trial_and2_sckt.spice:
    Temporary file for selecting AND2 gate sub-circuit version for trial characterizing run

working_and2_sckt.spice:
    Temporary file for selecting AND2 gate sub-circuit version for batch characterizing runs

working_batch_run_out.data:
    Data file to temporarily store SPICE output results in batch characterizing process

### Auxiliary Files
mosfet_dc.spice:
    SPICE deck to show characteristic I-V curves of the types of MOSFETs used in the characterized gate 

and2_101ro.spice:
    SPICE deck of a 101-stage ring-oscillator(RO) made up of many AND2 gates of the characterized type

## iccad_cellchar.py Command Examples
python iccad_cellchar.py -h  # show help

./iccad_cellchar.py -t  # trial run once with normal Pin-B gate

python iccad_cellchar.py -gw  # characterize in batch with weak Pin-B gate

python iccad_cellchar.py -r  # check characterization results

python iccad_cellchar.py -l 0.03 25  # look up cell timings on input slew and output load capacitance with values of (0.03ns, 25fF) 

./iccad_cellchar.py -e -fc 100 -ic 30  # evaluate the 100-gate chain's timings with final stage load capacitance of 100fF, and 10-gate interval load capacitance of 30fF