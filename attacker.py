#%%
import netsquid as ns
from netsquid.protocols import NodeProtocol
from component import BitflipError
import random
from bool_function import bool_func
#%%
class Alice_g(NodeProtocol):
    def __init__(self, node=None, name=None):
        super().__init__(node, name)
        self.basis = None
        self.qubit = None
        self.answer = None   
        self.port_q = self.node.ports['Alice_q']
        self.port_c0 = self.node.ports['Alice_c0']
        self.port_c1 = self.node.ports['Alice_c1']
        self.port_c2 = self.node.ports['Alice_c2']
    
    def random_guess(self):
         self.basis = random.randint(0, 2)
         if self.basis == 0:
                state, prob = ns.qubits.measure(self.qubit)
                labels_z =  ("|0>", "|1>")
                self.answer = labels_z[state]
         else:
            state, prob = ns.qubits.measure(self.qubit, observable=ns.X)
            labels_z =  ("|+>", "|->")
            self.answer = labels_z[state]
    
    def run(self):
        while True:
            yield (self.await_port_input(self.port_q))
            self.qubit = self.port_q.rx_input().items[0]
            self.random_guess()
            yield (self.await_port_input(self.port_c0) or self.await_port_input(self.port_c2) or self.await_port_input(self.port_c1))
            x = self.port_c0.rx_input().items[0]
            y = self.port_c1.rx_input().items[0]
            z = self.port_c2.rx_input().items[0]

            if bool_func(x, y, z) != self.basis:
                self.answer = None

            print(self.answer)
            self.port_c0.tx_output(self.answer)
            self.port_c1.tx_output(self.answer)
            self.port_c2.tx_output(self.answer)

class Bob_g(NodeProtocol):
    def __init__(self, node=None, name=None):
        super().__init__(node, name)
        self.answer = None        
        self.port_ba = self.node.ports['ba']
        self.port_c = self.node.ports['Bob']
    
    def run(self):
        while True:
            yield self.await_port_input(self.port_c)
            self.answer = self.port_c.rx_input().items[0]
            self.port_ba.tx_output(self.answer)
            yield self.await_port_input(self.port_ba)
            self.port_c.tx_output(self.answer)

class Charlie_g(NodeProtocol):
    def __init__(self, node=None, name=None):
        super().__init__(node, name)
        self.answer = None        
        self.port_ca = self.node.ports['ca']
        self.port_c = self.node.ports['Charlie']
    
    def run(self):
        while True:
            yield self.await_port_input(self.port_c)
            self.answer = self.port_c.rx_input().items[0]
            self.port_ca.tx_output(self.answer)
            yield self.await_port_input(self.port_ca)
            self.port_c.tx_output(self.answer)