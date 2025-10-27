from django.shortcuts import render, redirect
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, r2_score, mean_absolute_error, mean_squared_error
import plotly.graph_objs as go
import plotly.io as pio
import time
import requests
import os
import json


def home(request):
    return render(request, 'weather/home.html')


def weather_info(request):
    return render(request, 'weather/weather_info.html')


def get_weather(request):
    """
    Fetches weather data, stores in session, redirects to dam_control.
    """
    weather_data = None
    error_message = None

    if request.method == "POST":
        city = request.POST.get("city")
        api_key_path = r"C:\Users\VIKRAM\OneDrive\Desktop\DESKTOPP (1)\SIH\weather_app\myproject\weather_factorAPI_KEY.txt"
        if not os.path.exists(api_key_path):
            error_message = "❌ API key file not found."
        else:
            API_KEY = open(api_key_path).read().strip()
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            try:
                response = requests.get(url, timeout=5)
                data = response.json()
                if response.status_code == 200 and data.get("cod") == 200:
                    weather_data = {
                        "city": data["name"],
                        "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "wind_speed": data["wind"]["speed"],
                        "description": data["weather"][0]["description"].title(),
                        "latitude": data["coord"]["lat"],
                        "longitude": data["coord"]["lon"],
                    }
                    request.session["weather_data"] = weather_data
                    return redirect("dam_control")
                else:
                    error_message = "⚠️ Invalid city name."
            except Exception as e:
                error_message = f"Error fetching weather: {e}"

    return render(request, "weather/get_weather.html", {
        "weather": weather_data,
        "error": error_message,
    })


def dam_control(request):
    """
    Runs ML model on dam & weather data, computes metrics, feature importance,
    renders results including dynamic charts.
    """

    # Reset functionality: if "reset" button pressed clear session and reset context
    if request.method == "POST" and "reset" in request.POST:
        request.session.pop("weather_data", None)
        return render(request, "dam/dam_control.html", {
            "weather_data": None,
            "result": None,
            "confusion_data": None,
            "regression_metrics": None,
            "alert_status": "NORMAL",
            "inflow_capacity": 0,
            "recommended_release": 0,
            "prediction_data": None,
            "feature_data": None,
        })

    start_time = time.time()
    weather_data = request.session.get("weather_data", None)

    result_text = None
    alert_status = "NORMAL"
    inflow_capacity = 0
    recommended_release = 0
    confusion_data = None
    regression_metrics = None
    prediction_data = None
    feature_data = None

    csv_file_path = r"C:\Users\VIKRAM\OneDrive\Desktop\DESKTOPP (1)\SIH\weather_app\myproject\weather_project\dam\threegorges-water-storage.csv"

    # Only run computation when form is submitted (POST request without reset)
    if request.method == "POST" and "reset" not in request.POST:
        try:
            df = pd.read_csv(csv_file_path).fillna(0)

            if weather_data:
                df["temperature"] = weather_data.get("temperature", 0)
                df["humidity"] = weather_data.get("humidity", 0)
                df["wind_speed"] = weather_data.get("wind_speed", 0)
            else:
                df["temperature"] = 0
                df["humidity"] = 0
                df["wind_speed"] = 0

            df["Success"] = df["upstream_water_level"].diff().fillna(0) > 0
            df["Success"] = df["Success"].astype(int)

            features = ["upstream_water_level", "downstream_water_level", "inflow_rate", "outflow_rate", "temperature", "humidity", "wind_speed"]
            X = df[features]
            y = df["Success"]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            cm = confusion_matrix(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = mean_squared_error(y_test, y_pred, squared=False)
            TP, FN, FP, TN = cm[1, 1], cm[1, 0], cm[0, 1], cm[0, 0]

            confusion_data = {
                "TP": int(TP), 
                "FN": int(FN), 
                "FP": int(FP), 
                "TN": int(TN), 
                "accuracy": round(accuracy, 2)
            }
            regression_metrics = {
                "r2": round(r2, 2), 
                "mae": round(mae, 2), 
                "rmse": round(rmse, 2)
            }

            
            pred_counts = pd.Series(y_pred).value_counts()
            prediction_dict = {
                "Success": int(pred_counts.get(1, 0)),
                "Failure": int(pred_counts.get(0, 0))
            }
            prediction_data = json.dumps(prediction_dict)  # Convert to JSON string

            # FIXED: Properly serialize feature importance as JSON string
            importances = model.feature_importances_
            feature_dict = {features[i]: round(float(importances[i]), 3) for i in range(len(features))}
            feature_dict = dict(sorted(feature_dict.items(), key=lambda x: x[1], reverse=True))
            feature_data = json.dumps(feature_dict)  # Convert to JSON string

            if (FP + FN) > 10 or accuracy < 0.8:
                alert_status = "HIGH ALERT"
                inflow_capacity = int(df["inflow_rate"].max())
                recommended_release = int(df["outflow_rate"].max() + 50)
            elif (FP + FN) > 5:
                alert_status = "LOW ALERT"
                inflow_capacity = int(df["inflow_rate"].max())
                recommended_release = int(df["outflow_rate"].max())
            else:
                alert_status = "NORMAL"

            elapsed_time = round(time.time() - start_time, 2)
            result_text = f"Model Accuracy: {accuracy:.2%}. Current Alert Status: {alert_status}. Computation completed in {elapsed_time} seconds."

        except Exception as ex:
            result_text = f"Error during computation: {ex}"
            # Log the full error for debugging
            import traceback
            print(f"Full error traceback: {traceback.format_exc()}")

    return render(request, "dam/dam_control.html", {
        "weather_data": weather_data,
        "result": result_text,
        "confusion_data": confusion_data,
        "regression_metrics": regression_metrics,
        "alert_status": alert_status,
        "inflow_capacity": inflow_capacity,
        "recommended_release": recommended_release,
        "prediction_data": prediction_data,  # Now properly serialized as JSON
        "feature_data": feature_data,  # Now properly serialized as JSON
    })


def hydroalert(request):
    result = None
    graph_div = None
    alerts = []
    csv_file_path = r"C:\Users\VIKRAM\OneDrive\Desktop\DESKTOPP (1)\SIH\weather_app\myproject\weather_project\dam\threegorges-water-storage.csv"

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
        df = pd.read_csv(csv_file_path)

        df.rename(columns={
            'measurement_date': 'Date',
            'upstream_water_level': 'Current Water Level (mcft)'
        }, inplace=True)

        if 'Rainfall Amount (mm)' not in df.columns:
            df['Rainfall Amount (mm)'] = 0

        df['Total Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).sum().fillna(0)
        df['Average Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).mean().fillna(0)

        required_features = ['Rainy Season Indicator', 'Inflow (cubic feet/sec)', 'Outflow (cubic feet/sec)',
                             'Water Flow (cubic feet/sec)', 'Total Rainfall Last 3 Days', 'Average Rainfall Last 3 Days']

        for f in required_features:
            if f not in df.columns:
                df[f] = 0

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
            row, high_rainfall_threshold, high_inflow_threshold, low_water_level_threshold, low_inflow_threshold), axis=1)
        alerts = df['Alert'].unique().tolist()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Current Water Level (mcft)'],
                                 mode='lines+markers', name='Water Level'))
        fig.add_trace(go.Scatter(x=df[df['Alert'] == "ALERT: High water level detected!"]['Date'],
                                 y=df[df['Alert'] == "ALERT: High water level detected!"]['Current Water Level (mcft)'],
                                 mode='markers', name='High Alert', marker=dict(color='red', size=10)))
        fig.add_trace(go.Scatter(x=df[df['Alert'] == "ALERT: Low water level detected!"]['Date'],
                                 y=df[df['Alert'] == "ALERT: Low water level detected!"]['Current Water Level (mcft)'],
                                 mode='markers', name='Low Alert', marker=dict(color='blue', size=10)))
        
        # Update layout for better visualization
        fig.update_layout(
            title="Water Level Monitoring with Alerts",
            xaxis_title="Date",
            yaxis_title="Water Level (mcft)",
            hovermode='x unified',
            template='plotly_white'
        )
        
        graph_div = pio.to_html(fig, full_html=False)
        result = f"Hydro Alert data processed successfully. Model Accuracy: {accuracy:.2%}"

    except Exception as e:
        result = f"Error processing hydro alert data: {str(e)}"
        # Log the full error for debugging
        import traceback
        print(f"Full error traceback: {traceback.format_exc()}")

    return render(request, 'dam/hydroalert.html', {
        'result': result,
        'graph_div': graph_div,
        'alerts': alerts,
    })
