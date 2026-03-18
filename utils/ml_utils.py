"""
Machine Learning utilities for BrookStream.Ai
Centralized ML operations to eliminate code duplication.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, confusion_matrix, r2_score, 
    mean_absolute_error, mean_squared_error
)
import plotly.graph_objs as go
import plotly.io as pio
import matplotlib.pyplot as plt
import io
import base64
import logging
from typing import Dict, List, Tuple, Any, Optional
from config import config

logger = logging.getLogger(__name__)


class MLPredictor:
    """Centralized ML predictor for water level and dam operations."""
    
    def __init__(self, random_state: int = config.DEFAULT_RANDOM_STATE):
        self.random_state = random_state
        self.model = None
        self.feature_names = []
        self.accuracy = 0.0
        self.metrics = {}
        
    def prepare_data(self, df: pd.DataFrame, target_column: str, 
                    feature_columns: List[str]) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for ML training."""
        try:
            # Ensure all required columns exist
            missing_cols = [col for col in feature_columns if col not in df.columns]
            if missing_cols:
                logger.warning(f"Missing columns: {missing_cols}. Adding with zeros.")
                for col in missing_cols:
                    df[col] = 0
            
            # Handle missing values
            df[feature_columns] = df[feature_columns].fillna(0)
            df[target_column] = df[target_column].fillna(0)
            
            X = df[feature_columns]
            y = df[target_column]
            
            self.feature_names = feature_columns
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            raise
    
    def train_model(self, X: pd.DataFrame, y: pd.Series, 
                   test_size: float = config.DEFAULT_TEST_SIZE,
                   n_estimators: int = 100, max_depth: int = 5) -> Dict[str, Any]:
        """Train Random Forest model and return metrics."""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=self.random_state
            )
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=5,
                random_state=self.random_state
            )
            self.model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = self.model.predict(X_test)
            
            # Calculate metrics
            self.accuracy = accuracy_score(y_test, y_pred)
            cm = confusion_matrix(y_test, y_pred)
            
            # Get confusion matrix values
            if cm.shape == (2, 2):
                TN, FP, FN, TP = cm.ravel()
            else:
                TP = FN = FP = TN = 0
            
            # Regression metrics
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            self.metrics = {
                'accuracy': round(self.accuracy, 4),
                'confusion_matrix': {
                    'TP': int(TP), 'TN': int(TN), 
                    'FP': int(FP), 'FN': int(FN)
                },
                'r2': round(r2, 4),
                'mae': round(mae, 4),
                'rmse': round(rmse, 4),
                'feature_importance': self.get_feature_importance()
            }
            
            logger.info(f"Model trained successfully. Accuracy: {self.accuracy:.4f}")
            return self.metrics
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model."""
        if not self.model or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importance_dict = {}
        for i, feature in enumerate(self.feature_names):
            importance_dict[feature] = round(float(self.model.feature_importances_[i]), 4)
        
        # Sort by importance
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions using trained model."""
        if not self.model:
            raise ValueError("Model not trained yet")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get prediction probabilities."""
        if not self.model:
            raise ValueError("Model not trained yet")
        
        return self.model.predict_proba(X)
    
    def create_prediction_chart(self, y_true: np.ndarray, y_pred: np.ndarray, 
                               title: str = "Model Predictions vs Actual") -> str:
        """Create a comparison chart and return as base64 string."""
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(y_true[:50], label='Actual', marker='o', linewidth=2)
            plt.plot(y_pred[:50], label='Predicted', marker='x', linewidth=2)
            plt.legend()
            plt.title(title)
            plt.xlabel('Sample Index')
            plt.ylabel('Value')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            plt.close()
            
            return base64.b64encode(image_png).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error creating prediction chart: {e}")
            return ""


class DamDataProcessor:
    """Utility class for processing dam-related data."""
    
    @staticmethod
    def load_dam_data(file_path: str) -> pd.DataFrame:
        """Load dam data from CSV file."""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded dam data: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading dam data: {e}")
            raise
    
    @staticmethod
    def preprocess_dam_data(df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess dam data for ML operations."""
        try:
            # Standardize column names
            column_mapping = {
                'measurement_date': 'Date',
                'upstream_water_level': 'Current Water Level (mcft)',
                'downstream_water_level': 'Downstream Water Level (mcft)',
                'inflow_rate': 'Inflow (cubic feet/sec)',
                'outflow_rate': 'Outflow (cubic feet/sec)',
                'rainfall_amount': 'Rainfall Amount (mm)'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Add missing columns with default values
            required_columns = [
                'Rainy Season Indicator', 'Inflow (cubic feet/sec)', 
                'Outflow (cubic feet/sec)', 'Water Flow (cubic feet/sec)',
                'Total Rainfall Last 3 Days', 'Average Rainfall Last 3 Days',
                'temperature', 'humidity', 'wind_speed'
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    df[col] = 0
            
            # Calculate rainfall features
            if 'Rainfall Amount (mm)' in df.columns:
                df['Total Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).sum().fillna(0)
                df['Average Rainfall Last 3 Days'] = df['Rainfall Amount (mm)'].rolling(window=3).mean().fillna(0)
            
            # Create target variable
            if 'Current Water Level (mcft)' in df.columns:
                df['Success'] = (df['Current Water Level (mcft)'].diff().fillna(0) > 0).astype(int)
            
            # Convert date column
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            logger.info("Dam data preprocessed successfully")
            return df
            
        except Exception as e:
            logger.error(f"Error preprocessing dam data: {e}")
            raise
    
    @staticmethod
    def check_alert_conditions(row: pd.Series, 
                             high_rainfall_threshold: float = config.DEFAULT_RAINFALL_THRESHOLD,
                             high_inflow_threshold: float = config.DEFAULT_INFLOW_THRESHOLD,
                             low_water_level_threshold: float = config.DEFAULT_WATER_LEVEL_THRESHOLD,
                             low_inflow_threshold: float = config.DEFAULT_OUTFLOW_THRESHOLD) -> str:
        """Check if row meets alert conditions."""
        try:
            total_rainfall = row.get('Total Rainfall Last 3 Days', 0)
            inflow = row.get('Inflow (cubic feet/sec)', 0)
            water_level = row.get('Current Water Level (mcft)', 0)
            
            if total_rainfall > high_rainfall_threshold or inflow > high_inflow_threshold:
                return "ALERT: High water level detected!"
            elif water_level < low_water_level_threshold or inflow < low_inflow_threshold:
                return "ALERT: Low water level detected!"
            return "Normal"
            
        except Exception as e:
            logger.error(f"Error checking alert conditions: {e}")
            return "Normal"
    
    @staticmethod
    def create_water_level_chart(df: pd.DataFrame, alert_column: str = 'Alert') -> str:
        """Create interactive water level chart with alerts."""
        try:
            fig = go.Figure()
            
            # Add main water level line
            fig.add_trace(go.Scatter(
                x=df['Date'], 
                y=df['Current Water Level (mcft)'],
                mode='lines+markers', 
                name='Water Level',
                line=dict(color='blue', width=2),
                marker=dict(size=4)
            ))
            
            # Add high alerts
            high_alert_mask = df[alert_column] == "ALERT: High water level detected!"
            if high_alert_mask.any():
                fig.add_trace(go.Scatter(
                    x=df[high_alert_mask]['Date'],
                    y=df[high_alert_mask]['Current Water Level (mcft)'],
                    mode='markers',
                    name='High Alert',
                    marker=dict(color='red', size=10, symbol='triangle-up')
                ))
            
            # Add low alerts
            low_alert_mask = df[alert_column] == "ALERT: Low water level detected!"
            if low_alert_mask.any():
                fig.add_trace(go.Scatter(
                    x=df[low_alert_mask]['Date'],
                    y=df[low_alert_mask]['Current Water Level (mcft)'],
                    mode='markers',
                    name='Low Alert',
                    marker=dict(color='orange', size=10, symbol='triangle-down')
                ))
            
            # Update layout
            fig.update_layout(
                title="Water Level Monitoring with Alerts",
                xaxis_title="Date",
                yaxis_title="Water Level (mcft)",
                hovermode='x unified',
                template='plotly_white',
                height=500,
                showlegend=True
            )
            
            return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
            
        except Exception as e:
            logger.error(f"Error creating water level chart: {e}")
            return ""


class WeatherDataProcessor:
    """Utility class for processing weather data."""
    
    @staticmethod
    def process_openweather_data(data: dict) -> dict:
        """Process OpenWeatherMap API response."""
        try:
            processed_data = {
                "city": data["name"],
                "country": data.get("sys", {}).get("country", ""),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"].get("speed", 0),
                "wind_deg": data["wind"].get("deg", 0),
                "description": data["weather"][0]["description"].title(),
                "icon": data["weather"][0]["icon"],
                "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"],
                "sunrise": data.get("sys", {}).get("sunrise"),
                "sunset": data.get("sys", {}).get("sunset")
            }
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            raise
    
    @staticmethod
    def process_forecast_data(data: dict) -> List[dict]:
        """Process OpenWeatherMap forecast response."""
        try:
            forecast_data = []
            used_dates = set()
            
            for item in data.get("list", []):
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
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item["wind"].get("speed", 0)
                    })
                    
                    if len(forecast_data) >= 5:
                        break
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error processing forecast data: {e}")
            return []
