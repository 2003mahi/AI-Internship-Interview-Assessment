"""
Test Cases for Patient Flow Management System
Tests core functionality of all modules
"""

import unittest
from datetime import datetime, timedelta
import pandas as pd
import os
import sys

from patient_queue import Patient, PatientQueue
from predictive_model import WaitTimePredictionModel, DoctorProfileManager
from data_generator import AppointmentDataGenerator
from dashboard import Dashboard, NotificationService


class TestPatientQueue(unittest.TestCase):
    """Test patient queue functionality"""
    
    def setUp(self):
        self.queue = PatientQueue()
    
    def test_register_patient(self):
        """Test patient registration"""
        patient = Patient(name="John Doe", doctor_id=1)
        patient_id = self.queue.register_patient(patient)
        
        self.assertIsNotNone(patient_id)
        self.assertIn(patient_id, self.queue.all_patients)
        self.assertEqual(len(self.queue.queues[1]), 1)
    
    def test_queue_position(self):
        """Test queue position tracking"""
        p1 = Patient(name="Patient 1", doctor_id=1)
        p2 = Patient(name="Patient 2", doctor_id=1)
        p3 = Patient(name="Patient 3", doctor_id=1)
        
        id1 = self.queue.register_patient(p1)
        id2 = self.queue.register_patient(p2)
        id3 = self.queue.register_patient(p3)
        
        self.assertEqual(self.queue.get_queue_position(id1), 1)
        self.assertEqual(self.queue.get_queue_position(id2), 2)
        self.assertEqual(self.queue.get_queue_position(id3), 3)
    
    def test_queue_length(self):
        """Test queue length calculation"""
        for i in range(5):
            patient = Patient(name=f"Patient {i}", doctor_id=1)
            self.queue.register_patient(patient)
        
        self.assertEqual(self.queue.get_queue_length(1), 5)
        self.assertEqual(self.queue.get_queue_length(2), 0)
    
    def test_start_consultation(self):
        """Test starting consultation"""
        patient = Patient(name="Test Patient", doctor_id=1)
        self.queue.register_patient(patient)
        
        started_patient = self.queue.start_consultation(1)
        
        self.assertIsNotNone(started_patient)
        self.assertEqual(started_patient.status, "in_consultation")
        self.assertEqual(self.queue.doctors_status[1], "busy")
    
    def test_complete_consultation(self):
        """Test completing consultation"""
        patient = Patient(name="Test Patient", doctor_id=1)
        patient_id = self.queue.register_patient(patient)
        
        self.queue.start_consultation(1)
        self.queue.complete_consultation(patient_id)
        
        self.assertEqual(patient.status, "completed")
    
    def test_statistics(self):
        """Test queue statistics"""
        for i in range(3):
            p = Patient(name=f"Patient {i}", doctor_id=1)
            self.queue.register_patient(p)
        
        stats = self.queue.get_statistics()
        
        self.assertEqual(stats['total_patients'], 3)
        self.assertEqual(stats['waiting'], 3)
        self.assertEqual(stats['in_consultation'], 0)
        self.assertEqual(stats['completed'], 0)


class TestDoctorProfileManager(unittest.TestCase):
    """Test doctor profile management"""
    
    def setUp(self):
        self.manager = DoctorProfileManager()
    
    def test_add_doctor(self):
        """Test adding doctor profile"""
        self.manager.add_doctor(1, "Dr. Smith", "Cardiology", 15.0)
        
        self.assertIn(1, self.manager.doctor_profiles)
        self.assertEqual(self.manager.doctor_profiles[1]['name'], "Dr. Smith")
        self.assertEqual(self.manager.doctor_profiles[1]['avg_consultation_time'], 15.0)
    
    def test_update_consultation_stats(self):
        """Test updating consultation statistics"""
        self.manager.add_doctor(1, "Dr. Smith", "Cardiology", 15.0)
        
        # Simulate consultations
        self.manager.update_consultation_stats(1, 10.0)
        self.manager.update_consultation_stats(1, 20.0)
        
        profile = self.manager.doctor_profiles[1]
        self.assertEqual(profile['total_consultations'], 2)
        self.assertEqual(profile['avg_consultation_time'], 15.0)  # (10 + 20) / 2
    
    def test_get_avg_consultation_time(self):
        """Test getting average consultation time"""
        self.manager.add_doctor(1, "Dr. Smith", "Cardiology", 12.5)
        
        avg_time = self.manager.get_avg_consultation_time(1)
        self.assertEqual(avg_time, 12.5)
        
        # Test default for unknown doctor
        avg_time_unknown = self.manager.get_avg_consultation_time(999)
        self.assertEqual(avg_time_unknown, 15.0)
    
    def test_recommend_doctor(self):
        """Test doctor recommendation"""
        self.manager.add_doctor(1, "Dr. Smith", "Cardiology", 20.0)
        self.manager.add_doctor(2, "Dr. Jones", "Dermatology", 10.0)
        
        recommended = self.manager.recommend_doctor(datetime.now())
        self.assertEqual(recommended, 2)  # Should recommend doctor with shortest time


class TestWaitTimePredictionModel(unittest.TestCase):
    """Test wait time prediction model"""
    
    def setUp(self):
        self.model = WaitTimePredictionModel()
    
    def test_fallback_prediction(self):
        """Test fallback prediction when model not trained"""
        wait_time = self.model.predict_wait_time(
            doctor_id=1,
            scheduled_time=datetime.now(),
            queue_length=3,
            avg_consultation_time=15.0
        )
        
        # Should use simple calculation: queue_length * avg_consultation_time
        self.assertEqual(wait_time, 45.0)
    
    def test_train_model(self):
        """Test model training"""
        # Generate sample data
        data = {
            'doctor_id': [1, 1, 2, 2, 3],
            'scheduled_time': [
                datetime(2024, 1, 1, 9, 0),
                datetime(2024, 1, 1, 10, 0),
                datetime(2024, 1, 1, 9, 0),
                datetime(2024, 1, 1, 17, 0),
                datetime(2024, 1, 1, 18, 0),
            ],
            'actual_time': [
                datetime(2024, 1, 1, 9, 20),
                datetime(2024, 1, 1, 10, 15),
                datetime(2024, 1, 1, 9, 10),
                datetime(2024, 1, 1, 17, 30),
                datetime(2024, 1, 1, 18, 25),
            ],
            'queue_length': [2, 1, 1, 5, 4],
            'avg_consultation_time': [15.0, 15.0, 10.0, 10.0, 12.0]
        }
        
        df = pd.DataFrame(data)
        
        # Add more samples for proper training (reduced from 50 to 10 iterations)
        for i in range(10):
            df = pd.concat([df, df], ignore_index=True)
        
        metrics = self.model.train(df)
        
        self.assertTrue(self.model.is_trained)
        self.assertIn('mae', metrics)
        self.assertIn('rmse', metrics)


class TestDataGenerator(unittest.TestCase):
    """Test data generation"""
    
    def setUp(self):
        self.generator = AppointmentDataGenerator(num_doctors=5, seed=42)
    
    def test_generate_daily_appointments(self):
        """Test daily appointment generation"""
        date = datetime(2024, 1, 1)
        records = self.generator._generate_daily_appointments(date, 100)
        
        self.assertEqual(len(records), 100)
        
        # Check peak hour distribution (75%)
        peak_count = sum(1 for r in records 
                        if pd.to_datetime(r['scheduled_time']).hour >= 17)
        self.assertGreaterEqual(peak_count, 70)  # Should be around 75
    
    def test_generate_historical_data(self):
        """Test historical data generation"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 5)
        
        df = self.generator.generate_historical_data(start_date, end_date, 50)
        
        # Should have ~250 records (50 per day * 5 days)
        self.assertGreater(len(df), 200)
        self.assertLess(len(df), 300)
    
    def test_doctor_profiles(self):
        """Test doctor profile generation"""
        profiles = self.generator.get_doctor_profiles()
        
        self.assertEqual(len(profiles), 5)
        for profile in profiles.values():
            self.assertIn('avg_consultation_time', profile)
            self.assertIn('specialty', profile)


class TestNotificationService(unittest.TestCase):
    """Test notification service"""
    
    def setUp(self):
        self.service = NotificationService()
    
    def test_send_wait_time_notification(self):
        """Test sending wait time notification"""
        notification = self.service.send_wait_time_notification("P001", 25.0)
        
        self.assertEqual(notification['type'], 'wait_time')
        self.assertEqual(notification['patient_id'], "P001")
        self.assertIn("25", notification['message'])
    
    def test_send_ready_notification(self):
        """Test sending ready notification"""
        notification = self.service.send_ready_notification("P002")
        
        self.assertEqual(notification['type'], 'ready')
        self.assertEqual(notification['patient_id'], "P002")
    
    def test_notification_history(self):
        """Test notification history tracking"""
        self.service.send_wait_time_notification("P001", 20.0)
        self.service.send_ready_notification("P002")
        
        history = self.service.get_notification_history()
        
        self.assertEqual(len(history), 2)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_end_to_end_flow(self):
        """Test complete patient flow"""
        # Setup
        queue = PatientQueue()
        manager = DoctorProfileManager()
        manager.add_doctor(1, "Dr. Test", "General", 15.0)
        
        # Register patient
        patient = Patient(name="John Doe", doctor_id=1)
        patient_id = queue.register_patient(patient)
        
        # Check queue
        position = queue.get_queue_position(patient_id)
        self.assertEqual(position, 1)
        
        # Start consultation
        started_patient = queue.start_consultation(1)
        self.assertEqual(started_patient.patient_id, patient_id)
        self.assertEqual(started_patient.status, "in_consultation")
        
        # Complete consultation
        queue.complete_consultation(patient_id)
        self.assertEqual(patient.status, "completed")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPatientQueue))
    suite.addTests(loader.loadTestsFromTestCase(TestDoctorProfileManager))
    suite.addTests(loader.loadTestsFromTestCase(TestWaitTimePredictionModel))
    suite.addTests(loader.loadTestsFromTestCase(TestDataGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestNotificationService))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
