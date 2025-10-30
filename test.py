import network
import socket
import ujson

# Connect Wi-Fi (skip this if already connected)
# sta = network.WLAN(network.STA_IF)
# sta.active(True)
# sta.connect('YOUR_WIFI_SSID', 'YOUR_WIFI_PASSWORD')

# Listen on port 80
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("Listening on", addr)

def send_response(client, status=200, body="OK", content_type="text/plain"):
    """Send an HTTP response with proper CORS headers"""
    headers = (
        f"HTTP/1.1 {status} OK\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        "Access-Control-Allow-Headers: Content-Type\r\n"
        f"Content-Type: {content_type}\r\n"
        "Connection: close\r\n\r\n"
    )
    client.send(headers)
    if body:
        client.send(body)

while True:
    client, addr = s.accept()
    print("Client connected from", addr)
    req = client.recv(1024).decode()
    print("Request:", req)

    # Respond to CORS preflight OPTIONS
    if "OPTIONS" in req:
        send_response(client, status=200)
        client.close()
        continue

    # Handle POST /gate
    if "POST /gate" in req:
        try:
            # Extract JSON from request body
            body = req.split("\r\n\r\n", 1)[1]
            data = ujson.loads(body)
            gate = data.get("gate")
            action = data.get("action")
            print(f"Received command: {action} {gate} gate")

            # TODO: control your gate here (GPIO, etc.)

            response = ujson.dumps({"status": "ok", "gate": gate, "action": action})
            send_response(client, status=200, body=response, content_type="application/json")

        except Exception as e:
            print("Error:", e)
            send_response(client, status=400, body="Invalid request")

    else:
        send_response(client, status=404, body="Not Found")

    client.close()
