#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import io
import configparser
import pytz as tz
import csv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from datetime import timedelta
from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
from Evento import Event

class snips(object):
    Levent=[]
    def __init__(self):
        self.Levent = []
        self.usr='default'

    def addEvent(self,event):
        enc=False
        if(not (any(x for x in self.Levent if x.__eq__(event)))):
            self.Levent.append(event)

    def toString(self):
        for x in range(len(self.Levent)): 
            print(self.Levent[x].med+","+self.Levent[x].fecha.strftime("%Y-%m-%d %H:%M:%S")+","+str(self.Levent[x].veces)+","+self.Levent[x].user, end="\n")

    def minutes(i):
        switcher={
            0:"",
            15:" y cuarto",
            30:" y media",
            45:" menos cuarto",
            }
        return switcher.get(i," y " + str(i))

    """
    def t():
        global idFile
        idFile += 1


    def add_Reminder(med,fecha):
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Añadir_Evento','Medicamento':med,'Fecha_Evento':fecha,'Nombre_Usuario':'','Error_output':''})
        t()

    def Change_User(user):
        date=datetime.now()
        writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Cambio_Usuario','Medicamento':'','Fecha_Evento':'','Nombre_Usuario':user,'Error_output':''})
        t()

    def Reminder(med):
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Recordatorio','Medicamento':med,'Fecha_Evento':'','Nombre_Usuario':'','Error_output':''})
        t()

    def AceptedReminder(med):
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Aceptado','Medicamento':med,'Fecha_Evento':'','Nombre_Usuario':'','Error_output':''})
        t()

    def Error(mensaje):
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Error','Medicamento':'','Fecha_Evento':'','Nombre_Usuario':'','Error_output':mensaje})
        t()
        """
    
CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"
def read_configuration_file(configuration_file):
        try:
            with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
                conf_parser = SnipsConfigParser()
                conf_parser.readfp(f)
                return conf_parser.to_dict()
        except (IOError, configparser.Error) as e:
            #Error('Error:Fichero no encontrado')
            return dict()

    #Intent Añadir mdicamento
    def subscribe_Anadir_callback(hermes, intentMessage):
        conf = read_configuration_file(CONFIG_INI)
        action_wrapper_Anadir(hermes, intentMessage, conf)

    def action_wrapper_Anadir(hermes, intentMessage,conf):
        fecha = intentMessage.slots.Fecha.first().value
        fecha=fecha [ :fecha.index('+')-1 ]
        date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
        med = intentMessage.slots.Medicamento.first().value
        #scheduler.add_job(recordatorio, 'date', run_date=date,id=fecha,args=['med'], max_instances=10000)
        msg="Añadiendo recordatorio para el día  " + str(date.day) + " de " + str(date.month) + " del " + str(date.year) + " a las " + str(date.hour) + minutes(date.minute)+" tomar " + med
        #add_Reminder(med,fecha)
        e=Event(m,datetime.strptime(date, "%Y-%m-%d %H:%M:%S"),self.usr)
        self.addEvent(e)
        self.toString()
        hermes.publish_end_session(intentMessage.session_id, msg)


    #Intent cambiar usuario
    def subscribe_user_callback(hermes, intentMessage):
        conf = read_configuration_file(CONFIG_INI)
        action_wrapper_user(hermes, intentMessage, conf)

    def action_wrapper_user(hermes, intentMessage,conf):
        user = intentMessage.slots.user.first().value
       
        msg="Cambio de usuario a "+user
        self.usr=user
        #Change_User(user)
        hermes.publish_end_session(intentMessage.session_id, msg)

    #Intent Acept
    def subscribe_event_callback(hermes, intentMessage):
        action_wrapper_event(hermes, intentMessage, conf)

    def action_wrapper_event(hermes, intentMessage,conf):   
        msg="Evento aceptado"
        #AceptedReminder(med)
        hermes.publish_end_session(intentMessage.session_id, msg)
        #scheduler1.remove_job('job2')
    """
    def recordatorio(med):
        print('Evento detectado para : %s' % datetime.now())
        #Para el recordatorio si no se ha dicho aceptar o algo así7
        i=0
        scheduler1.add_job(Acept, 'interval', minutes=5,id='job2',args=['med'])
        while (scheduler1.get_job('job2')!=None):
            Reminder(med)
            time.sleep(360)
            print("Vez "+str(i+1))
            i+=1
            if(i==4):
                scheduler1.remove_job('job2')

        if scheduler1.get_job('job2')!=None:
            print("Evento realizado")
        else:
            print("Evento ignorado")
       

    def Acept(med):
        print("Tomar "+med)

    """
if __name__ == '__main__':
    """idFile=0
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler1 = BackgroundScheduler()
    scheduler1.start()
     with open('prueba.csv', 'a') as csvfile:
        fieldnames = ['id', 'Fecha','Tipo','Medicamento','Fecha_Evento','Nombre_Usuario','Error_output']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()"""
    Snips=snips();
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        Snips.usr='default'
        h\
        .subscribe_intent("caguilary:Anadir", subscribe_Anadir_callback) \
        .subscribe_intent("caguilary:user", subscribe_user_callback) \
        .subscribe_intent("caguilary:event", subscribe_event_callback) \
        .start()