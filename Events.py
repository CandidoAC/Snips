from Evento import Event
from datetime import datetime
from Database import Database
from apscheduler.schedulers.background import BackgroundScheduler
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions

class Snips(object):
    
    def __init__(self):
        mqtt_opts = MqttOptions()
        self.scheduler = BackgroundScheduler({'apscheduler.timezone': 'Europe/Madrid'})
        self.scheduler.start()
        self.scheduler1 = BackgroundScheduler({'apscheduler.timezone': 'Europe/Madrid'})
        self.scheduler1.start()
        self.Database=Database()
        self.Database.connectDB()
        self.Database.createTable()
        self.Database.insertUsers('default')
        self.usr=self.Database.UserActive()
        with Hermes(mqtt_options=mqtt_opts) as mqttClient:
            if(self.usr==''):
                self.Database.changeActiveUsers('default')

            LEvent=self.Database.eventActives()
            for e in LEvent:
                if(e.rep):
                    Repeticion=e.when[e.when.index(' ')+1:]
                    veces=int(e.when[:e.when.index(' ')])
                    if(not e.fecha is None):
                        date=datetime.strptime(e.fecha,"%Y-%m-%d %H:%M:%S")
                    else:
                        fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")

                    if(Repeticion=='dia'):
                        self.scheduler.add_job(self.recordatorio, 'cron',id='Repeticion cada '+str(veces)+' dias,'+e.med+','+e.user,year=date.year,month=date.month,day=str(date.day)+'/'+str(veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True])
                    elif(Repeticion=='mes'):
                        self.scheduler.add_job(self.recordatorio, 'cron',id='Repeticion '+str(veces)+' meses ,'+e.med+','+e.userr,year=date.year,month=str(date.month)+'/'+str(veces),day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True]) 
                    elif(Repeticion=='semana'):
                        self.scheduler.add_job(self.recordatorio, 'cron',id='Repeticion' +str(veces)+' semanas,'+e.med+','+e.user,year=date.year,month=date.month,day=str(date.day)+'/'+str(7*veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True]) 
                    elif(Repeticion=='hora'):
                        self.scheduler.add_job(self.recordatorio, 'cron',id='Repeticion '+str(veces)+' horas,'+e.med+','+e.user,year=date.year,month=date.month,day=date.day,hour=str(date.hour)+'/'+str(veces),minute=date.minute, replace_existing=True, args=['default',e,True]) 
                    elif(Repeticion=='desayuno'):#HORA-1
                        self.scheduler.add_job(self.recordatorio, 'cron',id='Repeticion Desayuno'+','+e.med+','+e.user,year=date.year,month=date.month,day=date.day,hour='8/1',minute=0, replace_existing=True, args=['default',e,True]) 
                    elif(Repeticion=='comida'):#HORA-1
                        self.scheduler.add_job(self.recordatorio, 'cron',id='Repeticion Comida'+','+e.med+','+e.user,year=date.year,month=date.month,day=date.day,hour='13/1',minute=0, replace_existing=True, args=['default',e,True]) 
                    elif(Repeticion=='cena'): #HORA-1
                        self.scheduler.add_job(self.recordatorio, 'cron',id='Repeticion Cena'+','+e.med+','+e.user,year=date.year,month=date.month,day=date.day,hour='20/1',minute=0, replace_existing=True, args=['default',e,True]) 
                    else:
                        self.scheduler.add_job(self.recordatorio, 'cron',id='Repeticion semanal cada '+Repeticion+','+e.med+','+e.user,day_of_week=dia_sem(Repeticion),year=date.year,month=date.month,day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True]) 
                    
                    if(date>datetime.now()):
                        self.scheduler1.add_job(recordatorioTomar, 'interval', seconds=20,id='job2',args=[e,'default'])
                else:
                    date=datetime.strptime(e.fecha,"%Y-%m-%d %H:%M:%S")
                    if(datetime.strptime(e.fecha,"%Y-%m-%d %H:%M:%S")<datetime.now()):
                        self.scheduler.add_job(self.recordatorio, 'date', run_date=date,id=e.fecha+','+e.med+','+e.user,args=['default',e,False])
                    else:
                        self.scheduler1.add_job(self.recordatorioTomar, 'interval', seconds=20,id='job2',args=[e,'default'])
                
    def recordatorio(self,intentMessage,e,Repetitivo):
        print('Evento detectado para : %s' % datetime.now())
        if(e.user==self.usr):
            if(Repetitivo):
                self.NingunaVeces(e)
            say(intentMessage,e.user+' te toca tomarte '+e.med)
            self.scheduler1.add_job(self.recordatorioTomar, 'interval', seconds=20,id='job2',args=[e,intentMessage])
            Reminder(e)
   

    def recordatorioTomar(self,e,intentMessage):
        if(e.user==self.usr):
            if(e.veces<6):
                Reminder(e) 
                mqttClient.publish_start_session_action(site_id=intentMessage,
                session_init_text=e.user+'¿ te has tomado ' +e.med+'?',
                session_init_intent_filter=["caguilary:Confirmar","caguilary:Negar"],
                session_init_can_be_enqueued=False,
                session_init_send_intent_not_recognized=True,
                custom_data=None)
                msg=""
                print(e.user+'¿te has tomado ' +e.med+'?:Vez '+str(e.veces))
                self.Incrementar(e) 
                e.IncrementarVeces()    
                mqttClient.publish_end_session(intentMessage, msg)  
            else:
                msg=e.user+'ha ignorado el evento tomar '+e.med
                say(intentMessage,msg)
                self.scheduler1.remove_job('job2')
                self.FinishEvent(e)
                mqttClient.publish_end_session(intentMessage, msg)
        else:
            print("Usuario actual distinto al del evento")
            self.scheduler1.remove_job('job2')
    def addEvent(self,event):
    	self.Database.insertEvent(datetime.now(),event)

    def addUser(self,user):
        self.Database.insertUsers(user) 

    def existUser(self,user):   
        return self.Database.ExistsUser(user)

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
        self.Database.UserActive()