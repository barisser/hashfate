import datetime
import requests
import socket
import random
import sys

def now():
    a=datetime.fromtimestamp(time.time())
    return a.strftime("%H:%M:%S %Y-%m-%d")

def getmyip():
    a=requests.get('http://checkip.dyndns.org')
    a=a.content
    b=a[76:89]
    return b
