#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import io
import configparser
import csv
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from datetime import timedelta
from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
from Events import Snips
from Evento import Event
from threading import Timer

def minutes(i):
    switcher={
        0:"",
        15:" y cuarto",
        30:" y media",
        45:" menos cuarto",
        }
    return switcher.get(i," y " + str(i))


CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

def t():
    global idFile
    idFile+=1

def global_variables():
    global Recordatorio,e,Snips
    Snips=Snips();

def add_Reminder(med,fecha,usr):
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Añadir_Evento','Medicamento':med,'Fecha_Evento':fecha,'Nombre_Usuario':'','Error_output':''})
    t()

def Change_User(user):
    date=datetime.now()
    writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Cambio_Usuario','Medicamento':'','Fecha_Evento':'','Nombre_Usuario':user,'Error_output':''})
    t()

def Reminder(med,user):
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Recordatorio','Medicamento':med,'Fecha_Evento':'','Nombre_Usuario':'','Error_output':''})
    t()

def AceptedReminder(med,user):
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Aceptado','Medicamento':med,'Fecha_Evento':'','Nombre_Usuario':'','Error_output':''})
    t()

def Error(mensaje):
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Error','Medicamento':'','Fecha_Evento':'','Nombre_Usuario':'','Error_output':mensaje})
    t()


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
    global Snips
    session=intentMessage.session_id
    fecha = intentMessage.slots.Fecha.first().value
    fecha=fecha [ :fecha.index('+')-1 ]
    date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
    med = intentMessage.slots.Medicamento.first().value
    msg="Añadiendo recordatorio para el día  " + str(date.day) + " de " + str(date.month) + " del " + str(date.year) + " a las " + str(date.hour) + minutes(date.minute)+" tomar " + med
    #add_Reminder(med,fecha)
    """now=datetime.now()
    if((date - now).total_seconds()>0):
        t = Timer((date - now).total_seconds(), recordatorio,['default',med,fecha])
        t.start()"""
    e=Event(med,date,Snips.usr)
    e.IncrementarVeces()
    Snips.addEvent(e)
    Recordatorio=e
    add_Reminder(med,fecha,Snips.usr)
    scheduler.add_job(recordatorio, 'date', run_date=date,id=fecha,args=['default',e], max_instances=10000)
    hermes.publish_end_session(intentMessage.session_id, msg)

#Intent cambiar usuario
def subscribe_user_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_user(hermes, intentMessage, conf)

def action_wrapper_user(hermes, intentMessage,conf):
    global Snips
    user = intentMessage.slots.user.first().value
    msg="Cambio de usuario a "+user
    Snips.usr=user
    Change_User(user)
    hermes.publish_end_session(intentMessage.session_id, msg)

def subscribe_confirmar_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_Confirmar(hermes, intentMessage, conf)

def action_wrapper_Confirmar(hermes, intentMessage,conf):
    global Snips   
    msg="Evento aceptado"
    with open('/home/pi/prueba.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        print("Abriendo prueba.csv")
        for row in reversed(list(reader)):
            print (row)
            if row[2]=="Recordatorio":
                rec=row[3]
                ##AceptedReminder(rec,Snips.usr)
                print("Aceptando "+rec)
                break

    hermes.publish_end_session(intentMessage.session_id, msg)
    scheduler1.remove_job('job2')

def subscribe_Negar_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_Negar(hermes, intentMessage, conf)

def action_wrapper_Negar(hermes, intentMessage,conf):
    msg="Evento no aceptado.Se te volverá ha avisar en 20 segundos"
    hermes.publish_end_session(intentMessage.session_id, msg)

def say(intentMessage,text):
    mqttClient.publish_start_session_notification(intentMessage, text,None)

    
def recordatorio(intentMessage,e):
    print('Evento detectado para : %s' % datetime.now())
    if(e.user==Snips.usr):
        say(intentMessage,'Evento:Toca '+e.med)
        Reminder(e.med,e.user)
        scheduler1.add_job(recordatorioTomar, 'interval', seconds=20,id='job2',args=[e,intentMessage])
   

def recordatorioTomar(e,intentMessage):
    global Snips
    if(e.user==Snips.usr):
        if(e.veces<6):
            Reminder(e.med,e.user)
            mqttClient.publish_start_session_action(site_id=intentMessage,
            session_init_text="¿Te has tomado " +e.med+"?",
            session_init_intent_filter=["caguilary:Confirmar","caguilary:Negar","hermes/nlu/intentNotRecognized"],
            session_init_can_be_enqueued=False,
            session_init_send_intent_not_recognized=True,
            custom_data=None)
            msg=""
            print('¿Te has tomado ' +e.med+'?:Vez '+str(e.veces))
            Snips.Incrementar(e) 
            e.IncrementarVeces()    
            mqttClient.publish_end_session(intentMessage, msg)  
        else:
            msg='Evento ignorado:tomar '+e.med
            say(intentMessage,msg)
            scheduler1.remove_job('job2')
            mqttClient.publish_end_session(intentMessage, msg)
    else:
        print("Usuario actual distinto al del evento")
        scheduler1.remove_job('job2')

if __name__ == '__main__':
    scheduler = BackgroundScheduler({'apscheduler.timezone': 'Europe/Madrid'})
    scheduler.start()
    scheduler1 = BackgroundScheduler({'apscheduler.timezone': 'Europe/Madrid'})
    scheduler1.start()
    mqtt_opts = MqttOptions()
    idFile=0
    global_variables()
    filePath='/home/pi/prueba.csv'
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")

    with Hermes(mqtt_options=mqtt_opts) as h,Hermes(mqtt_options=mqtt_opts) as mqttClient,open('prueba.csv', 'a+') as csvfile:
        fieldnames = ['id', 'Fecha','Tipo','Medicamento','Fecha_Evento','Nombre_Usuario','Error_output']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        h\
        .subscribe_intent("caguilary:Anadir", subscribe_Anadir_callback) \
        .subscribe_intent("caguilary:user", subscribe_user_callback) \
        .subscribe_intent("caguilary:Confirmar", subscribe_confirmar_callback) \
        .subscribe_intent("caguilary:Negar", subscribe_Negar_callback) \
        .start()