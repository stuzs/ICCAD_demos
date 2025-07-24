#!/usr/bin/env python
"""An IC fabrication demo showing MPW photomask and its projections on
silicon wafer, with demos on Python code basics and using GUI in Python.
"""
# I used 'autopep8' to convert code to be PEP8 compliant,
# but some places looked not so concise as before, so modified a little
# for github re-post in 03/18/2024

# use Tkinter in Python 2, but tkinter in Python 3
import tkinter as tk


def sdist(x, y):
    """Return squared distance with respect to the (0, 0) origin,
    which is the center of the wafer.
    """
    return x * x + y * y


def fully_outside(x, y, w, h, radius):
    """Try to judge whether a rectangle is fully outside a circle.
    The rectangle is defined by its bottom-left corner, width and height;
    the circle's center is on (0,0), and has a given 'radius'.
    """
    R2 = radius * radius
    # can we remove '\' here?
    if sdist(x, y) > R2 and sdist(x + w - 1, y) > R2 \
            and sdist(x, y + h - 1) > R2 \
            and sdist(x + w - 1, y + h - 1) > R2:
        return True
    return False


def mpw(dlist):
    """Return the asked-for field width and height in a tuple 'wrap',
    and return all dice information(x/y/w/h) through parameter 'dlist'.
    The information in list 'planned' could be automatically generated
    by a dice placement optimizer, but here we just give a certain layout
    plan for demo; 'wrap' contains the two dimensions of the boundary box
    holding all planned dice (i.e., a bounding box).
    """
    planned = [(0, 0, 15, 15),
               (15, 0, 15, 10),
               (15, 10, 8, 8),
               (0, 15, 4, 5),
               (5, 15, 4, 5),
               (10, 15, 5, 5),
               (25, 12, 5, 7)]

    wrap = (30, 20)
    # let us try to automatically generate 'wrap' in homework

    for t in planned:
        dlist.append(t)
    # would you try use 'dlist = planned' to replace the 2 lines above?

    return wrap


def fields(width=30, height=30, diameter=300, detail=False):
    """Expose many fields (shots) on wafer by a stepper; each field has its
    width and height; each wafer has a specified diameter, the default
    'diameter=300' indicating a 12 inches wafer.
    When setting argument 'detail=True':
        Parameters 'width' and 'height' then have no meaning at all;
        mpw() will return a list of die positions and dimensions, and
        then each die inside each field is drawn finely.
    The wafer center might be on a field center or on field corners,
    but here to demonstrate Python list, we only implement the latter.
    """
    root = tk.Tk()
    radius = int(diameter / 2)
    x_c = 1.5 * radius
    y_c = 1.25 * radius
    cv = tk.Canvas(root, bg='white', width=2*x_c, height=2*y_c)

    # draw a wafer whose center is on canvas center, r=radius
    cv.create_oval(x_c - radius, y_c - radius,
                   x_c + radius, y_c + radius, outline='red')
    cv.pack()

    if detail:
        dice_list = []
        # if detail is True, field width and height are over-set by mpw()
        (width, height) = mpw(dice_list)

    # to expose all fields, first generate a xy_list of tuples which
    # contains the bottom-left corners of all fields in the 4 quadrants
    x_list = [x for x in range(0, radius, width)]
    y_list = [y for y in range(0, radius, height)]

    xy_list = [(x, y) for x in x_list for y in y_list] \
        + [(-x - width, y) for x in x_list for y in y_list] \
        + [(-x - width, -y - height) for x in x_list for y in y_list] \
        + [(x, -y - height) for x in x_list for y in y_list]

    field_count = 0
    for (x, y) in xy_list:
        if not fully_outside(x, y, width, height, radius):
            cv.create_rectangle(x_c + x, y_c + y,
                                x_c + x + width, y_c + y + height, width=1)
            field_count += 1

            # next, draw all mpw dice in detail; the coordinates are
            # already stored in dice_list by mpw()
            if detail:
                for (xx, yy, ww, hh) in dice_list:
                    x1 = x_c + x + xx
                    y1 = y_c + y + yy
                    cv.create_rectangle(x1, y1, x1 + ww, y1 + hh)

    print("Actual field width and height = %d, %d;" % (width, height))
    print("Total actually stepping fields = %d;" % field_count)
    # However, there might be some fields barely-touched wafer edge,
    # and which could be left for fine tuning in homework later.

    root.mainloop()


def show_mpw(n=10):
    """Show the MPW placement in detail with an enlarging scale 'n'.
    Usage: show_mpw() or show_mpw(n=value)
    """
    # get MPW geometrical information from function mpw()
    singleMPW = []
    (w, h) = mpw(singleMPW)

    root = tk.Tk()
    cv = tk.Canvas(root, bg='white', width=20+w*n, height=20+h*n)
    cv.pack()

    # initialize position setting
    xcor = 10
    ycor = 10

    cv.create_rectangle(xcor, ycor, xcor+w*n, ycor+h*n, fill='lightgrey')

    for (x, y, w, h) in singleMPW:
        x1 = xcor + x * n
        y1 = ycor + y * n
        cv.create_rectangle(x1, y1, x1+w*n, y1+h*n, width=3, fill='grey')

    root.mainloop()

# Let us try all commands below, one by one.
# It is easier in an interactive environment to run commands together.

#show_mpw()
#show_mpw(n=30)
#fields()
#fields(24,28,200)
#fields(30,20)
#fields(detail=True)
#fields(detail=True, diameter=450)

# Let us try another dice floor plan (and try using vim to copy them up
# and remove # signs on line beginnings).
#    planned = [(0, 0, 15, 15), \
#         (15, 0, 10, 15), \
#         (0, 15, 8, 8), \
#         (8, 15, 5, 4), \
#         (8, 19, 5, 4), \
#         (13, 15, 5, 5), \
#         (18, 15, 7, 5)]
#
#    wrap = (25, 23)
# also try to automatically generate 'wrap' as required in homework
