class Event(object):
    
    def __init__(self, med, fecha, user,rep,when):
        self.med = med
        self.fecha = fecha
        self.veces=0
        self.user=user
        self.rep=rep
        self.when=when
        self.activo=True
        
    def IncrementarVeces(self):
        self.veces += 1

    def NoActivo():
        self.activo=False

    def __eq__(self, other):
         return (
          self.__class__ == other.__class__ and
             self.med==other.med and self.fecha==other.fecha and self.user==other.user
         )
         
    def __str__(self):
        if(self.rep):
            return 'Evento :'+self.med+',,'+str(self.veces)+','+self.user+','+str(self.rep)+','+self.when+','+str(self.activo)
        else:
            return 'Evento :'+self.med+','+str(self.fecha)+','+str(self.veces)+','+self.user+','+str(self.rep)+',,'+str(self.activo)
