#%% Simulate various attacks
import netsquid as ns
import numpy as np
from netsquid.nodes import Node
from component import QuantumConnection, ClassicalConnection
from verifier import V0Protocol, V1Protocol, V2Protocol
from attacker import Alice_g
#%%
def random_guess(round, distance, x, y, z, measurement_error=0, loss_rate=0.2, spam=False):
    fibre_distance = np.arange(1, distance)
    p_err = []
    time = []
    for d in fibre_distance:
        correct_counter = 0
        for i in range(round):
            ns.sim_reset()
            # Init three nodes
            node_v0 = Node('v0', port_names = ['quantum', 'v0p'])
            node_v1 = Node('v1', port_names=['v1p'])
            node_v2 = Node('v2', port_names=['v2p'])
            # Init attackers
            node_Alice = Node('A', port_names=['Alice_q', 'Alice_c0', 'Alice_c1', 'Alice_c2'])
            # Classical channel with delay = distance/3e5, connection between V0 and A
            c_connection1 = ClassicalConnection(length=d, name='p0v1', direction='Bi')
            node_v0.ports['v0p'].connect(c_connection1.ports['A'])
            node_Alice.ports['Alice_c0'].connect(c_connection1.ports['B'])
            # Classical connection between P and V1
            c_connection2 = ClassicalConnection(length=d, name='v1p', direction='Bi')
            node_v1.ports['v1p'].connect(c_connection2.ports['A'])
            node_Alice.ports['Alice_c1'].connect(c_connection2.ports['B'])
            # Classical connection between P and V2
            c_connection3 = ClassicalConnection(length=d, name='v2p', direction='Bi')
            node_v2.ports['v2p'].connect(c_connection3.ports['A'])
            node_Alice.ports['Alice_c2'].connect(c_connection3.ports['B'])
            # Quantum connection between V0 and P, with delay = d/2e5, and attenuation
            q_connection = QuantumConnection(name="Channel_A2B", length=d, direction='A2B',  p_loss_length=loss_rate)
            node_v0.ports['quantum'].connect(q_connection.ports['A'])
            node_Alice.ports['Alice_q'].connect(q_connection.ports['B'])

            v0_protocol = V0Protocol(node=node_v0, x=x, y=y, z=z, len=d, p=measurement_error, spam=spam)
            Alice_protocol = Alice_g(node=node_Alice)
            v1_protocol = V1Protocol(node=node_v1, y=y, len=d)
            v2_protocol = V2Protocol(node=node_v2, z=z, len=d)
            # Start protocol
            Alice_protocol.start()
            v0_protocol.start()
            v1_protocol.start()
            v2_protocol.start()
            
            stats = ns.sim_run()
            # Check results
            a = v0_protocol.get_answer()
            b = v1_protocol.get_answer()
            c = v2_protocol.get_answer()
            m = v0_protocol.get_result()

            print(a, b, c, m)

            if a is None or b is None or c is None:
                print('loss')
            else:
                if a == b == m == c: 
                    print('correct')
                    correct_counter = correct_counter + 1
                elif a != b or a != m or c != m or a != c:
                    print('Wrong')
                else:
                    print('Abort')
            # Reset the timer
            ns.sim_reset()

        time.append(v0_protocol.get_elapsed_time())
        p_err.append((round-correct_counter)/round)
    return p_err, fibre_distance, time
#%%
def random_guess_photon_loss(round, eta, x, y, z, measurement_error=0, spam=False):
    d = 10
    p_err = []
    for e in eta:
        correct_counter = 0
        for i in range(round):
            ns.sim_reset()
            # Init three nodes
            node_v0 = Node('v0', port_names = ['quantum', 'v0p'])
            node_v1 = Node('v1', port_names=['v1p'])
            node_v2 = Node('v2', port_names=['v2p'])
            # Init attackers
            node_Alice = Node('A', port_names=['Alice_q', 'Alice_c0', 'Alice_c1', 'Alice_c2'])
            # Classical channel with delay = distance/3e5, connection between V0 and A
            c_connection1 = ClassicalConnection(length=d, name='p0v1', direction='Bi')
            node_v0.ports['v0p'].connect(c_connection1.ports['A'])
            node_Alice.ports['Alice_c0'].connect(c_connection1.ports['B'])
            # Classical connection between P and V1
            c_connection2 = ClassicalConnection(length=d, name='v1p', direction='Bi')
            node_v1.ports['v1p'].connect(c_connection2.ports['A'])
            node_Alice.ports['Alice_c1'].connect(c_connection2.ports['B'])
            # Classical connection between P and V2
            c_connection3 = ClassicalConnection(length=d, name='v2p', direction='Bi')
            node_v2.ports['v2p'].connect(c_connection3.ports['A'])
            node_Alice.ports['Alice_c2'].connect(c_connection3.ports['B'])
            # Quantum connection between V0 and P, with delay = d/2e5, and attenuation
            q_connection = QuantumConnection(name="Channel_A2B", length=d, direction='A2B',  p_loss_length=e/2)
            node_v0.ports['quantum'].connect(q_connection.ports['A'])
            node_Alice.ports['Alice_q'].connect(q_connection.ports['B'])

            v0_protocol = V0Protocol(node=node_v0, x=x, y=y, z=z, len=d, p=measurement_error, spam=spam)
            Alice_protocol = Alice_g(node=node_Alice)
            v1_protocol = V1Protocol(node=node_v1, y=y, len=d)
            v2_protocol = V2Protocol(node=node_v2, z=z, len=d)
            # Start protocol
            Alice_protocol.start()
            v0_protocol.start()
            v1_protocol.start()
            v2_protocol.start()
            
            stats = ns.sim_run()
            # Check results
            a = v0_protocol.get_answer()
            b = v1_protocol.get_answer()
            c = v2_protocol.get_answer()
            m = v0_protocol.get_result()

            print(a, b, c, m)

            if a is None or b is None or c is None:
                print('loss')
            else:
                if a == b == m == c: 
                    print('correct')
                    correct_counter = correct_counter + 1
                elif a != b or a != m or c != m or a != c:
                    print('Wrong')
                else:
                    print('Abort')
            # Reset the timer
            ns.sim_reset()
        p_err.append((round-correct_counter)/round)
    return p_err