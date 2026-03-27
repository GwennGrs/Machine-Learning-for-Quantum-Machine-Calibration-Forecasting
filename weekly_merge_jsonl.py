import pandas as pd
import json
import os
import re
from pathlib import Path

def get_date_range(input_folder, insert):
    ''' 
    Gather the dates from the filenames and return the minimum and maximum date for the given insert.
    Input:
        - input_folder: the folder where the jsonl files are located
        - insert: the type of data to look for (e.g., "qubits", "complete", "gates")
    Output:
        - date_min: the minimum date found in the filenames
        - date_max: the maximum date found in the filenames 
    '''
    dates = []
    pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    for filename in os.listdir(input_folder):
        if f"{insert}_" in filename and filename.endswith(".jsonl"):
            matches = pattern.findall(filename)
            dates.extend(matches)
    if not dates:
        return None, None
    return min(dates), max(dates)

def concatenation_jsonl(input_folder, output_folder, insert, concat_dataset=False, dataset_folder=None):
    ''' 
    Concatenate all jsonl files for a given insert type and date range.
    (Optionnaly : concatenate the weekly generated dataset with the total dataset)
    Input:
        - input_folder: the folder where the jsonl files are located
        - output_folder: the folder where the merged file will be saved
        - insert: the type of data to look for (e.g., "qubits", "complete", "gates")
        - concat_dataset: if True, will concatenate the weekly generated dataset with the total dataset (default: False)
    '''
    
    date_min, date_max = get_date_range(input_folder, insert)
    if date_min is None:
        print(f"No files found for insert '{insert}'")
        return

    output_filename = f"{date_min}_to_{date_max}_{insert}_data.jsonl"
    output_path = output_folder / output_filename

    all_data = []
    for filename in os.listdir(input_folder):
        if f"{insert}_" in filename and filename.endswith(".jsonl"):
            with open(os.path.join(input_folder, filename), 'r') as f:
                for line in f:
                    all_data.append(json.loads(line))

    with open(output_path, 'w') as f:
        for data in all_data:
            f.write(json.dumps(data) + "\n")
        print(f"Files build : {output_path}")

    ## Merge with dataset part 
    if concat_dataset and dataset_folder is not None:
        dataset_folder.mkdir(parents=True, exist_ok=True)

        dataset_files = None
        pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
        for filename in os.listdir(dataset_folder):
            if f"{insert}_" in filename and filename.endswith(".jsonl"):
                dataset_files = dataset_folder / filename
                exist_date = pattern.findall(filename)
        
        existing_data = []
        if dataset_files is not None:
            with open(dataset_files, 'r') as f:
                for line in f:
                    existing_data.append(json.loads(line))
        
        merged_data = existing_data + all_data
        merged_output_filename = f"{min(exist_date)}_to_{date_max}_{insert}_data.jsonl"
        output_dataset_path = dataset_folder / merged_output_filename
        
        if dataset_files is not None and dataset_files != output_dataset_path:
                dataset_files.unlink()
                print(f"Deleted old dataset file : {dataset_files.name}")

        with open(output_dataset_path, 'w') as f:
            for data in merged_data:
                f.write(json.dumps(data) + "\n")
        print(f"Dataset updated : {output_dataset_path}")



if __name__ == "__main__":
    ''' 
    Main function to execute the concatenation of jsonl files for qubits, complete, and gates data.
    Made to be run every 1/2 weeks.
    '''
    input_folder = Path("extract") ## Name of the repository where the extracted calibration are (default extract)
    print(f"Input folder: {input_folder}")
    output_folder = Path("dataset/weekly_merge") ## Name of the repository where we want to upload our weekly merged calibration (default dataset/weekly_merge)
    print(f"Output folder: {output_folder}")
    dataset_folder = Path("dataset") ## Name of the repository the main dataset is located in (default dataset)
    output_folder.mkdir(parents=True, exist_ok=True)

    concatenation_jsonl(input_folder, output_folder, "qubits", concat_dataset=True, dataset_folder=dataset_folder)
    concatenation_jsonl(input_folder, output_folder, "complete", concat_dataset=True, dataset_folder=dataset_folder)
    concatenation_jsonl(input_folder, output_folder, "gates", concat_dataset=True, dataset_folder=dataset_folder)

    print("Work fine !!")