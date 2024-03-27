* A wire cube's equivalent diagonal resistance 
* The cube has a wire framework that all wire edges
* have a 1-Ohm resistor on them.
* 4 nodes (cube vertices) are on up-plane
* 4 nodes (cube vertices) are on down-plane
* There are twelve 1-Ohm resistors connecting the nodes.
ru12 u1 u2 1
ru23 u2 u3 1
ru34 u3 u4 1
ru41 u4 u1 1
rd12 d1 d2 1
rd23 d2 d3 1
rd34 d3 d4 1
rd41 d4 d1 1
rv1 u1 d1 1
rv2 u2 d2 1
rv3 u3 d3 1
rv4 u4 d4 1
Vnull u3 Gnd 0
v1 d1 GND 1
