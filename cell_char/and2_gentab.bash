#!/bin/bash
# Running this program could generate a series of bash commands
# which could then be run again in bash to generate Python code of arrays
# containing cell timing information.
# Assume a fixed name "working_batch_char_out.data" is for the SPICE
# characterization output file in these two BASH programs.
# This SPICE output file could be saved during characterization using
# such a command below,
# "ngspice and2_batch_char.spice | tee working_batch_char_out.data"

declare -a parameterNameDefArray

parameterNameDefArray=(
    tr_in:Arr_Tr_in
    tf_in:Arr_Tf_in
    out_load_cap:Arr_out_load_cap
    tr_out_ain:Arr_Tr_out_Ain
    tr_out_bin:Arr_Tr_out_Bin
    tf_out_ain:Arr_Tf_out_Ain
    tf_out_bin:Arr_Tf_out_Bin
    tpdr_ain:Arr_Tpdr_Ain
    tpdr_bin:Arr_Tpdr_Bin
    tpdf_ain:Arr_Tpdf_Ain
    tpdf_bin:Arr_Tpdf_Bin
)

echo 'echo import numpy as np' > and2_gentab.second.bash

# The values of the 4 tpyes of capacitances are directly copied from
# capacitance measurement results after running "and2_incap.spice"
if [ "$1" = "weakB" ]; then
    echo 'echo CAPACITANCE_R_AIN = 2.21340e-15/1.1' >> and2_gentab.second.bash
    echo 'echo CAPACITANCE_R_BIN = 1.50988e-15/1.1' >> and2_gentab.second.bash
    echo 'echo CAPACITANCE_F_AIN = 2.21346e-15/1.1' >> and2_gentab.second.bash
    echo 'echo CAPACITANCE_F_BIN = 1.50983e-15/1.1' >> and2_gentab.second.bash
else
    echo 'echo CAPACITANCE_R_AIN = 2.21325e-15/1.1' >> and2_gentab.second.bash
    echo 'echo CAPACITANCE_R_BIN = 2.20588e-15/1.1' >> and2_gentab.second.bash
    echo 'echo CAPACITANCE_F_AIN = 2.21331e-15/1.1' >> and2_gentab.second.bash
    echo 'echo CAPACITANCE_F_BIN = 2.20592e-15/1.1' >> and2_gentab.second.bash
fi

# to generate text containing single quote, a general rule is that single
# quote could not occur inside single quotes, so a $ is added before the
# first single quote of some lines to solve this issue.
for PNDname in "${parameterNameDefArray[@]}"; do
    pname=$(echo $PNDname | cut -d: -f1)
    aname=$(echo $PNDname | cut -d: -f2)
    echo "echo '$aname = np.array('"
    echo $'echo "    "\'[\''
    echo -n "grep ^$pname "
    echo -n working_batch_char_out.data
    echo -e " | awk '{print \"        \"\$3\",\"}'"
    echo $'echo "    "\']\''
    echo $'echo \')\''
    echo 'echo'
done >> and2_gentab.second.bash
# The generated BASH commands are then stored in
# "and2_gentab.second.bash"
# Run the second round bash command program, and re-direct the output
# to a Python file, named as "working_and2_lut_array.py" as below,
# "bash and2_gentab.second.bash > working_and2_lut_array.py"
