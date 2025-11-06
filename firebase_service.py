"""
Firebase Service for managing help requests and knowledge base
"""
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv(".env")

logger = logging.getLogger(__name__)

# Initialize Firebase
cred_path = os.getenv("FIREBASE_CREDENTIALS")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Collection names
PENDING_REQUESTS = "pending_requests"
RESOLVED_REQUESTS = "resolved_requests"
KNOWLEDGE_BASE = "knowledge_base"
CALLER_NOTIFICATIONS = "caller_notifications"
APPOINTMENTS = "appointments"


class FirebaseService:
    """Service for managing help requests and knowledge base"""
    
    @staticmethod
    def create_help_request(
        question: str,
        caller_name: Optional[str] = None,
        caller_phone: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """
        Create a new help request when AI doesn't know the answer
        
        Returns: request_id
        """
        request_data = {
            "question": question,
            "caller_name": caller_name or "Unknown",
            "caller_phone": caller_phone or "Unknown",
            "context": context or "",
            "status": "pending",
            "created_at": firestore.SERVER_TIMESTAMP,
            "notified_supervisor": True,
            "supervisor_answer": None,
            "resolved_at": None
        }
        
        doc_ref = db.collection(PENDING_REQUESTS).add(request_data)
        request_id = doc_ref[1].id
        
        logger.info(f"Created help request: {request_id} - Question: {question}")
        
        # Simulate supervisor notification
        print(f"\n📱 [SUPERVISOR NOTIFICATION]")
        print(f"   Hey, I need help answering: '{question}'")
        print(f"   From: {caller_name or 'Unknown caller'}")
        print(f"   Request ID: {request_id}\n")
        
        return request_id
    
    @staticmethod
    def get_pending_requests() -> List[Dict]:
        """Get all pending help requests"""
        requests = []
        # Simplified query - just get all pending requests without ordering
        # This avoids needing a composite index in Firebase
        docs = db.collection(PENDING_REQUESTS).stream()
        
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            # Filter by status in Python instead of Firestore
            if data.get("status") == "pending":
                requests.append(data)
        
        # Sort by created_at in Python
        def get_sort_time(req):
            timestamp = req.get("created_at")
            if timestamp is None:
                return 0
            if hasattr(timestamp, 'timestamp'):
                return timestamp.timestamp()
            return 0
        
        requests.sort(key=get_sort_time, reverse=True)
        
        return requests
    
    @staticmethod
    def get_resolved_requests() -> List[Dict]:
        """Get all resolved help requests"""
        requests = []
        # Get all resolved requests without ordering to avoid index requirement
        docs = db.collection(RESOLVED_REQUESTS).stream()
        
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            requests.append(data)
        
        # Sort by resolved_at or rejected_at in Python
        # Use timestamp for sorting, handle both resolved and rejected requests
        def get_sort_time(req):
            timestamp = req.get("resolved_at") or req.get("rejected_at")
            if timestamp is None:
                return 0  # Put items without timestamp at the end
            # Convert timestamp to seconds for comparison
            if hasattr(timestamp, 'timestamp'):
                return timestamp.timestamp()
            return 0
        
        requests.sort(key=get_sort_time, reverse=True)
        
        # Limit to last 50
        return requests[:50]
    
    @staticmethod
    def submit_supervisor_answer(request_id: str, answer: str, supervisor_name: str = "Supervisor") -> bool:
        """
        Submit supervisor's answer to a help request
        
        Returns: True if successful
        """
        try:
            # Get the pending request
            doc_ref = db.collection(PENDING_REQUESTS).document(request_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.error(f"Request {request_id} not found")
                return False
            
            request_data = doc.to_dict()
            
            # Update with answer
            request_data["supervisor_answer"] = answer
            request_data["supervisor_name"] = supervisor_name
            request_data["status"] = "resolved"
            request_data["resolved_at"] = firestore.SERVER_TIMESTAMP
            
            # Move to resolved collection
            db.collection(RESOLVED_REQUESTS).document(request_id).set(request_data)
            
            # Delete from pending
            doc_ref.delete()
            
            # Add to knowledge base
            FirebaseService.add_to_knowledge_base(
                question=request_data["question"],
                answer=answer,
                source="supervisor"
            )
            
            # Simulate caller notification
            FirebaseService._notify_caller(
                caller_name=request_data.get("caller_name"),
                caller_phone=request_data.get("caller_phone"),
                question=request_data["question"],
                answer=answer
            )
            
            logger.info(f"Resolved request {request_id} with answer: {answer}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            return False
    
    @staticmethod
    def reject_request(request_id: str, reason: str = "No reason provided") -> bool:
        """
        Reject a help request without answering
        
        Returns: True if successful
        """
        try:
            # Get the pending request
            doc_ref = db.collection(PENDING_REQUESTS).document(request_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.error(f"Request {request_id} not found")
                return False
            
            request_data = doc.to_dict()
            
            # Update with rejection info
            request_data["status"] = "rejected"
            request_data["rejection_reason"] = reason
            request_data["rejected_at"] = firestore.SERVER_TIMESTAMP
            
            # Move to resolved collection (as rejected)
            db.collection(RESOLVED_REQUESTS).document(request_id).set(request_data)
            
            # Delete from pending
            doc_ref.delete()
            
            logger.info(f"Rejected request {request_id}: {reason}")
            
            # Console notification
            print(f"\n🚫 [REQUEST REJECTED]")
            print(f"   Question: '{request_data['question']}'")
            print(f"   From: {request_data.get('caller_name')} ({request_data.get('caller_phone')})")
            print(f"   Reason: {reason}\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Error rejecting request: {e}")
            return False
    
    @staticmethod
    def _notify_caller(caller_name: str, caller_phone: str, question: str, answer: str):
        """Simulate notifying the caller via SMS/webhook"""
        notification = {
            "caller_name": caller_name,
            "caller_phone": caller_phone,
            "question": question,
            "answer": answer,
            "sent_at": firestore.SERVER_TIMESTAMP,
            "status": "sent"
        }
        
        db.collection(CALLER_NOTIFICATIONS).add(notification)
        
        # Console simulation
        print(f"\n📞 [CALLER NOTIFICATION - SMS Simulated]")
        print(f"   To: {caller_name} ({caller_phone})")
        print(f"   Message: Hi {caller_name}, thanks for your patience!")
        print(f"   You asked: '{question}'")
        print(f"   Answer: {answer}\n")
    
    @staticmethod
    def add_to_knowledge_base(question: str, answer: str, source: str = "supervisor"):
        """Add learned answer to knowledge base"""
        knowledge_data = {
            "question": question.lower().strip(),
            "answer": answer,
            "source": source,
            "created_at": firestore.SERVER_TIMESTAMP,
            "times_used": 0,
            "tags": []  # Could add auto-tagging later
        }
        
        # Check if similar question exists
        existing = db.collection(KNOWLEDGE_BASE).where("question", "==", question.lower().strip()).limit(1).stream()
        
        if list(existing):
            # Update existing
            for doc in db.collection(KNOWLEDGE_BASE).where("question", "==", question.lower().strip()).stream():
                doc.reference.update({
                    "answer": answer,
                    "updated_at": firestore.SERVER_TIMESTAMP
                })
                logger.info(f"Updated knowledge base entry for: {question}")
        else:
            # Create new
            db.collection(KNOWLEDGE_BASE).add(knowledge_data)
            logger.info(f"Added to knowledge base: {question} -> {answer}")
    
    @staticmethod
    def search_knowledge_base(query: str) -> Optional[str]:
        """
        Search knowledge base for an answer with fuzzy matching
        
        Returns: answer if found, None otherwise
        """
        query = query.lower().strip()
        
        # Exact match first
        docs = db.collection(KNOWLEDGE_BASE).where("question", "==", query).limit(1).stream()
        
        for doc in docs:
            data = doc.to_dict()
            # Update usage count
            doc.reference.update({"times_used": firestore.Increment(1)})
            logger.info(f"Exact match found in knowledge base for: {query}")
            return data.get("answer")
        
        # Fuzzy matching - check if query words are in stored questions
        all_docs = db.collection(KNOWLEDGE_BASE).stream()
        
        # Extract key words from query (remove common words)
        common_words = {'a', 'an', 'the', 'is', 'are', 'do', 'does', 'you', 'have', 'what', 'how', 'when', 'where', 'why', 'can', 'could', 'would', 'we', 'your', 'my', 'our', 'i'}
        query_words = set(query.split()) - common_words
        
        best_match = None
        best_score = 0
        
        for doc in all_docs:
            data = doc.to_dict()
            stored_question = data.get("question", "").lower()
            stored_words = set(stored_question.split()) - common_words
            
            # Calculate similarity score (number of matching words)
            if not query_words or not stored_words:
                continue
            
            matching_words = query_words & stored_words
            
            # Score based on percentage of words matched (considering both directions)
            score_query = len(matching_words) / len(query_words)
            score_stored = len(matching_words) / len(stored_words)
            
            # Use the higher score (more lenient matching)
            score = max(score_query, score_stored)
            
            # If 50% or more words match, consider it a match
            if score >= 0.5 and score > best_score:
                best_score = score
                best_match = (doc, data)
        
        if best_match:
            doc, data = best_match
            # Update usage count
            doc.reference.update({"times_used": firestore.Increment(1)})
            logger.info(f"Fuzzy match found (score: {best_score:.2f}) for: {query}")
            logger.info(f"   Matched question: {data.get('question')}")
            return data.get("answer")
        
        logger.info(f"No match found in knowledge base for: {query}")
        return None
    
    @staticmethod
    def get_knowledge_base() -> List[Dict]:
        """Get all learned answers"""
        knowledge = []
        # Get all knowledge without ordering to avoid index requirement
        docs = db.collection(KNOWLEDGE_BASE).stream()
        
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            knowledge.append(data)
        
        # Sort by created_at in Python
        def get_sort_time(item):
            timestamp = item.get("created_at")
            if timestamp is None:
                return 0
            if hasattr(timestamp, 'timestamp'):
                return timestamp.timestamp()
            return 0
        
        knowledge.sort(key=get_sort_time, reverse=True)
        
        return knowledge
    
    @staticmethod
    def get_stats() -> Dict:
        """Get system statistics"""
        pending_count = len(list(db.collection(PENDING_REQUESTS).stream()))
        resolved_count = len(list(db.collection(RESOLVED_REQUESTS).stream()))
        knowledge_count = len(list(db.collection(KNOWLEDGE_BASE).stream()))
        
        # Only count confirmed appointments (exclude cancelled)
        confirmed_appointments = db.collection(APPOINTMENTS).where("status", "==", "confirmed").stream()
        appointments_count = len(list(confirmed_appointments))
        
        return {
            "pending_requests": pending_count,
            "resolved_requests": resolved_count,
            "knowledge_items": knowledge_count,
            "appointments": appointments_count
        }
    
    # ========== APPOINTMENT BOOKING METHODS ==========
    
    @staticmethod
    def get_available_slots(date_str: str) -> List[str]:
        """
        Get available time slots for a specific date
        Business hours: Monday-Saturday 9am-6pm (closed Sunday)
        Slots are 1 hour each: 9am, 10am, 11am, 12pm, 1pm, 2pm, 3pm, 4pm, 5pm
        
        Args:
            date_str: Date in format YYYY-MM-DD
        
        Returns: List of available time slots (e.g., ["9:00 AM", "10:00 AM"])
        """
        from datetime import datetime, timedelta
        
        try:
            # Parse the date
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Check if it's Sunday (6 = Sunday in weekday())
            if target_date.weekday() == 6:
                logger.info(f"Date {date_str} is Sunday - salon closed")
                return []
            
            # Define all possible slots (9am to 5pm, last appointment starts at 5pm)
            all_slots = [
                "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
                "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"
            ]
            
            # Get all booked appointments for this date
            appointments = db.collection(APPOINTMENTS)\
                .where("date", "==", date_str)\
                .where("status", "==", "confirmed")\
                .stream()
            
            booked_slots = set()
            for appt in appointments:
                data = appt.to_dict()
                booked_slots.add(data.get("time_slot"))
            
            # Return available slots
            available = [slot for slot in all_slots if slot not in booked_slots]
            
            logger.info(f"Date {date_str}: {len(available)} available slots out of {len(all_slots)}")
            return available
            
        except ValueError as e:
            logger.error(f"Invalid date format: {date_str}")
            return []
    
    @staticmethod
    def check_slot_availability(date_str: str, time_slot: str) -> bool:
        """
        Check if a specific time slot is available
        
        Args:
            date_str: Date in format YYYY-MM-DD
            time_slot: Time in format "9:00 AM"
        
        Returns: True if available, False if booked
        """
        available_slots = FirebaseService.get_available_slots(date_str)
        return time_slot in available_slots
    
    @staticmethod
    def create_appointment(
        date_str: str,
        time_slot: str,
        customer_name: str,
        customer_phone: str,
        service: str = "General"
    ) -> Optional[str]:
        """
        Book an appointment
        
        Args:
            date_str: Date in format YYYY-MM-DD
            time_slot: Time in format "9:00 AM"
            customer_name: Customer's name
            customer_phone: Customer's phone number
            service: Type of service requested
        
        Returns: appointment_id if successful, None if slot not available
        """
        # Check if slot is available
        if not FirebaseService.check_slot_availability(date_str, time_slot):
            logger.warning(f"Slot {time_slot} on {date_str} is not available")
            return None
        
        # Create appointment
        appointment_data = {
            "date": date_str,
            "time_slot": time_slot,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "service": service,
            "status": "confirmed",
            "created_at": firestore.SERVER_TIMESTAMP,
            "cancelled_at": None,
            "cancellation_reason": None
        }
        
        doc_ref = db.collection(APPOINTMENTS).add(appointment_data)
        appointment_id = doc_ref[1].id
        
        logger.info(f"Created appointment {appointment_id} for {customer_name} on {date_str} at {time_slot}")
        
        # Console notification
        print(f"\n📅 [APPOINTMENT BOOKED]")
        print(f"   Customer: {customer_name} ({customer_phone})")
        print(f"   Date: {date_str}")
        print(f"   Time: {time_slot}")
        print(f"   Service: {service}")
        print(f"   Appointment ID: {appointment_id}\n")
        
        return appointment_id
    
    @staticmethod
    def get_appointments(date_str: Optional[str] = None, status: str = "confirmed") -> List[Dict]:
        """
        Get appointments, optionally filtered by date and status
        
        Args:
            date_str: Optional date filter (YYYY-MM-DD)
            status: Filter by status (confirmed, cancelled, completed)
        
        Returns: List of appointments
        """
        appointments = []
        
        # Build query
        query = db.collection(APPOINTMENTS)
        
        if date_str:
            query = query.where("date", "==", date_str)
        
        if status:
            query = query.where("status", "==", status)
        
        docs = query.stream()
        
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            appointments.append(data)
        
        # Sort by date and time
        def get_sort_key(appt):
            try:
                date_str = appt.get("date", "")
                time_str = appt.get("time_slot", "9:00 AM")
                # Convert to sortable format
                datetime_str = f"{date_str} {time_str}"
                return datetime.strptime(datetime_str, "%Y-%m-%d %I:%M %p")
            except:
                return datetime.min
        
        appointments.sort(key=get_sort_key)
        
        return appointments
    
    @staticmethod
    def cancel_appointment(appointment_id: str, reason: str = "Customer request") -> bool:
        """
        Cancel an appointment
        
        Args:
            appointment_id: ID of appointment to cancel
            reason: Reason for cancellation
        
        Returns: True if successful
        """
        try:
            doc_ref = db.collection(APPOINTMENTS).document(appointment_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.error(f"Appointment {appointment_id} not found")
                return False
            
            # Update status to cancelled
            doc_ref.update({
                "status": "cancelled",
                "cancelled_at": firestore.SERVER_TIMESTAMP,
                "cancellation_reason": reason
            })
            
            appt_data = doc.to_dict()
            
            logger.info(f"Cancelled appointment {appointment_id}")
            
            # Console notification
            print(f"\n🚫 [APPOINTMENT CANCELLED]")
            print(f"   Customer: {appt_data.get('customer_name')}")
            print(f"   Date: {appt_data.get('date')} at {appt_data.get('time_slot')}")
            print(f"   Reason: {reason}\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return False
    
    @staticmethod
    def get_next_available_slot(date_str: str, preferred_time: Optional[str] = None) -> Optional[Dict]:
        """
        Get next available slot on a given date, or suggest alternative
        
        Args:
            date_str: Preferred date (YYYY-MM-DD)
            preferred_time: Optional preferred time slot
        
        Returns: Dict with date and time_slot, or None
        """
        available_slots = FirebaseService.get_available_slots(date_str)
        
        if not available_slots:
            logger.info(f"No slots available on {date_str}")
            return None
        
        # If preferred time is available, return it
        if preferred_time and preferred_time in available_slots:
            return {"date": date_str, "time_slot": preferred_time}
        
        # Otherwise return first available
        return {"date": date_str, "time_slot": available_slots[0]}

