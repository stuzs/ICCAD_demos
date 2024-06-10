#!/usr/bin/env python
"""
This program can return AND2 cell timing values when given a certain signal
slew and a load capacitance, by interpolations on previously stored 2-D
timing LUTs. It draws 2 graphs of cell timings if independently called.
The program is the basic calculation module being imported by
iccad_cellchar.py command console to estimate cell timings.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

# for interpolating regular grids use RegularGridInterpolator
from scipy.interpolate import RegularGridInterpolator

# The cell timing Look-Up Tables (LUTs) in this program, derived
# from the SPICE output file of automatic batch runs of the AND2
# cell characterization, contain delay information of Tr, Tf, Tpdr
# and Tpdf for both the input pins (pinA/pinB) of the characterized
# AND2 gate.

# I use bash commands such as,
#     grep ^tr_in $DATAFILE | awk '{print $3}'
# to filter out the needed data from SPICE output file.
# Commands for data filtering and array definition are stored in a separate
# BASH program, which can generate the characterized LUT arrays and store
# the data in a file "working_and2_lut_array.py".

# now take everything in, including LUT data arrays and pin capacitances
from working_and2_lut_array import *

# The detailed combinations of input waveform conditions and output
# loading conditions are actually chosen in SPICE batch run. The numbers
# are input again here.
LUT_INPUT_CONDS = 4
LUT_OUTPUT_CONDS = 4
LUT_TOTAL_CONDS = LUT_INPUT_CONDS * LUT_OUTPUT_CONDS


def check_reldiff(a, b):
    """
    Check relative difference of two input values
    False means no significant difference, True means the contrast
    """
    if a == 0.0 and b == 0.0:
        return False
    if a == 0.0:
        div = b
    else:
        div = a
    if abs(a-b) / div < 5e-3:  # choose a relative error threshold
        return False
    return True


# check difference between input wave slews (their output loading
# conditions differ) on each input condition
for idx in range(0, LUT_TOTAL_CONDS, LUT_OUTPUT_CONDS):
    tr_in_load0 = Arr_Tr_in[idx]
    tf_in_load0 = Arr_Tf_in[idx]
    for ofst in range(1, LUT_OUTPUT_CONDS):
        if check_reldiff(tr_in_load0, Arr_Tr_in[idx+ofst]):
            print("Input rising slews have unignorable difference:")
            print(tr_in_load0, "vs.", Arr_Tr_in[idx+ofst])
            sys.exit()
        if check_reldiff(tf_in_load0, Arr_Tf_in[idx+ofst]):
            print("Input falling slews have unignorable difference:")
            print(tf_in_load0, "vs.", Arr_Tf_in[idx+ofst])
            sys.exit()

# If the input rising/falling waveform slews have small differences on
# different output loading capacitances, the LUT can be based on a regular
# grid mesh for easier interpolating. Use the average value of them
# as the regular shape grid point.

# define the two axes (the plural of axis) of each LUT
LUT_slew_grids = []
LUT_cap_grids = []

# average input slew values of each input condition as a LUT axis point
for idx in range(0, LUT_INPUT_CONDS):
    base = idx * LUT_OUTPUT_CONDS
    tail = base + LUT_INPUT_CONDS
    LUT_slew_grids.append(Arr_Tr_in[base:tail].sum()/LUT_INPUT_CONDS)

# just use the first input condition's loading values as LUT axis points
for idx in range(0, LUT_INPUT_CONDS):
    LUT_cap_grids.append(Arr_out_load_cap[idx])


def lookupAND2CellTiming(slew, cap, trans_type, rise_type, pinA_type):
    """
    It returns interpolated timing for input argument pair(slew, cap)
    from one of 8 look-up tables. The totally 8 look-up timing tables
    are for 8 different settings of the 3 input types below,
        Transition or Propagation: bool trans_type
        Rise or Fall: bool rise_type
        Pin A or Pin B: bool pinA_type
    """
    # It directly calls the interpolating function
    return lookupAND2CellTimingFunc(trans_type,
                                    rise_type, pinA_type)((slew, cap))


def lookupAND2CellTimingFunc(trans_type, rise_type, pinA_type):
    """
    It returns the interpolating function for the asked type
    """
    timing_type = (trans_type, rise_type, pinA_type)
    timing_array_dict = {
        (True, True, True): Arr_Tr_out_Ain,
        (True, True, False): Arr_Tr_out_Bin,
        (True, False, True): Arr_Tf_out_Ain,
        (True, False, False): Arr_Tf_out_Bin,
        (False, True, True): Arr_Tpdr_Ain,
        (False, True, False): Arr_Tpdr_Bin,
        (False, False, True): Arr_Tpdf_Ain,
        (False, False, False): Arr_Tpdf_Bin,
    }

    grid_array = timing_array_dict.get(timing_type).reshape(
        (LUT_INPUT_CONDS, LUT_OUTPUT_CONDS))
    # print (grid_array)

    # if bounds_error is False, fill_value is used when out of bounds
    # while if fill_value is None, extrapolated value is returned
    interp = RegularGridInterpolator(
        (LUT_slew_grids, LUT_cap_grids), grid_array,
        method="linear", bounds_error=False, fill_value=None)
    return interp


def drawAND2CellTiming(ax, trans_type, rise_type, pinA_type):
    """
    It draws a scatter plot of characterized points in one of the
    AND2 cell timing LUTs with the corresponding interpolated point
    mesh of this LUT.
    The 3 input types are the same as in the lookup function, so just
    pass them to the lookup function.
    ax is the axis passed in
    """
    # generate 9 mesh grid points between every two LUT axis points,
    # all LUT axis points are also included for this mesh grid.
    # concatenate all grid points together into arrays ss and cc.
    ss, cc = np.array([]), np.array([])
    for i in range(len(LUT_slew_grids)-1):
        if i != len(LUT_slew_grids) - 2:
            ss = np.concatenate((ss, np.linspace(
                LUT_slew_grids[i], LUT_slew_grids[i+1],
                num=10, endpoint=False)))
        else:
            ss = np.concatenate(
                (ss, np.linspace(LUT_slew_grids[i], LUT_slew_grids[i+1],
                                 num=11, endpoint=True)))
    for i in range(len(LUT_cap_grids)-1):
        if i != len(LUT_cap_grids) - 2:
            cc = np.concatenate(
                (cc, np.linspace(LUT_cap_grids[i], LUT_cap_grids[i+1],
                                 num=10, endpoint=False)))
        else:
            cc = np.concatenate(
                (cc, np.linspace(LUT_cap_grids[i], LUT_cap_grids[i+1],
                                 num=11, endpoint=True)))

    # numpy.meshgrid() uses 1-D arrays as coordinates; here the two
    # LUT_ arrays define the 2-D coordinates. It returns a list of
    # ndarrays of grids; where 'ij' indexing is for 'matrix' indexing
    # order of the output.
    xg, yg = np.meshgrid(LUT_slew_grids, LUT_cap_grids, indexing='ij')

    # data are thus evaluated on 2-D mesh points defined by xg and yg
    data = lookupAND2CellTiming(
        xg, yg, trans_type, rise_type, pinA_type)

    # now data and its coordinates are ready, draw a Scatter Plot on them
    ax.scatter(
        xg.ravel(), yg.ravel(), data.ravel(), s=50, c='r',
        label='SPICE output points in LUT')

    # draw dense mesh grids defined by arrays ss and cc
    xmg, ymg = np.meshgrid(ss, cc, indexing='ij')
    ax.plot_wireframe(
        xmg, ymg, lookupAND2CellTimingFunc(
            trans_type, rise_type, pinA_type)((xmg, ymg)),
        rstride=3, cstride=3, alpha=0.4, label='Interpolated points')
    ax.legend()


def test_draw():
    """
    Draw data mesh figures of 2 cell timing LUTs
    """
    fig0 = plt.figure()
    ax0 = fig0.add_subplot(projection='3d')
    drawAND2CellTiming(ax0, True, True, True)

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(projection='3d')
    drawAND2CellTiming(ax1, False, False, False)


if __name__ == '__main__':
    # test draw some cell timing LUTs
    test_draw()
    plt.show()
