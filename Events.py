from Evento import Event
from datetime import datetime

class Snips(object):
    
    Levent=[]
    def __init__(self):
        self.Levent = []
        self.usr='default'

    def addEvent(self,event):
    	enc=False
    	if(not (any(x for x in self.Levent if x.__eq__(event)))):
    		self.Levent.append(event)

    def Incrementar(self,event):
    	for x in range(len(Snips.Levent)):
	    	print("Nombre:"+Recordatorio.med+",fecha:"+str(Recordatorio.fecha)+",veces:"+str(Recordatorio.veces))
	    	if (event==Snips.Levent[x]):
	        	Snips.Levent[x].IncrementarVeces()
        