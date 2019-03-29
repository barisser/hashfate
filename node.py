import hashlib
import time
import math
import random
import socket
import sys
from thread import *
import threading
from bitcoin import *
import requests
from time import mktime
from datetime import datetime
import ast

elementlength=1000 #max number per array element, not number of elements
vectorlength=32  #number of elements per vector
neighbormax=10

max_neighbors=10
timelistening=100

active=True

def now():
    a=datetime.fromtimestamp(time.time())
    return a.strftime("%H:%M:%S %Y-%m-%d")

def getmyip():
    a=requests.get('http://checkip.dyndns.org')
    a=a.content
    b=a[76:89]
    return b
   
homeip=getmyip()


def hashvector(hashid):
    global lastin
    lastin=hashid
    print "input hashid: "+str(hashid)
    r=0
    v=[0]*vectorlength
    print hashid
    if hashid>-1:
        inth=int(hashid, 16)
        while inth>0:
            v[r]=int(inth%elementlength)
            inth=inth/elementlength
            r=r+1
    else:
        v=[99]*vectorlength
    return v


def nodedistance(nodeavector, nodebvector):
    d=0
    if len(nodeavector)==len(nodebvector):
        a=0
        while a<len(nodeavector):
            d=d+(nodeavector[a]-nodebvector[a])*(nodeavector[a]-nodebvector[a])

            a=a+1
        #print d
        d=math.pow(float(d), 0.5)
        return d
    else:
        return -1


class node:

    def __init__(self, listeningport):
        timestamp=time.time()
        self.listeningport=listeningport
        self.timestamp=timestamp
        self.hashid=hashlib.sha256(str(timestamp+random.random()*1000000)).hexdigest()
        inth=int(self.hashid, 16)
        self.hashvector=[0]*vectorlength
        self.neighbors=[[-1, '', 8888]]*max_neighbors   #list of 2 element arrays of HASHID, IP ADDRESS, AND THEIR PORT
        self.ip=homeip
        self.logs=''
        
        r=0
        while inth>0:
            self.hashvector[r]=int(inth%elementlength)
            inth=inth/elementlength
            r=r+1

        self.sockets=[0]*(max_neighbors+1) #first socket should be SERVER socket

        #listening socket
        self.sockets[0]=self.create_socket('', self.listeningport)
  

    def create_socket(self, HOST, PORT):    #RETURNS SOCKET OBJECT
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'Socket created'
        self.logs=self.logs+'\n\nSocket Created '+str(now())

        #Bind socket to local host and port
        try:
            s.bind((HOST, PORT))
            #self.sockets[socketn]=s
            return s
        except socket.error , msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]


    def closest_neighbor(self, newneighbordata):
        nd=[]
        for y in newneighbordata:
            if y[0]>-1:
                nd.append(nodedistance(hashvector(y[0]), self.hashvector))
        a=0
        closest=9999999999999999
        closestid=-1
        while a<len(nd):
            if nd[a]<closest:
                closest=nd[a]
                closestid=a
            a=a+1

        return closestid

    def farthest_neighbor(self, neighbordata):
        global nd
        nd=[]
        for y in neighbordata:
            if y[0]>-1:
                nd.append(nodedistance(hashvector(y[0]), self.hashvector))
            else:
                nd.append(999999)
        a=0
        farthest=0
        farthestid=-1
        while a<len(nd):
            if nd[a]>=farthest:
                farthest=nd[a]
                farthestid=a
            a=a+1

        return farthestid

    def adjust_neighbors(self, newneighbordata):
        print "ADJUSTING NEIGHBORS"
        newneighbordata=newneighbordata['body']
        ok=True
        while ok:
            a=self.closest_neighbor(newneighbordata)
            b=self.farthest_neighbor(self.neighbors)
            
            nda=nodedistance(hashvector(newneighbordata[0][0]), self.hashvector)
            ndb=nodedistance(hashvector(self.neighbors[b][0]), self.hashvector)
            if nda>=ndb:
                ok=False
            else:
                self.neighbors[b]=newneighbordata[a]
                ok=False
                self.logs=self.logs+"\nI changed my neighbors"
            

    def neighbor_info_message(self):
        a={}
        a['my_hashid']=self.hashid
        a['header']='neighbors'
        a['body']=[]
        for x in self.neighbors:
            if x[0]>-1:
                a['body'].append(x)
        return a

    def client_thread(self, connection, actionlogic, *args):  #Whatever this node does as a SERVER
        #while True:
        global data, reply
        data=connection.recv(1024)
        print str(self.hashid)+" Reporting"
        print ''
        print "SERVER RECEIVING DATA: "
        print data
        print ''
        self.logs=self.logs+'\n\nI heard a message at '+str(now())+':\n'+str(data)+'n'

        if isinstance(data, str):
            data=ast.literal_eval(data)
        global data
        print "DATA HERE: "+str(data)
        reply=actionlogic(data)
         
        
        print "SERVER REPLYING with "
        print ''
        print reply
        print ''
        self.logs=self.logs+'\n\nAt '+str(now())+ ' I replied with: \n'+str(reply)
        connection.sendall(reply)
        connection.close()
        #print "here\n"

    def message(self, host, port, message): 
        
        remote_ip=socket.gethostbyname(host)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((remote_ip , port))
            #message = "GET / HTTP/1.1\r\n\r\n"
        s.sendall(message)
        print "MESSAGE SENT"
        print ''
        print message
        print ''
        self.logs=self.logs+'\n\nI initiated a message saying: \n'+str(message)
        reply = s.recv(4096)
             
        print "REPLY RECEIVED:"
        print ''
        print reply
        print ''
        self.logs=self.logs+'\n\nWhat I heard in reply was:     '+str(now())+'\n'+str(reply)

    def serve(self):
        j=0
        while active:
            j=j+1
            
            connection, address=self.sockets[0].accept()
            print j
            
            k=threading.Thread(target=self.client_thread, args=(connection, self.reply,))
            k.daemon=True
            k.start()
            #self.client_thread(connection)
            print "Connected with "+str(address[0])+":"+str(address[1])
            print ''
            self.logs=self.logs+'\nThis node contacted me: '+str(address[0])+':'+str(address[1])
            
    def chat(self):
        for x in self.neighbors:
            if x[0]>-1:
                #m="my name is: "+str(self.hashid)
                #m={}
                #m['hashid']=str(self.hashid)
                m=str(self.neighbor_info_message())
                h=x[1]
                p=x[2]
                #a=threading.Thread(target=self.message,args=(h,p,m,))
                self.message(h, p, m)
        

    def online(self):
        
        #SETUP A REPLYING SERVER
        self.sockets[0].listen(max_neighbors)
        print 'Socket now listening'
        self.logs=self.logs+'\n\nI started listening\n'
        active=True
        
        g=threading.Thread(target=self.serve)
        g.daemon=True
        g.start()
        print "I am online"
        self.logs=self.logs+'\n\nI went online\n'

        r=threading.Thread(target=self.chat)
                           
        r.daemon=True
        r.start()

    def log(self):
        print self.logs

    def reply(self, args):

        self.adjust_neighbors(args)
        t=time.time()
        interval=5
        ok=True
        while ok:
            if time.time()>=t+interval:
                ok=False
                return str(self.neighbor_info_message())
            
        



p=int(random.random()*1000)+8000
a=node(p)
b=node(p+1)
c=node(p+2)

a.neighbors[0]=[b.hashid, homeip, b.listeningport]
b.neighbors[0]=[a.hashid, homeip, a.listeningport]
c.neighbors[0]=[b.hashid, homeip, b.listeningport]
a.online()
b.online()
c.online()


