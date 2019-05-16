from Evento import Event
from datetime import datetime

class Snips(object):
    
    Levent=[]
    def __init__(self):
        self.Levent = []

    def addEvent(self,event):
    	enc=False
    	if(not (any(x for x in self.Levent if x.__eq__(event)))):
    		self.Levent.append(event)
        
    def toString(self):
    	for x in range(len(self.Levent)): 
    		print(self.Levent[x].med+","+self.Levent[x].fecha.strftime("%Y-%m-%d %H:%M:%S")+","+str(self.Levent[x].veces)+","+self.Levent[x].user, end=" ")