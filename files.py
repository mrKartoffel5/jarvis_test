import os
from playsound import playsound

def raspred(what,name:str):
    dir=os.path.dirname(os.path.realpath(f'{name}'))
    os.open(dir,os.O_RDWR)
