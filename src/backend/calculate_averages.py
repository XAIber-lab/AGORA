import pandas as pd
import os
import asyncio


def calculate_averages():
    try:
        data_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))
        file_path = os.path.join(data_dir, 'IM_log.csv')

        df = pd.read_csv(file_path)

        if 'fitness' not in df.columns or 'costTotal' not in df.columns:
            raise ValueError("The CSV file must contain 'fitness' and 'costTotal' columns.")

        fitness_avg = df['fitness'].mean()
        cost_total_avg = df['costTotal'].mean()

        return fitness_avg, cost_total_avg

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None, None
    except ValueError as ve:
        print(ve)
        return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

