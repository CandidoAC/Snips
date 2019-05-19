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
        