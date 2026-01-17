"""
Demo Script - Patient Flow Management System
Demonstrates system capabilities without requiring user interaction
"""

import sys
import time
from datetime import datetime
from main import PatientFlowManagementSystem


def demo_system():
    """Run automated demo of the system"""
    print("\n" + "=" * 80)
    print(" " * 20 + "PATIENT FLOW MANAGEMENT SYSTEM")
    print(" " * 25 + "AUTOMATED DEMO")
    print("=" * 80)
    
    # Initialize system
    print("\n🚀 Initializing system...")
    system = PatientFlowManagementSystem()
    system.initialize_system()
    
    print("\n✅ System initialized successfully!\n")
    time.sleep(2)
    
    # Demo 1: Register multiple patients
    print("\n" + "=" * 80)
    print("DEMO 1: REGISTERING PATIENTS")
    print("=" * 80)
    
    patients_to_register = [
        ("Rajesh Kumar", 1),
        ("Priya Sharma", 2),
        ("Amit Patel", 3),
        ("Sneha Reddy", 1),
        ("Vijay Singh", 4),
        ("Anjali Gupta", 2),
        ("Rahul Mehta", 5),
        ("Deepika Iyer", 1),
    ]
    
    registered_patients = []
    for name, doctor_id in patients_to_register:
        patient = system.register_new_patient(name, doctor_id)
        registered_patients.append(patient)
        print(f"✓ Registered: {name} → Dr. {doctor_id} (Wait: {patient.predicted_wait_time:.0f} min)")
        time.sleep(0.5)
    
    print(f"\nTotal patients registered: {len(registered_patients)}")
    time.sleep(2)
    
    # Demo 2: Display dashboard
    print("\n" + "=" * 80)
    print("DEMO 2: REAL-TIME DASHBOARD")
    print("=" * 80)
    
    statistics, doctor_queues, patient_data, recommendations = system.get_dashboard_data()
    
    print("\n📊 System Statistics:")
    print(f"  Total Patients: {statistics['total_patients']}")
    print(f"  Waiting: {statistics['waiting']}")
    print(f"  In Consultation: {statistics['in_consultation']}")
    print(f"  Completed: {statistics['completed']}")
    
    print("\n👨‍⚕️ Doctor Queue Status (Top 5):")
    for i, doc in enumerate(doctor_queues[:5], 1):
        status_icon = "🔴" if doc['status'] == "busy" else "🟢"
        print(f"  {i}. Dr. {doc['doctor_id']} ({doc['specialty']}) - "
              f"{doc['queue_length']} waiting, {doc['avg_wait_time']:.1f}min avg {status_icon}")
    
    print("\n📋 Current Queue (Next 5 patients):")
    for i, p in enumerate(patient_data[:5], 1):
        print(f"  {i}. {p['name']:<20} Dr. {p['doctor_id']:<5} "
              f"Wait: {p.get('predicted_wait_time', 0):.0f} min")
    
    time.sleep(3)
    
    # Demo 3: Start consultations
    print("\n" + "=" * 80)
    print("DEMO 3: STARTING CONSULTATIONS")
    print("=" * 80)
    
    doctors_to_consult = [1, 2, 1]
    for doctor_id in doctors_to_consult:
        patient = system.simulate_consultation(doctor_id)
        if patient:
            print(f"✓ Dr. {doctor_id} started consultation with {patient.name} (ID: {patient.patient_id})")
            time.sleep(1)
    
    print(f"\nConsultations started: {len(doctors_to_consult)}")
    time.sleep(2)
    
    # Demo 4: Updated dashboard
    print("\n" + "=" * 80)
    print("DEMO 4: UPDATED DASHBOARD AFTER CONSULTATIONS")
    print("=" * 80)
    
    statistics, doctor_queues, patient_data, recommendations = system.get_dashboard_data()
    
    print("\n📊 Updated Statistics:")
    print(f"  Waiting: {statistics['waiting']}")
    print(f"  In Consultation: {statistics['in_consultation']}")
    print(f"  Completed: {statistics['completed']}")
    print(f"  Doctors Busy: {statistics['doctors_busy']}")
    
    time.sleep(2)
    
    # Demo 5: Complete consultations
    print("\n" + "=" * 80)
    print("DEMO 5: COMPLETING CONSULTATIONS")
    print("=" * 80)
    
    # Complete first 2 consultations
    completed_count = 0
    for patient_id, patient in system.queue.all_patients.items():
        if patient.status == "in_consultation" and completed_count < 2:
            system.complete_patient(patient_id)
            print(f"✓ Completed consultation for {patient.name} (ID: {patient_id})")
            completed_count += 1
            time.sleep(1)
    
    print(f"\nConsultations completed: {completed_count}")
    time.sleep(2)
    
    # Demo 6: Recommendations
    print("\n" + "=" * 80)
    print("DEMO 6: SYSTEM RECOMMENDATIONS")
    print("=" * 80)
    
    statistics, doctor_queues, patient_data, recommendations = system.get_dashboard_data()
    
    print("\n💡 AI-Powered Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    time.sleep(2)
    
    # Demo 7: Notification history
    print("\n" + "=" * 80)
    print("DEMO 7: NOTIFICATION HISTORY")
    print("=" * 80)
    
    notifications = system.notification_service.get_notification_history()
    print(f"\nTotal notifications sent: {len(notifications)}")
    print("\nRecent notifications:")
    for notif in notifications[-5:]:
        print(f"  [{notif['type'].upper()}] Patient {notif['patient_id']}: {notif['message'][:60]}...")
    
    time.sleep(2)
    
    # Demo 8: Final statistics
    print("\n" + "=" * 80)
    print("DEMO 8: FINAL SYSTEM REPORT")
    print("=" * 80)
    
    statistics, doctor_queues, patient_data, recommendations = system.get_dashboard_data()
    
    print("\n📈 Performance Summary:")
    print(f"  Total Patients Processed: {statistics['total_patients']}")
    print(f"  Still Waiting: {statistics['waiting']}")
    print(f"  Currently Being Seen: {statistics['in_consultation']}")
    print(f"  Completed Today: {statistics['completed']}")
    
    if patient_data:
        wait_times = [p.get('predicted_wait_time', 0) for p in patient_data]
        avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0
        max_wait = max(wait_times) if wait_times else 0
        print(f"\n⏱️  Wait Time Analysis:")
        print(f"  Average Wait Time: {avg_wait:.1f} minutes")
        print(f"  Maximum Wait Time: {max_wait:.1f} minutes")
    
    print("\n🎯 Key Achievements:")
    print("  ✅ Real-time queue management")
    print("  ✅ Predictive wait time calculation")
    print("  ✅ Automated patient notifications")
    print("  ✅ Load balancing recommendations")
    print("  ✅ Comprehensive system monitoring")
    
    # Feature importance
    print("\n🤖 AI Model Feature Importance:")
    feature_importance = system.predictor.get_feature_importance()
    for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {importance:.3f}")
    
    print("\n" + "=" * 80)
    print(" " * 25 + "DEMO COMPLETE")
    print("=" * 80)
    print("\n✨ The Patient Flow Management System successfully demonstrated:")
    print("   • Efficient patient registration and queuing")
    print("   • AI-powered wait time predictions")
    print("   • Real-time dashboard updates")
    print("   • Intelligent load balancing")
    print("   • Automated notifications")
    print("   • Comprehensive analytics\n")


if __name__ == "__main__":
    try:
        demo_system()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
