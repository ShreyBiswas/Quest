from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister,execute,Aer

def stringify(k,n,bit_size):
    k_string = format(k,f'0{bit_size}b')
    n_string = format(n,f'0{bit_size}b')[::-1] # reversed because qiskit's qubits are in reverse order
    return k_string,n_string


def ccOR(circ,a,b,ancilla): #controlled-controlled-OR gate
    circ.barrier()
    circ.x(a)
    circ.x(b)
    circ.x(ancilla)

    circ.ccx(a,b,ancilla)

    circ.x(a)
    circ.x(b)
    circ.barrier()
    return circ

def single_qubit_comparison(circ,a,b):
    if a == 0:# and b=='1': # there is no a-1 ancilla for a=0, so only a single CNOT is needed
        circ.cx(inputs[0],ancillae[0])
        return circ

    if b=='1':
        circ.barrier()
        circ.ccx(inputs[a],ancillae[a-1],ancillae[a])
    else:
        circ = ccOR(circ,inputs[a],ancillae[a-1],ancillae[a])
    return circ

def comparison(circ,k,n,bit_size):

    for i in range(len(k_string)):
        circ.barrier()
        circ = single_qubit_comparison(circ,i,k_string[i])

    circ.barrier()
    circ.cx(ancillae[-1],output[0]) # copy onto output
    circ.barrier()
    circ.measure(output[0],0)
    return circ

def simulate(circ):
    job = execute(circ,backend=Aer.get_backend('aer_simulator'),shots=1,memory=True)
    return job.result().get_memory()

if __name__ == '__main__':

    bit_size = 3
    for k in range(2**bit_size):
        for n in range(2**bit_size):

            k_string, n_string = stringify(k,n,bit_size)

            inputs = QuantumRegister(bit_size,name='inputs')
            ancillae = QuantumRegister(bit_size,name='ancillae')
            output = QuantumRegister(1,name='output')

            circ = QuantumCircuit(inputs,ancillae,output,ClassicalRegister(1))

            # loading numbers
            for i in range(len(n_string)): # initialise the inputs to n_string
                if n_string[i]=='1':
                    circ.x(inputs[i])

            circ = comparison(circ,k,n,bit_size)

            ans = simulate(circ)
            if n>k != bool(int(ans[0])):
                print(f'Error: {n,k} returned {ans}.')
                print(circ)