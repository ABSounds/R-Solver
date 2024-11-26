# Simple script for generating R-type adaptors.
# The resulting Scattring matrics will be in terms
# of the port impedance (Rp).

from datetime import datetime

import argparse
from sympy import SparseMatrix
from r_solver_utils.parse_netlist import parse_netlist
from r_solver_utils.matrix_helpers import adapt_port, compute_S_matrix, construct_X_matrix, remove_datum_node
from r_solver_utils.print_helpers import print_matrix, print_shape, verbose_print

def main(args, custom_args=False):
    # Print the start time (only the time part)
    start_time = datetime.now()
    print(f"Process started at: {start_time.strftime('%H:%M:%S')}")

    elements, num_nodes, num_ports, num_extras = parse_netlist(args.netlist)
    
    print('Constructing X matrix...')
    X_mat = construct_X_matrix(elements, num_nodes, num_ports, num_extras)
    print(f'Shape of the initial X matrix: {X_mat.shape}')
    
    print('Removing datum node...')
    X_mat = remove_datum_node(X_mat, int(args.datum))
    X_mat = SparseMatrix(X_mat)
    print(f'Shape of the X matrix after removing datum node: {X_mat.shape}')

    print('Trying to simplify X matrix...')
    X_mat = X_mat.simplify()

    print('Inverting X matrix...')
    X_inv = X_mat.inv(method='LU', try_block_diag=True)
    del X_mat

    print('Computing scattering matrix...')
    Scattering_mat, Rp = compute_S_matrix(X_inv, elements, num_ports, num_extras)
    del X_inv

    port_to_adapt = int(args.adapted_port)
    adapt_expr = None
    if port_to_adapt >= 0:
        print('Adapting port...')
        Scattering_mat, adapt_expr = adapt_port(Scattering_mat, Rp, port_to_adapt)
    else:
        print('No port to adapt')
    
    print('Simplifying matrix...')
    Scattering_mat = Scattering_mat.simplify()

    # Print the end time in the same format
    end_time = datetime.now()
    print(f"Process completed at: {end_time.strftime('%H:%M:%S')}")
    print('All done!')
    print_matrix(Scattering_mat, args.out_file, num_ports, adapt_expr, args, custom_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Derive the R-type scattering matrix for a given circuit.')
    
    parser.add_argument('netlist', type=argparse.FileType('r'),
                        help='The netlist to construct the matrix for')

    parser.add_argument('--datum', dest='datum', default=0,
                        help='The \"datum\" node to remove from the MNA matrix. Note that indexing starts at 0.')

    parser.add_argument('--adapt', dest='adapted_port', default=-1,
                        help='Specify a port index to adapt. If this argument is not specified, no port will be adapted. Note that indexing starts at 0.')

    parser.add_argument('--out', dest='out_file', type=argparse.FileType('w'), default=None,
                        help='Output file to write the scattering matrix to')

    parser.add_argument('--verbose', action='store_const', const=True,
                        help='Use this flag to have the solver print extra intermediate information')
    parser.set_defaults(verbose=False)

    args = parser.parse_args()
    main(args)
