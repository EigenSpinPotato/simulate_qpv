
#%%
from netsquid.components import QuantumChannel, ClassicalChannel
from netsquid.nodes import DirectConnection, Connection
from netsquid.components.models.qerrormodels import FibreLossModel
from netsquid.components.models import qerrormodels
import netsquid as ns
import random
#%%
class ClassicalConnection(DirectConnection):
    def __init__(self, length, name='ClassicalConnection', direction='Bi', models=None):
        '''
        Init classical connection(s) between nodes. We assume data is tranmistted with microwave at speed c=3e5.

        IMPORTANT NOTE: it seems the default fibre delay model is broken. 
        '''
        super().__init__(name=name)
        self.len = length

        if direction != 'B2A':
            self.add_subcomponent(ClassicalChannel('Channel_A2B', length=self.len, delay=self.len/3e5, models=models),
                                  forward_input=[('A', 'send')],
                                  forward_output=[('B', 'recv')])

        if direction != 'A2B':
            self.add_subcomponent(ClassicalChannel('Channel_B2A', length=self.len, delay=self.len/3e5, models=models),
                                  forward_input=[('B', 'send')],
                                  forward_output=[('A', 'recv')])
# %%
class QuantumConnection(Connection):
    def __init__(self, length, name='QuantumConnection', direction='A2B', models=None, p_loss_init=0, p_loss_length=0.2):
        super().__init__(name=name)
        self.len = length
        if models is None:
            models = {
                'quantum_loss_model': FibreLossModel(p_loss_init=p_loss_init, p_loss_length=p_loss_length)
            }

        if direction != 'B2A':
            self.add_subcomponent(QuantumChannel('QChannel_A2B', length=self.len, delay=self.len/2e5, models=models),
                                  forward_input=[('A', 'send')],
                                  forward_output=[('B', 'recv')])

        if direction != 'A2B':
            self.add_subcomponent(QuantumChannel('QChannel_B2A', length=self.len, delay=self.len/2e5, models=models),
                                  forward_input=[('B', 'send')],
                                  forward_output=[('A', 'recv')])
# %%
class BitflipError():
    def __init__(self, p=0.1):
        self.p = p * 100
        self.qubit = None
    
    def error_operation(self, qubit):
        self.qubit = qubit
        r = random.randint(1, 100)
        if r <= self.p:
            dice = random.randint(0, 1)
            if dice == 1:
                ns.qubits.operate(self.qubit, ns.X)
            else:
                ns.qubits.operate(self.qubit, ns.H)
        else:
            ns.qubits.operate(self.qubit, ns.I)

        return self.qubit