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
                if(' 'in self.when.strip()):##Se hace el strip para borrar el blanco a la derecha en las comidas
                    Repeticion=self.when[self.when.index(' ')+1:]
                    veces=int(self.when[:self.when.index(' ')])
                    #print(Repeticion)
                    return 'Evento repetitivo para ' +self.user+' tomar '+self.med+' cada '+str(veces)+' '+Repeticion+' empezando el '+str(self.fecha)
                else:
                    Repeticion=self.when
                    return 'Evento repetitivo para ' +self.user+' tomar '+self.med+' cada '+Repeticion
        else:
            return 'Evento para '+self.user+' tomar '+self.med+' el '+str(self.fecha)
