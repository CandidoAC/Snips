#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import io
import configparser
import os
import csv
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
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Evento no aceptado','¿Repetitivo?':'','Recordatorio':'','Medicamento':'','Nombre_Usuario':Snips.usr,'Error_output':''})
    t()

def Error(mensaje):
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    writer.writerow({'timestamp':date,'id': str(idFile),'Tipo':'Error','¿Repetitivo?':'','Recordatorio':'','Medicamento':'','Nombre_Usuario':'','Error_output':mensaje})
    t()

def lastEventReminder():
        aux=None
        with open('prueba.csv', 'r') as csvfile:
            myreader = csv.DictReader(csvfile)
            headers = myreader.fieldnames
            for row in myreader:
                print(row[headers[2]])
                if(row['Tipo']=='Recordatorio'):
                   aux=row
            if(aux):     
                if(aux['¿Repetitivo?']=='Si'):
                    e=Event(aux['Medicamento'],None,aux['Nombre_Usuario'],True,aux['Recordatorio'])
                else:
                    e=Event(aux['Medicamento'],aux['Recordatorio'],aux['Nombre_Usuario'],False,None)
                return e
            else:
                return None


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
        Snips.scheduler.add_job(recordatorio, 'date', run_date=date,id=fecha+','+e.med+','+e.user,args=['default',e,False])
        hermes.publish_end_session(intentMessage.session_id, msg)
    else:
        session=intentMessage.session_id
        if(intentMessage.slots.Fecha): 
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
            e=Event(med,date,Snips.usr,True,'1 dias')
            e.IncrementarVeces()
            Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion diaria,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/1',hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True])
        elif(frecuencia=='dia'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' dias empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' dias')
            e.IncrementarVeces()
            Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion cada '+str(veces)+' dias,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/'+str(veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True])             
        elif(frecuencia=='mes'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' meses empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' meses')
            e.IncrementarVeces()
            Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion '+str(veces)+' meses ,'+med+','+Snips.usr,year=date.year,month=str(date.month)+'/'+str(veces),day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True]) 
        elif(frecuencia=='semana'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' semanas empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' semanas')
            e.IncrementarVeces()
            Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion' +str(veces)+' semanas,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/'+str(7*veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True]) 
        elif(frecuencia=='hora'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' horas empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' horas')
            e.IncrementarVeces() 
            Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion '+str(veces)+' horas,'+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour=str(date.hour)+'/'+str(veces),minute=date.minute, replace_existing=True, args=['default',e,True]) 
        elif(frecuencia=='desayuno'):#HORA-1
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en el desayuno'
            e=Event(med,date,Snips.usr,True,'Desayuno')
            e.IncrementarVeces()
            Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion Desayuno'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='8/1',minute=0, replace_existing=True, args=['default',e,True]) 
        elif(frecuencia=='comida'):#HORA-1
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en la comida'
            e=Event(med,date,Snips.usr,True,'Comida')
            e.IncrementarVeces()
            Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion Comida'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='13/1',minute=0, replace_existing=True, args=['default',e,True]) 
        elif(frecuencia=='cena'): #HORA-1
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en la cena'
            e=Event(med,date,Snips.usr,True,'Cena')
            e.IncrementarVeces()
            Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion Cena'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='20/1',minute=0, replace_existing=True, args=['default',e,True]) 
        else:
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+frecuencia+' empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,Repeticion)
            e.IncrementarVeces()
            Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion semanal cada '+frecuencia+','+med+','+Snips.usr,day_of_week=dia_sem(frecuencia),year=date.year,month=date.month,day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True]) 

        Snips.addEvent(e)
        add_Reminder(e)
        hermes.publish_end_session(intentMessage.session_id, msg)

#Intent cambiar usuario
def subscribe_user_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_user(hermes, intentMessage, conf)

def action_wrapper_user(hermes, intentMessage,conf):
    global Snips
    user = intentMessage.slots.user.first().value
    if(Snips.existUser(user)):
        msg="Cambio de usuario a "+user
        Snips.changeActiveUsers(user)
        Change_User(user)
    else:
        msg="El usuario "+user+" no existe"
    hermes.publish_end_session(intentMessage.session_id, msg)

def subscribe_AnadirUsuario_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_AnadirUsuario(hermes, intentMessage, conf)

def action_wrapper_AnadirUsuario(hermes, intentMessage,conf):
    global Snips
    user = intentMessage.slots.user.first().value
    if(not Snips.existUser(user)):
        msg="Añadiendo usuario "+user +' y cambio a dicho usuario'
        Snips.addUser(user)
        Snips.changeActiveUsers(user)
        Add_User(user)
    else:
        msg="El usuario "+user+" ya existe"
    hermes.publish_end_session(intentMessage.session_id, msg)

def subscribe_CheckUsuario_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_CheckUsuario(hermes, intentMessage, conf)

def action_wrapper_CheckUsuario(hermes, intentMessage,conf):
    global Snips
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
    event=lastEventReminder()
    if(event):
        Snips.FinishEvent(event)

    hermes.publish_end_session(intentMessage.session_id, msg)
    Snips.scheduler1.remove_job('job2')

def subscribe_Negar_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_Negar(hermes, intentMessage, conf)

def action_wrapper_Negar(hermes, intentMessage,conf):
    msg="Evento no aceptado por "+Snips.usr+" se te volverá ha avisar en 20 segundos"
    NotAceptedReminder()
    hermes.publish_end_session(intentMessage.session_id, msg)

def say(intentMessage,text):
    mqttClient.publish_start_session_notification(intentMessage, text,None) 

    
def recordatorio(intentMessage,e,Repetitivo):
    global Snips
    print('Evento detectado para : %s' % datetime.now())
    if(e.user==Snips.usr):
        if(Repetitivo):
            Snips.NingunaVeces(e)
        say(intentMessage,e.user+' te toca tomarte '+e.med)
        Snips.scheduler1.add_job(recordatorioTomar, 'interval', seconds=20,id='job2',args=[e,intentMessage])
        Reminder(e)
   

def recordatorioTomar(e,intentMessage):
    global Snips
    if(e.user==Snips.usr):
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
            Snips.Incrementar(e) 
            e.IncrementarVeces()    
            mqttClient.publish_end_session(intentMessage, msg)  
        else:
            msg=e.user+'ha ignorado el evento tomar '+e.med
            say(intentMessage,msg)
            Snips.scheduler1.remove_job('job2')
            Snips.FinishEvent(e)
            mqttClient.publish_end_session(intentMessage, msg)
    else:
        print("Usuario actual distinto al del evento")
        Snips.scheduler1.remove_job('job2')

if __name__ == '__main__':
    mqtt_opts = MqttOptions()
    idFile=0
    global_variables()
    with Hermes(mqtt_options=mqtt_opts) as h,Hermes(mqtt_options=mqtt_opts) as mqttClient,open('/prueba.csv', 'a+') as csvfile:
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