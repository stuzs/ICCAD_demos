#!/usr/bin/env python
'''For demo of delay calculation on model-order-reduced ladder.
This program uses moment matching method to reduce the model order.
The original ladder code is in iccad_ladder.py, which is imported for
waveform comparing.
Numpy is used for matrix manipulation, Matplotlib for plotting.
Scipy.signal is used for evaluating step response of a system with
a defined Hr(s) transfer function'''

# Import package 'time' to measure elapsed time, but be aware of its limit,
# as actual CPU loading is not exactly equivalent to elapsed time
import time as tm

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Import the previous demo_ladder.py code
import iccad_ladder as lad


def momentMatching(N=10, qParam=1, endTime=300, deltaTime=0.1):
    '''
    Model-order-reduced ladder waveform simulator(MOMENT MATCHING):
    returns approximate waveform on ladder end, according to the inputted
    truncating order qParam.
    The uniform ladder has a 1 Ohm resistor and a 1 Faraday capacitor
    on each stage. The input is a 1 Volt step voltage source. This voltage
    source can be converted to an equivalent Norton current source of
    1A step.
    The model order reduction method used here is so-called moment-matching.
    It simulates an ODE's analytic solution H(s) with an approximate transfer
    function Hr(s), in numerator/denominator polynomial form.
    ---
    + N -> order of uniform RC ladder, default is 10-order
    + qParam -> using how many approximate orders to simulate exact wave
    + endTime determines how long the transient simulation takes;
    + deltaTime is the Euler step-length;
    Returns a (t, v) data pair <- time points and waveform data points,
    directly from the result of scipy.signal.step().
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
    # Last node has only one resistor connected, so change -2 to -1 on diagonal
    G[N - 1][N - 1] += g_val

    # Input step stimulus. The input node is kept as 1V
    # Per Norton's Theorem, the equivalent input current source is 1 amp
    i_source = np.zeros([N, 1])
    i_source[0] = 1

    # Check matrices C and G
    # per KCL, Iout=Iin, [C]*[dv/dt] = [G]*[v] + i_source
    # now let,
    #    Amat = inv(C) * G
    #    bmat = inv(C) * [i_source]
    #    cmat = [0, 0, ..., 0, 1] (of the same dimension)
    # and so we can rewrite the original equation into,
    #    [dv/dt] =  Amat * [V] + bmat
    # the output of last ladder stage y (stage N-1) is obtained as,
    #    y = cmat * [v]  (y is one value on one time point)
    # note bmat and cmat are actually 1-D vectors.
    Amat = np.dot(np.linalg.inv(C), G)
    bmat = np.dot(np.linalg.inv(C), i_source)
    cmat = np.zeros([N, 1])
    cmat[N - 1] = 1

    # MOMENT MATCHING is based on an assumption that Hr(s) ~= H(s),
    # where H(s) is the transfer function of a linear system, and
    # Hr(s) is the transfer function of a reduced linear system.
    # Can we find a transfer function Hr(s) approximate to original H(s)?

    # For the linear system defined above and below again,
    #    [dv/dt] =  Amat * [V] + bmat  &  y = cmat * [v]
    # we apply Laplace Transform to it and obtain,
    #    s*V(s) = Amat*V(s) + bmat*U(s)  &  Y(s) = cmat * V(s)
    # where U(s) is the Laplace Transform of step function.
    # Therefore, V(s) = 1 / (s * I - Amat) * bmat * U(s)
    # and, Y(S) = cmat * 1 / (s*I - Amat) * bmat * U(s)
    # then we have, H(s) = cmat * 1 / (s*I - Amat) * bmat

    # Expand H(s) above in Taylor series with respect to s,
    #     H(s) = m0 + m1*s + m2*s^2 + ... + mk*s^ k + (inf)
    #     where mk is called as k-th moment and decided by Taylor method,
    #         mk = -cmat * Amat^(-k-1) * bmat    (k-th derivatives of H(s))
    # This equation can be verified by a 1-order ladder, which has
    # Amat=[-1.0], H(s) = 1 / (1+s), and H(s) = 1-s+s^2-s^3+s^4+...

    # An order-q system has Hr(s) defined as,
    #     Hr(s) = (b0 + b1*s + ... + b(q-1)*s^(q-1))/(1 + a1*s + ... + aq*s^q)
    # If Hr(s) ~= H(s), what are the a's and b's in Hr(s)? When these a's
    # and b's are solved, the reduced order system with Hr(s) can replace
    # the original high-order H(s) in fast simulation.

    # Our whole problem now becomes to solve a's and b's that satisfying,
    # (b(0) + b(1)*s + ... + b(q-1)*s^(q-1)) / (1 + a(1)*s + ... + a(q)*s^q)
    #     = m(0) + m(1)*s + m(2)*s^2 + ... + m(2q-1)*s^(2q-1)
    # Of course, we can choose many individual S values, and put them
    # into this equation to form many equations about a and b. That is called
    # as POINT MATCHING in S domain.
    #
    # In MOMENT MATCHING, we use below to evaluate a's and b's,
    # --------
    #   m0     m1  ... m(q-1)        aq            mq
    #   m1     m2  ... mq            a(q-1)        m(q+1)
    # [ ...    ...             ] *  [ ...  ] = - [ ...     ]    <1>
    #   m(q-1) mq  ... m(2q-2)       a1            m(2q-1)
    # --------
    # which is obtained by cross multiplying Hr(s) and H(s), and matching
    # terms of same order (from m0 to m(2q-1)). In other words, Hr(s)
    # can matches m0 through m(2q-1) of H(s)

    # Prepare all first 2*q moments for H(s), stored in moment_list
    invAmat = np.linalg.inv(Amat)
    invAmat_i = invAmat    # temporarily holding Amat^(-i)
    moment_list = []   # holding m0, m1, ... , m(2q-1)
    for i in range(qParam * 2):
        # see minus sign in moment mk definition
        moment_list.append(-1.0*float(np.dot(np.dot(cmat.T, invAmat_i), bmat)))
        invAmat_i = np.dot(invAmat_i, invAmat)

    print("moment_list", moment_list)

    # Task ONE, solving -> momentMAT * [aV] = momentV
    # momentMAT is the moment matrix on left of equations <1>
    # momentV is the moment vector on right of equations <1>
    # [aV] is for a vector of coefficients a's on Hr(s) denominator,
    # and [aV] element order is also as in equations <1>
    # elements of both momentMAT and momentV are in moment_list now,
    # and the final result,
    # [aV] = inv(momentMAT) * momentV

    momentMAT = np.diag([0.0] * qParam)
    momentV = np.zeros([qParam, 1])
    aV = np.zeros([qParam, 1])

    for i in range(qParam):    # row
        for j in range(qParam):    # column
            momentMAT[i][j] = moment_list[i+j]
        momentV[i] = moment_list[qParam+i]

    # See <1> for this minus sign
    aV = -1.0 * np.dot(np.linalg.inv(momentMAT), momentV)

    # den stands for denominator of Hr(s), and be noted of its order
    den = []
    for each in aV:
        den.append(float(each))
    den.append(1)    # append a '1' to it

    # denominator polynomial coefficients with order of,
    #     a_q, a_q-1, ..., a_2, a_1, 1
    #print(den)

    # Task TWO, calculating the numerator of Hr(s)- bV from below,
    # --------
    #   a(q-1) a(q-2) ...   a2   a1  1      m0           b(q-1)
    #   a(q-2) ...    ...   a1   1   0      m1           ...
    # [  ...   ...    ...   ...  ...  ] * [ ...   ] =  [ ...   ]  <2>
    #   a2     a1     1     ...  0   0      m(q-3)       b2
    #   a1     1      ... 0 ...  0   0      m(q-2)       b1
    #   1      0      ... 0 ...  0   0      m(q-1)       b0
    # --------
    # which is equivalent to,
    #   den_1   den_2   ...   den_q-1  den_q      m0           b(q-1)
    #   den_2   ...     ...   den_q    0          m1           ...
    # [  ...    ...     ...   ...      0     ] * [ ...   ] =  [...   ]
    #   den_q-2 den_q-1 ...   ...      0          m(q-3)       b2
    #   den_q-1 den_q   ...   ...      0          m(q-2)       b1
    #   den_q   0       ...   ...      0          m(q-1)       b0

    bV = np.zeros([qParam, 1])
    for i in range(qParam):
        for j in range(qParam):
            if j+i+1 <= qParam:
                bV[i] = bV[i] + moment_list[j] * den[j+i+1]

    # num stands for numerator of Hr(s), and be noted of its order
    num = []
    for each in bV:
        num.append(float(each))
    #print(num)

    # a's and b's coefficient vectors are stored in their corresponding
    # lists [num] and [den] with elements in ascending form -->
    # num = [b(q-1), b(q-2), ..., b2, b1, b0]
        # num = [b(q-1)*s^(q-1), b(q-2)*s^(q-2), ..., b2*s^2, b1*s, b0]
    # den = [aq, a(q-1), ..., a2, a1, 1]
        # den = [aq*s^q, a(q-1)*s^(q-1), ..., a2*s^2, a1*s, 1]

    # For usage of signal.TransferFunction(), see docs.scipy.org pages
    print("num", num)
    print("den", den)
    system = signal.TransferFunction(num, den)
    time = np.arange(0, endTime, deltaTime)
    # It is not difficult to calculate system response, after being given
    # a transfer function. Remember how to do inverse Laplace Transform?
    # Using scipy function here for simplicity.
    resTup = signal.step(system, T=time)
    return resTup


if __name__ == '__main__':
    # If this program is not 'imported' by other program,
    # call momentMatching() to get voltage waves and time intervals;
    # also get corresponding exact curve of the same N(order)
    # from ladderWave().
    # Here, for clarity and full convergence, we set time=20000, and try
    # N=10, qParam=1
    # N=100, qParam=2

    #order = 10
    #reduction_order = 1

    order = 300
    reduction_order = 2

    t1 = tm.time()
    (v, t) = lad.ladderWave(N=order, endTime=50000, deltaTime=0.1)
    lad.plot_wave(t, v, 'r--', name='N=' + str(order) + ' original')

    t2 = tm.time()

    data = momentMatching(N=order, qParam=reduction_order, endTime=50000,
                          deltaTime=0.1)
    lad.plot_wave(data[0], data[1], 'y:', name='N=' + str(order) +
                  ', order ' + str(reduction_order) + ' moments matching')

    t3 = tm.time()

    print("Time costs are (original vs. moment-matched):")
    print("%.4f" % (t2-t1) + "s", "vs.", "%.4f" % (t3-t2) + "s")

    # Elmore delay of your ladder is?
    print("Elmore delay of %.3d order ladder is %.4fs"
          % (order, lad.elmoreDelay(order)))

    plt.title("Moment matching(yellow) vs. Original(red)", fontsize=12)
    plt.ylabel("Output(V)")
    plt.xlabel("Time: in your deltaTime unit")
    plt.legend()
    plt.show()
