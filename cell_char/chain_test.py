#!/usr/bin/env python
"""
100 AND2 gates form a gate chain. All gates use the same name input
pin (pinA or pinB) to receive pulse signal from a gate in its front.
The pulse signal input to the first gate of the chain is of 1.1V
amplitude and of 0.02ns pulse slope (for both rise and fall sides).
The default output load capacitance is 100fF.
The program takes 2 command line arguments of final stage load capacitance
and 10-gates interval load capacitance, both in standard unit of Farad.
The same circuit is also described in a SPICE deck that can be
simulated by transient analysis, which takes minutes to run.
(Circuit settings can be adjusted to other values, but should be
synchronized with the corresponding SPICE deck)
Now calculate the output waveform slope and total signal propagation
delay of the chain, feel the running speed and check the accuracy.
"""
import sys
import numpy as np
import and2_lut_calc as lut


# can redefine circuit settings, but do synchronize with SPICE deck
AND2_CHAIN_LENGTH = 100
LAST_STAGE_LOAD_CAP = 40e-15  # i.e., 40fF final stage loading
FIRST_STAGE_IN_SLEW = 0.2e-11 * 0.4  # slew definition: 30%<->70% of Vdd
EVERY_10GATES_EXTRA_CAP = 10e-15  # the extra interval loading in test

if len(sys.argv) == 3:
    try:
        LAST_STAGE_LOAD_CAP = float(sys.argv[1])  # in standard unit F
        EVERY_10GATES_EXTRA_CAP = float(sys.argv[2])
    except ValueError:
        print(sys.argv[1], sys.argv[2],
              ": at least one argument is not a real number",
              file=sys.stderr)
        sys.exit()

# The program will call lookupAND2CellTiming() many times. Be sure
# of the exact meanings of the arguments being passed.

# define input pin capacitance for (Rise/Fall, pinA/pinB) type selection
capacitance_dict = {
    (True, True): lut.CAPACITANCE_R_AIN,
    (True, False): lut.CAPACITANCE_R_BIN,
    (False, True): lut.CAPACITANCE_F_AIN,
    (False, False): lut.CAPACITANCE_F_BIN,
}

print("Final stage load cap. is: %.3f fF"
      % (LAST_STAGE_LOAD_CAP/1e-15))
print("10-gates interval extra load cap. is: %.3f fF"
      % (EVERY_10GATES_EXTRA_CAP/1e-15))

# Calculate 4 types of gate chain configuration in the order of:
# (Rise, PinA), (Rise, PinB), (Fall, PinA), (Fall, PinB)
for (rise_type, pinA_type) in (
        (True, True), (True, False), (False, True), (False, False)):
    signal_in_slews = np.zeros([AND2_CHAIN_LENGTH])
    signal_in_slews[0] = FIRST_STAGE_IN_SLEW
    gate_prop_delays = np.zeros([AND2_CHAIN_LENGTH])
    pin_in_cap = capacitance_dict[(rise_type, pinA_type)]

    for i in range(AND2_CHAIN_LENGTH-1):
        if EVERY_10GATES_EXTRA_CAP != 0.0 and i % 10 == 9:
            actual_cap = pin_in_cap + EVERY_10GATES_EXTRA_CAP
        else:
            actual_cap = pin_in_cap
        signal_in_slews[i+1] = lut.lookupAND2CellTiming(
            signal_in_slews[i], actual_cap,
            True, rise_type, pinA_type)
        gate_prop_delays[i] = lut.lookupAND2CellTiming(
            signal_in_slews[i], actual_cap,
            False, rise_type, pinA_type)

    # whether the last stage has the 10-gates extra load cap?
    if AND2_CHAIN_LENGTH % 10 == 0:
        ACTUAL_LAST_CAP = LAST_STAGE_LOAD_CAP + EVERY_10GATES_EXTRA_CAP
    else:
        ACTUAL_LAST_CAP = LAST_STAGE_LOAD_CAP

    signal_out_slew = lut.lookupAND2CellTiming(
        signal_in_slews[AND2_CHAIN_LENGTH-1], ACTUAL_LAST_CAP,
        True, rise_type, pinA_type)
    gate_prop_delays[AND2_CHAIN_LENGTH-1] = lut.lookupAND2CellTiming(
        signal_in_slews[AND2_CHAIN_LENGTH-1], ACTUAL_LAST_CAP,
        False, rise_type, pinA_type)
    if pinA_type:
        OUT_TYPE_STR = "Pin-A"
    else:
        OUT_TYPE_STR = "Pin-B"
    OUT_TYPE_STR += " linked 100-gates chain "
    if rise_type:
        OUT_TYPE_STR += "(rising output)"
    else:
        OUT_TYPE_STR += "(falling output)"

    print(OUT_TYPE_STR)
    print("  output signal slope: %.7e" % signal_out_slew)
    print("  propagation delay:   %.7e" % gate_prop_delays.sum())

# May take a look of the graphs of pulse slews and propagation delays
# on the last one of 4 conditions (i.e., falling output signal on Pin B)
# in an interactive Python environment

#import matplotlib.pyplot as plt
#plt.figure()
#plt.title("Input Signal Slew to Each Gate")
#plt.plot(signal_in_slews)
#plt.figure()
#plt.title("Propagation Delay through Each Gate")
#plt.plot(gate_prop_delays)
#plt.show()
