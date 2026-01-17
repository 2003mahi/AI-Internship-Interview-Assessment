"""
Data Generation Module
Generates synthetic historical appointment data for training and testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


class AppointmentDataGenerator:
    """Generates synthetic appointment data for the clinic"""
    
    def __init__(self, num_doctors: int = 15, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        self.num_doctors = num_doctors
        
        # Doctor profiles with varying consultation times
        self.doctor_profiles = {
            i: {
                'avg_consultation_time': random.uniform(8, 22),
                'variance': random.uniform(2, 5),
                'specialty': random.choice(['Cardiology', 'Orthopedics', 'Dermatology', 
                                          'Pediatrics', 'General Medicine'])
            }
            for i in range(1, num_doctors + 1)
        }
    
    def generate_historical_data(self, start_date: datetime, end_date: datetime, 
                                patients_per_day: int = 300) -> pd.DataFrame:
        """Generate historical appointment data"""
        records = []
        current_date = start_date
        
        while current_date <= end_date:
            # Generate appointments for the day
            daily_records = self._generate_daily_appointments(current_date, patients_per_day)
            records.extend(daily_records)
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(records)
        return df
    
    def _generate_daily_appointments(self, date: datetime, total_patients: int) -> list:
        """Generate appointments for a single day"""
        records = []
        
        # Peak hours: 5-8 PM (75% of patients)
        peak_patients = int(total_patients * 0.75)
        non_peak_patients = total_patients - peak_patients
        
        # Generate non-peak appointments (9 AM - 5 PM)
        records.extend(self._generate_time_slot_appointments(
            date, 9, 17, non_peak_patients
        ))
        
        # Generate peak appointments (5 PM - 8 PM)
        records.extend(self._generate_time_slot_appointments(
            date, 17, 20, peak_patients
        ))
        
        return records
    
    def _generate_time_slot_appointments(self, date: datetime, start_hour: int, 
                                        end_hour: int, num_patients: int) -> list:
        """Generate appointments for a specific time slot"""
        records = []
        
        for _ in range(num_patients):
            # Random doctor
            doctor_id = random.randint(1, self.num_doctors)
            doctor_profile = self.doctor_profiles[doctor_id]
            
            # Random scheduled time within the slot
            hour = random.randint(start_hour, end_hour - 1)
            minute = random.choice([0, 15, 30, 45])
            scheduled_time = date.replace(hour=hour, minute=minute, second=0)
            
            # Calculate actual time with delays
            base_delay = random.gauss(5, 10)  # Base delay in minutes
            
            # Peak hour additional delay
            if 17 <= hour < 20:
                peak_delay = random.gauss(15, 10)
                base_delay += peak_delay
            
            # Queue-based delay (simulate backlog)
            queue_factor = random.randint(0, 5)
            queue_delay = queue_factor * random.uniform(5, 15)
            
            total_delay = max(0, base_delay + queue_delay)
            
            # Consultation time
            consultation_time = random.gauss(
                doctor_profile['avg_consultation_time'],
                doctor_profile['variance']
            )
            consultation_time = max(5, consultation_time)  # Minimum 5 minutes
            
            actual_time = scheduled_time + timedelta(minutes=total_delay + consultation_time)
            
            # Current queue length at appointment time
            queue_length = random.randint(0, 8) if 17 <= hour < 20 else random.randint(0, 3)
            
            records.append({
                'patient_id': f"P{len(records):05d}",
                'doctor_id': doctor_id,
                'scheduled_time': scheduled_time,
                'actual_time': actual_time,
                'queue_length': queue_length,
                'avg_consultation_time': doctor_profile['avg_consultation_time'],
                'specialty': doctor_profile['specialty']
            })
        
        return records
    
    def generate_and_save(self, filepath: str, months: int = 3, 
                         patients_per_day: int = 300):
        """Generate and save appointment data to CSV"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        df = self.generate_historical_data(start_date, end_date, patients_per_day)
        df.to_csv(filepath, index=False)
        
        print(f"Generated {len(df)} appointment records")
        print(f"Date range: {start_date.date()} to {end_date.date()}")
        print(f"Saved to: {filepath}")
        
        return df
    
    def get_doctor_profiles(self) -> dict:
        """Get doctor profiles with consultation times"""
        return self.doctor_profiles


if __name__ == "__main__":
    # Generate sample data
    generator = AppointmentDataGenerator(num_doctors=15)
    df = generator.generate_and_save("appointments.csv", months=3)
    
    # Print statistics
    print("\n=== Data Statistics ===")
    print(f"Total appointments: {len(df)}")
    print(f"Date range: {df['scheduled_time'].min()} to {df['scheduled_time'].max()}")
    print(f"\nPeak hour appointments (5-8 PM): {len(df[pd.to_datetime(df['scheduled_time']).dt.hour >= 17])}")
    print(f"Non-peak appointments: {len(df[pd.to_datetime(df['scheduled_time']).dt.hour < 17])}")
