import netsquid as ns
from netsquid.protocols import NodeProtocol
from bool_function import bool_func
from component import BitflipError

class PProtocol(NodeProtocol):
    def __init__(self, node=None, name=None, p=0, me=True):
        super().__init__(node, name)
        self.x = None
        self.y = None
        self.z = None
        self.p = p
        self.me = me
        self.port_q = self.node.ports['quantum']
        self.port_c = self.node.ports['pv0']
        self.port_c2 = self.node.ports['pv1']
        self.port_c3 = self.node.ports['pv2']
    
    def apply_measurement_error(self, qubit):
        error = BitflipError(p = self.p)
        error.error_operation(qubit=qubit)

    def run(self):
        while True:
            yield self.await_port_input(self.port_q) 
            qubit = self.port_q.rx_input().items[0]
            yield (self.await_port_input(self.port_c) or self.await_port_input(self.port_c2) or self.await_port_input(self.port_c3))
            self.x = self.port_c.rx_input().items[0]
            self.y = self.port_c2.rx_input().items[0]
            self.z = self.port_c3.rx_input().items[0]
            
            if self.me is True:
                self.apply_measurement_error(qubit=qubit)

            if bool_func(self.x, self.y, self.z) == 0:
                state, prob = ns.qubits.measure(qubit)
                labels_z =  ("|0>", "|1>")
                print(f"{ns.sim_time()}: Particle p received and measured "f"{labels_z[state]} with probability {prob:.2f}")
            else:
                state, prob = ns.qubits.measure(qubit, observable=ns.X)
                labels_z =  ("|+>", "|->")
                print(f"{ns.sim_time()}: Particle p received and measured "
                    f"{labels_z[state]} with probability {prob:.2f}")
            
            self.port_c.tx_output(labels_z[state])
            self.port_c2.tx_output(labels_z[state])
            self.port_c3.tx_output(labels_z[state])