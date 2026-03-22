from django.shortcuts import render, redirect
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, r2_score, mean_absolute_error, mean_squared_error, root_mean_squared_error
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
        API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
        if not API_KEY:
            error_message = "❌ OpenWeather API key not found in environment."
        else:
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
    feature_names_json = None
    feature_importances_json = None
    prediction_details = None

    dam_name = "mettur" # safe default
    if weather_data and "dam_id" in weather_data:
        dam_name = weather_data["dam_id"]
        
    from django.conf import settings
    base_dir = settings.BASE_DIR
    csv_file_path = os.path.join(base_dir, 'dam', 'data', 'dams', f"{dam_name}.csv")

    if request.method == "POST" and "reset" not in request.POST:
        try:
            from sklearn.ensemble import RandomForestRegressor
            df = pd.read_csv(csv_file_path).fillna(0)

            features = ["rainfall_mm", "inflow_cusecs", "outflow_cusecs", "storage_tmcft", "water_level_ft", "temperature_c", "humidity_percent", "spillway_open"]
            X = df[features]
            y_class = df["risk_label"]
            y_reg = df["storage_tmcft"].shift(-1).ffill()

            # Train/Test Split
            X_train, X_test, y_train_c, y_test_c = train_test_split(X, y_class, test_size=0.3, random_state=42)
            _, _, y_train_r, y_test_r = train_test_split(X, y_reg, test_size=0.3, random_state=42)

            # Train Models
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_train, y_train_c)
            
            reg = RandomForestRegressor(n_estimators=100, random_state=42)
            reg.fit(X_train, y_train_r)

            # Test metrics
            y_pred_c = clf.predict(X_test)
            accuracy = accuracy_score(y_test_c, y_pred_c)
            
            y_pred_r = reg.predict(X_test)
            r2 = r2_score(y_test_r, y_pred_r)
            mae = mean_absolute_error(y_test_r, y_pred_r)
            rmse = root_mean_squared_error(y_test_r, y_pred_r)
            
            # Confusion Matrix calculation. 
            # Because risks can be Low/Medium/High, cm is 3x3. We'll simplify TP/FP stats for the UI.
            labels = clf.classes_
            cm = confusion_matrix(y_test_c, y_pred_c, labels=labels)
            
            # For simplicity in UI, we just pass accuracy map since TP/FN meant for binary
            confusion_data = {
                "TP": "N/A", "FN": "N/A", "FP": "N/A", "TN": "N/A", 
                "accuracy": round(accuracy, 2)
            }
            regression_metrics = {
                "r2": round(r2, 3), 
                "mae": round(mae, 3), 
                "rmse": round(rmse, 3)
            }
            
            pred_counts = pd.Series(y_pred_c).value_counts()
            prediction_dict = {
                "Low": int(pred_counts.get("Low", 0)),
                "Medium": int(pred_counts.get("Medium", 0)),
                "High": int(pred_counts.get("High", 0))
            }
            prediction_data = json.dumps(prediction_dict)

            # Feature Importance — sorted descending
            raw_importances = clf.feature_importances_.tolist()
            paired = sorted(
                zip(features, raw_importances),
                key=lambda x: x[1],
                reverse=True
            )
            feature_names_sorted    = [str(p[0]) for p in paired]
            importances_sorted      = [round(float(p[1]), 4) for p in paired]

            # Kept for legacy compatibility
            feature_dict = dict(zip(feature_names_sorted, importances_sorted))
            feature_data = json.dumps(feature_dict)

            # New separate JSON arrays consumed by the overhauled JS chart
            feature_names_json      = json.dumps(feature_names_sorted)
            feature_importances_json = json.dumps(importances_sorted)

            # Debug — confirms values in Django terminal
            print("FEATURE NAMES:", feature_names_sorted)
            print("IMPORTANCES:  ", importances_sorted)

            # Create live testing vector from the last row + live weather
            latest_row = df.iloc[-1].copy()
            if weather_data:
                latest_row["temperature_c"] = weather_data.get("temperature", latest_row["temperature_c"])
                latest_row["humidity_percent"] = weather_data.get("humidity", latest_row["humidity_percent"])
                desc = weather_data.get("description", "").lower()
                if "rain" in desc:
                    latest_row["rainfall_mm"] += 20.0 # simulate rain impact
                    latest_row["inflow_cusecs"] += 500.0

            live_X = pd.DataFrame([latest_row[features].values], columns=features)
            
            live_risk = clf.predict(live_X)[0]
            live_next_storage = reg.predict(live_X)[0]
            
            capacity = df["capacity_tmcft"].iloc[0]
            current_storage = latest_row["storage_tmcft"]
            
            # alert logic
            if live_risk == "High":
                alert_status = "RELEASE"
            elif live_risk == "Medium":
                alert_status = "MONITOR"
            else:
                alert_status = "HOLD"

            # Generate 7-day projection timeline for charting
            avg_daily_change = df["storage_tmcft"].diff().dropna().tail(30).mean()
            timeline = [live_next_storage]
            for _ in range(6):
                timeline.append(timeline[-1] + avg_daily_change)
            timeline = [float(round(max(0, val), 2)) for val in timeline]

            prediction_details = {
                "live_risk": live_risk,
                "current_storage": float(round(current_storage, 2)),
                "next_storage": float(round(live_next_storage, 2)),
                "capacity": float(capacity),
                "storage_pct": round(min(100, (current_storage / capacity) * 100)) if capacity > 0 else 0,
                "rainfall_mm": float(round(latest_row["rainfall_mm"], 2)),
                "temperature_c": float(round(latest_row["temperature_c"], 1)),
                "humidity_percent": float(round(latest_row["humidity_percent"], 1)),
                "dam_id": dam_name,
                "timeline": timeline
            }

            elapsed_time = round(time.time() - start_time, 2)
            result_text = f"Trained on: {dam_name}.csv (simulated data). Computation completed in {elapsed_time}s."

        except Exception as ex:
            result_text = f"Error during computation: {ex}"
            import traceback
            print(f"Full error traceback: {traceback.format_exc()}")

    return render(request, "dam/dam_control.html", {
        "weather_data": weather_data,
        "result": result_text,
        "confusion_data": confusion_data,
        "regression_metrics": regression_metrics,
        "alert_status": alert_status,
        "prediction_details": prediction_details,
        "prediction_data": prediction_data,
        "feature_data": feature_data,
        "feature_names_json": feature_names_json if feature_names_json is not None else "[]",
        "feature_importances_json": feature_importances_json if feature_importances_json is not None else "[]",
        "dam_name_display": weather_data.get("dam_display", dam_name.capitalize()) if weather_data else "Unknown Dam"
    })


def hydroalert(request):
    import glob
    import datetime
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'dam', 'data', 'dams')
    
    dam_alerts = []
    
    try:
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        for file in csv_files:
            dam_filename = os.path.basename(file)
            dam_id = dam_filename.replace('.csv', '')
            dam_name_display = dam_id.replace('_', ' ').capitalize() + " Dam"
            
            df = pd.read_csv(file)
            if df.empty: continue
            
            last_row = df.iloc[-1]
            risk = last_row.get('risk_label', 'Low')
            storage = last_row.get('storage_tmcft', 0)
            capacity = last_row.get('capacity_tmcft', 1)
            storage_pct = round(min(100, (storage / capacity) * 100)) if capacity > 0 else 0
            
            timestamp = last_row.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
            
            if risk == "High":
                action = "RELEASE / Critical"
            elif risk == "Medium":
                action = "MONITOR / Proceed with caution"
            else:
                action = "HOLD / Safe"
                
            dam_alerts.append({
                "dam_id": dam_id,
                "dam_name": dam_name_display,
                "risk_label": risk,
                "storage_pct": storage_pct,
                "action": action,
                "timestamp": timestamp
            })
            
        # Sort by risk severity (High -> Medium -> Low)
        risk_order = {"High": 0, "Medium": 1, "Low": 2}
        dam_alerts.sort(key=lambda x: risk_order.get(x['risk_label'], 3))
        
    except Exception as e:
        print(f"Error in hydroalert loading: {e}")
        
    return render(request, 'dam/hydroalert.html', {
        'dam_alerts': dam_alerts
    })
