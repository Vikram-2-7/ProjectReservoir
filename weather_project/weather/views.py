# weather/views.py
from django.shortcuts import render
import pandas as pd
import requests
from django.http import JsonResponse
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Sample datasets
df_main = pd.DataFrame({
    'Date': ['2024-09-01', '2024-09-02', '2024-09-03', '2024-09-04', '2024-09-05',
             '2024-09-06', '2024-09-07', '2024-09-08', '2024-09-09', '2024-09-10'],
    'Inflow (cubic feet/sec)': [100, 200, 50, 300, 150, 20, 250, 100, 180, 70],
    'Outflow (cubic feet/sec)': [80, 50, 100, 75, 150, 120, 80, 90, 40, 110],
    'Water Flow (cubic feet/sec)': [20, 150, -50, 225, 0, -100, 170, 10, 140, -40],
    'Current Water Level (mcft)': [600, 650, 600, 700, 700, 600, 650, 660, 700, 660]
})

df_rainfall = pd.DataFrame({
    'Date': ['2024-09-01', '2024-09-02', '2024-09-03', '2024-09-04', '2024-09-05',
             '2024-09-06', '2024-09-07', '2024-09-08', '2024-09-09', '2024-09-10'],
    'Rainfall Amount (mm)': [25.0, 30.0, 0.0, 15.0, 20.0, 5.0, 10.0, 0.0, 5.0, 0.0],
    'Rainy Season Indicator': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
})

df_main['Date'] = pd.to_datetime(df_main['Date'])
df_rainfall['Date'] = pd.to_datetime(df_rainfall['Date'])
df = pd.merge(df_main, df_rainfall, on='Date')
df['Success'] = df['Current Water Level (mcft)'].diff().fillna(0) > 0
df['Success'] = df['Success'].astype(int)
df['Total Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).sum().fillna(0)
df['Average Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).mean().fillna(0)

# Define features and target for model
features = ['Rainy Season Indicator', 'Inflow (cubic feet/sec)', 'Outflow (cubic feet/sec)',
            'Water Flow (cubic feet/sec)', 'Total Rainfall Last 3 Days', 'Average Rainfall Last 3 Days']
X = df[features]
y = df['Success']

# Train test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train RandomForestClassifier model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

 # Render the home page

def get_weather(request):
    city = request.GET.get('city', 'Chennai')  # Default to Chennai
    api_key = "fcf0d663119bd00da60961cedcfe6ff4"  # Replace with your actual OpenWeather API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if 'main' in data and 'wind' in data:
            # Collect weather data
            weather_data = {
                'City': city,
                'Temperature': data['main']['temp'],
                'Description': data['weather'][0]['description'],
                'Humidity': data['main']['humidity'],
                'Wind_Speed': data['wind']['speed'],
                'Latitude': data['coord']['lat'],  # Get latitude
                'Longitude': data['coord']['lon']   # Get longitude
            }

            # Prepare data for the chart
            chart_data = {
                'labels': ['Temperature', 'Wind Speed', 'Humidity'],
                'datasets': [{
                    'label': f'Weather Data for {city}',
                    'data': [weather_data['Temperature'], weather_data['Wind_Speed'], weather_data['Humidity']],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                }]
            }

            # Pass weather and chart data to the template
            context = {
                'weather_data': weather_data,
                'chart_data': chart_data
            }

            return render(request, 'weather/weather_info.html', context)

        else:
            return render(request, 'weather/weather_info.html', {'error': 'Place not found or invalid response from weather API.'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def home(request):
    return render(request, 'weather/home.html')  # Render the home page
def weather_info(request):
    # This view can be used to display detailed weather information
    return render(request, 'weather/weather_info.html')  # Ensure this returns an HttpResponse

def dam_control(request):
    # Render a simple template for the dam control center
    return render(request, 'weather/dam_control.html')  # Ensure this template exists

def hydro_alert(request):
    # Render a simple template for hydro alerts
    return render(request, 'weather/hydro_alert.html')  # Ensure this template exists
