from django.shortcuts import render, redirect
import requests, os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, r2_score, mean_absolute_error, mean_squared_error
import plotly.graph_objs as go
import plotly.io as pio
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
def home(request):
    return render(request, 'weather/home.html')
def weather_info(request):
    return render(request, 'weather/weather_info.html')
def get_weather(request):
    weather_data = None
    error_message = None
    forecast_data = None
    if request.method == "POST":
        city = request.POST.get("city")
        api_key_path = r"C:\Users\VIKRAM\OneDrive\Desktop\DESKTOPP (1)\SIH\weather_app\myproject\weather_factorAPI_KEY.txt"
        if not os.path.exists(api_key_path):
            error_message = "❌ API key file not found."
        else:
            API_KEY = open(api_key_path).read().strip()
            url_weather = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            url_forecast = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

            try:
                response_weather = requests.get(url_weather, timeout=5)
                weather = response_weather.json()
                response_forecast = requests.get(url_forecast, timeout=5)
                forecast = response_forecast.json()

                if response_weather.status_code == 200 and weather.get("cod") == 200:
                    weather_data = {
                        "city": weather["name"],
                        "country": weather.get("sys", {}).get("country", ""),
                        "temperature": weather["main"]["temp"],
                        "feels_like": weather["main"]["feels_like"],
                        "humidity": weather["main"]["humidity"],
                        "pressure": weather["main"]["pressure"],
                        "wind_speed": weather["wind"].get("speed", "N/A"),
                        "wind_deg": weather["wind"].get("deg", "N/A"),
                        "description": weather["weather"][0]["description"].title(),
                        "icon": weather["weather"][0]["icon"],
                        "visibility": weather.get("visibility", "N/A"),
                        "uv_index": "N/A",  
                        "sunrise": weather.get("sys", {}).get("sunrise", "N/A"),
                        "sunset": weather.get("sys", {}).get("sunset", "N/A"),
                    }
                   
                    forecast_data = []
                    if forecast.get("list", None):
                        used_dates = set()
                        for item in forecast["list"]:
                            dt_txt = item.get("dt_txt", "")
                            date_str = dt_txt.split(" ")[0]
                            if date_str not in used_dates:
                                used_dates.add(date_str)
                                forecast_data.append({
                                    "date": dt_txt,
                                    "description": item["weather"][0]["description"].title(),
                                    "icon": item["weather"][0]["icon"],
                                    "min_temp": item["main"]["temp_min"],
                                    "max_temp": item["main"]["temp_max"],
                                })
                                if len(forecast_data) >= 5: break

                    request.session["weather_data"] = weather_data
                else:
                    error_message = "⚠️ Invalid city name."
            except Exception as e:
                error_message = f"Error fetching weather: {e}"

    return render(request, "weather/get_weather.html", {
        "weather": weather_data,
        "forecast": forecast_data,
        "error": error_message,
    })
def dam_control(request):
    weather_data = request.session.get('weather_data', None)
    context = {'weather': weather_data}
#rest
    if request.method == "POST" and "reset" in request.POST:
        request.session.pop("weather_data", None)
        context = {
            "weather": None,
            "graph": None,
            "accuracy": None,
            "TP": None, "FN": None, "FP": None, "TN": None,
            "r2": None, "mae": None, "rmse": None,
            "model_status": None
        }
        return render(request, 'weather/dam_control.html', context)

    # Main computation
    if request.method == 'POST' and "reset" not in request.POST:
        from sklearn.datasets import load_iris  # Example only
        iris = load_iris()
        X_train, X_test, y_train, y_test = train_test_split(
            iris.data, iris.target, test_size=0.3, random_state=42
        )
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        TP, FN, FP, TN = cm[0, 0], cm[0, 1], cm[1, 0], cm[1, 1]

        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        plt.figure(figsize=(5, 3))
        plt.plot(y_test[:20], label='Actual', marker='o')
        plt.plot(y_pred[:20], label='Predicted', marker='x')
        plt.legend()
        plt.title("Model Predictions vs Actual")
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', transparent=True)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graph_base64 = base64.b64encode(image_png).decode('utf-8')

        context.update({
            'graph': graph_base64,
            'accuracy': round(acc, 2),
            'TP': TP, 'FN': FN, 'FP': FP, 'TN': TN,
            'r2': round(r2, 2),
            'mae': round(mae, 2),
            'rmse': round(rmse, 2),
            'model_status': "✅ Model trained successfully."
        })

    return render(request, 'weather/dam_control.html', context)

def hydroalert(request):
    result = None
    graph_div = None
    alerts = []
    dam_name = "Hubei/Chongqing,China"
    high_rainfall_threshold = 50
    high_inflow_threshold = 200
    low_water_level_threshold = 600
    low_inflow_threshold = 50

    def check_critical_situation(row, high_rainfall, high_inflow, low_water_level, low_inflow):
        if row['Total Rainfall Last 3 Days'] > high_rainfall or row['Inflow (cubic feet/sec)'] > high_inflow:
            return "ALERT: High water level detected!"
        elif row['Current Water Level (mcft)'] < low_water_level or row['Inflow (cubic feet/sec)'] < low_inflow:
            return "ALERT: Low water level detected!"
        return "Normal"

    try:
        df = pd.read_csv(r"C:\Users\VIKRAM\OneDrive\Desktop\DESKTOPP (1)\SIH\weather_app\myproject\weather_project\dam\\threegorges-water-storage.csv")

        if 'measurement_date' not in df.columns or 'upstream_water_level' not in df.columns:
            raise ValueError("Dataset must contain 'measurement_date' and 'upstream_water_level' columns.")

        df.rename(columns={
            'measurement_date': 'Date',
            'upstream_water_level': 'Current Water Level (mcft)'
        }, inplace=True)

        if 'Rainfall Amount (mm)' not in df.columns:
            df['Rainfall Amount (mm)'] = 0

        df['Total Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).sum().fillna(0)
        df['Average Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).mean().fillna(0)

        required_features = [
            'Rainy Season Indicator', 'Inflow (cubic feet/sec)', 'Outflow (cubic feet/sec)',
            'Water Flow (cubic feet/sec)', 'Total Rainfall Last 3 Days', 'Average Rainfall Last 3 Days',
        ]
        for feature in required_features:
            if feature not in df.columns:
                df[feature] = 0

        df['Success'] = df['Current Water Level (mcft)'].diff().fillna(0) > 0
        df['Success'] = df['Success'].astype(int)

        X = df[required_features]
        y = df['Success']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = RandomForestClassifier(n_estimators=200, max_depth=5, min_samples_split=5, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        df['Alert'] = df.apply(lambda row: check_critical_situation(
            row, high_rainfall_threshold, high_inflow_threshold, low_water_level_threshold, low_inflow_threshold
        ), axis=1)
        alerts = df['Alert'].unique().tolist()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Current Water Level (mcft)'],
            mode='lines+markers', name='Water Level'
        ))
        fig.add_trace(go.Scatter(
            x=df[df['Alert'] == "ALERT: High water level detected!"]['Date'],
            y=df[df['Alert'] == "ALERT: High water level detected!"]['Current Water Level (mcft)'],
            mode='markers', name='High Alert', marker=dict(color='red')
        ))
        fig.add_trace(go.Scatter(
            x=df[df['Alert'] == "ALERT: Low water level detected!"]['Date'],
            y=df[df['Alert'] == "ALERT: Low water level detected!"]['Current Water Level (mcft)'],
            mode='markers', name='Low Alert', marker=dict(color='blue')
        ))
        graph_div = pio.to_html(fig, full_html=False)
        result = f"Data for {dam_name} has been retrieved successfully."

    except Exception as e:
        result = f"Error fetching data for {dam_name}: {str(e)}"

    return render(request, 'dam/hydroalert.html', {
        'result': result,
        'graph_div': graph_div,
        'alerts': alerts,
    })
