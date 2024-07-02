
# Digital Simulator Demo
A minimal-scale event-driven digital simulator is demonstrated. A Verilog module of a few LFSRs (Linear Feedback Shift Registers) working as TPG (Test Pattern Generator) and RA (Response Analyzer) of a BIST (Built-In Self Test) circuitry is provided as a vehicle to show the digital simulation mechanism, whose focal point is managing the **Time Wheel** for "creatures" in the forms of Event, Signal, Device and etc.

## Demo Files

iccad_dsim.py:
	The program to simulate the demo BIST circuit

dsim_class.py:
	Defining all basic classes and various member functions for digital simulation purpose

lfsr.v:
	The demo BIST circuit to test the functional correctness of a multiplier in Verilog

run_lfsr.bash:
	BASH commands simulating lfsr.v by iverilog and showing waveforms in gtkwave

### Generated Waveform Data Files

lfsr_wave.vcd:
	Waveform data in VCD format created by a Verilog simulator (e.g., iverilog)

dsim_wave.vcd:
	Waveform data in VCD format created by this demo simulator
