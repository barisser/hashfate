import node
import math


def hashvector(hashid):
    global lastin
    lastin=hashid
    print "input hashid: "+str(hashid)
    r=0
    v=[0]*vectorlength
    print hashid
    if hashid>-1:
        inth=int(hashid,16)
        while inth>0:
            v[r]=int(inth%elementlength)
            inth=inth/elementlength
            r=r+1
    else:
        v=[99]*vectorlength
    return v


def nodedistance(nodeavector,nodebvector):
    d=0
    if len(nodeavector)==len(nodebvector):
        a=0
        while a<len(nodeavector):
            d=d+(nodeavector[a]-nodebvector[a])*(nodeavector[a]-nodebvector[a])

            a=a+1
        #print d
        d=math.pow(float(d),0.5)
        return d
    else:
        return -1


