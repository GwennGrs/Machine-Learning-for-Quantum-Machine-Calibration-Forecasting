from iqm.qiskit_iqm import IQMProvider
RESONANCE_API_TOKEN="8Gh0R5Ce4bsagrjhXGrK8ZSz6UamMz2dnfZWsPFzJJ8BmpzbZY94U6VZzKA3EMYH"

provider = IQMProvider("https://cocos.resonance.meetiqm.com/garnet",
            token= RESONANCE_API_TOKEN)
backend = provider.get_backend()

props = backend.properties()

for qubit, qubit_props in enumerate(props.qubits):
    print(f"Qubit {qubit}")
    for item in qubit_props:
        print(f"  {item.name}: {item.value} {item.unit}")
