#!/usr/bin/env python
'''This program simulates a digital circuit with several LFSRs working as
pattern generator and signature analyzer. The original verilog code
"lfsr.v" describes the same test circuit (although in a hierarchical form
instead of the flatten form here).
'''

from dsim_class import Digital_Sim_Top, Device_Reg_NOT, Device_Reg_DFF, \
    Device_Wire_XOR, Device_Wire_4bitMUL, leave_prog


# Device and signal defining sections
# i.e., the structure part of test_top verilog module
top = Digital_Sim_Top("test_top", end_time=160, dumpfile="dsim_wave.vcd")
top.create_signal("clk", "reg")
top.create_signal("on", "reg")
top.create_device_Reg_NOT("clk", 5, "clk")
# TPG1
top.create_signal("tpg1_q3", "reg")
top.create_signal("tpg1_q2", "reg")
top.create_signal("tpg1_q1", "reg")
top.create_signal("tpg1_q0", "reg")
top.create_signal("tpg1_d", "wire")
top.create_device_Wire_XOR("tpg1_d", 2, "tpg1_q0", "tpg1_q3")
top.create_device_Reg_DFF("tpg1_q3", 1, "clk", "on", "tpg1_d")
top.create_device_Reg_DFF("tpg1_q2", 1, "clk", "on", "tpg1_q3")
top.create_device_Reg_DFF("tpg1_q1", 1, "clk", "on", "tpg1_q2")
top.create_device_Reg_DFF("tpg1_q0", 1, "clk", "on", "tpg1_q1")
# TPG2
top.create_signal("tpg2_q3", "reg")
top.create_signal("tpg2_q2", "reg")
top.create_signal("tpg2_q1", "reg")
top.create_signal("tpg2_q0", "reg")
top.create_signal("tpg2_d", "wire")
top.create_device_Wire_XOR("tpg2_d", 2, "tpg2_q0", "tpg2_q1")
top.create_device_Reg_DFF("tpg2_q3", 1, "clk", "on", "tpg2_d")
top.create_device_Reg_DFF("tpg2_q2", 1, "clk", "on", "tpg2_q3")
top.create_device_Reg_DFF("tpg2_q1", 1, "clk", "on", "tpg2_q2")
top.create_device_Reg_DFF("tpg2_q0", 1, "clk", "on", "tpg2_q1")
# Multiplier under Test
top.create_device_Wire_4bitMUL(
    "Mult DUT",
    ["prod_7", "prod_6", "prod_5", "prod_4",
     "prod_3", "prod_2", "prod_1", "prod_0"],
    1,
    ["tpg1_q3", "tpg1_q2", "tpg1_q1", "tpg1_q0",
     "tpg2_q3", "tpg2_q2", "tpg2_q1", "tpg2_q0"]
)
# RA_MISR
top.create_signal("ra1_q7", "reg")
top.create_signal("ra1_q6", "reg")
top.create_signal("ra1_q5", "reg")
top.create_signal("ra1_q4", "reg")
top.create_signal("ra1_q3", "reg")
top.create_signal("ra1_q2", "reg")
top.create_signal("ra1_q1", "reg")
top.create_signal("ra1_q0", "reg")
top.create_signal("ra1_d7", "wire")
top.create_signal("ra1_d6", "wire")
top.create_signal("ra1_d5", "wire")
top.create_signal("ra1_d4", "wire")
top.create_signal("ra1_d3", "wire")
top.create_signal("ra1_d2", "wire")
top.create_signal("ra1_d1", "wire")
top.create_signal("ra1_d0", "wire")
top.create_device_Reg_DFF("ra1_q7", 1, "clk", "on", "ra1_d7")
top.create_device_Reg_DFF("ra1_q6", 1, "clk", "on", "ra1_d6")
top.create_device_Reg_DFF("ra1_q5", 1, "clk", "on", "ra1_d5")
top.create_device_Reg_DFF("ra1_q4", 1, "clk", "on", "ra1_d4")
top.create_device_Reg_DFF("ra1_q3", 1, "clk", "on", "ra1_d3")
top.create_device_Reg_DFF("ra1_q2", 1, "clk", "on", "ra1_d2")
top.create_device_Reg_DFF("ra1_q1", 1, "clk", "on", "ra1_d1")
top.create_device_Reg_DFF("ra1_q0", 1, "clk", "on", "ra1_d0")
top.create_signal("feedback", "wire")
top.create_signal("tmp_02", "wire")
top.create_signal("tmp_34", "wire")
top.create_device_Wire_XOR("tmp_02", 2, "ra1_q0", "ra1_q2")
top.create_device_Wire_XOR("tmp_34", 2, "ra1_q3", "ra1_q4")
top.create_device_Wire_XOR("feedback", 2, "tmp_02", "tmp_34")
top.create_device_Wire_XOR("ra1_d7", 1,  "feedback", "prod_7")
top.create_device_Wire_XOR("ra1_d6", 1,  "ra1_q7", "prod_6")
top.create_device_Wire_XOR("ra1_d5", 1,  "ra1_q6", "prod_5")
top.create_device_Wire_XOR("ra1_d4", 1,  "ra1_q5", "prod_4")
top.create_device_Wire_XOR("ra1_d3", 1,  "ra1_q4", "prod_3")
top.create_device_Wire_XOR("ra1_d2", 1,  "ra1_q3", "prod_2")
top.create_device_Wire_XOR("ra1_d1", 1,  "ra1_q2", "prod_1")
top.create_device_Wire_XOR("ra1_d0", 1,  "ra1_q1", "prod_0")

# Signals "[7:0] prod" are the product of two 4-bit inputs in "lfsr.v"
top.create_signal("prod_0", "wire")
top.create_signal("prod_1", "wire")
top.create_signal("prod_2", "wire")
top.create_signal("prod_3", "wire")
top.create_signal("prod_4", "wire")
top.create_signal("prod_5", "wire")
top.create_signal("prod_6", "wire")
top.create_signal("prod_7", "wire")

# The initial begin ... end part for signal initialization
top.assign_signal_constant("clk", 0, "0")
top.assign_signal_constant("on", 0, "1")
top.assign_signal_constant("on", 10, "0")

top.current_CTLeval_device_set = set()
top.current_UPDeval_device_set = set()
top.current_PPGeval_device_set = set()

if top.dumpfp:
    top.output_vcd_header()
    # borrow the same `timescale 1ns/100ps setting from "lvsr.v"
    print("#%s" % (top.current_time * 10), file=top.dumpfp)
    for sig in top.signal_list:
        print("%s%s" % (sig.value, sig.vcd_dump_symbol), file=top.dumpfp)

# begin the event processing loop
loop_count = 0
while (top.current_time < top.end_time) and loop_count < 1000:
    loop_count += 1
    # take a peek at the next event in system event list
    current_next_event = top.peek_next_first_event()
    if current_next_event is None or \
            top.current_time < current_next_event.time:
        # Very likely will move to next time point, but, before that,
        # should evaluate all combinational circuits ONCE, and be sure
        # this evaluate won't bring any event right on this current time
        # point; that is, no #0-delay component (or assignment) is allowed.
        top.evaluate_current_device_sets()
        loop_event = top.get_newest_event()
        if loop_event is None:
            print("Reach the end of all active events at #%s" %
                  top.current_time)
            break
        if loop_event.time == top.current_time:
            leave_prog("an 0-delay event happens: %s, not allowed so far"
                       % loop_event.signal.name)
        if current_next_event and loop_event.time > current_next_event.time:
            leave_prog("might have lost the trace of event: %s"
                       % current_next_event.signal.name)
    else:
        # there is at least one unhandled event at current time point
        loop_event = top.get_newest_event()

    # turn on below to show all events to be handled in debugging time
    # print("currently @#%s" % top.current_time, "to handle", loop_event)

    if loop_event is None:
        print("Reach the end of all active events at #%s" %
              top.current_time)
        break

    if top.current_time < loop_event.time:  # so now advance system time
        top.current_time = loop_event.time
        top.clear_all_signal_edgemark()  # any time advance clears marks
        top.current_eval_CTLdevice_set = set()
        top.current_eval_UPDdevice_set = set()
        top.current_eval_PPGdevice_set = set()
        if top.dumpfp:
            # borrow the same `timescale 1ns/100ps setting from "lvsr.v"
            print("#%s" % (top.current_time * 10), file=top.dumpfp)

    # update the newest event's signal value, as well as mark the edge
    # transitions
    if top.update_signal_constant(loop_event.signal.name, loop_event.value):
        if top.dumpfp:
            print("%s%s"
                  % (loop_event.value, loop_event.signal.vcd_dump_symbol),
                  file=top.dumpfp)
        # if the signal does change
        # and then...
        # search all will-be affected devices of the above signal update
        for loop_device in top.get_sensitive_device_list(
                loop_event.signal.name):
            if isinstance(loop_device, Device_Reg_NOT):
                # Reg_NOT output update, only for clk in our example,
                # add to State Control type set
                top.current_eval_CTLdevice_set.add(loop_device)
            elif isinstance(loop_device, Device_Reg_DFF):
                # Q of DFF output update, add to State Update type set
                top.current_eval_UPDdevice_set.add(loop_device)
            elif isinstance(loop_device, Device_Wire_XOR):
                # XOR output update, add to Propagation type set
                top.current_eval_PPGdevice_set.add(loop_device)
            elif isinstance(loop_device, Device_Wire_4bitMUL):
                # Multiplier output update, add to Propagation type set
                top.current_eval_PPGdevice_set.add(loop_device)
            else:
                leave_prog("device: %s not supported" % loop_device)

if top.dumpfp:
    top.dumpfp.close()
