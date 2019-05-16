class Event(object):
    
    def __init__(self, med, fecha, user):
        self.med = med
        self.fecha = fecha
        self.veces=0
        self.user=user

    def setNextDate(self,date):
        self.fecha=date
        
    def IncrementarVeces(self):
        self.veces += 1

    def __eq__(self, other):
         return (
          self.__class__ == other.__class__ and
             self.med==other.med and self.fecha==other.fecha and self.user==other.user
         )