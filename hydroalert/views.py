from django.shortcuts import render
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import plotly.graph_objs as go
import plotly.io as pio


def hydroalert(request):
    result = None
    graph_div = None
    alerts = []

    dam_name = "Hubei/Chongqing,China"
    high_rainfall_threshold = 50
    high_inflow_threshold = 200
    low_water_level_threshold = 600
    low_inflow_threshold = 50

    try:
        df = pd.read_csv(r"C:\Users\VIKRAM\OneDrive\Desktop\DESKTOPP (1)\SIH\weather_app\myproject\weather_project\dam\\threegorges-water-storage.csv")

        # Check required columns
        if 'measurement_date' not in df.columns or 'upstream_water_level' not in df.columns:
            raise ValueError("Dataset must contain 'measurement_date' and 'upstream_water_level' columns.")

        # Rename columns
        df.rename(columns={
            'measurement_date': 'Date',
            'upstream_water_level': 'Current Water Level (mcft)',
        }, inplace=True)

        # Add placeholder rainfall data if none exists
        if 'Rainfall Amount (mm)' not in df.columns:
            df['Rainfall Amount (mm)'] = 0

        # Define success column
        df['Success'] = df['Current Water Level (mcft)'].diff().fillna(0) > 0
        df['Success'] = df['Success'].astype(int)

        # Rolling rainfall features
        df['Total Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).sum().fillna(0)
        df['Average Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).mean().fillna(0)

        # Define required features, add missing columns as zero-filled
        required_features = [
            'Rainy Season Indicator', 'Inflow (cubic feet/sec)', 'Outflow (cubic feet/sec)',
            'Water Flow (cubic feet/sec)', 'Total Rainfall Last 3 Days', 'Average Rainfall Last 3 Days'
        ]
        for feature in required_features:
            if feature not in df.columns:
                df[feature] = 0

        X = df[required_features]
        y = df['Success']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = RandomForestClassifier(n_estimators=200, max_depth=5, min_samples_split=5, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy:.2f}")  # Log to console

        # Alert detection using helper
        df['Alert'] = df.apply(lambda row: check_critical_situation(
            row,
            high_rainfall_threshold,
            high_inflow_threshold,
            low_water_level_threshold,
            low_inflow_threshold,
        ), axis=1)
        alerts = df['Alert'].unique().tolist()

        # Prepare Plotly graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Current Water Level (mcft)'], mode='lines+markers', name='Water Level'
        ))
        # High alerts marked red
        fig.add_trace(go.Scatter(
            x=df[df['Alert'] == "ALERT: High water level detected!"]['Date'],
            y=df[df['Alert'] == "ALERT: High water level detected!"]['Current Water Level (mcft)'],
            mode='markers', name='High Alert', marker=dict(color='red')
        ))
        # Low alerts marked blue
        fig.add_trace(go.Scatter(
            x=df[df['Alert'] == "ALERT: Low water level detected!"]['Date'],
            y=df[df['Alert'] == "ALERT: Low water level detected!"]['Current Water Level (mcft)'],
            mode='markers', name='Low Alert', marker=dict(color='blue')
        ))
        graph_div = pio.to_html(fig, full_html=False)

        result = f"Data for {dam_name} has been retrieved successfully."
    except Exception as e:
        result = f"Error fetching data for {dam_name}: {str(e)}"

    return render(request, 'hydroalert/hydroalert.html', {
        'result': result,
        'graph_div': graph_div,
        'alerts': alerts,
    })


def check_critical_situation(row, high_rainfall_threshold, high_inflow_threshold, low_water_level_threshold, low_inflow_threshold):
    if row['Total Rainfall Last 3 Days'] > high_rainfall_threshold or row['Inflow (cubic feet/sec)'] > high_inflow_threshold:
        return "ALERT: High water level detected!"
    elif row['Current Water Level (mcft)'] < low_water_level_threshold or row['Inflow (cubic feet/sec)'] < low_inflow_threshold:
        return "ALERT: Low water level detected!"
    return "Normal"
