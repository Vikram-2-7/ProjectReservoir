import pandas as pd

# Dummy function for fetching dam data based on name (replace with actual logic)
def fetch_dam_data(dam_name):
    # Sample data
    df_main = pd.DataFrame({
        'Date': ['2024-09-01', '2024-09-02', '2024-09-03', '2024-09-04', '2024-09-05'],
        'Inflow (cubic feet/sec)': [100, 200, 50, 300, 150],
        'Outflow (cubic feet/sec)': [80, 50, 100, 75, 150],
        'Water Flow (cubic feet/sec)': [20, 150, -50, 225, 0],
        'Current Water Level (mcft)': [600, 650, 600, 700, 700],
        'Latitude': [12.34, 12.34, 12.34, 12.34, 12.34],  # Example coordinates
        'Longitude': [77.56, 77.56, 77.56, 77.56, 77.56]
    })
    
    df_rainfall = pd.DataFrame({
        'Date': ['2024-09-01', '2024-09-02', '2024-09-03', '2024-09-04', '2024-09-05'],
        'Rainfall Amount (mm)': [25.0, 30.0, 0.0, 15.0, 20.0],
        'Rainy Season Indicator': [1, 1, 1, 1, 1]
    })
    
    # Assuming you fetch data based on dam_name (can be used for filtering)
    return df_main, df_rainfall
