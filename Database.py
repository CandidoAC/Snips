#!/usr/bin/env pytho
import sqlite3

class Database(object):
    def connectDB(self):
        self.con_bd = sqlite3.connect('Reminders.db', check_same_thread=False)
        self.cursor=self.con_bd.cursor()
        
    def createTable(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Eventos(ID INTEGER,timestamp date,med text,user integer, Repeticion boolean, veces integer, FechaEvento Date, Tipo_rep text,cant_rep integer,Active boolean , PRIMARY KEY(ID ASC),FOREIGN KEY (user) REFERENCES Users (ID))''')
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
    def eventActives(self):
       result=self.cursor.execute('SELECT * FROM Eventos WHERE Active=1')
       return result.fetchall()

    def eventByUser(self,user):
        if(self.ExistsUser(e.user)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.user,)).fetchone()[0])
           print(ID)
           result=self.cursor.execute('SELECT * FROM Eventos WHERE user=?',(ID,))
           return result.fetchall()
       
    def ExistsEvent(self,e,userID):
        if(e.when==None):
            result=self.cursor.execute('SELECT ID FROM Eventos WHERE user == ? and med LIKE ? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL',(userID,e.med,e.rep,e.fecha))
        else:
            result=self.cursor.execute('SELECT ID FROM Eventos WHERE user == ? and med LIKE ? and Repeticion=? and FechaEvento IS NULL and Tipo_rep LIKE ? and cant_rep == ?',(userID,e.med,e.rep,e.when[e.when.index(' ')+1:],int(e.when[:e.when.index(' ')])))

        if(result.fetchall()):
            print(True)
            return True
        else:
            print(False)
            return False
    
    def insertEvent(self,timestamp,e):
        if(self.ExistsUser(e.user)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.user,)).fetchone()[0])
           print(ID)
           if (not self.ExistsEvent(e,ID)):
                if(e.rep):
                    event = [(timestamp,e.med,ID,e.rep,e.veces,e.fecha,e.when[e.when.index(' ')+1:],int(e.when[:e.when.index(' ')]))]
                else:
                    event = [(timestamp,e.med,ID,e.rep,e.veces,e.fecha,None,None)]
                self.cursor.executemany('INSERT INTO Eventos(timestamp,med,user,Repeticion,veces,FechaEvento,Tipo_rep,cant_rep,Active) VALUES (?,?,?,?,?,?,?,?,1)', event)
                self.con_bd.commit()

    def IncrementarVeces(self,e):
        if(self.ExistsUser(e.user)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.user,)).fetchone()[0])
           print(ID)
           if (self.ExistsEvent(e,ID)):
                if(e.rep):
                    params=(ID,e.med,e.rep,e.when[e.when.index(' ')+1:],int(e.when[:e.when.index(' ')]))
                    query='UPDATE Eventos SET veces = veces + 1 WHERE user = ? and med=? and Repeticion=? and FechaEvento IS NULL and Tipo_rep=? and cant_rep=?'
                else:
                    params=(ID,e.med,e.rep,e.fecha)
                    query='UPDATE Eventos SET veces = veces + 1 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL'

                self.cursor.execute(query,params)
                self.con_bd.commit()
        
    def FinishedEvent(self,e):
        if(self.ExistsUser(e.user)):
           ID=int(self.cursor.execute('SELECT ID FROM Users where Name LIKE ?',(e.user,)).fetchone()[0])
           print(ID)
           if (self.ExistsEvent(e,ID)):
                self.con_bd.set_trace_callback(print)
                if(e.rep):
                    params=(ID,e.med,e.rep,e.when[:e.when.index(' ')],e.when[e.when.index(' ')+1:])
                    query='UPDATE Eventos SET Active = 0  WHERE user = ? and med=? and Repeticion=? and FechaEvento IS NULL and Tipo_rep=? and cant_rep=?'
                else:
                    params=(ID,e.med,e.rep,e.fecha)
                    query='UPDATE Eventos SET Active = 0 WHERE user = ? and med=? and Repeticion=? and FechaEvento=? and Tipo_rep IS NULL and cant_rep IS NULL'
                self.cursor.execute(query,params )
                self.con_bd.commit()