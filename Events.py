from Evento import Event
from datetime import datetime

class Snips(object):
    
    Levent=[]
    Luser=[]

    def __init__(self):
        self.Levent = []
        self.Luser = []
        self.usr='default'
        self.Levent.append(self.usr)

    def addEvent(self,event):
    	enc=False
    	if(not (any(x for x in self.Levent if x.__eq__(event)))):
    		self.Levent.append(event)

    def addUser(self,user):
        enc=False
        if(not (any(x for x in self.Luser if x.__eq__(user)))):
            self.Levent.append(user)

    def existUser(self,user):
        enc=False
        if(any(x for x in self.Luser if x.__eq__(user))):
            enc=True    
        return enc

    def Incrementar(self,event):
    	for x in range(len(Snips.Levent)):
	    	print("Nombre:"+Recordatorio.med+",fecha:"+str(Recordatorio.fecha)+",veces:"+str(Recordatorio.veces))
	    	if (event==Snips.Levent[x]):
	        	Snips.Levent[x].IncrementarVeces()
        