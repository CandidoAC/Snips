#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime
from Evento import Event

class Database(object):
    def connectDB(self):
        self.con_bd = sqlite3.connect('/home/pi/Desktop/symmetric-server-3.10.3/corp.sqlite', check_same_thread=False)
        self.cursor=self.con_bd.cursor()
        #self.con_bd.set_trace_callback(print)
        
    def createTable(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Eventos(ID INTEGER,
						fecha_creacion text,
						med text NOT NULL,
						user integer, 
						nombreUser text,
						Repeticion boolean, 
						veces integer, 
						FechaEvento TEXT, 
						Tipo_rep text,
						cant_rep integer,
						Active boolean,
                        Actualizado boolean,
						UNIQUE(fecha_creacion,med,nombreUser), 
						PRIMARY KEY(fecha_creacion,med,nombreUser),
						FOREIGN KEY (user) REFERENCES Users (ID))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Users(ID INTEGER,name text, Active boolean, PRIMARY KEY(ID ASC))''')
        self.con_bd.commit()

    def printTable(self):
        self.cursor.execute('SELECT * FROM Eventos')
        print ('Tabla Eventos:\n'+str(self.cursor.fetchall()))
        self.cursor.execute('SELECT * FROM Users')
        print ('Tabla Users:\n'+str(self.cursor.fetchall()))
        
    def DropTable(self):
        self.cursor.execute('''DROP TABLE IF EXISTS Eventos''')
        self.con_bd.commit()
        self.cursor.execute('''DROP TABLE IF EXISTS Users''')
        self.con_bd.commit()

    def ExistsUser(self,User):
        if(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(User,)).fetchall()):
           return True 
        else:
            return False
        
    def insertUsers(self,User):
        if(not self.ExistsUser(User)):
            self.cursor.execute('INSERT INTO Users(Name,Active) VALUES (?,?)', (User,False))
            self.con_bd.commit()

        
    def changeActiveUsers(self,User):
        self.cursor.execute('UPDATE Users SET Active = 0 WHERE Active==1')
        self.cursor.execute('UPDATE Users SET Active = 1 WHERE Name LIKE ?',(User,))
        self.con_bd.commit()

    def UserActive(self):
        s=''
        for (row,) in self.cursor.execute('SELECT Name FROM Users where Active == 1').fetchall():
            s+=row
        return s
    def IDUser(self,name):
      return int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(name,)).fetchone()[0])

    def eventActives(self):
       LEvents=[]
       result=self.cursor.execute('SELECT * FROM Eventos WHERE Active=1 and user IS NOT NULL')
       for x in result.fetchall():
           med=x[2]
           s=''
           for row in self.cursor.execute('SELECT Name FROM Users where ID=?',(x[3],)).fetchone():
               s+=row
           user=s
           rep=bool(x[5])
           if(rep):
               fecha=datetime.strptime(x[7],"%Y-%m-%d %H:%M:%S")
               if(str(x[9]!='')):
                when=str(x[9])+' '+x[8]
               else:
                when=x[8]
           else:
               fecha=datetime.strptime(x[7],"%Y-%m-%d %H:%M:%S")
               when=None
            
           e=Event(med,fecha,user,rep,when)
           e.veces=x[6]
           LEvents.append(e)
       return LEvents

    def eventByUser(self,user):
        if(self.ExistsUser(user)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(user,)).fetchone()[0])
           result=self.cursor.execute('SELECT * FROM Eventos WHERE user=?',(ID,))
           LEvents=[]
           for x in result.fetchall():
               med=x[2]
               s=''
               for row in self.cursor.execute('SELECT Name FROM Users where ID=?',(x[3],)).fetchone():
                   s+=row
               user=s
               rep=bool(x[5])
               if(rep):
                   fecha=datetime.strptime(x[7],"%Y-%m-%d %H:%M:%S")
                   print(str[9]+'\n')
                   if(str(x[9]!="")):
                     when=str(x[9])+' '+x[8]
                   else:
                     when=x[8]
               else:
                   fecha=x[7]
                   when=None
                
               e=Event(med,fecha,user,rep,when)
               e.veces=x[6]
               LEvents.append(e)
           return LEvents
       
    def ExistsEvent(self,e,userID):
        if(not e.rep):
            result=self.cursor.execute('SELECT * FROM Eventos WHERE user == ? and med LIKE ? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL',(userID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S")))
        else:
          #print(userID)
          if(' 'in e.when):
            result=self.cursor.execute('SELECT * FROM Eventos WHERE user == ? and med LIKE ? and Repeticion=? and FechaEvento=? and Tipo_rep LIKE ? and cant_rep == ?',(userID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.when[e.when.index(' ')+1:],int(e.when[:e.when.index(' ')])))
          else:
            result=self.cursor.execute('SELECT * FROM Eventos WHERE user == ? and med LIKE ? and Repeticion=? and FechaEvento=? and Tipo_rep LIKE ? and cant_rep == ?',(userID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.when,''))
        if(result.fetchall()):
            ##print(True)
            return True
        else:
            ##print(False)
            return False
    
    def insertEvent(self,fecha_creacion,e):
        if(self.ExistsUser(e.user)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.user,)).fetchone()[0])
           print(ID)
           if (not self.ExistsEvent(e,ID)):
                if(e.rep):
                  if(' 'in e.when):
                    event = [(fecha_creacion,e.med,ID,e.rep,e.veces,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.when[e.when.index(' ')+1:],int(e.when[:e.when.index(' ')]),e.user)]
                  else:
                    event = [(fecha_creacion,e.med,ID,e.rep,e.veces,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.when,'',e.user)]
                else:
                    event = [(fecha_creacion,e.med,ID,e.rep,e.veces,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),None,None,e.user)]
                self.cursor.executemany('INSERT INTO Eventos(fecha_creacion,med,user,Repeticion,veces,FechaEvento,Tipo_rep,cant_rep,Active,Actualizado,nombreUser) VALUES (?,?,?,?,?,?,?,?,1,0,?)', event)
                self.con_bd.commit()
 
    def IncrementarVeces(self,e):
        if(self.ExistsUser(e.user)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.user,)).fetchone()[0])
           print(ID)
           if (self.ExistsEvent(e,ID)):
                if(e.rep):
                  if(' 'in e.when):
                    params=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.when[e.when.index(' ')+1:],int(e.when[:e.when.index(' ')]))
                  else:
                    params=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.when,'')
                  query='UPDATE Eventos SET veces = veces + 1 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep=? and cant_rep=?'
                else:
                    params=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"))
                    query='UPDATE Eventos SET veces = veces + 1 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL'

                self.cursor.execute(query,params)
                self.con_bd.commit()

    def NingunaVeces(self,e):
        if(self.ExistsUser(e.user)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.user,)).fetchone()[0])
           print(ID)
           if (self.ExistsEvent(e,ID)):
                if(e.rep):
                  if(' 'in e.when):
                    params=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.when[e.when.index(' ')+1:],int(e.when[:e.when.index(' ')]))
                  else:
                    params=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.when,'')
                  query='UPDATE Eventos SET veces = 0 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep=? and cant_rep=?'
                else:
                    params=(ID,e.med,e.rep,e.fechae.fecha.strftime("%Y-%m-%d %H:%M:%S"))
                    query='UPDATE Eventos SET veces = 0 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL'

                self.cursor.execute(query,params)
                self.con_bd.commit()
        
    def FinishedEvent(self,e):
       if(self.ExistsUser(e.user)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.user,)).fetchone()[0])
           print(ID)
           if (self.ExistsEvent(e,ID)):
                #self.con_bd.set_trace_callback(print)
                if(e.rep):
                  if(' 'in e.when):
                    params=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.when[e.when.index(' ')+1:],int(e.when[:e.when.index(' ')]))
                  else:
                    params=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"),e.when,'')
                  query='UPDATE Eventos SET Active = 0  WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep=? and cant_rep=?'
                else:
                    params=(ID,e.med,e.rep,e.fecha.strftime("%Y-%m-%d %H:%M:%S"))
                    query='UPDATE Eventos SET Active = 0 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL'
                self.cursor.execute(query,params )
                self.con_bd.commit()
                
    def EventIsActive(self,med,FechaEvento,user,Repeticion,Tipo_rep,cant_rep):
        print('EventIsActive')
        if(Repeticion):
            print('Rep')
            if(Tipo_rep):
                params=(med,user,FechaEvento.strftime("%Y-%m-%d %H:%M:%S"),Tipo_rep,cant_rep)
                query='SELECT * FROM Eventos WHERE med LIKE ? and user=? and fechaEvento=? and Repeticion=1 and Tipo_rep=? and cant_rep=?'
        else:
            print('No rep')
            params=(med,user,FechaEvento.strftime("%Y-%m-%d %H:%M:%S"))
            query='SELECT * FROM Eventos WHERE med LIKE ? and user=? and fechaEvento=? and Repeticion=0 and Tipo_rep IS NULL and cant_rep IS NULL'

        result=self.cursor.execute(query,params).fetchone()
        print(result)
        if(result):
                print('Hay resultado'+str(result[10]))
                return result[10]
        return None

    def deleteEvent(self,med,FechaEvento,user,Repeticion,Tipo_rep,cant_rep):
          print('**************************************')
          if(self.ExistsUser(user)):
               ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(user,)).fetchone()[0])
               if(Repeticion):
                  params=(med,ID,FechaEvento.strftime("%Y-%m-%d %H:%M:%S"),Tipo_rep,cant_rep)
                  query='DELETE FROM Eventos WHERE med LIKE ? and user=? and fechaEvento=? and Repeticion=1 and Tipo_rep=? and cant_rep=?'
               else:
                  params=(med,ID,FechaEvento.strftime("%Y-%m-%d %H:%M:%S"))
                  query='DELETE FROM Eventos WHERE med LIKE ? and user=? and fechaEvento=? and Repeticion=0 and Tipo_rep IS NULL and cant_rep IS NULL'
               self.cursor.execute(query,params)
               self.con_bd.commit()
          print('**************************************')
               
    def HayActualizados(self):
        return self.cursor.execute('SELECT * FROM Eventos where Actualizado=1 and user IS NOT NULL').fetchall()
        
    def cambioANoActualizado(self):
        for row in self.cursor.execute('SELECT * FROM Eventos where Actualizado=1 and user IS NOT NULL').fetchall():
            print(row)
            self.cursor.execute('UPDATE Eventos SET Actualizado = 0 WHERE fecha_creacion=?',(row[1],))
            self.con_bd.commit()
        
