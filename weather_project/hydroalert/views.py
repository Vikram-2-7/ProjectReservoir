from django.shortcuts import render
from .forms import HydroAlertForm
from .utils import fetch_dam_data
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import plotly.graph_objs as go
import plotly.io as pio

def hydroalert(request):
    result = None
    graph_div = None
    map_div = None
    graph_data = None  # Initialize graph_data for rendering the graph

    if request.method == 'POST':
        form = HydroAlertForm(request.POST)
        if form.is_valid():
            dam_name = form.cleaned_data['dam_name']

            try:
                # Fetch dam data from utility function
                df_main, df_rainfall = fetch_dam_data(dam_name)

                # Merge main and rainfall datasets
                df = pd.merge(df_main, df_rainfall, on='Date')

                # Success criteria
                df['Success'] = df['Current Water Level (mcft)'].diff().fillna(0) > 0
                df['Success'] = df['Success'].astype(int)

                # Calculate features for model input
                df['Total Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).sum().fillna(0)
                df['Average Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).mean().fillna(0)

                # Features and labels
                features = ['Rainy Season Indicator', 'Inflow (cubic feet/sec)', 'Outflow (cubic feet/sec)',
                            'Water Flow (cubic feet/sec)', 'Total Rainfall Last 3 Days', 'Average Rainfall Last 3 Days']
                X = df[features]
                y = df['Success']

                # Train-test split
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

                # Model training
                model = RandomForestClassifier(n_estimators=200, max_depth=5, min_samples_split=5, random_state=42)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                # Model accuracy
                accuracy = accuracy_score(y_test, y_pred)
                print(f"Accuracy: {accuracy:.2f}")

                # Check for critical situations
                df['Alert'] = df.apply(check_critical_situation, axis=1)

                # Separate alerts
                df_alerts_high = df[df['Alert'] == "ALERT: High water level detected!"]
                df_alerts_low = df[df['Alert'] == "ALERT: Low water level detected!"]

                # Prepare graph data
                graph_data = {
                    'date': df['Date'].tolist(),
                    'water_level': df['Current Water Level (mcft)'].tolist(),
                    'high_alert_dates': df_alerts_high['Date'].tolist(),
                    'low_alert_dates': df_alerts_low['Date'].tolist(),
                    'high_alert_levels': df_alerts_high['Current Water Level (mcft)'].tolist(),
                    'low_alert_levels': df_alerts_low['Current Water Level (mcft)'].tolist(),
                }

                # Prepare Plotly graph
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=graph_data['date'], y=graph_data['water_level'], mode='lines+markers', name='Water Level'))
                fig.add_trace(go.Scatter(x=graph_data['high_alert_dates'], y=graph_data['high_alert_levels'], mode='markers', name='High Alert', marker=dict(color='red')))
                fig.add_trace(go.Scatter(x=graph_data['low_alert_dates'], y=graph_data['low_alert_levels'], mode='markers', name='Low Alert', marker=dict(color='blue')))
                graph_div = pio.to_html(fig, full_html=False)

                # Render map (assumes latitude and longitude are available in the dataset)
                latitude = df_main['Latitude'].iloc[0]
                longitude = df_main['Longitude'].iloc[0]
                map_div = f'''
                <div id="map" style="height: 400px;" data-latitude="{latitude}" data-longitude="{longitude}"></div>
                <script>
                    var map = L.map('map').setView([{latitude}, {longitude}], 13);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {{
                        maxZoom: 19,
                    }}).addTo(map);
                    L.marker([{latitude}, {longitude}]).addTo(map)
                        .bindPopup('Location: {dam_name}')
                        .openPopup();
                </script>
                '''

                result = f"Data for {dam_name} has been retrieved successfully."
            except Exception as e:
                result = f"Error fetching data for {dam_name}: {str(e)}"
    else:
        form = HydroAlertForm()

    return render(request, 'hydroalert/hydroalert.html', {
        'form': form,
        'result': result,
        'graph_div': graph_div,  # Pass graph data to template
        'map_div': map_div,      # Pass map div to template
    })

def check_critical_situation(row):
    # High water level alert criteria
    if row['Total Rainfall Last 3 Days'] > 50 or row['Inflow (cubic feet/sec)'] > 200:
        return "ALERT: High water level detected!"
    # Low water level alert criteria
    elif row['Current Water Level (mcft)'] < 600 or row['Inflow (cubic feet/sec)'] < 50:
        return "ALERT: Low water level detected!"
    return "Normal"

def fetch_critical_data(request):
    result = None

    if request.method == 'POST':
        form = HydroAlertForm(request.POST)
        if form.is_valid():
            dam_name = form.cleaned_data['dam_name']
            try:
                df_main, df_rainfall = fetch_dam_data(dam_name)
                result = f"Data for {dam_name} has been retrieved."
            except Exception as e:
                result = f"Error: {str(e)}"
    else:
        form = HydroAlertForm()

    return render(request, 'hydroalert/fetch_critical_data.html', {
        'form': form,
        'result': result
    })

def fetch_dam_location(request):
    result = None
    map_div = None

    if request.method == 'POST':
        form = HydroAlertForm(request.POST)
        if form.is_valid():
            dam_name = form.cleaned_data['dam_name']
            try:
                # Assuming `fetch_dam_data` returns the location data for the dam
                df_main, df_rainfall = fetch_dam_data(dam_name)
                
                # Prepare the map_div for the location
                map_div = f'<div id="map" data-latitude="{df_main["Latitude"][0]}" data-longitude="{df_main["Longitude"][0]}"></div>'
                
                result = f"Location data for {dam_name} has been retrieved."
            except Exception as e:
                result = f"Error: {str(e)}"
    else:
        form = HydroAlertForm()

    return render(request, 'hydroalert/fetch_dam_location.html', {
        'form': form,
        'result': result,
        'map_div': map_div,
    })