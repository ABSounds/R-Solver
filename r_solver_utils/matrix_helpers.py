from sympy import Matrix, symbols, eye, solve, simplify, SparseMatrix

from r_solver_utils.element_stamps import stamp_element
from r_solver_utils.element_stamps import RES_TYPE


def construct_X_matrix(elements, num_nodes, num_ports, num_extras):
    '''Constructs an \'X\' Matrix for doing MNA'''
    X_mat = Matrix.zeros(num_nodes + num_ports + num_extras, num_nodes + num_ports + num_extras)

    for el in elements:
        X_mat = stamp_element(X_mat, el, num_nodes, num_ports)

    return X_mat


def remove_datum_node(X_mat, datum):
    matrix_range = [x for x in range(X_mat.shape[0]) if x != datum]
    return X_mat[matrix_range, :][:, matrix_range]  # SymPy handles the slicing 


def compute_S_matrix(X_inv, elements, num_ports, num_extras):
    start_ports = -(num_ports + num_extras)
    end_ports = -num_extras if num_extras > 0 else X_inv.shape[1]

    # Create symbolic identity matrices
    vert_id = Matrix.zeros(X_inv.shape[0], num_ports)
    vert_id[start_ports:end_ports, :] = eye(num_ports)

    hor_id = Matrix.zeros(num_ports, X_inv.shape[1])
    hor_id[:, start_ports:end_ports] = eye(num_ports)

    # Construct the Rp diagonal matrix
    Rp_diag = Matrix.zeros(num_ports, num_ports)
    for el in elements:
        if el.type == 'RES':
            Rp_diag[el.port, el.port] = el.impedance

    # Compute the scattering matrix S
    S_mat = eye(num_ports) + 2 * Rp_diag * hor_id * X_inv * vert_id

    return S_mat, Rp_diag


def adapt_port(S_mat, Rp, port):
    '''Adapts one port of the scattering matrix to be a reflection-free port'''
    if port < 0 or port >= S_mat.shape[0]:
        raise IndexError('Port index must be less than the number of available ports')

    # Get the S matrix element at (port, port)
    S_nn = S_mat[port, port]
    
    # Get the impedance matrix element at (port, port)
    R_n = Rp[port, port]

    # Solve the equation S_nn == 0 for the impedance R_n
    R_n_solves = solve(S_nn - 0, R_n)
    R_n_solve_expr = R_n_solves[0]  # Take the first solution (assuming it exists)

    # Get the solved impedance value (right-hand side of the expression)
    R_n_solved = R_n_solve_expr.rhs

    # Print the adapted impedance value
    print('')
    print('Adapted Port Impedance:')
    print(R_n_solve_expr)

    # Substitute the solved impedance back into the scattering matrix
    S_mat_substituted = S_mat.subs({R_n: R_n_solved})

    return S_mat_substituted, R_n_solve_expr
