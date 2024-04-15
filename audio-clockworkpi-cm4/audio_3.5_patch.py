import os
import time

def init_gpio():
    os.popen("gpio mode 11 out")
    os.popen("gpio mode 10 in")

def check_3_5():
    tmp = os.popen("gpio read 10").readline().strip("\n")
    return tmp


def enable_speaker_gpio():
    os.popen("gpio write 11 1")

def disable_speaker_gpio():
    os.popen("gpio write 11 0")

init_gpio()

while True:
    tmp =  check_3_5()
    if tmp == "0":
        enable_speaker_gpio()
    elif tmp == "1":
        disable_speaker_gpio()
    
    time.sleep(1)




