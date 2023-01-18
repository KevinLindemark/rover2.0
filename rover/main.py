import network
import espnow
import ubinascii
from machine import Pin, PWM, unique_id
from time import sleep
import _thread
from hcr04 import HCSR04
buzzer_pin = Pin(13, Pin.OUT)
buzz = PWM(buzzer_pin, freq=500, duty=0)
speed = 1023
stop = 0

ultrasonic = HCSR04(5, 18)

L_IN1 = PWM(Pin(32),freq=50, duty=0)
L_IN2 = PWM(Pin(33),freq=50, duty=0)
L_IN3 = PWM(Pin(26),freq=50, duty=0)
L_IN4 = PWM(Pin(25),freq=50, duty=0)

R_IN1 = PWM(Pin(17),freq=50, duty=0)
R_IN2 = PWM(Pin(16),freq=50, duty=0)
R_IN3 = PWM(Pin(19),freq=50, duty=0)
R_IN4 = PWM(Pin(22),freq=50, duty=0)

UP_MAX = 130
DOWN_MAX = 40
RIGHT_MAX = 120
LEFT_MAX = 40
GRAB_CLOSE_MAX = 30
GRAB_DROP_MAX = 90
FORWARD_MIN = 40
FORWARD_MAX = 120

class ServoControl:
    def __init__(self, rotate, forward, grab, updown):
        self.rotate = rotate
        self.forward = forward
        self.grab = grab
        self.updown = updown
        self.servo_horizontal = PWM(Pin(12), duty = 0, freq=50)
        self.servo_vertical = PWM(Pin(27), duty = 0, freq=50)
        self.servo_forward_backward = PWM(Pin(23), duty = 0, freq=50)
        self.servo_grab = PWM(Pin(14), duty = 0, freq=50)
       
    # function to set value of rotate
    def set_left_right(self, servo_rotate_val):
        self.rotate +=servo_rotate_val
        print(f"servo_rotate_val setter method called with val {servo_rotate_val}")
        if self.rotate <= LEFT_MAX:
            self.rotate = LEFT_MAX
            self.servo_horizontal.duty(LEFT_MAX)
            print("LEFT_MAX")
        else:
            self.servo_horizontal.duty(self.rotate)
        if self.rotate >= RIGHT_MAX:
            self.rotate = RIGHT_MAX
            self.servo_horizontal.duty(RIGHT_MAX)
            print("RIGHT_MAX")
        else:
            self.servo_horizontal.duty(self.rotate) 
    # function to set value of forward
    def set_forward_backward(self, servo_forward_backward_val):
        self.forward += servo_forward_backward_val
        if self.forward >= FORWARD_MAX:
            self.forward = FORWARD_MAX
            self.servo_forward_backward.duty(FORWARD_MAX)
        else:
            self.servo_forward_backward.duty(self.forward)
        if self.forward <= FORWARD_MIN:
            self.forward = FORWARD_MIN
            self.servo_forward_backward.duty(FORWARD_MIN)
        else:
            self.servo_forward_backward.duty(self.forward)
        print(servo_forward_backward_val)
        print(f"servo_forward_backward_val setter method called with val {servo_forward_backward_val} and duty is{self.servo_forward_backward.duty()}")
    # function to set value of grab
    def set_servo_grab(self, servo_grab_val):
        self.grab = servo_grab_val
        print(f"servo_grab setter method called with val {servo_grab_val}")
        self.servo_grab.duty(self.grab)
    # function to set value of grab
    def set_up_down(self, servo_up_down_val):
        self.updown += servo_up_down_val
        if self.updown >= UP_MAX:
            self.updown = UP_MAX
            self.servo_vertical.duty(UP_MAX)
        else:
            self.servo_vertical.duty(self.updown)
        if self.updown <= DOWN_MAX:
            self.updown = DOWN_MAX
            self.servo_vertical.duty(DOWN_MAX)
        else:
            self.servo_vertical.duty(self.updown)
                        
        print(f"servo_up_down setter method called with val {servo_up_down_val}")   
        

control = ServoControl(70, 90, 50, 85)

def set_all_speed(x):
   #print("Adjusting speed")
   R_IN1.duty(x)
   R_IN2.duty(x)
   R_IN3.duty(x)
   R_IN4.duty(x)
   
   L_IN1.duty(x)
   L_IN2.duty(x)
   L_IN3.duty(x)
   L_IN4.duty(x)
   
def motor_R_backwards():
    R_IN1.duty(stop)
    R_IN2.duty(speed)
    R_IN3.duty(stop)
    R_IN4.duty(speed)
   
def motor_R_forward():
    R_IN1.duty(speed)
    R_IN2.duty(stop)
    R_IN3.duty(speed)
    R_IN4.duty(stop)
   
def motor_L_backwards():
    L_IN1.duty(stop)
    L_IN2.duty(speed)
    L_IN3.duty(stop)
    L_IN4.duty(speed)

def motor_L_forward():
    L_IN1.duty(speed)
    L_IN2.duty(stop)
    L_IN3.duty(speed)
    L_IN4.duty(stop)
   
set_all_speed(0)

print("MAC ADDRESS OF THIS DEVICE IS:",ubinascii.hexlify(unique_id(), ":").decode().upper())
# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()   # Because ESP8266 auto-connects to last Access Point

e = espnow.ESPNow()
e.active(True)

peer = b'\x40\x91\x51\x9b\x26\x5c'   # MAC address of peer's wifi interface
e.add_peer(peer)

def convert_to_list(msg):
    data_string = msg.decode('utf-8')
    data_list = data_string.split(",")
    for i in range(0, len(data_list)):
        data_list[i] = int(data_list[i])
    return data_list


state = {"autopilot":"off", "btn1_status":None,  "btn1_presses":0, "joy1_btn_presses":0, "joy1_btn_state":True, "grab_button":0, "grab_toggle":0}

def main():

    # Servo duty ranges
    print("starting loop")
    while True:
        #sleep(0.1)
        host, msg = e.recv()
        if msg:
            try:
                # msg == None if timeout in recv()
                #print(msg)
                """{btn1.value()},{joy1_btn_pin.value()},{j1_vert.read()},{j1_horz.read()},
                   {btn2.value()},{joy2_btn_pin.value()},{j2_vert.read()},{j2_horz.read()}"""
                data_list = convert_to_list(msg)
                #print(data_list[2]-2048, data_list[3]-2048)
                #print(data_list)
                if data_list[1] == False and state["joy1_btn_state"] == True:
                    print(f"joy1_btn_pin pressed {state["joy1_btn_presses"]} times, and button status is {state["joy1_btn_state"]}")
                    buzz.duty(1000)
                    sleep(0.2)
                    state["joy1_btn_presses"] +=1
                else:
                    buzz.duty(0)    
                state["joy1_btn_state"] = data_list[1]
                if data_list[0] == False and state["btn1_status"] == True:
                    print(f"btn1 pressed {state["btn1_presses"]} times, and button status is {state["btn1_status"]}")
                    state["btn1_status"] +=1
                    state["autopilot"] = "on"   
                if state["autopilot"] == "on":
                    print("auto thread startet")
                    _thread.start_new_thread(auto_pilot, ())
                    _thread.exit()           
                state["btn1_status"] = data_list[0]
                
                if data_list[2] > 2200:
                    motor_R_forward()
                    motor_L_forward()
                    print("UP")       
                elif data_list[2] < 1000:
                    motor_R_backwards()
                    motor_L_backwards()
                    print("DOWN")
                elif data_list[3] < 1000:
                    motor_L_forward()
                    motor_R_backwards()
                    print("LEFT")
                elif data_list[3] > 2200:
                    motor_L_backwards()
                    motor_R_forward()
                    print("RIGHT")        
                else:
                    set_all_speed(0)

                if data_list[6] > 2200:
                    control.set_forward_backward(3)
                    if control.servo_forward_backward.duty() == 120:
                        try:
                            print("ARM DOWN!________________________!")
                            control.set_up_down(-10)
                        except:
                            control.servo_vertical = PWM(Pin(27), duty = 0, freq=50)
                    else:
                        control.servo_vertical.deinit()
                elif data_list[6] < 1000:
                    #control.set_up_down(-3)
                    control.set_forward_backward(-3)
                    if control.servo_forward_backward.duty() < 80:
                        try:
                            print("ARM UP!________________________!")
                            control.set_up_down(10)
                        except:
                            control.servo_vertical = PWM(Pin(27), duty = 0, freq=50)
                    else:
                        control.servo_vertical.deinit()
                elif data_list[7] < 1000:
                    control.set_left_right(3)
                    print("LEFT") 
                elif data_list[7] > 2200:
                    control.set_left_right(-3)
                    print("RIGHT")
                elif data_list[5] == 0 and state["grab_button"]:
                    if state["grab_toggle"]:
                        control.set_servo_grab(GRAB_DROP_MAX)
                        state["grab_toggle"]=0
                    else:
                        control.set_servo_grab(GRAB_CLOSE_MAX)
                        state["grab_toggle"]=1
                state["grab_button"] = data_list[5]  
            except KeyboardInterrupt:
                print("Ctrl C pressed - Exit program")
                control.servo_horizontal.deinit()
                control.servo_vertical.deinit()
                control.servo_forward_backward.deinit()
                control.servo_grab.deinit()
                
def autopilot_controls():
            """ run threadded to have faster toogle between autopilot and manual mode"""
            while True:
                if state["autopilot"] == "off":
                    _thread.exit()
                servo.duty(50)
                left = ultrasonic.distance_cm()
                sleep(0.01)
                print("right distance", left)
                sleep(1)
                servo.duty(65)
                midt = ultrasonic.distance_cm()
                sleep(0.01)
                print("midt distance", midt)
                sleep(1)
                servo.duty(85)
                right = ultrasonic.distance_cm()
                sleep(0.01)
                print("left distance", right)
                sleep(1)
                if midt < 10:
                    motor_R_backwards()
                    motor_L_backwards()
                    sleep(0.1)
                    motor_L_forward()
                    motor_R_backwards()
                    sleep(0.3)
                    set_all_speed(0)
                elif  left > right:
                    motor_R_backwards()
                    motor_L_forward()
                    sleep(0.1)
                    motor_L_forward()
                    motor_R_forward()
                    sleep(0.3)
                    set_all_speed(0)
                elif left < right:
                    motor_L_backwards()
                    motor_R_forward()
                    sleep(0.1)
                    motor_L_forward()
                    motor_R_forward()
                    sleep(0.3)
                    set_all_speed(0)
                else:
                    set_all_speed(0)

def auto_pilot():
    print("starting auto loop")
    _thread.start_new_thread(autopilot_controls, ())
    state["btn1_status"] = False
    while True:
        host, msg = e.recv()
        if msg:             # msg == None if timeout in recv()
            data_list = convert_to_list(msg)
            if data_list[0] == False and state["btn1_status"] == True:
                print(f" auto btn1 pressed {state["btn1_presses"]} times, and button status is {state["btn1_status"]}")
                state["btn1_presses"] +=1
                print(data_list)
                state["autopilot"] = "off"
            state["btn1_status"] = data_list[0]
            print("autopilote state :", state["autopilot"])
            if state["autopilot"] == "off":
                _thread.start_new_thread(main, ())
                _thread.exit()
            
_thread.start_new_thread(main, ())