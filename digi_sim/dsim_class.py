#!/usr/bin/env python
'''This program defines the basic classes of Signal, Event, Device and
Digital_Sim_Top with member functions for later digital simulation.
Four supported devices are defined as sub-classes of Device, which appear
in the simulation example of LFSR based pattern generator and signature
analyzer.
'''

import sys
import datetime


def leave_prog(message: str, exit_code=1):
    """
    Leave the program with an exit value
    """
    if exit_code != 0:
        print(message, file=sys.stderr)
    else:
        print(message)
    sys.exit(exit_code)


# Allowed Signal Values
SIGV_0 = '0'
SIGV_1 = '1'
SIGV_X = 'x'


class Signal:
    """
    A digital signal has a name; a stype of wire/reg (reg holds value)
    3 possible values 0, 1 and X; 2 edge transition marks; and a symbol
    used in data dumping.
    """

    def __init__(self, name: str, stype="wire", value=SIGV_X):
        self.name = name
        self.stype = stype
        self.value = value
        self.posedge = False
        self.negedge = False
        self.last_updated_time = -1  # -1 as the initial setting
        self.vcd_dump_symbol = ""

    def __repr__(self):
        return "signal %s: %s, %s, %s, %s, #%s" % (
            self.name, self.stype, self.value, self.posedge,
            self.negedge, self.last_updated_time)

    def __str__(self):
        return "signal %s: %s, %s, %s, %s, #%s" % (
            self.name, self.stype, self.value, self.posedge,
            self.negedge, self.last_updated_time)


# Allowed Event Types
EVT_CTL = "State Related Control"
EVT_UPD = "State Value Update"
EVT_PPG = "Signal Propagation"
EVT_ANY = "No Difference"


class Event:
    """
    An event defines a signal to change at a certain time to a certain
    value. In practice, events could be divided into 3 categories,
      state control type (e.g., synchronized clock, set/reset, D_in change);
      state value update type (e.g., the change of output Q);
      signal propagation type for input/output of combinational circuits.
    Though happening at the same time point, state control type event should
    be processed before all state update events (triggering edges already
    passed during update stage).
    Propagation events could be treated in a way to avoid race/competition
    between input signals of combinational logic gate, which is the likely
    source of output hazard (although input signals may arrive at the same
    time point, the serial processing of events still has a time order to
    make them compete with each other). If not taken care of, we would see
    small glitches before any output change stabilizes.
    """

    def __init__(self, signal: Signal, time, value=SIGV_X, etype=EVT_ANY):
        self.signal = signal
        self.time = time
        self.value = value
        self.etype = EVT_ANY  # assign to EVT_ANY if not specified
        # etype is left as EVT_ANY so far; as in our LFSR example,
        # these 3 event types are raised by output changes of devices
        # being easily assigned to 3 device type sets.

    def __repr__(self):
        return "event of signal %s: #%s, %s" % (
            self.signal.name, self.time, self.value)

    def __str__(self):
        return "event of signal %s: #%s, %s" % (
            self.signal.name, self.time, self.value)


class Device:
    """
    It supports an output signal list nd input signal name list.
    If there is only one output, then the device is named after this
    output signal if not specified. For multiple output devices, a
    name is required (and so device can be searched by this name).
    A Device instance is connected to output/input pins by name lists
    of instantiated signals; these signals could then be accessed by
    name searching.
    Here one device instance has only one intrinsic delay value.
    """

    def __init__(self, name, outsig_names: list, delay,
                 insig_names: list):
        if name:
            self.name = name
        elif outsig_names[0]:
            self.name = outsig_names[0]
        else:
            leave_prog("no name, no output device met")
        self.delay = delay
        self.outsig_names = outsig_names
        self.insig_names = insig_names
        self.device_type = None  # to be specified in actual device type

    def __repr__(self):
        return "device %s %s: *%s, #%s, <-%s" % (
            self.device_type, self.name, self.outsig_names,
            self.delay, self.insig_names)


class Device_Reg_NOT(Device):
    """
    Inverter gate with register storage, specifically used for clock
    generation.  The eval_input() return value is always True, which means
    any input change will surely cause an output event (after the device's
    delay).
    A Reg_NOT device is always named after its output ('clk' in example).
    """

    def __init__(self, outsig_name: str, delay, insig_name: str):
        super().__init__(outsig_name, [outsig_name], delay, [insig_name])
        self.stored_state = SIGV_X
        self.device_type = "Reg-NOT"

    def get_tobe_output_value(self):
        return self.stored_state

    def eval_input(self, sim_top):
        sig = sim_top.get_signal_byname(self.insig_names[0])
        if not sig:
            leave_prog("signal name %s not found" % self.insig_names[0])
        val = sig.value
        if val == SIGV_0:
            self.stored_state = SIGV_1
        elif val == SIGV_1:
            self.stored_state = SIGV_0
        else:
            self.stored_state = SIGV_X
        return True  # input change event => output always a new event


class Device_Wire_XOR(Device):
    """
    XOR Gate is a pure combinational logic gate with an output delay;
    and an evaluation can return a value according to the inputs.
    A Wire_XOR device is always named after the output.
    """

    def __init__(self, outsig_name: str, delay, insig0_name: str,
                 insig1_name: str):
        super().__init__(outsig_name, [outsig_name], delay,
                         [insig0_name, insig1_name])
        self.device_type = "Wire-XOR"

    def get_eval_output_value(self, sim_top):
        ''' Return output value by input value (output may actually change
        after a delay, but not being considered in this function)'''
        sig0 = sim_top.get_signal_byname(self.insig_names[0])
        if not sig0:
            leave_prog("signal name %s not found" % self.insig_names[0])
        sig0_v = sig0.value
        sig1 = sim_top.get_signal_byname(self.insig_names[1])
        if not sig1:
            leave_prog("signal name %s not found" % self.insig_names[1])
        sig1_v = sig1.value
        if SIGV_X in (sig0_v, sig1_v):
            return SIGV_X
        if (sig0_v == SIGV_0 and sig1_v == SIGV_0) or \
                (sig0_v == SIGV_1 and sig1_v == SIGV_1):
            return SIGV_0
        if (sig0_v == SIGV_0 and sig1_v == SIGV_1) or \
                (sig0_v == SIGV_1 and sig1_v == SIGV_0):
            return SIGV_1
        return None


class Device_Reg_DFF(Device):
    """
    Edge-triggered D Flip-Flop with a set pin; only works on positive
    clock edge.
    There is an internal state to keep the registered signal in storage.
    A Reg_DFF device is always named after the Q-pin output.
    """

    def __init__(self, q_name: str, delay, clk_name: str,
                 set_name: str, d_name: str):
        super().__init__(q_name, [q_name], delay,
                         [clk_name, set_name, d_name])
        self.stored_state = SIGV_X
        self.device_type = "Reg-DFF"

    def get_tobe_output_value(self):
        return self.stored_state

    def eval_input(self, sim_top):
        clk_sig = sim_top.get_signal_byname(self.insig_names[0])
        set_sig = sim_top.get_signal_byname(self.insig_names[1])
        d_sig = sim_top.get_signal_byname(self.insig_names[2])
        if clk_sig is None or set_sig is None or d_sig is None:
            self.stored_state = SIGV_X
            leave_prog("device %s input signal wrong" % self.name)
        if clk_sig.posedge:
            if set_sig.value == SIGV_1 and self.stored_state != SIGV_1:
                self.stored_state = SIGV_1
                return True  # raise an output event
            if self.stored_state != d_sig.value:
                self.stored_state = d_sig.value
                return True  # raise an output event
        return False  # does not cause an output change event


class Device_Wire_4bitMUL(Device):
    """
    A virtual model of multiplier of two unsigned 4-bit inputs (totally
    8 input signals), and one 8-bit output.
    """

    def __init__(self, name, outsig_names: list, delay, insig_names: list):
        if len(outsig_names) != 8 or len(insig_names) != 8:
            leave_prog("multiplier %s pins mismatch" % name)
        super().__init__(name, outsig_names, delay, insig_names)
        self.device_type = "Wire-4bitMUL"

    def get_eval_output_value(self, sim_top):
        ''' Return output value by input value (output may actually change
        after a delay, but not being considered in this function'''
        mul1 = sim_top.get_number_from_siglist(self.insig_names[0:4])
        mul2 = sim_top.get_number_from_siglist(self.insig_names[4:8])
        if None not in (mul1, mul2):
            product = mul1 * mul2
            # signature printing below is only for debugging purpose, and
            # can be commented out
            signature = sim_top.get_number_from_siglist(
                ["ra1_q7", "ra1_q6", "ra1_q5", "ra1_q4",
                 "ra1_q3", "ra1_q2", "ra1_q1", "ra1_q0"])
            print("%s * %s = %s, RA signature is %s"
                  % (mul1, mul2, product, signature))
            return product
        return None

    def set_eval_output_value(self, sim_top, product, event_time):
        ''' Set this multiplier's output signals to a product's value
        on a given event time'''
        sim_top.set_siglist_by_number(product, self.outsig_names,
                                      event_time)


class Digital_Sim_Top:
    """
    The top test bench with many functions to handle devices, signals
    and events
    """

    def __init__(self, name: str, end_time=100, dumpfile=None):
        self.name = name
        self.signal_list = []
        self.event_list = []
        self.event_list_sorted = False
        self.device_list = []
        self.current_time = -1  # initial at -1
        self.end_time = end_time
        self.current_eval_CTLdevice_set = set()
        self.current_eval_UPDdevice_set = set()
        self.current_eval_PPGdevice_set = set()
        if dumpfile:
            try:
                self.dumpfp = open(dumpfile, "w")
            except:
                leave_prog("dumpfile %s open error" % dumpfile)

    def create_signal(self, name: str, stype: str):
        ''' Declare a new signal by name
        '''
        if name in [sig.name for sig in self.signal_list]:
            leave_prog("logic signal %s already exists" % name)
        self.signal_list.append(Signal(name, stype))
        return True

    def assign_signal_constant(self, name: str, time, value: str):
        ''' Assign a certain value to signal, which surely raises an event
        at a specified time point. Always returns True.
        '''
        self.event_list.append(Event(self.get_signal_byname(name),
                               time, value))
        self.event_list_sorted = False
        return True

    def update_signal_constant(self, name: str, value: str):
        ''' Update the signal by name when actually handling an
        assign event. If signal already has the same value, return
        False, which means no event raised at all.
        '''
        for sig in self.signal_list:
            if name == sig.name:
                if sig.value != value:  # a really needed update
                    if sig.value == SIGV_0 and value == SIGV_1:
                        sig.posedge = True
                    elif sig.value == SIGV_1 and value == SIGV_0:
                        sig.negedge = False
                    sig.value = value
                    # leave a time tag for future use
                    sig.last_updated_time = self.current_time
                    return True
                return False
        return False

    def create_device_Reg_NOT(
            self, outsig_name: str, delay, insig_name: str):
        if outsig_name in [dev.name for dev in self.device_list]:
            leave_prog("device output %s already exists" % outsig_name)
        self.device_list.append(
            Device_Reg_NOT(outsig_name, delay, insig_name))
        return True

    def create_device_Wire_XOR(
            self, outsig_name: str, delay, insig0_name: str,
            insig1_name: str):
        if outsig_name in [dev.name for dev in self.device_list]:
            leave_prog("device output %s already exists" % outsig_name)
        self.device_list.append(
            Device_Wire_XOR(outsig_name, delay, insig0_name, insig1_name))
        return True

    def create_device_Reg_DFF(
            self, outsig_name: str, delay, insig0_name: str,
            insig1_name: str, insig2_name: str):
        if outsig_name in [dev.name for dev in self.device_list]:
            leave_prog("device output %s already exists" % outsig_name)
        self.device_list.append(
            Device_Reg_DFF(outsig_name, delay, insig0_name,
                           insig1_name, insig2_name))
        return True

    def create_device_Wire_4bitMUL(
            self, name, outsig_names: list, delay, insig_names: list):
        if name in [dev.name for dev in self.device_list]:
            leave_prog("device output %s already exists" % name)
        self.device_list.append(
            Device_Wire_4bitMUL(name, outsig_names, delay, insig_names))
        return True

    def get_signal_value_byname(self, name: str):
        ''' As the function name suggests; return a value
        '''
        for sig in self.signal_list:
            if name == sig.name:
                return sig.value
        return SIGV_X

    def get_signal_byname(self, name: str):
        ''' As the function name suggests; return a Signal instance
        '''
        for sig in self.signal_list:
            if name == sig.name:
                return sig
        return None

    def clear_all_signal_edgemark(self):
        ''' As the function name suggests
        '''
        for sig in self.signal_list:
            sig.posedge = False
            sig.negedge = False
        return True

    def sort_event_list(self):
        ''' Sort the event list by time order, which is the core of any
        digital simulation
        '''
        self.event_list.sort(key=lambda e: e.time)
        self.event_list_sorted = True

    def peek_next_first_event(self):
        ''' Return the current newest event from the sorted event
        list without its removal
        '''
        if self.event_list is None or self.event_list == []:
            return None
        if self.event_list_sorted is False:
            self.sort_event_list()
        first_event = self.event_list[0]
        return first_event

    def get_newest_event(self):
        ''' Take away one of the newest event from the sorted event
        list; for many events on the same time point, the returning order
        is possibly random; may use EVT_CTL, EVT_UPD, EVT_PPG types to
        finely tell event priority in future.
        '''
        if self.event_list is None or self.event_list == []:
            return None
        if self.event_list_sorted is False:
            self.sort_event_list()
        newest_event = self.event_list[0]
        self.remove_newest_event()
        return newest_event

    def remove_newest_event(self):
        ''' As the function name suggests
        '''
        if self.event_list is not None and self.event_list != []:
            self.event_list.pop(0)
            return True
        return False

    def get_sensitive_device_list(self, name: str):
        ''' Return a Device list of devices who are sensitive to
        the change of the named signal
        '''
        if self.device_list is None or self.device_list == []:
            return None
        return [device for device in self.device_list if
                name in device.insig_names]

    def get_number_from_siglist(self, bits_namelist: list):
        ''' Return an unsigned number from a list of signals (of MSB
        first order)
        '''
        number = 0
        for bit_name in bits_namelist:
            number *= 2
            sig_v = self.get_signal_value_byname(bit_name)
            if sig_v == SIGV_X:
                return None
            if sig_v == SIGV_1:
                number += 1
        return number

    def set_siglist_by_number(self, number, bits_namelist: list,
                              event_time):
        ''' Set the value of a bundle of signals to a number (of MSB
        first order)
        '''
        for bit_name in reversed(bits_namelist):
            bit_v = number % 2
            if bit_v == 1:
                sig_v = SIGV_1
            else:
                sig_v = SIGV_0
            self.assign_signal_constant(bit_name, event_time, sig_v)
            number = int(number / 2)

    def evaluate_current_device_sets(self):
        '''
        At current time point, evaluate all devices' output signal
        in the order of:
          1. state control type output
          2. state update type output
          3. propagation type output
        '''
        for dev in self.current_eval_CTLdevice_set:
            self.eval_current_one_device(dev)
        for dev in self.current_eval_UPDdevice_set:
            self.eval_current_one_device(dev)
        for dev in self.current_eval_PPGdevice_set:
            self.eval_current_one_device(dev)

    def eval_current_one_device(self, device):
        ''' As the function name suggests, evaluate one device and
        assign value to device's output (and surely raise an event)
        '''
        if isinstance(device, Device_Reg_NOT):
            if device.eval_input(self):  # eval_input may return False
                self.assign_signal_constant(
                    device.outsig_names[0],
                    self.current_time + device.delay,
                    device.get_tobe_output_value())
        elif isinstance(device, Device_Wire_XOR):
            wire_output = device.get_eval_output_value(self)
            self.assign_signal_constant(
                device.outsig_names[0],
                self.current_time + device.delay,
                wire_output)
        elif isinstance(device, Device_Reg_DFF):
            if device.eval_input(self):  # but reg type can keep state
                self.assign_signal_constant(
                    device.outsig_names[0],
                    self.current_time + device.delay,
                    device.get_tobe_output_value())
        elif isinstance(device, Device_Wire_4bitMUL):
            wire_output = device.get_eval_output_value(self)
            device.set_eval_output_value(
                self, wire_output, self.current_time + device.delay)

    def output_vcd_header(self):
        ''' Generate header section of a VCD file. Assign an ASCII
        character to a signal, but maximally 93 signals are allowed in
        this one character code representation.
        '''
        if self.dumpfp:
            now_time = datetime.datetime.now().ctime()
            print("$date\n\t%s\n$end" % now_time, file=self.dumpfp)
            print("$timescale\n\t100ps\n$end", file=self.dumpfp)
            print("$scope module test_top $end", file=self.dumpfp)
            ascii_code = 33  # begin from ASCII symbol '!'
            for sig in self.signal_list:
                sig.vcd_dump_symbol = chr(ascii_code)
                print("$var %s 1 %s %s $end"
                      % (sig.stype, sig.vcd_dump_symbol, sig.name),
                      file=self.dumpfp)
                if ascii_code > 126:
                    leave_prog(
                        "currently only support the dump of less than \
                        93 signals")
                ascii_code += 1
