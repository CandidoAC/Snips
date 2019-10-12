#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime
from Evento import Evento

class BaseDeDatos(object):
    def conectarDB(self):
        self.con_bd = sqlite3.connect('/home/pi/Desktop/symmetric-server-3.10.3/corp.sqlite', check_same_thread=False)
        self.cursor=self.con_bd.cursor()
        #self.con_bd.set_trace_callback(print)
        
    def crearTabla(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Eventos(ID INTEGER,
						fecha_creacion texto,
						med texto NOT NULL,
						user integer, 
						nombreUser texto,
						Repeticion boolean, 
						veces integer, 
						FechaEvento TEXT, 
						Tipo_rep texto,
						cant_rep integer,
						Active boolean,
                        Actualizado boolean,
						UNIQUE(fecha_creacion,med,nombreUser), 
						PRIMARY KEY(fecha_creacion,med,nombreUser),
						FOREIGN KEY (fecha_creacion,med,nombreUser) REFERENCES Users (ID))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Users(ID INTEGER,name texto, Active boolean, PRIMARY KEY(ID ASC))''')
        self.con_bd.commit()

    def mostrarTabla(self):
        self.cursor.execute('SELECT * FROM Eventos')
        print ('Tabla Eventos:\n'+str(self.cursor.fetchall()))
        self.cursor.execute('SELECT * FROM Users')
        print ('Tabla Users:\n'+str(self.cursor.fetchall()))
        
    def BorrarTablas(self):
        self.cursor.execute('''DROP TABLE IF EXISTS Eventos''')
        self.con_bd.commit()
        self.cursor.execute('''DROP TABLE IF EXISTS Users''')
        self.con_bd.commit()

    def ExisteUsuario(self, Usuario):
        if(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?', (Usuario,)).fetchall()):
           return True 
        else:
            return False
        
    def insertarUsuario(self, Usuario):
        if(not self.ExisteUsuario(Usuario)):
            self.cursor.execute('INSERT INTO Users(Name,Active) VALUES (?,?)', (Usuario, False))
            self.con_bd.commit()

        
    def cambiarUsuarioActivo(self, Usuario):
        self.cursor.execute('UPDATE Users SET Active = 0 WHERE Active==1')
        self.cursor.execute('UPDATE Users SET Active = 1 WHERE Name LIKE ?', (Usuario,))
        self.con_bd.commit()

    def usuarioActivo(self):
        s=''
        for (columna,) in self.cursor.execute('SELECT Name FROM Users where Active == 1').fetchall():
            s+=columna
        return s
    def IDUsuario(self, nombre):
      return int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?', (nombre,)).fetchone()[0])

    def eventosActivos(self):
       LEventos=[]
       resultados=self.cursor.execute('SELECT * FROM Eventos WHERE Active=1 and user IS NOT NULL')
       for x in resultados.fetchall():
           med=x[2]
           s=''
           for columna in self.cursor.execute('SELECT Name FROM Users where ID=?',(x[3],)).fetchone():
               s+=columna
           usuario=s
           rep=bool(x[5])
           if(rep):
               fecha=datetime.strptime(x[7],"%Y-%m-%d %H:%M:%S")
               if(str(x[9]!='')):
                cuando=str(x[9])+' '+x[8]
               else:
                cuando=x[8]
           else:
               fecha=datetime.strptime(x[7],"%Y-%m-%d %H:%M:%S")
               cuando=None
            
           e=Evento(med, fecha, usuario, rep, cuando)
           e.veces=x[6]
           LEventos.append(e)
       return LEventos

    def EventoPorUsuario(self, usuario):
        if(self.ExisteUsuario(usuario)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?', (usuario,)).fetchone()[0])
           resultados=self.cursor.execute('SELECT * FROM Eventos WHERE user=?',(ID,))
           LEventos=[]
           for x in resultados.fetchall():
               med=x[2]
               s=''
               for columna in self.cursor.execute('SELECT Name FROM Users where ID=?',(x[3],)).fetchone():
                   s+=columna
               usuario=s
               rep=bool(x[5])
               if(rep):
                   fecha=datetime.strptime(x[7],"%Y-%m-%d %H:%M:%S")
                   print(str[9]+'\n')
                   if(str(x[9]!="")):
                     cuando=str(x[9])+' '+x[8]
                   else:
                     cuando=x[8]
               else:
                   fecha=x[7]
                   cuando=None
                
               e=Evento(med, fecha, usuario, rep, cuando)
               e.veces=x[6]
               LEventos.append(e)
           return LEventos
       
    def ExisteEvento(self, e, usuarioID):
        if(not e.rep):
            resultados=self.cursor.execute('SELECT * FROM Eventos WHERE user == ? and med LIKE ? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL', (usuarioID, e.med, e.rep, e.fecha.strftime("%Y-%m-%d %H:%M:%S")))
        else:
          if(' 'in e.cuando):
            resultados=self.cursor.execute('SELECT * FROM Eventos WHERE user == ? and med LIKE ? and Repeticion=? and FechaEvento=? and Tipo_rep LIKE ? and cant_rep == ?', (usuarioID, e.med, e.rep, e.fecha.strftime("%Y-%m-%d %H:%M:%S"), e.cuando[e.cuando.index(' ') + 1:], int(e.cuando[:e.cuando.index(' ')])))
          else:
            resultados=self.cursor.execute('SELECT * FROM Eventos WHERE user == ? and med LIKE ? and Repeticion=? and FechaEvento=? and Tipo_rep LIKE ? and cant_rep == ?', (usuarioID, e.med, e.rep, e.fecha.strftime("%Y-%m-%d %H:%M:%S"), e.cuando, ''))
        if(resultados.fetchall()):
            ##print(True)
            return True
        else:
            ##print(False)
            return False
    
    def insertarEvento(self, fecha_creacion, e):
        if(self.ExisteUsuario(e.usuario)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.usuario,)).fetchone()[0])
           print(ID)
           if (not self.ExisteEvento(e, ID)):
                if(e.rep):
                  if(' 'in e.cuando):
                    evento = [(fecha_creacion,e.med,ID,e.rep,e.veces,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.cuando[e.cuando.index(' ')+1:],int(e.cuando[:e.cuando.index(' ')]),e.usuario)]
                  else:
                    evento = [(fecha_creacion,e.med,ID,e.rep,e.veces,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.cuando,'',e.usuario)]
                else:
                    evento = [(fecha_creacion,e.med,ID,e.rep,e.veces,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),None,None,e.usuario)]
                self.cursor.executemany('INSERT INTO Eventos(fecha_creacion,med,user,Repeticion,veces,FechaEvento,Tipo_rep,cant_rep,Active,Actualizado,nombreUser) VALUES (?,?,?,?,?,?,?,?,1,0,?)', evento)
                self.con_bd.commit()
 
    def IncrementarVeces(self,e):
        if(self.ExisteUsuario(e.usuario)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.usuario,)).fetchone()[0])
           print(ID)
           if (self.ExisteEvento(e, ID)):
                if(e.rep):
                  if(' 'in e.cuando):
                    parametros=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.cuando[e.cuando.index(' ')+1:],int(e.cuando[:e.cuando.index(' ')]))
                  else:
                    parametros=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.cuando,'')
                  consulta='UPDATE Eventos SET veces = veces + 1 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep=? and cant_rep=?'
                else:
                    parametros=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"))
                    consulta='UPDATE Eventos SET veces = veces + 1 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL'

                self.cursor.execute(consulta,parametros)
                self.con_bd.commit()

    def NingunaVeces(self,e):
        if(self.ExisteUsuario(e.usuario)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.usuario,)).fetchone()[0])
           print(ID)
           if (self.ExisteEvento(e, ID)):
                if(e.rep):
                  if(' 'in e.cuando):
                    parametros=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.cuando[e.cuando.index(' ')+1:],int(e.cuando[:e.cuando.index(' ')]))
                  else:
                    parametros=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.cuando,'')
                  consulta='UPDATE Eventos SET veces = 0 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep=? and cant_rep=?'
                else:
                    parametros=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"))
                    consulta='UPDATE Eventos SET veces = 0 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL'

                self.cursor.execute(consulta,parametros)
                self.con_bd.commit()
        
    def EventoFinalizado(self, e):
       if(self.ExisteUsuario(e.usuario)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.usuario,)).fetchone()[0])
           print(ID)
           if (self.ExisteEvento(e, ID)):
                #self.con_bd.set_trace_callback(print)
                if(e.rep):
                  if(' 'in e.cuando):
                    parametros=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.cuando[e.cuando.index(' ')+1:],int(e.cuando[:e.cuando.index(' ')]))
                  else:
                    parametros=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.cuando,'')
                  consulta='UPDATE Eventos SET Active = 0  WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep=? and cant_rep=?'
                else:
                    parametros=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"))
                    consulta='UPDATE Eventos SET Active = 0 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL'
                self.cursor.execute(consulta,parametros )
                self.con_bd.commit()
                
    def EventoEsActivo(self, med, FechaEvento, usuario, Repeticion, Tipo_rep, cant_rep):
        print('EventIsActive')
        if(Repeticion):
            print('Rep')
            if(Tipo_rep):
                parametros=(med, usuario, FechaEvento.strftime("%Y-%m-%d %H:%M:%S"), Tipo_rep, cant_rep)
                consulta='SELECT * FROM Eventos WHERE med LIKE ? and user=? and fechaEvento=? and Repeticion=1 and Tipo_rep=? and cant_rep=?'
        else:
            print('No rep')
            parametros=(med, usuario, FechaEvento.strftime("%Y-%m-%d %H:%M:%S"))
            consulta='SELECT * FROM Eventos WHERE med LIKE ? and user=? and fechaEvento=? and Repeticion=0 and Tipo_rep IS NULL and cant_rep IS NULL'

        resultado=self.cursor.execute(consulta,parametros).fetchone()
        print(resultado)
        if(resultado):
                print('Hay resultado'+str(resultado[10]))
                return resultado[10]
        return None

    def borrarEvento(self, med, FechaEvento, usuario, Repeticion, Tipo_rep, cant_rep):
          if(self.ExisteUsuario(usuario)):
               ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?', (usuario,)).fetchone()[0])
               if(Repeticion):
                  parametros=(med,ID,FechaEvento.strftime("%Y-%m-%d %H:%M:%S"),Tipo_rep,cant_rep)
                  consulta='DELETE FROM Eventos WHERE med LIKE ? and user=? and fechaEvento=? and Repeticion=1 and Tipo_rep=? and cant_rep=?'
               else:
                  parametros=(med,ID,FechaEvento.strftime("%Y-%m-%d %H:%M:%S"))
                  consulta='DELETE FROM Eventos WHERE med LIKE ? and user=? and fechaEvento=? and Repeticion=0 and Tipo_rep IS NULL and cant_rep IS NULL'
               self.cursor.execute(consulta,parametros)
               self.con_bd.commit()
               
    def HayActualizados(self):
        return self.cursor.execute('SELECT * FROM Eventos where Actualizado=1 and user IS NOT NULL').fetchall()
        
    def cambioANoActualizado(self):
        for columna in self.cursor.execute('SELECT * FROM Eventos where Actualizado=1 and user IS NOT NULL').fetchall():
            print(columna)
            self.cursor.execute('UPDATE Eventos SET Actualizado = 0 WHERE fecha_creacion=?',(columna[1],))
            self.con_bd.commit()
        
