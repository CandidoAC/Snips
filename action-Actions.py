#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import io
import configparser
import os
import csv
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

def dia_sem(i):
    switcher={
        'Lunes':0,
        'Martes':1,
        'Miercoles':2,
        'Jueves':3,
        'Viernes':4,
        'Sabado':5,
        'Domingo':6
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

def add_Reminder(e):
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if(e.rep):
        writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Añadir_Evento','¿Repetitivo?':'Si','Recordatorio':e.when,'Medicamento':e.med,'Nombre_Usuario':e.user,'Error_output':''})
    else:
        writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Añadir_Evento','¿Repetitivo?':'No','Recordatorio':str(e.fecha),'Medicamento':e.med,'Nombre_Usuario':e.user,'Error_output':''})
    t()

def Change_User(user):
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Cambio_Usuario','¿Repetitivo?':'','Recordatorio':'','Medicamento':'','Nombre_Usuario':user,'Error_output':''})
    t()

def Add_User(user):
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Añadir_Usuario','¿Repetitivo?':'','Recordatorio':'','Medicamento':'','Nombre_Usuario':user,'Error_output':''})
    t()

def Reminder(e):
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if(e.rep):
        writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Recordatorio','¿Repetitivo?':'Si','Recordatorio':e.when,'Medicamento':e.med,'Nombre_Usuario':e.user,'Error_output':''})
    else:
        writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Recordatorio','¿Repetitivo?':'No','Recordatorio':str(e.fecha),'Medicamento':e.med,'Nombre_Usuario':e.user,'Error_output':''})
    t()

def AceptedReminder():
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Evento aceptado','¿Repetitivo?':'','Recordatorio':'','Medicamento':'','Nombre_Usuario':Snips.usr,'Error_output':''})
    t()

def NotAceptedReminder():
    writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Evento no aceptado','¿Repetitivo?':'','Recordatorio':'','Medicamento':'','Nombre_Usuario':Snips.usr,'Error_output':''})
    t()

def Error(mensaje):
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Error','¿Repetitivo?':'','Recordatorio':'','Medicamento':'','Nombre_Usuario':'','Error_output':mensaje})
    t()


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        Error('Intent no reconocido')
        return dict()

    #Intent Añadir mdicamento
def subscribe_Anadir_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_Anadir(hermes, intentMessage, conf)

def action_wrapper_Anadir(hermes, intentMessage,conf):
    global Snips
    print(str(intentMessage.slots.Repeticion))
    if(not intentMessage.slots.Repeticion):
        session=intentMessage.session_id
        fecha = intentMessage.slots.Fecha.first().value
        fecha=fecha [ :fecha.index('+')-1 ]
        date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
        med = intentMessage.slots.Medicamento.first().value
        msg=Snips.usr+" está añadiendo un recordatorio para el día  " + str(date.day) + " de " + str(date.month) + " del " + str(date.year) + " a las " + str(date.hour) + minutes(date.minute)+" tomar " + med
        #add_Reminder(med,fecha)
        """now=datetime.now()
        if((date - now).total_seconds()>0):
            t = Timer((date - now).total_seconds(), recordatorio,['default',med,fecha])
            t.start()"""
        e=Event(med,date,Snips.usr,False,'')
        e.IncrementarVeces()
        Snips.addEvent(e)
        add_Reminder(e)
        scheduler.add_job(recordatorio, 'date', run_date=date,id=fecha+','+e.med+','+e.user,args=['default',e])
        hermes.publish_end_session(intentMessage.session_id, msg)
    else:
        session=intentMessage.session_id
        if(intentMessage.slots.cantidad):
            fecha = intentMessage.slots.Fecha.first().value
            fecha=fecha [ :fecha.index('+')-1 ]
            date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
        else:
            fecha=datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")

        med = intentMessage.slots.Medicamento.first().value
        if(not intentMessage.slots.cantidad):
            veces=1
        else:
            veces= int(intentMessage.slots.cantidad.first().value)

        frecuencia=intentMessage.slots.Repeticion.first().value
        if(frecuencia=='diariamente'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' todos los dias empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,'Diario')
            e.IncrementarVeces()
            scheduler.add_job(recordatorio, 'cron',id='Repeticion diaria,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/1',hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e])
        elif(frecuencia=='dia'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' dias empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' dias')
            e.IncrementarVeces()
            scheduler.add_job(recordatorio, 'cron',id='Repeticion cada '+str(veces)+' dias,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/'+str(veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e])             
        elif(frecuencia=='mes'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' meses empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' meses')
            e.IncrementarVeces()
            scheduler.add_job(recordatorio, 'cron',id='Repeticion '+str(veces)+' meses ,'+med+','+Snips.usr,year=date.year,month=str(date.month)+'/'+str(veces),day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e]) 
        elif(frecuencia=='semana'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' semanas empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' semanas')
            e.IncrementarVeces()
            scheduler.add_job(recordatorio, 'cron',id='Repeticion' +str(veces)+' semanas,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/'+str(7*veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e]) 
        elif(frecuencia=='hora'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' horas empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' horas')
            e.IncrementarVeces()
            scheduler.add_job(recordatorio, 'cron',id='Repeticion '+str(veces)+' horas,'+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour=str(date.hour)+'/'+str(veces),minute=date.minute, replace_existing=True, args=['default',e]) 
        elif(frecuencia=='desayuno'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en el desayuno'
            e=Event(med,date,Snips.usr,True,'Desayuno')
            e.IncrementarVeces()
            scheduler.add_job(recordatorio, 'cron',id='Repeticion Desayuno'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='9/1',minute=date.minute, replace_existing=True, args=['default',e]) 
        elif(frecuencia=='comida'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en la comida'
            e=Event(med,date,Snips.usr,True,'Comida')
            e.IncrementarVeces()
            scheduler.add_job(recordatorio, 'cron',id='Repeticion Comida'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='14/1',minute=date.minute, replace_existing=True, args=['default',e]) 
        elif(frecuencia=='cena'): 
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en la cena'
            e=Event(med,date,Snips.usr,True,'Cena')
            e.IncrementarVeces()
            scheduler.add_job(recordatorio, 'cron',id='Repeticion Cena'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='21/1',minute=date.minute, replace_existing=True, args=['default',e]) 
        else:
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+frecuencia+' empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,Repeticion)
            e.IncrementarVeces()
            scheduler.add_job(recordatorio, 'cron',id='Repeticion semanal cada '+frecuencia+','+med+','+Snips.usr,day_of_week=dia_sem(frecuencia),year=date.year,month=date.month,day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e]) 

        Snips.addEvent(e)
        add_Reminder(e)
        hermes.publish_end_session(intentMessage.session_id, msg)

#Intent cambiar usuario
def subscribe_user_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_user(hermes, intentMessage, conf)

def action_wrapper_user(hermes, intentMessage,conf):
    global Snips
    print(str(Snips.usr))
    user = intentMessage.slots.user.first().value
    if(Snips.existUser):
        msg="Cambio de usuario a "+user
        Snips.usr=user
        Change_User(user)
    else:
        msg="El usuario "+user+" no existe"
    hermes.publish_end_session(intentMessage.session_id, msg)

def subscribe_AnadirUsuario_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_AnadirUsuario(hermes, intentMessage, conf)

def action_wrapper_AnadirUsuario(hermes, intentMessage,conf):
    global Snips
    print(str(Snips.usr))
    user = intentMessage.slots.user.first().value
    if(not Snips.existUser):
        msg="Añadiendo usuario "+user +' y cambio a dicho usuario'
        Snips.usr=user
        Snips.addUser(user)
        Add_User(user)
    else:
        msg="El usuario "+user+" ya existe"
    hermes.publish_end_session(intentMessage.session_id, msg)

def subscribe_CheckUsuario_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_CheckUsuario(hermes, intentMessage, conf)

def action_wrapper_CheckUsuario(hermes, intentMessage,conf):
    global Snips
    print(str(Snips.usr))
    msg="El usuario activo es "+Snips.usr
    hermes.publish_end_session(intentMessage.session_id, msg)
    

def subscribe_confirmar_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_Confirmar(hermes, intentMessage, conf)

def action_wrapper_Confirmar(hermes, intentMessage,conf):
    global Snips   
    #msg="Evento aceptado por "+e.user
    msg="Evento aceptado"
    AceptedReminder()

    hermes.publish_end_session(intentMessage.session_id, msg)
    scheduler1.remove_job('job2')

def subscribe_Negar_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_Negar(hermes, intentMessage, conf)

def action_wrapper_Negar(hermes, intentMessage,conf):
    msg="Evento no aceptado por "+Snips.usr+" se te volverá ha avisar en 20 segundos"
    NotAceptedReminder()
    hermes.publish_end_session(intentMessage.session_id, msg)

def say(intentMessage,text):
    mqttClient.publish_start_session_notification(intentMessage, text,None)

    
def recordatorio(intentMessage,e):
    print('Evento detectado para : %s' % datetime.now())
    if(e.user==Snips.usr):
        say(intentMessage,e.user+' te toca tomarte '+e.med)
        scheduler1.add_job(recordatorioTomar, 'interval', seconds=20,id='job2',args=[e,intentMessage])
        Reminder(e)
   

def recordatorioTomar(e,intentMessage):
    global Snips
    if(e.user==Snips.usr):
        if(e.veces<6):
            mqttClient.publish_start_session_action(site_id=intentMessage,
            session_init_text=e.user+'¿ te has tomado ' +e.med+'?',
            session_init_intent_filter=["caguilary:Confirmar","caguilary:Negar"],
            session_init_can_be_enqueued=False,
            session_init_send_intent_not_recognized=True,
            custom_data=None)
            Reminder(e)
            msg=""
            print(e.user+'¿te has tomado ' +e.med+'?:Vez '+str(e.veces))
            Snips.Incrementar(e) 
            e.IncrementarVeces()    
            mqttClient.publish_end_session(intentMessage, msg)  
        else:
            msg=e.user+'ha ignorado el evento tomar '+e.med
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

    with Hermes(mqtt_options=mqtt_opts) as h,Hermes(mqtt_options=mqtt_opts) as mqttClient,open('prueba.csv', 'a+') as csvfile:
        fieldnames = ['timestamp','id','Tipo', '¿Repetitivo?','Recordatorio','Medicamento','Nombre_Usuario','Error_output']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        h\
        .subscribe_intent("caguilary:Anadir", subscribe_Anadir_callback) \
        .subscribe_intent("caguilary:user", subscribe_user_callback) \
        .subscribe_intent("caguilary:Confirmar", subscribe_confirmar_callback) \
        .subscribe_intent("caguilary:Negar", subscribe_Negar_callback) \
        .subscribe_intent("caguilary:Anadir_usuario", subscribe_AnadirUsuario_callback) \
        .subscribe_intent("caguilary:userActivo", subscribe_CheckUsuario_callback) \
        .start()