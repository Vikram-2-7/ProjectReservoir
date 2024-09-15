from django.shortcuts import render
from .forms import DamDataForm
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import requests
from datetime import datetime, timedelta
import json

def fetch_weather_data(api_key, city, start_date, end_date):
    weather_data = []
    current_date = start_date

    while current_date <= end_date:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract required weather parameters
        temperature = data['main'].get('temp', 0)
        humidity = data['main'].get('humidity', 0)
        wind_speed = data['wind'].get('speed', 0)
        rainfall_amount = data.get('rain', {}).get('1h', 0)  # Rainfall for the last hour if available

        daily_data = {
            'Date': current_date,
            'Temperature (C)': temperature,
            'Humidity (%)': humidity,
            'Wind Speed (m/s)': wind_speed,
            'Rainfall Amount (mm)': rainfall_amount,
            'Rainy Season Indicator': 1 if rainfall_amount > 0 else 0,
            'Inflow (cubic feet/sec)': None,  # Placeholder
            'Outflow (cubic feet/sec)': None,  # Placeholder
            'Water Flow (cubic feet/sec)': None,  # Placeholder
            'Current Water Level (mcft)': None  # Placeholder
        }

        weather_data.append(daily_data)
        current_date += timedelta(days=1)

    return pd.DataFrame(weather_data)

def dam_control(request):
    result = None
    prediction_counts = None
    feature_importances = None
    prediction_data = {}
    feature_data = {}

    if request.method == 'POST':
        form = DamDataForm(request.POST)
        if form.is_valid():
            inflow = form.cleaned_data['inflow']
            outflow = form.cleaned_data['outflow']
            water_flow = form.cleaned_data['water_flow']
            city = form.cleaned_data['city']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Configuration
            api_key = "fcf0d663119bd00da60961cedcfe6ff4"  # Replace with your actual API key

            # Fetch real-time weather data
            df_weather = fetch_weather_data(api_key, city, start_date, end_date)

            # Ensure 'Date' column is in datetime format
            df_weather['Date'] = pd.to_datetime(df_weather['Date'])

            # Fill None values and convert columns to numeric
            df_weather = df_weather.fillna(0)
            df_weather = df_weather.apply(pd.to_numeric, errors='ignore')

            # Define 'success' as an increase in water level from the previous day
            df_weather['Success'] = df_weather['Current Water Level (mcft)'].diff().fillna(0) > 0
            df_weather['Success'] = df_weather['Success'].astype(int)

            # Feature Engineering
            df_weather['Total Rainfall Last 3 Days'] = df_weather['Rainfall Amount (mm)'].rolling(window=3).sum().fillna(0)
            df_weather['Average Rainfall Last 3 Days'] = df_weather['Rainfall Amount (mm)'].rolling(window=3).mean().fillna(0)

            # Prepare features and target
            features = ['Date', 'Temperature (C)', 'Humidity (%)', 'Wind Speed (m/s)', 'Rainfall Amount (mm)', 
                        'Rainy Season Indicator', 'Inflow (cubic feet/sec)', 'Outflow (cubic feet/sec)', 
                        'Water Flow (cubic feet/sec)', 'Current Water Level (mcft)', 
                        'Total Rainfall Last 3 Days', 'Average Rainfall Last 3 Days']
            X = df_weather[features]
            y = df_weather['Success']

            # Check if there is enough data to split
            if len(X) > 1:
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

                # Train model
                model = RandomForestClassifier(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)

                # Predict
                y_pred = model.predict(X_test)

                # Evaluate
                accuracy = accuracy_score(y_test, y_pred)
                result = f"Model Accuracy: {accuracy:.2f}"

                # Get prediction counts
                prediction_counts = pd.Series(y_pred).value_counts()
                prediction_data = {
                    'Success': int(prediction_counts.get(1, 0)),
                    'Failure': int(prediction_counts.get(0, 0))
                }

                # Get feature importances
                importances = model.feature_importances_
                feature_importances = [(features[i], float(importances[i])) for i in range(len(features))]
                feature_importances.sort(key=lambda x: x[1], reverse=True)

                # Prepare data for feature importance chart
                feature_data = {feature: float(importance) for feature, importance in feature_importances}

            else:
                result = "Not enough data to train the model."

    else:
        form = DamDataForm()

    return render(request, 'dam/dam_control.html', {
        'form': form, 
        'result': result, 
        'prediction_data': json.dumps(prediction_data), 
        'feature_data': json.dumps(feature_data)
    })