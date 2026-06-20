import os
from collections import defaultdict
import pandas as pd
import numpy as np

def get_csv_data(filters=None):
    try:
        data_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))
        file_path = os.path.join(data_dir, 'IM_log.csv')
        if not os.path.exists(file_path):
            return "File does not exist"

        columns_needed = ['incident_id', 'fitness', 'costTotal', 'severity']
        df = pd.read_csv(file_path, usecols=columns_needed)

        if filters:
            filter_groups = defaultdict(list)
            for metric, func in filters:
                filter_groups[metric].append(func)

            # Apply filters within each group using OR, then combine groups using AND
            combined_results = None
            for funcs in filter_groups.values():
                metric_results = np.array([False] * len(df))
                for func in funcs:
                    metric_results |= func(df)
                combined_results = metric_results if combined_results is None else combined_results & metric_results

            df = df[combined_results]

        return df.to_csv(index=False)
    except Exception as e:
        print("csv_reader.py")
        print(f"Error reading file: {e}")
        return "Error reading file"