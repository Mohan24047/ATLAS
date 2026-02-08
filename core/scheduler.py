import time
import threading
import datetime
from memory.memory_manager import memory


class Scheduler:
    def __init__(self, notification_callback=None):
        self.running = False
        self.thread = None
        self.notification_callback = notification_callback
        self.active_alerts = {}
        self.lock = threading.Lock()
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[Scheduler] Started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def confirm_all(self):
        """Confirm and complete all active alerts."""
        with self.lock:
            if not self.active_alerts:
                return False
            
            for rid in list(self.active_alerts.keys()):
                memory.complete_reminder(rid)
                del self.active_alerts[rid]
            return True

    def _loop(self):
        while self.running:
            try:
                self._check_reminders()
                self._process_active_alerts()
            except Exception as e:
                print(f"[Scheduler Error] {e}")
            time.sleep(5)

    def _check_reminders(self):
        try:
            pending = memory.list_pending_reminders()
            now = datetime.datetime.now()
            
            with self.lock:
                for r in pending:
                    if r['id'] in self.active_alerts:
                        continue
                        
                    due = datetime.datetime.fromisoformat(r['due_at'])
                    if now >= due:
                        self.active_alerts[r['id']] = {
                            'message': r['message'],
                            'last_announced': 0 
                        }
        except Exception as e:
            print(f"[Scheduler check error] {e}")

    def _process_active_alerts(self):
        now_ts = time.time()
        
        with self.lock:
            for rid, alert in self.active_alerts.items():
                if now_ts - alert['last_announced'] > 45:
                    msg = f"Reminder: {alert['message']}. Please confirm."
                    print(f"\n[ALERT] {msg}")
                    
                    if self.notification_callback:
                        self.notification_callback(msg)
                    
                    alert['last_announced'] = now_ts
