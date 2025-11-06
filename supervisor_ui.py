#Simple web UI for supervisors to handle help requests

from flask import Flask, render_template, request, jsonify, redirect, url_for
from firebase_service import FirebaseService
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

@app.route('/')
def index():
    """Dashboard showing all stats"""
    stats = FirebaseService.get_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/pending')
def pending_requests():
    """View all pending help requests"""
    requests = FirebaseService.get_pending_requests()
    return render_template('pending.html', requests=requests)

@app.route('/resolved')
def resolved_requests():
    """View resolved request history"""
    requests = FirebaseService.get_resolved_requests()
    return render_template('resolved.html', requests=requests)

@app.route('/knowledge')
def knowledge_base():
    """View learned answers"""
    knowledge = FirebaseService.get_knowledge_base()
    return render_template('knowledge.html', knowledge=knowledge)

@app.route('/appointments')
def appointments():
    """View all appointments"""
    appointments = FirebaseService.get_appointments()
    return render_template('appointments.html', appointments=appointments)

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """API endpoint to submit supervisor answer"""
    data = request.json
    request_id = data.get('request_id')
    answer = data.get('answer')
    supervisor_name = data.get('supervisor_name', 'Supervisor')
    
    if not request_id or not answer:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    success = FirebaseService.submit_supervisor_answer(request_id, answer, supervisor_name)
    
    if success:
        return jsonify({'success': True, 'message': 'Answer submitted and caller notified'})
    else:
        return jsonify({'success': False, 'error': 'Failed to submit answer'}), 500

@app.route('/api/add-knowledge', methods=['POST'])
def add_knowledge():
    """API endpoint to manually add knowledge"""
    data = request.json
    question = data.get('question')
    answer = data.get('answer')
    
    if not question or not answer:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    FirebaseService.add_to_knowledge_base(question, answer, source='manual')
    return jsonify({'success': True, 'message': 'Added to knowledge base'})

@app.route('/api/reject-request', methods=['POST'])
def reject_request():
    """API endpoint to reject a help request"""
    data = request.json
    request_id = data.get('request_id')
    reason = data.get('reason', 'No reason provided')
    
    if not request_id:
        return jsonify({'success': False, 'error': 'Missing request_id'}), 400
    
    success = FirebaseService.reject_request(request_id, reason)
    
    if success:
        return jsonify({'success': True, 'message': 'Request rejected'})
    else:
        return jsonify({'success': False, 'error': 'Failed to reject request'}), 500

@app.route('/api/cancel-appointment', methods=['POST'])
def cancel_appointment_api():
    """API endpoint to cancel an appointment"""
    data = request.json
    appointment_id = data.get('appointment_id')
    reason = data.get('reason', 'Supervisor cancellation')
    
    if not appointment_id:
        return jsonify({'success': False, 'error': 'Missing appointment_id'}), 400
    
    success = FirebaseService.cancel_appointment(appointment_id, reason)
    
    if success:
        return jsonify({'success': True, 'message': 'Appointment cancelled'})
    else:
        return jsonify({'success': False, 'error': 'Failed to cancel appointment'}), 500

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "="*50)
    print("  Supervisor UI Starting")
    print("="*50)
    print("\n📊 Dashboard: http://localhost:5000")
    print("📋 Pending Requests: http://localhost:5000/pending")
    print("✅ Resolved History: http://localhost:5000/resolved")
    print("📚 Knowledge Base: http://localhost:5000/knowledge")
    print("📅 Appointments: http://localhost:5000/appointments")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, port=5000)
