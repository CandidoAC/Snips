from Evento import Event
from datetime import datetime
from Database import Database

class Snips(object):
    
    def __init__(self):
        self.Database=Database()
        self.Database.connectDB()
        self.Database.createTable()
        self.Database.insertUsers('default')
        self.usr=self.Database.UserActive()
        if(not self.usr):
            self.Database.changeActiveUsers('default')

        LEvent=self.Database.eventActives()
        for e in LEvent:
            if(Rep):
                Repeticion=e.when[e.when.index(' ')+1:]
                veces=int(e.when[:e.when.index(' ')])
                if(not e.fecha is None):
                    date=e.fecha
                else:
                    fecha=datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                    date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")

                if(Repeticion=='dia'):
                    scheduler.add_job(recordatorio, 'cron',id='Repeticion cada '+str(veces)+' dias,'+e.med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/'+str(veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e])
                elif(Repeticion=='mes'):
                    scheduler.add_job(recordatorio, 'cron',id='Repeticion '+str(veces)+' meses ,'+e.med+','+Snips.usr,year=date.year,month=str(date.month)+'/'+str(veces),day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e]) 
                elif(Repeticion=='semana'):
                    scheduler.add_job(recordatorio, 'cron',id='Repeticion' +str(veces)+' semanas,'+e.med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/'+str(7*veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e]) 
                elif(Repeticion=='hora'):
                    scheduler.add_job(recordatorio, 'cron',id='Repeticion '+str(veces)+' horas,'+e.med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour=str(date.hour)+'/'+str(veces),minute=date.minute, replace_existing=True, args=['default',e]) 
                elif(Repeticion=='desayuno'):#HORA-1
                    scheduler.add_job(recordatorio, 'cron',id='Repeticion Desayuno'+','+e.med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='8/1',minute=0, replace_existing=True, args=['default',e]) 
                elif(Repeticion=='comida'):#HORA-1
                    scheduler.add_job(recordatorio, 'cron',id='Repeticion Comida'+','+e.med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='13/1',minute=0, replace_existing=True, args=['default',e]) 
                elif(Repeticion=='cena'): #HORA-1
                    scheduler.add_job(recordatorio, 'cron',id='Repeticion Cena'+','+e.med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='20/1',minute=0, replace_existing=True, args=['default',e]) 
                else:
                    scheduler.add_job(recordatorio, 'cron',id='Repeticion semanal cada '+Repeticion+','+e.med+','+Snips.usr,day_of_week=dia_sem(Repeticion),year=date.year,month=date.month,day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e]) 
            else:
                scheduler.add_job(recordatorio, 'e.date', run_date=date,id=fecha+','+e.med+','+e.user,args=['default',e])
                
    def addEvent(self,event):
    	self.Database.insertEvent(e.datetime.now(),event)

    def addUser(self,user):
        self.Database.insertUsers(e.datetime.now(),event)

    def existUser(self,user):   
        return self.Database.ExistsUser()

    def Incrementar(self,event):
    	self.Database.IncrementarVeces(event)

    def FinishEvent(e):
        self.Database.FinishedEvent(e)

    def insertUsers(User):
        self.Database.insertUsers(User)

    def changeActiveUsers(User):
        self.Database.changeActiveUsers(User)
        self.usr=User
    
    def UserActive():
        self.Database.UserActive()