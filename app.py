from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import RPi.GPIO as GPIO
import time
import signal
import sys

def cleanup_gpio(signal=None, frame=None):
    print(f"Cleaning up GPIO... Signal: {signal}, Frame: {frame}")
    try:
        pwm.stop()
    except Exception as e:
        print(f"Error stopping PWM: {e}")
    finally:
        GPIO.cleanup()
    print("Exiting application.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_gpio)
signal.signal(signal.SIGTERM, cleanup_gpio)

app = Flask(__name__)
socketio = SocketIO(app)

SERVO_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

current_angle = 0

def set_servo_angle(angle):
    angle = max(-45, min(45, angle))
    duty_cycle = 7.5 + (angle * (5.0/90.0))
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.1)
    return angle

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@socketio.on('message')
def handle_message(data):
    global current_angle
    print(f"Received WebSocket message: {data}")
    key_type = data.get('type', '')
    key = data.get('key', '')

    if key_type == 'keydown':
        if key == "ArrowRight":
            current_angle = 45  # move to +45 degrees
            current_angle = set_servo_angle(current_angle)
        elif key == "ArrowLeft":
            current_angle = -45 # move to -45 degrees
            current_angle = set_servo_angle(current_angle)
    elif key_type == 'keyup':
        # On key release, return to 0 degrees
        if key == "ArrowLeft" or key == "ArrowRight":
            current_angle = 0
            current_angle = set_servo_angle(current_angle)
            
if __name__ == '__main__':
    print("Starting Flask app...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
