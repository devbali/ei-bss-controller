import requests

def roll_call(receiver_id, id = 1):
  r = requests.post("http://0.0.0.0:8080", json={
    "id": id,
      "jsonrpc": "2.0",
      "method": "receiver_rollcall",
      "params": {
          "receiver_id": str(receiver_id)
      }
  })
  return r.json()

res = roll_call(20)
assert "result" in res and res["result"] == "registered"
print("Got back result")
