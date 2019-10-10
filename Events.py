#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Evento import Event
from datetime import datetime
from Database import Database
from apscheduler.schedulers.background import BackgroundScheduler
import csv
import os
import time
import threading

class Snips(object):
    def __init__(self):
        self.file=__import__('action-Actions')
        self.usr=""
        self.idFile=0
        self.fieldnames = ['Fecha Creación','Id','Tipo', '¿Repetitivo?','Frecuencia','Fecha','Medicamento','Nombre_Usuario','Modo de aceptar','Salida_error']
        if(not os.path.exists('/home/pi/Reporte.csv')):
            with open('/home/pi/Reporte.csv', 'a+') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
        self.scheduler = BackgroundScheduler({'apscheduler.timezone': 'Europe/Madrid'})
        self.scheduler1 = BackgroundScheduler({'apscheduler.timezone': 'Europe/Madrid'})
        self.Database=Database()
        self.scheduler.start()
        self.scheduler1.start()
        self.Database.connectDB()
        self.Database.createTable()
        self.Database.insertUsers('default')
        self.usr=self.Database.UserActive()
        if(not self.usr):
            self.Database.changeActiveUsers('default')
            self.usr='default'
        self.createReminder(self.file)
        ActThread=self.syncTriggers(self) 
        ActThread.start()
    
    def exist_Job1(self,job):
        enc=False
        if(self.scheduler1.get_jobs()):
            for x in self.scheduler1.get_jobs():
                if(x.__eq__(job)):
                    return True
        return enc 

    def exist_Job(self,job):
        enc=False
        if(self.scheduler.get_jobs()):
            for x in self.scheduler.get_jobs():
                if(x.__eq__(job)):
                    return True
        return enc

    def dia_sem(self,i):
        switcher={
            'Lunes':0,
            'Martes':1,
            'Miercoles':2,
            'Jueves':3,
            'Viernes':4,
            'Sabado':5,
            'Domingo':6
            }
        return switcher.get(i,str(i))
                
    def t(self):
        self.idFile+=1
        
        
    def log(self,e,user,Modo,Tipo,msg):
        with open('/home/pi/Reporte.csv', 'a+') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if(e):
                if(e.rep):
                    writer.writerow({'Fecha Creación':date,'Id': str(self.idFile),'Tipo':Tipo,'¿Repetitivo?':'Si','Fecha':str(e.fecha),'Frecuencia':e.when,'Medicamento':e.med,'Nombre_Usuario':e.user,'Modo de aceptar':'','Salida_error':''})
                else:
                    writer.writerow({'Fecha Creación':date,'Id': str(self.idFile),'Tipo':Tipo,'¿Repetitivo?':'No','Fecha':str(e.fecha),'Frecuencia':'','Medicamento':e.med,'Nombre_Usuario':e.user,'Modo de aceptar':'','Salida_error':''})
            else:
                writer.writerow({'Fecha Creación':date,'Id': str(self.idFile),'Tipo':Tipo,'¿Repetitivo?':'','Fecha':'','Frecuencia':'','Medicamento':'','Nombre_Usuario':user,'Modo de aceptar':Modo,'Salida_error':msg})
        self.t()
    def addEvent(self,event):
        self.Database.insertEvent(datetime.now(),event)

    def addUser(self,user):
        self.Database.insertUsers(user)

    def existUser(self,user):   
        return self.Database.ExistsUser(user)

    def ExistsEvent(self,event):
        return self.Database.ExistsEvent(event,self.Database.IDUser(self.usr))

    def Incrementar(self,event):
        self.Database.IncrementarVeces(event)

    def FinishEvent(self,e):
        self.Database.FinishedEvent(e)

    def insertUsers(self,User):
        self.Database.insertUsers(User)

    def changeActiveUsers(self,User):
        self.Database.changeActiveUsers(User)
        self.usr=User

    def NingunaVez(self,e):
        self.Database.NingunaVeces(e)
    
    def UserActive(self):
        return self.Database.UserActive()

    def eventActive(self,e):
        ID=self.Database.IDUser(self.usr)
        if(e.rep):
            return self.Database.EventIsActive(e.med,e.fecha,ID,e.rep,e.when[e.when.index(' ')+1:],int(e.when[:e.when.index(' ')]))
        else:
            return self.Database.EventIsActive(e.med,e.fecha,ID,e.rep,None,None)

    def borrarEvento(self,e):
        print(e)
        if(e.rep):
            if(' 'in e.when):
                self.Database.deleteEvent(e.med,e.fecha,e.user,e.rep,e.when[e.when.index(' ')+1:],int(e.when[:e.when.index(' ')]))
            else:
                self.Database.deleteEvent(e.med,e.fecha,e.user,e.rep,e.when,'')
        else:
            self.Database.deleteEvent(e.med,e.fecha,e.user,e.rep,None,None)

    def createReminder(self,file):
        LEvent=self.Database.eventActives()
        for e in LEvent:
            if(e.rep):
                if(' 'in e.when.strip()):##Se hace el strip para borrar el blanco a la derecha en las comidas
                    Repeticion=e.when[e.when.index(' ')+1:]
                    veces=int(e.when[:e.when.index(' ')])
                    #print(Repeticion)
                else:
                    Repeticion=e.when

                if(not e.fecha is None):
                    date=e.fecha

                if(Repeticion=='dia'):
                    if(not self.exist_Job('Repeticion cada '+str(veces)+' dias,'+e.med+','+e.user)):
                        self.scheduler.add_job(file.recordatorio, 'cron',id='Repeticion cada '+str(veces)+' dias,'+e.med+','+e.user,year=date.year,month=date.month,day=str(date.day)+'/'+str(veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True,self])
                elif(Repeticion=='mes'):
                    if(not self.exist_Job('Repeticion '+str(veces)+' meses ,'+e.med+','+e.user)):
                        self.scheduler.add_job(file.recordatorio, 'cron',id='Repeticion '+str(veces)+' meses ,'+e.med+','+e.user,year=date.year,month=str(date.month)+'/'+str(veces),day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True,self]) 
                elif(Repeticion=='semana'):
                    if(not self.exist_Job('Repeticion cada '+str(veces)+' dias,'+e.med+','+e.user)):
                        self.scheduler.add_job(file.recordatorio, 'cron',id='Repeticion' +str(veces)+' semanas,'+e.med+','+e.user,year=date.year,month=date.month,day=str(date.day)+'/'+str(7*veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True,self]) 
                elif(Repeticion=='hora'):
                    if(not self.exist_Job('Repeticion '+str(veces)+' horas,'+e.med+','+e.user)):
                        self.scheduler.add_job(file.recordatorio, 'cron',id='Repeticion '+str(veces)+' horas,'+e.med+','+e.user,year=date.year,month=date.month,day=date.day,hour=str(date.hour)+'/'+str(veces),minute=date.minute, replace_existing=True, args=['default',e,True,self]) 
                elif(Repeticion=='desayuno'):#HORA-1
                    if(not self.exist_Job('Repeticion Desayuno'+','+e.med+','+e.user)):
                        self.scheduler.add_job(file.recordatorio, 'cron',id='Repeticion Desayuno'+','+e.med+','+e.user,year=date.year,month=date.month,day=date.day,hour='8/1',minute=0, replace_existing=True, args=['default',e,True,self]) 
                elif(Repeticion=='comida'):#HORA-1
                    if(not self.exist_Job('Repeticion Comida'+','+e.med+','+e.user)):
                        self.scheduler.add_job(file.recordatorio, 'cron',id='Repeticion Comida'+','+e.med+','+e.user,year=date.year,month=date.month,day=date.day,hour='13/1',minute=0, replace_existing=True, args=['default',e,True,self]) 
                elif(Repeticion=='cena'): #HORA-1
                    if(not self.exist_Job('Repeticion Desayuno'+','+e.med+','+e.user)):
                        self.scheduler.add_job(file.recordatorio, 'cron',id='Repeticion Cena'+','+e.med+','+e.user,year=date.year,month=date.month,day=date.day,hour='20/1',minute=0, replace_existing=True, args=['default',e,True,self]) 
                else:
                    if(not self.exist_Job('Repeticion semanal cada '+Repeticion+','+e.med+','+e.user)):
                        self.scheduler.add_job(file.recordatorio, 'cron',id='Repeticion semanal cada '+Repeticion+','+e.med+','+e.user,day_of_week=self.dia_sem(Repeticion),year=date.year,month=date.month,day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True,self]) 
                ahora=datetime.now()
                fechaE=e.fecha
                #print(str(ahora)+" y "+fechaE)
                if(ahora<fechaE):  
                    if(not self.exist_Job1('Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when)):
                        self.scheduler1.add_job(file.recordatorioTomar, 'interval', seconds=20,id='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when,args=[e,'default',self])
            else:
                if(not e.fecha is None):
                    date=e.fecha

                ahora=datetime.now()
                fechaE=e.fecha
                #print(str(ahora)+" y "+fechaE)
                if(ahora<fechaE):    
                    if(not self.exist_Job(str(e.fecha)+','+e.med+','+e.user)):
                        self.scheduler.add_job(file.recordatorio, 'date', run_date=date,id=str(e.fecha)+','+e.med+','+e.user,args=['default',e,False,self])
                else:
                    if(not self.exist_Job1('Evento no repetitivo:recordando tomar '+e.med+' a '+e.user)):
                        self.scheduler1.add_job(file.recordatorioTomar, 'interval', seconds=20,id='Evento no repetitivo: recordando tomar '+e.med+' a '+e.user,args=[e,'default',self])
    class syncTriggers(threading.Thread):
        def __init__(self,Snips):
            threading.Thread.__init__(self)
            self.user=Snips.usr
            self.Snips=Snips
        
        def run(self):
            while True:
                if(self.Snips.Database.HayActualizados()):
                    print('Actualizando threads')
                    self.Snips.createReminder(self.Snips.file)
                    self.Snips.Database.cambioANoActualizado()
                time.sleep(5)
