import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# ALL CONSTANTS SETUP HERE
# CONSTANTS 
PYTHON_SERVER_IP = get_local_ip()
PYTHON_SERVER_PORT = 9999
MICROPYTHON_IP = 180.11
PORT = 8888
MAX_CAR = 5
TOTAL_SLOTS = 5
SSID = "Ming's"
PASSWORD = "88888888"

# PIN SETUP
# COUNTER PIN SETUP
LCD_ENTRY_PIN 		= 1
LCD_EXIT_PIN		= 0

AIR_ENTRY_PIN       = 22
AIR_EXIT_PIN        = 2

SERVO_ENTRY_PIN     = 3
SERVO_EXIT_PIN      = 4

I2C_SCL_ENTRY_PIN   = 27
I2C_SCL_EXIT_PIN    = 1

I2C_SDA_ENTRY_PIN   = 26
I2C_SDA_EXIT_PIN    = 0

# ULTRASONIC SETUP
TRIG_PIN_1 = 19
ECHO_PIN_1 = 21

TRIG_PIN_2 = 18
ECHO_PIN_2 = 16

TRIG_PIN_3 = 13
ECHO_PIN_3 = 15

TRIG_PIN_4 = 12
ECHO_PIN_4 = 10

TRIG_PIN_5 = 9
ECHO_PIN_5 = 7

# ULTRASONIC CONFIGS
INITIAL_STATUS      = [0, 0, 0, 0, 0]
DISTANCE_THRESHOLD  = 10.2 # in cm
STABLE_LIMIT        = 5

# LED SETUP
LED_PIN_1 = 20
LED_PIN_2 = 17
LED_PIN_3 = 14
LED_PIN_4 = 11
LED_PIN_5 = 8

LED_ON  = 1
LED_OFF = 0 

# DEBUG SETUP
def Debug(msg):
    print(f"[DEBUGGER]: {msg}")


