import logging
from livekit import api
from livekit.agents import function_tool, RunContext, get_job_context
from firebase_service import FirebaseService


@function_tool
async def search_knowledge_base(ctx: RunContext, question: str) -> str:
    """
    Search the knowledge base for answers to customer questions.
    ALWAYS call this FIRST before requesting help from supervisor.
    
    Args:
        question: The customer's question
    
    Returns:
        The answer if found in knowledge base, or "not_found" if no answer exists
    """
    logger = logging.getLogger("phone-assistant")
    
    try:
        logger.info(f"Searching knowledge base for: {question}")
        answer = FirebaseService.search_knowledge_base(question)
        
        if answer:
            logger.info(f"Found answer in knowledge base: {answer[:50]}...")
            return f"found:{answer}"
        else:
            logger.info("No answer found in knowledge base")
            return "not_found"
            
    except Exception as e:
        logger.error(f"Failed to search knowledge base: {e}", exc_info=True)
        return "not_found"


@function_tool
async def end_call(ctx: RunContext) -> str:
    """End call. If the user isn't interested, expresses general disinterest or wants to end the call"""
    import sys
    import os
    logger = logging.getLogger("phone-assistant")
    
    job_ctx = get_job_context()
    
    # If there's a job context (real call), delete the room
    if job_ctx is not None:
        logger.info(f"Ending call for room {job_ctx.room.name}")
        
        try:
            await job_ctx.api.room.delete_room(
                api.DeleteRoomRequest(
                    room=job_ctx.room.name,
                )
            )
            logger.info(f"Successfully ended call for room {job_ctx.room.name}")
        except Exception as e:
            logger.error(f"Failed to end call: {e}", exc_info=True)
    
    # Always terminate the agent program
    logger.info("User requested to end call - terminating agent program")
    print("\n" + "="*60)
    print("📞 Call Ended - User requested to end the call")
    print("👋 Thank you for using AI Salon Assistant!")
    print("="*60 + "\n")
    
    # Give a moment for the message to display
    import asyncio
    await asyncio.sleep(1)
    
    # Exit the program
    os._exit(0)  # Force exit the entire process
    
    return "ended"  # This line won't be reached, but keeps the function signature


@function_tool
async def request_help(ctx: RunContext, question: str, caller_name: str = "Unknown") -> str:
    """
    Request help from supervisor when AI doesn't know the answer.
    Waits up to 60 seconds for supervisor response.
    Plays hold music while waiting.
    
    Args:
        question: The question the caller asked that you cannot answer
        caller_name: The name of the caller asking the question
    """
    import asyncio
    from datetime import datetime, timedelta
    
    logger = logging.getLogger("phone-assistant")
    
    try:
        # Create help request in Firebase
        request_id = FirebaseService.create_help_request(
            question=question,
            caller_name=caller_name,
            caller_phone="Unknown",
            context=f"Caller asked during phone call"
        )
        
        logger.info(f"Created help request {request_id}, waiting for supervisor response...")
        
        # Wait up to 60 seconds for supervisor answer
        timeout_seconds = 60
        check_interval = 2  # Check every 2 seconds
        elapsed = 0
        
        # TODO: Play hold music here (requires audio file)
        logger.info("Playing hold music while waiting...")
        
        while elapsed < timeout_seconds:
            await asyncio.sleep(check_interval)
            elapsed += check_interval
            
            # Check if supervisor has answered
            resolved_requests = FirebaseService.get_resolved_requests()
            for req in resolved_requests:
                if req.get("id") == request_id and req.get("supervisor_answer"):
                    answer = req.get("supervisor_answer")
                    logger.info(f"Supervisor answered within {elapsed} seconds!")
                    return f"supervisor_answered:{answer}"
            
            logger.info(f"Still waiting... ({elapsed}/{timeout_seconds} seconds)")
        
        # Timeout - supervisor didn't respond in time
        logger.info(f"Timeout reached. Supervisor did not respond within {timeout_seconds} seconds")
        return "timeout:no_answer"
        
    except Exception as e:
        logger.error(f"Failed to create help request: {e}", exc_info=True)
        return "error"


@function_tool
async def check_available_slots(ctx: RunContext, date: str) -> str:
    """
    Check available appointment slots for a specific date.
    Use this when customer asks about availability.
    
    Args:
        date: Date in format YYYY-MM-DD (e.g., "2025-11-15")
    
    Returns:
        List of available time slots or message if date is closed/invalid
    """
    logger = logging.getLogger("phone-assistant")
    
    try:
        logger.info(f"Checking available slots for {date}")
        
        # Validate date format
        from datetime import datetime
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "invalid_date:Please provide date in format YYYY-MM-DD"
        
        # Check if it's in the past
        today = datetime.now().date()
        if parsed_date.date() < today:
            return "past_date:Cannot book appointments in the past"
        
        # Get available slots
        available_slots = FirebaseService.get_available_slots(date)
        
        if not available_slots:
            # Check if it's Sunday
            if parsed_date.weekday() == 6:
                return "closed:We are closed on Sundays"
            else:
                return "fully_booked:All slots are booked for this date"
        
        # Return available slots
        slots_str = ", ".join(available_slots)
        logger.info(f"Available slots on {date}: {slots_str}")
        return f"available:{slots_str}"
        
    except Exception as e:
        logger.error(f"Error checking available slots: {e}", exc_info=True)
        return "error:Unable to check availability"


@function_tool
async def book_appointment(
    ctx: RunContext,
    date: str,
    time_slot: str,
    customer_name: str,
    customer_phone: str,
    service: str = "General appointment"
) -> str:
    """
    Book an appointment for a customer.
    IMPORTANT: Always check available slots FIRST before booking.
    
    Args:
        date: Date in format YYYY-MM-DD (e.g., "2025-11-15")
        time_slot: Time in format "9:00 AM", "10:00 AM", etc.
        customer_name: Customer's full name
        customer_phone: Customer's phone number
        service: Type of service (e.g., "Haircut", "Hair Coloring", "Bridal Makeup")
    
    Returns:
        Confirmation message with appointment details or error message
    """
    logger = logging.getLogger("phone-assistant")
    
    try:
        logger.info(f"Attempting to book appointment for {customer_name} on {date} at {time_slot}")
        
        # Validate date format
        from datetime import datetime
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "error:Invalid date format. Use YYYY-MM-DD"
        
        # Check if it's in the past
        today = datetime.now().date()
        if parsed_date.date() < today:
            return "error:Cannot book appointments in the past"
        
        # Check if it's Sunday
        if parsed_date.weekday() == 6:
            return "error:We are closed on Sundays"
        
        # Check if slot is available
        if not FirebaseService.check_slot_availability(date, time_slot):
            return "error:This time slot is not available. Please choose another time"
        
        # Book the appointment
        appointment_id = FirebaseService.create_appointment(
            date_str=date,
            time_slot=time_slot,
            customer_name=customer_name,
            customer_phone=customer_phone,
            service=service
        )
        
        if appointment_id:
            logger.info(f"Successfully booked appointment {appointment_id}")
            return f"success:Appointment booked! Confirmation number: {appointment_id[:8]}. {customer_name} is scheduled for {service} on {date} at {time_slot}"
        else:
            return "error:Unable to book appointment. Slot may have just been taken"
        
    except Exception as e:
        logger.error(f"Error booking appointment: {e}", exc_info=True)
        return "error:System error while booking appointment"


@function_tool
async def cancel_appointment(ctx: RunContext, appointment_id: str, reason: str = "Customer request") -> str:
    """
    Cancel an existing appointment.
    
    Args:
        appointment_id: The appointment confirmation number
        reason: Reason for cancellation
    
    Returns:
        Confirmation of cancellation or error message
    """
    logger = logging.getLogger("phone-assistant")
    
    try:
        logger.info(f"Attempting to cancel appointment {appointment_id}")
        
        success = FirebaseService.cancel_appointment(appointment_id, reason)
        
        if success:
            return "success:Appointment cancelled successfully"
        else:
            return "error:Appointment not found or already cancelled"
        
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}", exc_info=True)
        return "error:Unable to cancel appointment"


