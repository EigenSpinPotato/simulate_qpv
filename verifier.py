#%%
import netsquid as ns
from netsquid.protocols import NodeProtocol
from component import BitflipError
from bool_function import bool_func
#%%
class V0Protocol(NodeProtocol):
    def __init__(self, len, node=None, name=None, x=1, y=1, z=1, p=0,spam=False, me=True, sp=False):
        super().__init__(node, name)
        self.result = None
        self.answer = None
        self.start_time = 0
        self.end_time = 0
        self.len = len
        self.x = x
        self.y = y
        self.z = z 
        self.p = p
        self.spam = spam
        self.me = me
        self.sp = sp
        self.wait_time = 0
    
    def set_time(self):
        self.wait_time = (self.len/2e5-self.len/3e5)*1e9

    def get_elapsed_time(self):
        return self.end_time - self.start_time
    
    def get_ideal_time(self):
        return 2 * (self.len/2e5) + 1e-5
    
    def apply_sp_error(self, qubit):
        error = BitflipError(p=self.p)
        error.error_operation(qubit=qubit)

    def apply_measurement_error(self, qubit):
        error = BitflipError(p = self.p)
        error.error_operation(qubit=qubit)

    def get_result(self):
        return self.result
    
    def get_answer(self):
        return self.answer
    
    def prepare_epr_pair(self):
        q1 = ns.qubits.create_qubits(1)[0]
        q2 = ns.qubits.create_qubits(1)[0]
        if self.spam is True or self.sp is True:
            self.apply_sp_error(q1)
            self.apply_sp_error(q2)
        ns.qubits.operate(q1, ns.H)
        ns.qubits.operate([q1,q2], ns.CNOT)
        return q1, q2
    
    def run(self):
        self.start_time = ns.sim_time()
        port_q = self.node.ports['quantum']
        port_c1 = self.node.ports['v0p']
        q1, q2 = self.prepare_epr_pair()
        port_q.tx_output(q1)
        yield self.await_timer(duration = (self.len/2e5-self.len/3e5)*1e9)
        port_c1.tx_output(self.x)

        while True:
            yield self.await_port_input(port_c1)
            answer = port_c1.rx_input().items[0]
            print(f'answer received at V0 with state {self.answer} ')
            if self.me is True:
                self.apply_measurement_error(q2)
            if answer is not None:
                if bool_func(self.x, self.y, self.z) == 0:
                    state, prob = ns.qubits.measure(q2)
                    labels_z =  ("|0>", "|1>")
                    # print(f"V0's particle {self.node.name} measured "
                    #       f"{labels_z[state]} with probability {prob:.2f}")
                else:
                    state, prob = ns.qubits.measure(q2, observable=ns.X)
                    labels_z =  ("|+>", "|->")
                    # print(f"V0's particle {self.node.name} measured "
                    #     f"{labels_z[state]} with probability {prob:.2f}")
                self.result = labels_z[state]
            else:
                self.result = None

            self.end_time = ns.sim_time()
            self.answer = answer
#%%
class V1Protocol(NodeProtocol):
    def __init__(self, len, y=1, node=None, name=None):
        super().__init__(node, name)
        self.answer = None
        self.end_time = 0
        self.start_time = 0
        self.y = y
        self.len = len

    def run(self):
        port_c2 = self.node.ports['v1p']
        yield self.await_timer(duration = (self.len/2e5-self.len/3e5)*1e9)
        port_c2.tx_output(self.y)
        self.start_time = ns.sim_time()
        while True:
            yield self.await_port_input(port_c2)
            self.answer = port_c2.rx_input().items[0]
            self.end_time = ns.sim_time()
            print(f'answer received at V1 with state {self.answer} ')

    def get_elapsed_time(self):
        return self.end_time - self.start_time
    
    def get_answer(self):
        return self.answer
# %%
class V2Protocol(NodeProtocol):
    def __init__(self, len, z=1, node=None, name=None):
        super().__init__(node, name)
        self.answer = None
        self.end_time = 0
        self.start_time = 0
        self.z = z
        self.len = len

    def run(self):
        port_c3 = self.node.ports['v2p']
        yield self.await_timer(duration = (self.len/2e5-self.len/3e5)*1e9)
        port_c3.tx_output(self.z)
        self.start_time = ns.sim_time()
        while True:
            yield self.await_port_input(port_c3)
            self.answer = port_c3.rx_input().items[0]
            self.end_time = ns.sim_time()
            print(f'answer received at V2 with state {self.answer} ')

    def get_elapsed_time(self):
        return self.end_time - self.start_time
    
    def get_answer(self):
        return self.answer