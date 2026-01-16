"""
Main Application for Patient Flow Management System
Integrates all modules and provides CLI interface
"""

import sys
import os
from datetime import datetime, timedelta
from patient_queue import Patient, PatientQueue
from predictive_model import WaitTimePredictionModel, DoctorProfileManager
from data_generator import AppointmentDataGenerator
from dashboard import Dashboard, NotificationService
import pandas as pd
import time


class PatientFlowManagementSystem:
    """Main system coordinating all components"""
    
    def __init__(self):
        self.queue = PatientQueue()
        self.predictor = WaitTimePredictionModel()
        self.doctor_manager = DoctorProfileManager()
        self.dashboard = Dashboard()
        self.notification_service = NotificationService()
        self.is_initialized = False
    
    def initialize_system(self):
        """Initialize system with doctors and train prediction model"""
        print("Initializing Patient Flow Management System...")
        
        # Initialize doctors (15 specialists)
        self.dashboard.animate_loading("Loading doctor profiles", 1)
        doctors = [
            (1, "Dr. Sharma", "Cardiology", 12.5),
            (2, "Dr. Patel", "Orthopedics", 18.0),
            (3, "Dr. Kumar", "Dermatology", 10.0),
            (4, "Dr. Singh", "Pediatrics", 15.0),
            (5, "Dr. Reddy", "General Medicine", 12.0),
            (6, "Dr. Rao", "Cardiology", 14.0),
            (7, "Dr. Mehta", "Orthopedics", 22.0),
            (8, "Dr. Joshi", "Dermatology", 8.0),
            (9, "Dr. Gupta", "Pediatrics", 16.0),
            (10, "Dr. Iyer", "General Medicine", 11.0),
            (11, "Dr. Khan", "Cardiology", 13.0),
            (12, "Dr. Nair", "Orthopedics", 20.0),
            (13, "Dr. Desai", "Dermatology", 9.0),
            (14, "Dr. Verma", "Pediatrics", 14.5),
            (15, "Dr. Pillai", "General Medicine", 12.5),
        ]
        
        for doctor in doctors:
            self.doctor_manager.add_doctor(*doctor)
        
        # Generate training data if not exists
        data_file = "appointments.csv"
        if not os.path.exists(data_file):
            self.dashboard.animate_loading("Generating historical appointment data", 2)
            generator = AppointmentDataGenerator(num_doctors=15)
            generator.generate_and_save(data_file, months=3)
        
        # Train prediction model
        self.dashboard.animate_loading("Training AI prediction model", 2)
        df = pd.read_csv(data_file)
        metrics = self.predictor.train(df)
        
        print(f"\nModel trained successfully!")
        print(f"  - Mean Absolute Error: {metrics['mae']:.2f} minutes")
        print(f"  - Root Mean Squared Error: {metrics['rmse']:.2f} minutes")
        print(f"  - Training samples: {metrics['train_samples']}")
        
        self.is_initialized = True
        time.sleep(2)
    
    def register_new_patient(self, name: str, doctor_id: int = None, 
                            appointment_time: datetime = None) -> Patient:
        """Register a new patient"""
        if doctor_id is None:
            doctor_id = self.doctor_manager.recommend_doctor(datetime.now())
        
        patient = Patient(
            name=name,
            doctor_id=doctor_id,
            appointment_time=appointment_time or datetime.now(),
            arrival_time=datetime.now()
        )
        
        # Register in queue
        patient_id = self.queue.register_patient(patient)
        
        # Predict wait time
        queue_length = self.queue.get_queue_length(doctor_id)
        avg_consultation_time = self.doctor_manager.get_avg_consultation_time(doctor_id)
        
        predicted_wait = self.predictor.predict_wait_time(
            doctor_id=doctor_id,
            scheduled_time=patient.appointment_time,
            queue_length=queue_length,
            avg_consultation_time=avg_consultation_time
        )
        
        patient.predicted_wait_time = predicted_wait
        
        # Send notification
        self.notification_service.send_wait_time_notification(patient_id, predicted_wait)
        
        return patient
    
    def get_dashboard_data(self):
        """Prepare data for dashboard display"""
        # Get statistics
        statistics = self.queue.get_statistics()
        
        # Get doctor queue info
        doctor_queues = []
        for doctor_id, profile in self.doctor_manager.doctor_profiles.items():
            queue_length = self.queue.get_queue_length(doctor_id)
            avg_wait = queue_length * profile['avg_consultation_time']
            status = self.queue.doctors_status.get(doctor_id, "available")
            
            doctor_queues.append({
                'doctor_id': doctor_id,
                'specialty': profile['specialty'],
                'queue_length': queue_length,
                'avg_wait_time': avg_wait,
                'status': status
            })
        
        # Sort by queue length
        doctor_queues.sort(key=lambda x: x['queue_length'], reverse=True)
        
        # Get waiting patients
        waiting_patients = self.queue.get_waiting_patients()
        patient_data = []
        
        for patient in waiting_patients:
            position = self.queue.get_queue_position(patient.patient_id)
            patient_dict = patient.to_dict()
            patient_dict['position'] = position
            patient_data.append(patient_dict)
        
        # Sort by predicted wait time
        patient_data.sort(key=lambda x: x.get('predicted_wait_time', 0))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(doctor_queues, statistics)
        
        return statistics, doctor_queues, patient_data, recommendations
    
    def _generate_recommendations(self, doctor_queues, statistics):
        """Generate system recommendations"""
        recommendations = []
        
        # Check for load imbalance
        if len(doctor_queues) > 0:
            max_queue = max(doctor_queues, key=lambda x: x['queue_length'])
            min_queue = min(doctor_queues, key=lambda x: x['queue_length'])
            
            if max_queue['queue_length'] - min_queue['queue_length'] > 3:
                recommendations.append(
                    f"Consider redirecting patients from Dr. {max_queue['doctor_id']} "
                    f"({max_queue['specialty']}) to Dr. {min_queue['doctor_id']} "
                    f"({min_queue['specialty']})"
                )
        
        # Check for high wait times
        high_wait_doctors = [d for d in doctor_queues if d['avg_wait_time'] > 40]
        if high_wait_doctors:
            recommendations.append(
                f"{len(high_wait_doctors)} doctor(s) have wait times exceeding 40 minutes. "
                "Consider adding support staff or extending hours."
            )
        
        # Peak hour alert
        current_hour = datetime.now().hour
        if 17 <= current_hour < 20 and statistics['waiting'] > 20:
            recommendations.append(
                "Peak hour detected with high patient volume. All staff should be on duty."
            )
        
        if not recommendations:
            recommendations.append("System operating normally. No immediate actions required.")
        
        return recommendations
    
    def simulate_consultation(self, doctor_id: int):
        """Simulate starting a consultation"""
        patient = self.queue.start_consultation(doctor_id)
        if patient:
            self.notification_service.send_ready_notification(patient.patient_id)
            return patient
        return None
    
    def complete_patient(self, patient_id: str):
        """Mark patient consultation as complete"""
        self.queue.complete_consultation(patient_id)
    
    def interactive_menu(self):
        """Display interactive CLI menu"""
        while True:
            self.dashboard.clear_screen()
            print("\n" + "=" * 80)
            print(" " * 25 + "MAIN MENU")
            print("=" * 80)
            print("\n1. Register New Patient")
            print("2. View Dashboard")
            print("3. Start Consultation (Doctor)")
            print("4. Complete Consultation")
            print("5. View Patient Info")
            print("6. Generate Detailed Report")
            print("7. View Notifications")
            print("8. Exit")
            print("\n" + "=" * 80)
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                self._register_patient_interactive()
            elif choice == "2":
                self._view_dashboard_interactive()
            elif choice == "3":
                self._start_consultation_interactive()
            elif choice == "4":
                self._complete_consultation_interactive()
            elif choice == "5":
                self._view_patient_info_interactive()
            elif choice == "6":
                self._generate_report()
            elif choice == "7":
                self._view_notifications()
            elif choice == "8":
                print("\nThank you for using Patient Flow Management System!")
                print("Goodbye!\n")
                break
            else:
                print("\nInvalid choice. Please try again.")
                time.sleep(1)
    
    def _register_patient_interactive(self):
        """Interactive patient registration"""
        self.dashboard.clear_screen()
        print("\n" + "=" * 80)
        print(" " * 25 + "PATIENT REGISTRATION")
        print("=" * 80)
        
        name = input("\nEnter patient name: ").strip()
        if not name:
            print("Invalid name. Registration cancelled.")
            time.sleep(2)
            return
        
        print("\nAvailable Doctors:")
        for doctor_id, profile in sorted(self.doctor_manager.doctor_profiles.items()):
            queue_len = self.queue.get_queue_length(doctor_id)
            print(f"  {doctor_id}. Dr. {profile['name']} - {profile['specialty']} "
                  f"(Queue: {queue_len}, Avg: {profile['avg_consultation_time']:.1f}min)")
        
        doctor_input = input("\nEnter doctor ID (or press Enter for auto-assignment): ").strip()
        doctor_id = int(doctor_input) if doctor_input.isdigit() else None
        
        patient = self.register_new_patient(name, doctor_id)
        
        print("\n✓ Patient registered successfully!")
        self.dashboard.display_patient_info(patient.to_dict())
        print(f"\n📱 SMS sent to patient: Your estimated wait time is {patient.predicted_wait_time:.0f} minutes")
        
        input("\nPress Enter to continue...")
    
    def _view_dashboard_interactive(self):
        """Display dashboard in interactive mode"""
        statistics, doctor_queues, patient_data, recommendations = self.get_dashboard_data()
        self.dashboard.display_full_dashboard(statistics, doctor_queues, patient_data, recommendations)
        input("\nPress Enter to return to menu...")
    
    def _start_consultation_interactive(self):
        """Start consultation interactively"""
        self.dashboard.clear_screen()
        print("\n" + "=" * 80)
        print(" " * 25 + "START CONSULTATION")
        print("=" * 80)
        
        doctor_id = input("\nEnter doctor ID: ").strip()
        if not doctor_id.isdigit():
            print("Invalid doctor ID.")
            time.sleep(2)
            return
        
        patient = self.simulate_consultation(int(doctor_id))
        if patient:
            print(f"\n✓ Consultation started for Patient {patient.patient_id} ({patient.name})")
            print(f"📱 SMS sent: The doctor is ready to see you now.")
        else:
            print(f"\n✗ No waiting patients for Doctor {doctor_id}")
        
        input("\nPress Enter to continue...")
    
    def _complete_consultation_interactive(self):
        """Complete consultation interactively"""
        self.dashboard.clear_screen()
        print("\n" + "=" * 80)
        print(" " * 25 + "COMPLETE CONSULTATION")
        print("=" * 80)
        
        patient_id = input("\nEnter patient ID: ").strip()
        if patient_id in self.queue.all_patients:
            self.complete_patient(patient_id)
            print(f"\n✓ Consultation completed for Patient {patient_id}")
        else:
            print("\n✗ Patient not found")
        
        input("\nPress Enter to continue...")
    
    def _view_patient_info_interactive(self):
        """View patient information interactively"""
        self.dashboard.clear_screen()
        print("\n" + "=" * 80)
        print(" " * 25 + "PATIENT INFORMATION")
        print("=" * 80)
        
        patient_id = input("\nEnter patient ID: ").strip()
        if patient_id in self.queue.all_patients:
            patient = self.queue.all_patients[patient_id]
            position = self.queue.get_queue_position(patient_id)
            patient_dict = patient.to_dict()
            patient_dict['position'] = position
            self.dashboard.display_patient_info(patient_dict)
        else:
            print("\n✗ Patient not found")
        
        input("\nPress Enter to continue...")
    
    def _generate_report(self):
        """Generate detailed system report"""
        self.dashboard.clear_screen()
        statistics, doctor_queues, patient_data, recommendations = self.get_dashboard_data()
        
        print("\n" + "=" * 80)
        print(" " * 25 + "SYSTEM REPORT")
        print("=" * 80)
        print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Overall statistics
        print("\n📊 Overall Statistics:")
        for key, value in statistics.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Doctor performance
        print("\n👨‍⚕️ Doctor Performance:")
        for doc in doctor_queues[:5]:  # Top 5
            print(f"  Dr. {doc['doctor_id']} ({doc['specialty']}): "
                  f"{doc['queue_length']} waiting, {doc['avg_wait_time']:.1f}min avg wait")
        
        # Wait time analysis
        if patient_data:
            wait_times = [p.get('predicted_wait_time', 0) for p in patient_data]
            avg_wait = sum(wait_times) / len(wait_times)
            max_wait = max(wait_times)
            print(f"\n⏱️ Wait Time Analysis:")
            print(f"  Average: {avg_wait:.1f} minutes")
            print(f"  Maximum: {max_wait:.1f} minutes")
        
        # Recommendations
        print("\n💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "=" * 80)
        input("\nPress Enter to continue...")
    
    def _view_notifications(self):
        """View notification history"""
        self.dashboard.clear_screen()
        print("\n" + "=" * 80)
        print(" " * 25 + "NOTIFICATION HISTORY")
        print("=" * 80)
        
        notifications = self.notification_service.get_notification_history()
        
        if not notifications:
            print("\nNo notifications sent yet.")
        else:
            for notif in notifications[-20:]:  # Last 20
                print(f"\n[{notif['timestamp'].strftime('%H:%M:%S')}] {notif['type'].upper()}")
                print(f"  Patient: {notif['patient_id']}")
                print(f"  Message: {notif['message']}")
        
        print("\n" + "=" * 80)
        input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    system = PatientFlowManagementSystem()
    
    # Display welcome screen
    system.dashboard.display_welcome_screen()
    input("\nPress Enter to start the system...")
    
    # Initialize system
    system.initialize_system()
    
    # Run interactive menu
    system.interactive_menu()


if __name__ == "__main__":
    main()
