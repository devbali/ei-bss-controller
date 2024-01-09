from pox.web.jsonrpc import JSONRPCHandler
from pox.core import core
import time
import threading

log = core.getLogger()

ROLL_CALL_SLEEP = 2 # seconds
DEAD_ROLL_CALL_INTERVAL = 5

class Receiver:
  def __init__ (self, id, roll_call):
    self.id = id
    self.last_rollcall = roll_call
  
  def refresh (self, roll_call):
    self.last_rollcall = roll_call


class ReceiversTracker:
  def __init__ (self):
    self.current_rollcall = 0
    self.receivers : dict[str, Receiver] = {}
    self.receivers_lock = threading.Lock()
    self.to_kill_thread = False
    thread = threading.Thread(target=self.roll_call_update, args=[])
    thread.start()
  
  def roll_call_update (self):
    while not self.to_kill_thread:
      time.sleep(ROLL_CALL_SLEEP)

      for receiver_id in set(self.receivers.keys()):
        receiver = self.receivers[receiver_id]
        if receiver.last_rollcall <= self.current_rollcall - DEAD_ROLL_CALL_INTERVAL:
          with self.receivers_lock:
            del self.receivers[receiver_id]

      print("Rollcall #", self.current_rollcall, "receivers", self.receivers)
      self.current_rollcall += 1
    
  def receiver_rollcall (self, receiver_id):
    with self.receivers_lock:
      if receiver_id not in self.receivers:
        self.receivers[receiver_id] = Receiver(receiver_id, self.current_rollcall)
      else:
        self.receivers[receiver_id].refresh(self.current_rollcall)

receivers_tracker = ReceiversTracker()

class BSSController (JSONRPCHandler):
  def __init__ (self, *args, **kwargs):
    super().__init__(*args, **kwargs)
  
  def _exec_hello (self):
    log.info("Hello JSON RPC function called")
    return {"result": "hello"}
  
  def _exec_receiver_rollcall (self, receiver_id):
    receivers_tracker.receiver_rollcall(receiver_id)
    return {"result": "registered"}
  
  @classmethod
  def shutdown(cls):
    receivers_tracker.to_kill_thread = True

