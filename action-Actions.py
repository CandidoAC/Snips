#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import io
import configparser
import os
from datetime import datetime
from datetime import timedelta
from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes 
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
from Events import Snips
from Evento import Event
 
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
def global_variables():
    global Recordatorio,e,Snips
    Snips=Snips();

def read_configuration_file(configuration_file):
    global Snips
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        Snips.Error('Intent no reconocido')
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
        Snips.add_Reminder(e)
        Snips.scheduler.add_job(Snips.recordatorio, 'date', run_date=date,id=fecha+','+e.med+','+e.user,args=['default',e,False])
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
            Snips.scheduler.add_job(Snips.recordatorio, 'cron',id='Repeticion diaria,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/1',hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True])
        elif(frecuencia=='dia'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' dias empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' dias')
            e.IncrementarVeces()
            Snips.scheduler.add_job(Snips.recordatorio, 'cron',id='Repeticion cada '+str(veces)+' dias,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/'+str(veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True])             
        elif(frecuencia=='mes'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' meses empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' meses')
            e.IncrementarVeces()
            Snips.scheduler.add_job(Snips.recordatorio, 'cron',id='Repeticion '+str(veces)+' meses ,'+med+','+Snips.usr,year=date.year,month=str(date.month)+'/'+str(veces),day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True]) 
        elif(frecuencia=='semana'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' semanas empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' semanas')
            e.IncrementarVeces()
            Snips.scheduler.add_job(Snips.recordatorio, 'cron',id='Repeticion' +str(veces)+' semanas,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/'+str(7*veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True]) 
        elif(frecuencia=='hora'):
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' horas empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,str(veces)+' horas')
            e.IncrementarVeces()
            Snips.scheduler.add_job(Snips.recordatorio, 'cron',id='Repeticion '+str(veces)+' horas,'+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour=str(date.hour)+'/'+str(veces),minute=date.minute, replace_existing=True, args=['default',e,True]) 
        elif(frecuencia=='desayuno'):#HORA-1
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en el desayuno'
            e=Event(med,date,Snips.usr,True,'Desayuno')
            e.IncrementarVeces()
            Snips.scheduler.add_job(Snips.recordatorio, 'cron',id='Repeticion Desayuno'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='8/1',minute=0, replace_existing=True, args=['default',e,True]) 
        elif(frecuencia=='comida'):#HORA-1
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en la comida'
            e=Event(med,date,Snips.usr,True,'Comida')
            e.IncrementarVeces()
            Snips.scheduler.add_job(Snips.recordatorio, 'cron',id='Repeticion Comida'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='13/1',minute=0, replace_existing=True, args=['default',e,True]) 
        elif(frecuencia=='cena'): #HORA-1
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en la cena'
            e=Event(med,date,Snips.usr,True,'Cena')
            e.IncrementarVeces()
            Snips.scheduler.add_job(Snips.recordatorio, 'cron',id='Repeticion Cena'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='20/1',minute=0, replace_existing=True, args=['default',e,True]) 
        else:
            msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+frecuencia+' empezando '+str(fecha)
            e=Event(med,date,Snips.usr,True,Repeticion)
            e.IncrementarVeces()
            Snips.scheduler.add_job(Snips.Snips.recordatorio, 'cron',id='Repeticion semanal cada '+frecuencia+','+med+','+Snips.usr,day_of_week=dia_sem(frecuencia),year=date.year,month=date.month,day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True]) 

        Snips.addEvent(e)
        Snips.add_Reminder(e)
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
        Snips.Change_User(user)
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
        Snips.Add_User(user)
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
    Snips.AceptedReminder()
    event=snips.lastEventReminder()
    if(event):
        snips.FinishEvent(event)

    hermes.publish_end_session(intentMessage.session_id, msg)
    Snips.scheduler1.remove_job('job2')

def subscribe_Negar_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI) 
    action_wrapper_Negar(hermes, intentMessage, conf)

def action_wrapper_Negar(hermes, intentMessage,conf):
    global Snips
    msg="Evento no aceptado por "+Snips.usr+" se te volverá ha avisar en 20 segundos"
    Snips.NotAceptedReminder()
    hermes.publish_end_session(intentMessage.session_id, msg)

    

if __name__ == '__main__':
    mqtt_opts = MqttOptions()
    global_variables()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h\
        .subscribe_intent("caguilary:Anadir", subscribe_Anadir_callback) \
        .subscribe_intent("caguilary:user", subscribe_user_callback) \
        .subscribe_intent("caguilary:Confirmar", subscribe_confirmar_callback) \
        .subscribe_intent("caguilary:Negar", subscribe_Negar_callback) \
        .subscribe_intent("caguilary:Anadir_usuario", subscribe_AnadirUsuario_callback) \
        .subscribe_intent("caguilary:userActivo", subscribe_CheckUsuario_callback) \
        .start()