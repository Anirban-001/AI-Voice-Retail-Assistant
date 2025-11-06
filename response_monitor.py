"""
Background monitoring service for late supervisor responses
Keeps terminal open and displays text notifications when supervisor answers
"""
import time
import asyncio
from datetime import datetime
from firebase_service import FirebaseService
from typing import Set

class ResponseMonitor:
    """Monitors for late supervisor responses after calls end"""
    
    def __init__(self):
        self.monitored_requests: Set[str] = set()
        self.running = True
    
    def add_request(self, request_id: str, caller_name: str, question: str):
        """Add a request to monitor for late responses"""
        self.monitored_requests.add(request_id)
        print(f"\n📱 [MONITORING] Watching for supervisor response to: '{question}'")
        print(f"   For caller: {caller_name}")
        print(f"   Request ID: {request_id}")
    
    async def monitor_loop(self):
        """Continuously check for late supervisor responses"""
        print("\n" + "="*70)
        print("📡 RESPONSE MONITOR ACTIVE")
        print("="*70)
        print("Monitoring for late supervisor responses...")
        print("Press Ctrl+C to stop monitoring\n")
        
        check_interval = 5  # Check every 5 seconds
        
        while self.running:
            try:
                await asyncio.sleep(check_interval)
                
                if not self.monitored_requests:
                    continue
                
                # Check resolved requests
                resolved = FirebaseService.get_resolved_requests()
                
                for req in resolved:
                    req_id = req.get("id")
                    if req_id in self.monitored_requests:
                        # Found a late response!
                        self._display_late_response(req)
                        self.monitored_requests.remove(req_id)
                        
            except KeyboardInterrupt:
                print("\n\n✋ Stopping monitor...")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
    
    def _display_late_response(self, request):
        """Display a notification for a late supervisor response"""
        print("\n" + "="*70)
        print("📨 LATE SUPERVISOR RESPONSE RECEIVED!")
        print("="*70)
        print(f"🕐 Time: {datetime.now().strftime('%I:%M:%S %p')}")
        print(f"👤 Caller: {request.get('caller_name')}")
        print(f"❓ Question: {request.get('question')}")
        print(f"💡 Answer: {request.get('supervisor_answer')}")
        print(f"🧑‍💼 Answered by: {request.get('supervisor_name', 'Supervisor')}")
        print("="*70)
        print("\n📱 TEXT MESSAGE SENT TO CALLER:")
        print(f"   Hi {request.get('caller_name')}, thanks for your patience!")
        print(f"   You asked: '{request.get('question')}'")
        print(f"   Answer: {request.get('supervisor_answer')}")
        print("="*70 + "\n")


# Global monitor instance
monitor = ResponseMonitor()


async def start_monitoring():
    """Start the monitoring service"""
    await monitor.monitor_loop()


if __name__ == "__main__":
    # Run monitor as standalone service
    print("\n🚀 Starting Response Monitor Service...")
    asyncio.run(start_monitoring())
