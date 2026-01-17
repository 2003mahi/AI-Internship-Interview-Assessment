"""
Predictive Analytics Module
Forecasts patient wait times based on historical data and current queue length
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pickle
import os


class WaitTimePredictionModel:
    """Predicts patient wait times using machine learning"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.feature_columns = ['doctor_id', 'hour', 'day_of_week', 'queue_length', 'avg_consultation_time']
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features from raw appointment data"""
        # Extract time-based features
        data['scheduled_time'] = pd.to_datetime(data['scheduled_time'])
        data['actual_time'] = pd.to_datetime(data['actual_time'])
        data['hour'] = data['scheduled_time'].dt.hour
        data['day_of_week'] = data['scheduled_time'].dt.dayofweek
        
        # Calculate delays
        data['delay'] = (data['actual_time'] - data['scheduled_time']).dt.total_seconds() / 60
        
        return data
    
    def train(self, data: pd.DataFrame) -> Dict[str, float]:
        """Train the prediction model on historical data"""
        # Prepare features
        data = self.prepare_features(data)
        
        # Select features and target
        X = data[self.feature_columns]
        y = data['delay']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        return {
            'mae': mae,
            'rmse': rmse,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
    
    def predict_wait_time(self, doctor_id: int, scheduled_time: datetime, 
                         queue_length: int, avg_consultation_time: float) -> float:
        """Predict wait time for a patient"""
        if not self.is_trained:
            # Fallback to simple calculation if model not trained
            return queue_length * avg_consultation_time
        
        hour = scheduled_time.hour
        day_of_week = scheduled_time.weekday()
        
        features = pd.DataFrame([[
            doctor_id, hour, day_of_week, queue_length, avg_consultation_time
        ]], columns=self.feature_columns)
        
        predicted_delay = self.model.predict(features)[0]
        
        # Base wait time = queue_length * avg_consultation_time + predicted delay
        base_wait = queue_length * avg_consultation_time
        total_wait = max(0, base_wait + predicted_delay)
        
        return total_wait
    
    def batch_predict(self, patients_data: List[Dict]) -> List[float]:
        """Predict wait times for multiple patients"""
        if not patients_data:
            return []
        
        predictions = []
        for patient in patients_data:
            wait_time = self.predict_wait_time(
                doctor_id=patient['doctor_id'],
                scheduled_time=patient['scheduled_time'],
                queue_length=patient['queue_length'],
                avg_consultation_time=patient['avg_consultation_time']
            )
            predictions.append(wait_time)
        
        return predictions
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'is_trained': self.is_trained,
                'feature_columns': self.feature_columns
            }, f)
    
    def load_model(self, filepath: str):
        """Load trained model from disk"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.is_trained = data['is_trained']
                self.feature_columns = data['feature_columns']
            return True
        return False
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the trained model"""
        if not self.is_trained:
            return {}
        
        importances = self.model.feature_importances_
        return dict(zip(self.feature_columns, importances))


class DoctorProfileManager:
    """Manages doctor consultation patterns and availability"""
    
    def __init__(self):
        self.doctor_profiles: Dict[int, Dict] = {}
    
    def add_doctor(self, doctor_id: int, name: str, specialty: str, 
                   avg_consultation_time: float):
        """Add or update a doctor profile"""
        self.doctor_profiles[doctor_id] = {
            'name': name,
            'specialty': specialty,
            'avg_consultation_time': avg_consultation_time,
            'total_consultations': 0,
            'total_time': 0.0
        }
    
    def update_consultation_stats(self, doctor_id: int, consultation_time: float):
        """Update doctor's consultation statistics"""
        if doctor_id in self.doctor_profiles:
            profile = self.doctor_profiles[doctor_id]
            profile['total_consultations'] += 1
            profile['total_time'] += consultation_time
            profile['avg_consultation_time'] = (
                profile['total_time'] / profile['total_consultations']
            )
    
    def get_avg_consultation_time(self, doctor_id: int) -> float:
        """Get average consultation time for a doctor"""
        if doctor_id in self.doctor_profiles:
            return self.doctor_profiles[doctor_id]['avg_consultation_time']
        return 15.0  # Default 15 minutes
    
    def get_all_doctors(self) -> List[Dict]:
        """Get all doctor profiles"""
        return [
            {'doctor_id': did, **profile}
            for did, profile in self.doctor_profiles.items()
        ]
    
    def recommend_doctor(self, current_time: datetime) -> int:
        """Recommend doctor with shortest expected wait time"""
        if not self.doctor_profiles:
            return 1
        
        # Simple recommendation: doctor with lowest avg consultation time
        min_time = float('inf')
        recommended_id = list(self.doctor_profiles.keys())[0]
        
        for doctor_id, profile in self.doctor_profiles.items():
            if profile['avg_consultation_time'] < min_time:
                min_time = profile['avg_consultation_time']
                recommended_id = doctor_id
        
        return recommended_id
