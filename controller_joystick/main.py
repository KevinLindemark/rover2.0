import network
import espnow
import ubinascii
from machine import ADC, Pin, unique_id
from time import sleep

print("MAC ADDRESS OF THIS DEVICE IS:", ubinascii.hexlify(unique_id()).decode())

sta = network.WLAN(network.STA_IF)
sta.active(True)
e = espnow.ESPNow()
e.active(True)

peer = b'\x40\x91\x51\xAB\x56\x8C'
e.add_peer(peer)

red_led = Pin(25, Pin.OUT)
green_led = Pin(23, Pin.OUT)

btn1 = Pin(13, Pin.IN, Pin.PULL_DOWN)

joy1_btn_pin = Pin(36, Pin.IN)
j1_vert_pin = Pin(34, Pin.IN)
j1_horz_pin = Pin(39, Pin.IN)

j1_vert = ADC(j1_vert_pin)
j1_vert.atten(ADC.ATTN_11DB)
j1_vert.width(ADC.WIDTH_12BIT)

j1_horz = ADC(j1_horz_pin)
j1_horz.atten(ADC.ATTN_11DB)
j1_horz.width(ADC.WIDTH_12BIT)

btn2 = Pin(15, Pin.IN, Pin.PULL_DOWN)
joy2_btn_pin = Pin(33, Pin.IN)
j2_vert_pin = Pin(35, Pin.IN)
j2_horz_pin = Pin(32, Pin.IN)

j2_vert = ADC(j2_vert_pin)
j2_vert.atten(ADC.ATTN_11DB)
j2_vert.width(ADC.WIDTH_12BIT)

j2_horz = ADC(j2_horz_pin)
j2_horz.atten(ADC.ATTN_11DB)
j2_horz.width(ADC.WIDTH_12BIT)

while True:
    values = f"""{btn1.value()},{joy1_btn_pin.value()},{j1_vert.read()},{j1_horz.read()},
                 {btn2.value()},{joy2_btn_pin.value()},{j2_vert.read()},{j2_horz.read()}"""
    e.send(peer, values)
    print("BTN1", btn1.value(), "j1BTN", joy1_btn_pin.value(), "j1_vert", j1_vert.read(), "j1_horz", j1_horz.read())
    print("BTN2", btn2.value(), "j2BTN", joy2_btn_pin.value(), "j2_vert", j2_vert.read(), "j2_horz", j2_horz.read())
    if joy1_btn_pin():
        red_led.value(1)
    else:
        red_led.value(0)
    if joy2_btn_pin():
        green_led.value(1)
    else:
        green_led.value(0)
        
