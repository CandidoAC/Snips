class Evento(object):
    
    def __init__(self, med, fecha, usuario, rep, cuando):
        self.med = med
        self.fecha = fecha
        self.veces=0
        self.usuario=usuario
        self.rep=rep
        self.cuando=cuando
        self.activo=True
        
    def IncrementarVeces(self):
        self.veces += 1

    def NoActivo(self):
        self.activo=

    def __eq__(self, other):
         return (
                 self.__class__ == other.__class__ and
                 self.med == other.med and self.fecha == other.fecha and self.usuario == other.user
         )
         
    def __str__(self):
        if(self.rep):
                if(' 'in self.cuando.strip()):##Se hace el strip para borrar el blanco a la derecha en las comidas
                    Repeticion= self.cuando[self.cuando.index(' ') + 1:]
                    veces=int(self.cuando[:self.cuando.index(' ')])
                    #print(Repeticion)
                    return 'Evento repetitivo para ' + self.usuario + ' tomar ' + self.med + ' cada ' + str(veces) + ' ' + Repeticion + ' empezando el ' + str(self.fecha)
                else:
                    Repeticion=self.cuando
                    return 'Evento repetitivo para ' + self.usuario + ' tomar ' + self.med + ' cada ' + Repeticion
        else:
            return 'Evento para ' + self.usuario + ' tomar ' + self.med + ' el ' + str(self.fecha)
