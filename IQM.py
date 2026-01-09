from iqm.qiskit_iqm import IQMProvider
RESONANCE_API_TOKEN="bnjru9YD0h359Dua8qQ4QIByn6uUYJA7Nih1xVTDAj0Bm5VP88J9ELmI5Be5Xz8F"

provider = IQMProvider("https://resonance.meetiqm.com/", quantum_computer="garnet",
            token=RESONANCE_API_TOKEN)
backend = provider.get_backend(use_metrics = True)

target = backend.get_real_target()

# To collect 
for i in range(backend.num_qubits):
    props = target.qubit_properties[i]
    print(f"Qubit {i}:")
    print(f"Properties qubit {i}: {props}")

print(target.operation_names)