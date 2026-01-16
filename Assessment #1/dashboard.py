"""
Real-Time Dashboard Module
Displays current queue status, wait times, and system statistics
"""

from datetime import datetime
from typing import Dict, List
import os
import time


class Dashboard:
    """Real-time dashboard for patients and staff"""
    
    def __init__(self):
        self.last_update = datetime.now()
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display dashboard header"""
        print("=" * 80)
        print(" " * 20 + "JAYANAGAR SPECIALTY CLINIC")
        print(" " * 15 + "Patient Flow Management System")
        print("=" * 80)
        print(f"Last Updated: {self.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def display_queue_overview(self, statistics: Dict):
        """Display overall queue statistics"""
        print("\n📊 SYSTEM OVERVIEW")
        print("-" * 80)
        print(f"Total Patients Today:        {statistics['total_patients']}")
        print(f"Currently Waiting:           {statistics['waiting']}")
        print(f"In Consultation:             {statistics['in_consultation']}")
        print(f"Completed:                   {statistics['completed']}")
        print(f"Doctors Busy:                {statistics['doctors_busy']}")
        print("-" * 80)
    
    def display_doctor_queues(self, queue_data: List[Dict]):
        """Display queue status for each doctor"""
        print("\n👨‍⚕️ DOCTOR-WISE QUEUE STATUS")
        print("-" * 80)
        print(f"{'Doctor ID':<12} {'Specialty':<20} {'Waiting':<10} {'Avg Wait':<12} {'Status':<10}")
        print("-" * 80)
        
        for data in queue_data:
            doctor_id = data['doctor_id']
            specialty = data.get('specialty', 'General')[:18]
            waiting = data['queue_length']
            avg_wait = data['avg_wait_time']
            status = data['status']
            
            status_symbol = "🔴" if status == "busy" else "🟢"
            
            print(f"{doctor_id:<12} {specialty:<20} {waiting:<10} {avg_wait:<10.1f}min {status_symbol} {status}")
        
        print("-" * 80)
    
    def display_patient_queue(self, patients: List[Dict], max_display: int = 10):
        """Display current patient queue"""
        print(f"\n📋 CURRENT QUEUE (Next {max_display} patients)")
        print("-" * 80)
        print(f"{'Position':<10} {'Patient ID':<15} {'Name':<20} {'Doctor':<10} {'Est. Wait':<12}")
        print("-" * 80)
        
        for i, patient in enumerate(patients[:max_display], 1):
            position = i
            patient_id = patient['patient_id']
            name = patient['name'][:18]
            doctor_id = patient['doctor_id']
            wait_time = patient.get('predicted_wait_time', 0)
            
            print(f"{position:<10} {patient_id:<15} {name:<20} Dr. {doctor_id:<6} {wait_time:<10.0f}min")
        
        if len(patients) > max_display:
            print(f"\n... and {len(patients) - max_display} more patients in queue")
        
        print("-" * 80)
    
    def display_patient_info(self, patient: Dict):
        """Display individual patient information"""
        print("\n" + "=" * 80)
        print("                          PATIENT INFORMATION")
        print("=" * 80)
        print(f"Patient ID:              {patient['patient_id']}")
        print(f"Name:                    {patient['name']}")
        print(f"Doctor Assigned:         Dr. {patient['doctor_id']}")
        print(f"Appointment Time:        {patient['appointment_time']}")
        print(f"Arrival Time:            {patient['arrival_time']}")
        print(f"Status:                  {patient['status'].upper()}")
        print(f"Estimated Wait Time:     {patient.get('predicted_wait_time', 0):.0f} minutes")
        print(f"Queue Position:          {patient.get('position', 'N/A')}")
        print("=" * 80)
    
    def display_recommendations(self, recommendations: List[str]):
        """Display system recommendations"""
        print("\n💡 RECOMMENDATIONS")
        print("-" * 80)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        print("-" * 80)
    
    def display_full_dashboard(self, statistics: Dict, doctor_queues: List[Dict], 
                              patient_queue: List[Dict], recommendations: List[str] = None):
        """Display complete dashboard"""
        self.clear_screen()
        self.last_update = datetime.now()
        
        self.display_header()
        self.display_queue_overview(statistics)
        self.display_doctor_queues(doctor_queues)
        self.display_patient_queue(patient_queue)
        
        if recommendations:
            self.display_recommendations(recommendations)
    
    def display_welcome_screen(self):
        """Display welcome screen"""
        self.clear_screen()
        print("\n" * 3)
        print("=" * 80)
        print(" " * 20 + "WELCOME TO JAYANAGAR SPECIALTY CLINIC")
        print(" " * 15 + "Patient Flow Management System v1.0")
        print("=" * 80)
        print("\n" * 2)
        print("Features:")
        print("  ✓ Smart Patient Registration")
        print("  ✓ AI-Powered Wait Time Predictions")
        print("  ✓ Real-Time Queue Updates")
        print("  ✓ Doctor Load Balancing")
        print("  ✓ SMS Notifications (Simulated)")
        print("\n" * 2)
        print("=" * 80)
    
    def animate_loading(self, message: str, duration: int = 2):
        """Display loading animation"""
        animation = ["|", "/", "-", "\\"]
        end_time = time.time() + duration
        i = 0
        
        while time.time() < end_time:
            print(f"\r{message} {animation[i % len(animation)]}", end="", flush=True)
            time.sleep(0.1)
            i += 1
        
        print(f"\r{message} ✓")


class NotificationService:
    """Simulates SMS/notification service"""
    
    def __init__(self):
        self.notifications_sent = []
    
    def send_wait_time_notification(self, patient_id: str, wait_time: float):
        """Send wait time notification to patient"""
        notification = {
            'type': 'wait_time',
            'patient_id': patient_id,
            'message': f"Your estimated wait time is {wait_time:.0f} minutes",
            'timestamp': datetime.now()
        }
        self.notifications_sent.append(notification)
        return notification
    
    def send_ready_notification(self, patient_id: str):
        """Send ready notification to patient"""
        notification = {
            'type': 'ready',
            'patient_id': patient_id,
            'message': "The doctor is ready to see you now. Please proceed to the consultation room.",
            'timestamp': datetime.now()
        }
        self.notifications_sent.append(notification)
        return notification
    
    def send_queue_update(self, patient_id: str, position: int):
        """Send queue position update"""
        notification = {
            'type': 'queue_update',
            'patient_id': patient_id,
            'message': f"You are now #{position} in the queue",
            'timestamp': datetime.now()
        }
        self.notifications_sent.append(notification)
        return notification
    
    def get_notification_history(self) -> List[Dict]:
        """Get all sent notifications"""
        return self.notifications_sent
