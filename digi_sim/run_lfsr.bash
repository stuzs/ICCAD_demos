#!/bin/bash
# Following commands generate a simulation executable 'lfsr' from lfsr.v
# and invoke gtkwave to see the waveforms
iverilog -o lfsr -s test_top lfsr.v
./lfsr
gtkwave lfsr_wave.vcd
