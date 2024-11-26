from r_solver_utils.element import Element, RES_TYPE, VOLTAGE_TYPE, VCVS_TYPE

import sympy as sp

def parse_netlist(file):
    lines = file.readlines()

    num_nodes = 0
    num_voltages = 0
    num_resistors = 0
    num_extras = 0
    elements = []
    
    for l in lines:
        l = l.strip()  # Remove any extra whitespace/newlines
        if l.startswith('R'):
            el_type = 'RES'  # Indicating resistor
            port = num_resistors
            num_resistors += 1
        elif l.startswith('V'):
            el_type = 'VOLTAGE'  # Indicating voltage source
            port = num_voltages
            num_voltages += 1
        elif l.startswith('E'):
            el_type = 'VCVS'  # Indicating voltage-controlled voltage source
            num_extras += 1
        
        parts = l.split()  # Split by spaces to get individual components
        el_impedance = parts[0]
        el_node1 = int(parts[1])
        el_node2 = int(parts[2])

        num_nodes = max(num_nodes, el_node1, el_node2)

        if el_type == 'VCVS':  # VCVS elements have additional nodes and a gain
            el_node3 = int(parts[3])
            el_node4 = int(parts[4])
            el_gain = sp.symbols(parts[5])  # Create a symbolic variable for the gain
            elements.append(Element(
                type=el_type, node1=el_node1 - 1, node2=el_node2 - 1,
                impedance=sp.symbols(el_impedance), port=num_extras - 1, 
                node3=el_node3 - 1, node4=el_node4 - 1, gain=el_gain
            ))
        else:
            print(f'Adding element: {el_type} {el_node1} {el_node2} {el_impedance}')
            elements.append(Element(
                type=el_type, node1=el_node1 - 1, node2=el_node2 - 1,
                impedance=sp.symbols(el_impedance), port=port
            ))

    assert(num_resistors == num_voltages)  # Make sure number of resistors matches voltages
    num_ports = num_voltages  # Set the number of ports to the number of voltage sources

    return elements, num_nodes, num_ports, num_extras
