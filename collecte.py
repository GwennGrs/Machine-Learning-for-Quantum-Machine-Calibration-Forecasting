#!/usr/bin/env python3

# Can be used with Qiskit
from qiskit_ibm_runtime import QiskitRuntimeService
import datetime
import pandas as pd
import numpy as np
import json

import os 

def connect():
    QiskitRuntimeService.save_account(
    token="pvbodFRTX18hEPsOobvl0Ivkz8JTppcD97GrX4rHr98M",
    instance="open-instance",
    overwrite=True,
    set_as_default = True
    )
    service = QiskitRuntimeService()
    return service

def collect_data_qubit(qubit_props):
    t1 = qubit_props.get("T1", (None,))[0]
    t2 = qubit_props.get("T2", (None,))[0]
    frequency = qubit_props.get("frequency", (None,))[0]
    anharmonicity = qubit_props.get("anharmonicity", (None,))[0]
    readout_error = qubit_props.get("readout_error", (None,))[0]
    prob_meas0_prep1 = qubit_props.get("prob_meas0_prep1", (None,))[0]
    prob_meas1_prep0 = qubit_props.get("prob_meas1_prep0", (None,))[0]
    readout_length = qubit_props.get("readout_length", (None,))[0]
    return np.array([t1, t2, frequency, anharmonicity, readout_error, prob_meas0_prep1, prob_meas1_prep0, readout_length])
    
def collect_data_gates(properties, qub):
    id_props = properties.gate_property("id", qub)
    id_error = id_props.get('gate_error', (None,))[0]
    id_length = id_props.get('gate_length', (None,))[0]

    rz_props = properties.gate_property("rz", qub)
    rz_error = rz_props.get('gate_error', (None,))[0]
    rz_length = rz_props.get('gate_length', (None,))[0]

    sx_props = properties.gate_property("sx", qub)
    sx_error = sx_props.get('gate_error', (None,))[0]
    sx_length = sx_props.get('gate_length', (None,))[0]

    rx_props = properties.gate_property("rx", qub)
    rx_error = rx_props.get('gate_error', (None,))[0]
    rx_length = rx_props.get('gate_length', (None,))[0]

    measure_props = properties.gate_property("measure", qub)
    measure_error = measure_props.get('gate_error', (None,))[0]
    measure_length = measure_props.get('gate_length', (None,))[0]
    
    return np.array([
        id_error, id_length,
        rz_error, rz_length,
        sx_error, sx_length,
        rx_error, rx_length,
        measure_error, measure_length
    ])

def collect_data_backend(backend):
    data_qub = []
    data_gates = []
    name = backend.name
    nb_qubits =  backend.num_qubits
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    col_nom = np.full((nb_qubits, 2), [name, date])

    for index in range(nb_qubits):
        data_qub.append(
            collect_data_qubit(
                backend.properties().qubit_property(index)
                ))
        data_gates.append(
            collect_data_gates(
                backend.properties(), index
            )
        )

    # Merging the properties of gates and qubits to create a df
    times_qub_data = np.c_[col_nom, data_qub]
    data_add_gates = np.c_[times_qub_data, data_gates]
    df_tot = pd.DataFrame(
        data=data_add_gates, 
        columns = ["nom","time",
               "T1", "T2", "frequency", "anharmonicity","readout_error","prob_meas0_prep1", "prob_meas1_prep0", "readout_length", 
                "id_error", "id_length", "rz_error", "rz_length", "sx_error", "sx_length", "rx_error", "rx_length", "measure_error", "measure_length"]
                )
    
    # Only qubits data
    df_qub = pd.DataFrame(
        data=times_qub_data, 
        columns = ["nom","time",
               "T1", "T2", "frequency", "anharmonicity","readout_error","prob_meas0_prep1", "prob_meas1_prep0", "readout_length"
                ]
                )
    
    # Only gates data
    times_gates_data = np.c_[col_nom, data_gates]
    df_gates = pd.DataFrame(
        data=times_gates_data, 
        columns = ["nom","time",
               "id_error", "id_length", "rz_error", "rz_length", "sx_error", "sx_length", "rx_error", "rx_length", "measure_error", "measure_length"]
                )

    return df_tot, df_qub, df_gates

def full_collect(service):
    backends = service.backends(simulator=False, operational=True)
    
    datas_tot = []
    datas_qub = []
    datas_gates = []
    for back in backends:
        df_tot, df_qub, df_gates = collect_data_backend(back)
        datas_tot.append(df_tot)
        datas_qub.append(df_qub)
        datas_gates.append(df_gates)
    complet_set = pd.concat(datas_tot, ignore_index=True)
    qubit_set = pd.concat(datas_qub, ignore_index=True)
    gates_set = pd.concat(datas_gates, ignore_index=True)
    return complet_set, qubit_set, gates_set

# 3 fonctions de créations de csv
def create_csv_complet(data, folder):
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    name_file = os.path.join(folder, "ibm_backends_complet_" + date + ".json")
    return data.to_json(name_file, index=False)

def create_csv_qubit(data, folder):
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    name_file = os.path.join(folder, "ibm_backends_qubit_" + date + ".json")
    return data.to_json(name_file, index=False)

def create_csv_gates(data, folder):
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    name_file = os.path.join(folder, "ibm_backends_gates_" + date + ".json")
    return data.to_json(name_file, index=False)

if __name__=="__main__":
    target_folder = "/home/gwenn/Desktop/Projet"
    service = connect()
    complete_data, qubit_data, gates_data = full_collect(service)
    create_csv_complet(complete_data, target_folder)
    create_csv_qubit(qubit_data, target_folder)
    create_csv_gates(gates_data, target_folder)