# Write your code here :-)
import sys

import board
import digitalio
import time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

DEBUG_PRINT = False

def print_debug(msg: str) -> None:
    if DEBUG_PRINT:
        print(msg)

while True:
    print_debug("About to turn the LED on")
    led.value = True
    time.sleep(0.1)
    print("LED on")
    led.value = False
    time.sleep(0.1)
    print_debug("About to turn the LED off")
    print("Hello world!")