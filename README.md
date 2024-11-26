# R-Solver

A Python tool for deriving R-Type adaptors for
[Wave Digital Filters](https://github.com/jatinchowdhury18/WaveDigitalFilters).

## How It Works

In order to use this script, you must have the [SymPy](https://www.sympy.org/)
package installed. You can run the `r_solver.py` script from command line using
using the command `python r_solver.py my_netlist.txt`, to generate a scattering
matrix for a given netlist. For more options, use `r_solver.py --help`.

## Netlist Format
The format for the input netlists can be seen in the
example netlists provided in the `netlists/` directory.
One important thing to note, is that all resistors must
be given a 2-character label, e.g. 'Ra'. Remember that
voltage sources are defined with the "positive" node first.
