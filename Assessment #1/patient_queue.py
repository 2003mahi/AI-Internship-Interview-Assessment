"""
Patient Queue Management Module
Handles patient registration, queue management, and real-time updates
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid


class Patient:
    """Represents a patient in the system"""
    
    def __init__(self, name: str, patient_id: str = None, doctor_id: int = None, 
                 appointment_time: datetime = None, arrival_time: datetime = None):
        self.patient_id = patient_id or str(uuid.uuid4())[:8]
        self.name = name
        self.doctor_id = doctor_id
        self.appointment_time = appointment_time or datetime.now()
        self.arrival_time = arrival_time or datetime.now()
        self.status = "waiting"  # waiting, in_consultation, completed
        self.actual_consultation_time = None
        self.predicted_wait_time = None
        
    def to_dict(self) -> Dict:
        """Convert patient to dictionary"""
        return {
            'patient_id': self.patient_id,
            'name': self.name,
            'doctor_id': self.doctor_id,
            'appointment_time': self.appointment_time.strftime('%Y-%m-%d %H:%M:%S'),
            'arrival_time': self.arrival_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'predicted_wait_time': self.predicted_wait_time
        }


class PatientQueue:
    """Manages patient queues for multiple doctors"""
    
    def __init__(self):
        self.queues: Dict[int, List[Patient]] = {}  # doctor_id -> list of patients
        self.all_patients: Dict[str, Patient] = {}  # patient_id -> patient
        self.doctors_status: Dict[int, str] = {}  # doctor_id -> status (available, busy)
        
    def register_patient(self, patient: Patient) -> str:
        """Register a new patient in the queue"""
        self.all_patients[patient.patient_id] = patient
        
        if patient.doctor_id not in self.queues:
            self.queues[patient.doctor_id] = []
            self.doctors_status[patient.doctor_id] = "available"
            
        self.queues[patient.doctor_id].append(patient)
        return patient.patient_id
    
    def get_queue_position(self, patient_id: str) -> Optional[int]:
        """Get the position of a patient in their doctor's queue"""
        if patient_id not in self.all_patients:
            return None
            
        patient = self.all_patients[patient_id]
        doctor_queue = self.queues.get(patient.doctor_id, [])
        
        for i, p in enumerate(doctor_queue):
            if p.patient_id == patient_id:
                return i + 1
        return None
    
    def get_queue_length(self, doctor_id: int) -> int:
        """Get the current queue length for a doctor"""
        return len([p for p in self.queues.get(doctor_id, []) if p.status == "waiting"])
    
    def start_consultation(self, doctor_id: int) -> Optional[Patient]:
        """Start consultation with the next patient in queue"""
        queue = self.queues.get(doctor_id, [])
        
        for patient in queue:
            if patient.status == "waiting":
                patient.status = "in_consultation"
                patient.actual_consultation_time = datetime.now()
                self.doctors_status[doctor_id] = "busy"
                return patient
        
        return None
    
    def complete_consultation(self, patient_id: str):
        """Mark a patient's consultation as completed"""
        if patient_id in self.all_patients:
            patient = self.all_patients[patient_id]
            patient.status = "completed"
            
            # Check if doctor has more patients
            if self.get_queue_length(patient.doctor_id) == 0:
                self.doctors_status[patient.doctor_id] = "available"
    
    def get_waiting_patients(self, doctor_id: Optional[int] = None) -> List[Patient]:
        """Get all waiting patients, optionally filtered by doctor"""
        if doctor_id is not None:
            return [p for p in self.queues.get(doctor_id, []) if p.status == "waiting"]
        
        all_waiting = []
        for queue in self.queues.values():
            all_waiting.extend([p for p in queue if p.status == "waiting"])
        return all_waiting
    
    def get_statistics(self) -> Dict:
        """Get queue statistics"""
        total_patients = len(self.all_patients)
        waiting = sum(1 for p in self.all_patients.values() if p.status == "waiting")
        in_consultation = sum(1 for p in self.all_patients.values() if p.status == "in_consultation")
        completed = sum(1 for p in self.all_patients.values() if p.status == "completed")
        
        return {
            'total_patients': total_patients,
            'waiting': waiting,
            'in_consultation': in_consultation,
            'completed': completed,
            'doctors_busy': sum(1 for status in self.doctors_status.values() if status == "busy")
        }
