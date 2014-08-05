import datetime
import requests
import socket
import random
import sys
import time

def now():
    a=datetime.fromtimestamp(time.time())
    return a.strftime("%H:%M:%S %Y-%m-%d")

def getmyip():
    a=requests.get('http://checkip.dyndns.org')
    a=a.content
    b=a[76:89]
    return b



class node:

    def __init__(self, listeningport):
        timestamp=time.time()
        self.listeningport=listeningport
        self.timestamp=timestamp
        self.hashid=hashlib.sha256(str(timestamp+random.random()*1000000)).hexdigest()
        inth=int(self.hashid,16)
        self.hashvector=[0]*vectorlength
        self.neighbors=[[-1,'',8888]]*max_neighbors   #list of 2 element arrays of HASHID, IP ADDRESS, AND THEIR PORT
        self.ip=homeip
        self.logs=''
        
        r=0
        while inth>0:
            self.hashvector[r]=int(inth%elementlength)
            inth=inth/elementlength
            r=r+1
        self.sockets=[0]*(max_neighbors+1) #first socket should be SERVER socket

        #listening socket
        self.sockets[0]=self.create_socket('',self.listeningport)
        #self.create_socket('',listeningport,0)
  
