import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_dummy_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'dam', 'data', 'dams')
    os.makedirs(data_dir, exist_ok=True)

    dams = {
        'poondi':         {'capacity': 3.231,  'max_level': 140},
        'red_hills':      {'capacity': 3.300,  'max_level': 50},
        'chembarambakkam':{'capacity': 3.645,  'max_level': 85},
        'krishnagiri':    {'capacity': 1.666,  'max_level': 52},
        'mettur':         {'capacity': 93.470, 'max_level': 120},
        'amaravathi':     {'capacity': 4.047,  'max_level': 90},
        'bhavanisagar':   {'capacity': 32.800, 'max_level': 105},
        'pilloor':        {'capacity': 1.560,  'max_level': 100},
        'parambikulam':   {'capacity': 13.430, 'max_level': 72},
        'aliyar':         {'capacity': 3.864,  'max_level': 120},
        'vaigai':         {'capacity': 6.140,  'max_level': 71},
        'sathanur':       {'capacity': 7.321,  'max_level': 119},
        'papanasam':      {'capacity': 5.500,  'max_level': 143},
        'manimuthar':     {'capacity': 5.511,  'max_level': 118},
        'pechiparai':     {'capacity': 4.300,  'max_level': 48},
        'kodaikanal':     {'capacity': 0.500,  'max_level': 30},
        'krishnapuram':   {'capacity': 2.000,  'max_level': 60},
    }

    np.random.seed(42)
    start_date = datetime.now() - timedelta(days=365)

    for dam_name, params in dams.items():
        capacity   = params['capacity']
        max_level  = params['max_level']

        dates = [start_date + timedelta(days=i) for i in range(365)]

        # Simulate seasons: monsoon Jun–Nov has 3× higher rainfall
        monsoon_factor = np.array([3.0 if 6 <= dt.month <= 11 else 0.5 for dt in dates])

        rainfall = np.random.exponential(10, 365) * monsoon_factor
        inflow   = rainfall * np.random.uniform(80, 200, 365) + np.random.normal(400, 150, 365)
        inflow   = np.maximum(inflow, 0)

        # ── Storage simulation ────────────────────────────────────────────────
        # Start at 25% so early dry-season rows are clearly Low-risk
        storage  = np.zeros(365)
        outflow  = np.zeros(365)
        level    = np.zeros(365)

        current_storage = capacity * 0.25

        for i in range(365):
            inflow_tmc = inflow[i] * 0.0000864   # 1 cusec-day ≈ 8.64e-5 TMC

            pct = current_storage / capacity

            # Outflow rules — designed to oscillate through all three risk bands:
            #   > 80% → aggressive release (High zone)
            #   50–80% → moderate release (Medium zone)
            #   < 50% → minimal release (Low zone)
            if pct > 0.80:
                outflow_cusecs = inflow[i] * 2.0 + np.random.uniform(1500, 3000)
            elif pct > 0.50:
                outflow_cusecs = inflow[i] * 1.0 + np.random.uniform(200, 600)
            elif pct > 0.25:
                outflow_cusecs = inflow[i] * 0.5 + np.random.uniform(50, 150)
            else:
                outflow_cusecs = np.random.uniform(5, 30)

            outflow_cusecs = max(outflow_cusecs, 0)
            outflow[i]     = outflow_cusecs
            outflow_tmc    = outflow_cusecs * 0.0000864

            current_storage = current_storage + inflow_tmc - outflow_tmc
            current_storage = max(min(current_storage, capacity), 0)

            storage[i] = current_storage
            level[i]   = (current_storage / capacity) * max_level

        temp     = np.random.normal(30, 5, 365)
        humidity = np.random.uniform(40, 98, 365)

        # Spillway opens above 80% capacity
        spillway_open = ((storage / capacity) > 0.80).astype(int)

        # Risk labels — thresholds chosen to guarantee a mix across the year:
        #   Low    : < 50% full
        #   Medium : 50–80%
        #   High   : > 80%
        ratio      = storage / capacity
        risk_label = np.where(ratio < 0.50, 'Low',
                     np.where(ratio <= 0.80, 'Medium', 'High'))

        # Quick sanity print
        unique, counts = np.unique(risk_label, return_counts=True)
        print(f"{dam_name}: {dict(zip(unique, counts))}")

        df = pd.DataFrame({
            'date':             dates,
            'rainfall_mm':      np.round(rainfall, 2),
            'inflow_cusecs':    np.round(inflow,   2),
            'outflow_cusecs':   np.round(outflow,  2),
            'storage_tmcft':    np.round(storage,  3),
            'capacity_tmcft':   capacity,
            'water_level_ft':   np.round(level,    2),
            'max_water_level_ft': max_level,
            'temperature_c':    np.round(temp,     1),
            'humidity_percent': np.round(humidity, 1),
            'spillway_open':    spillway_open,
            'risk_label':       risk_label,
        })

        file_path = os.path.join(data_dir, f'{dam_name}.csv')
        df.to_csv(file_path, index=False)
        print(f"  → wrote {file_path}")


if __name__ == "__main__":
    create_dummy_data()
