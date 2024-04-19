#!/usr/bin/env python
'''For demo of delay calculation on model-order-reduced ladder.
This program uses a method to truncate insignificant Eigen components in
exact result waveform and keep some significant ones (i.e., M orders kept).
The original ladder code is in iccad_ladder.py, which is imported for
waveform comparing.
NumPy is used for matrix operation, MatplotLib for plotting'''

# Import package 'time' to measure elapsed time, but be aware of its limit,
# as actual CPU loading is not exactly equivalent to elapsed time
import time as tm

import numpy as np
import matplotlib.pyplot as plt

# Import the existing iccad_ladder.py code
import iccad_ladder as lad


def truncatedWave(N=10, M=1, endTime=1000, deltaTime=0.01):
    '''
    Model-order-reduced ladder waveform simulator 1: returns approximate
    waveform on ladder end, according to the inputted truncating order M.
    The uniform ladder has a 1 Ohm resistor and a 1 Faraday capacitor
    on each stage. The input is a 1 Volt step voltage source. This voltage
    source can be converted to an equivalent Norton current source of
    1A step.
    The model order reduction method used here is just one of many algorithms.
    It just keeps a few slowest changing factors in an ODE's analytic solution.
    ---
    + N -> order of uniform RC ladder, default is 10-order
    + M -> using how many approximate orders to simulate exact wave
    + endTime determines how long the transient simulation takes;
    + deltaTime is the Euler step-length;
    Returns a (t, v) data pair <- time points and waveform data points
    '''
    # Everything is the same as in ladderWave() for matrix initialization
    c_val = 1
    g_val = 1

    C = np.zeros([N, N])
    G = np.zeros([N, N])

    diagC = [c_val] * N
    diagG = [-2 * g_val] * N
    sub_diagG = [g_val] * (N - 1)

    C = np.diag(diagC)
    G = np.diag(diagG)
    G = G + np.diag(sub_diagG, -1) + np.diag(sub_diagG, 1)
    # Last node has only 1 resistor connected, so change -2 to -1 on diagonal
    G[N - 1][N - 1] += g_val

    # Input step stimulus. The input node is kept as 1V.
    # Per Norton's Theorem, the equivalent input current source is 1A.
    i_source = np.zeros([N, 1])
    i_source[0] = 1

    # Discretize time; time is a list for discrete intervals
    start = 0
    time = [x * deltaTime for x in range(start, int(endTime / deltaTime))]

    # Begin simulation.
    # In conventional method in ladderWave(), we begin with,
    # C * [dv/dt] = G * [v] + [i_source]
    # and then use Forward/Backward Euler method to solve it.
    # However, in this program we first change the above ODE to,
    # [dv/dt] = inv(C) * G * [v] + inv(C) * [i_source]
    # Let A = inv(C) * G, and let B = inv(C) * [i_source]
    # we now have rewritten the ODE below to solve,
    # [dv/dt] = A * [v] + B
    A = np.dot(np.linalg.inv(C), G)
    B = np.dot(np.linalg.inv(C), i_source)

    # Now we perform Eigen analysis on A
    eigVal, eigVect = np.linalg.eig(A)

    # Thus transformed ODE -> [dv/dt] = eV * L * inv(eV) * [v] + B
    # where L is a diagonal matrix containing eigVal (lambda1, ..., lambdaN),
    # ev is a matrix being composed of all eigVect's as its columns
    # let [v] = eV * [w]
    # => eV * [dw/dt] = eV * L * [w] + B
    # => [dw/dt] = L * [w] + inv(eV) * B
    # => [dw/dt] = L * [w] + B_tilde
    #   i.e.
    #     dw1/dt     lambda1                          w1        b_t1
    #     dw2/dt           lambda2                    w2        b_t2
    #    [ ...  ] = [          ......           ] * [ ... ] + [ ...  ]
    #     dwN/dt                        lambdaN       wN        b_tN
    #
    # Now treat row by row separately, i.e., dwi/dt = lambdai * wi + b_ti
    # Transform it again by letting xi = wi + b_ti / lambdai
    # => dxi/dt = lambadi * xi, and solved in time domain:
    #     x(i)(t) = 1/lambdai * exp(lambdai * t) * constanti
    # and so, w(i)(t) = x(i)(t) - b_ti / lambdai, which details as,
    #     1/lambdai * exp(lambdai * t) * constanti - b_ti / lambdai
    # where 'constanti' is determined for:
    #     when t = 0, w(i)(t) = 0
    # => constanti = b_ti
    # thus, w(i)(t) = 1/lambdai * b_ti * (exp(lambdai * t) - 1)
    # Since [v] = eV * [w], we can then get all v from w.
    b_t = np.dot(np.linalg.inv(eigVect), B)  # the B~ matrix mentioned above

    # From the above discussion, if we just keep a few of the
    # slowest changing eigVal's of A, and throw away small lambdas,
    # the whole system can be hence simplified (reduced, or truncated).
    # That is,
    #     du1/dt     lambda_m1                        u1        b_t_m1
    #     du2/dt           lambda_m2                  u2        b_t_m2
    #    [ ...  ] = [          ......           ] * [ ... ] + [ ...  ]
    #     duM/dt                        lambda_mM     uM        b_t_mM
    # where lambda_mi's are M largest eigen values of A, and
    # [u], [b_t_m] are swapped [w], [b_t] according to lambda sorting.
    # Therefore, the N X N matrix about [w] is truncated into an M X M
    # matrix about [u], which has the M largest eigenvalues of A kept.

    # Find the M largest eigen values from eigVal.
    # eigVal.argsort() returns who is in what position for array members,
    # and those largest in eigVal are on the end of this array.
    # Check the output of eigVal.argsort()?
    kept_nodes = list(eigVal.argsort())[N-1:N-M-1:-1]

    # Make a dictionary to map the M nodes of [u] to original N nodes of [w],
    nodemap = {kept_nodes.index(x): x for x in kept_nodes}

    # and an N X M matrix to help map a size M vector [u] to
    # a size N vector [w], in the way of [w] = mapping_UW * [u]
    mapping_UW = np.zeros([N, M])

    # Initialize the truncated matrix; its elements are mapped by nodemap.
    # See the above truncated matrix and think how it is derived from old one.
    L_m = np.zeros([M, M])
    b_t_m = np.zeros([M, 1])
    for i in range(M):
        L_m[i, i] = eigVal[nodemap[i]]
        b_t_m[i][0] = b_t[nodemap[i]]
        mapping_UW[nodemap[i], i] = 1

    # Check the truncated matrix L_m?
    print(L_m)

    # Now, du/dt = L_m * u + b_t_m is ready; [u] -> [w] mapping is ready too.
    # To solve du/dt = L_m * u + b_t_m, where L_m is the re-ordered
    # and truncated M X M matrix, we can also use backward Euler method as,
    # (ut1 - ut0) / deltaT = L_m * ut1 + b_t_m
    # => (I - deltaT * L_m) * ut1 = ut0 + detlaT * b_t_m
    # Let A_r = I - deltaT * L_m, and let B_r = delta * b_t_m,
    # try solving => A_r * ut1 = ut0 + B_r
    A_r_inv = np.linalg.inv(np.eye(M) - deltaTime * L_m)
    B_r = deltaTime * b_t_m

    # v_nodes is a list of voltages on all v nodes, for just one time point;
    # vout is another list for voltage on the last stage, for all time points.
    v_nodes = np.zeros([N, 1])
    vout = []

    # Since v = eV * w, and we are solving u, so the
    # mapping from u to v is v = eV * mappingUW * [u]
    mapping_UV = eigVect.dot(mapping_UW)

    # u_nodes is a list of voltages on all u nodes, for just one time point
    u_nodes = np.zeros([M, 1])
    index = 0
    for tt in time:  # for all time points
        index += 1
        u_nodes = np.dot(A_r_inv, u_nodes + B_r)

        # Get v from w, as previously stated, v = mappingUV * [u]
        v_nodes = np.dot(mapping_UV, u_nodes)

        # Add the last stage voltage to vout, for current time point tt
        vout.append(v_nodes[N-1][0])

    return vout, time[0:index]

# Calculate original wave and the model-reduced wave,
# and compare the waveforms and costed time.


# Change ladder-length N and kept-order M below to see wave differences
Order = 200
Reduction_Order = 20

t1 = tm.time()

v, t = lad.ladderWave(N=Order, endTime=30000, deltaTime=0.1)
lad.plot_wave(t, v, 'b', name='N=' + str(Order) + ' original')

t2 = tm.time()

# Try different orders, and see the waveform errors and computing seconds
v, t = truncatedWave(N=Order, M=Reduction_Order, endTime=30000, deltaTime=0.1)
lad.plot_wave(t, v, 'r', name='N=' + str(Order) +
              ', order ' + str(Reduction_Order) + ' truncated-model')

t3 = tm.time()

print("Time costs are (original vs. truncated):")
print("%.4f" % (t2-t1) + "s", "vs.", "%.4f" % (t3-t2) + "s")
# Elmore delay of your ladder is?
print("Elmore delay of %.3d order ladder is %.4fs"
      % (Order, lad.elmoreDelay(Order)))

plt.title("Compared R/C Ladder Waveforms", fontsize=14)
plt.ylabel("Output(V)")
plt.xlabel("Time: in your deltaTime unit")
plt.legend()
plt.show()
