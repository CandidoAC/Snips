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
import threading
import RPi.GPIO as GPIO
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
 
def global_variables():
    global Recordatorio,e,Snips
    Snips=Snips()

def lastEventReminderByUser():
        aux=None
        with open('/home/pi/Reporte.csv', 'r') as csvfile:
            myreader = csv.DictReader(csvfile)
            headers = myreader.fieldnames
            listaRec=[]
            for row in myreader:
                #print(row[headers[2]])
                if(row['Nombre_Usuario']==Snips.usr and row['Tipo']=='Recordatorio'):
                   listaRec.append(row)
            print(*listaRec)
            for row in listaRec:
                    if(row['¿Repetitivo?']=='Si'):
                        e=Event(row['Medicamento'],datetime.strptime(row['Fecha'],"%Y-%m-%d %H:%M:%S"),row['Nombre_Usuario'],True,row['Frecuencia'])
                        print(e)
                        if(Snips.eventActive(e)):
                            aux=e
                    else:
                        e=Event(row['Medicamento'],datetime.strptime(row['Fecha'],"%Y-%m-%d %H:%M:%S"),row['Nombre_Usuario'],False,None)
                        print(e)
                        if(Snips.eventActive(e)):
                            aux=e
            print('Va a aceptar '+aux.__str__())
            if(aux):
                return aux
            else:
                return None


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        Snips.log(None,'','','Error','Intent no reconocido')
        return dict()

    #Intent Añadir mdicamento
def subscribe_Anadir_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_Anadir(hermes, intentMessage, conf)

def action_wrapper_Anadir(hermes, intentMessage,conf):
    global Snips
    #print(str(intentMessage.slots.Repeticion))
    if(not intentMessage.slots.Repeticion):
        session=intentMessage.session_id
        if(intentMessage.slots.Fecha):
	        fecha = intentMessage.slots.Fecha.first().value
	        fecha=fecha [ :fecha.index('+')-1 ] 
	        date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
	        if(datetime.now() < date):
	            med = intentMessage.slots.Medicamento.first().value 
	            msg=Snips.usr+" está añadiendo un recordatorio para el día  " + str(date.day) + " de " + str(date.month) + " del " + str(date.year) + " a las " + str(date.hour) + minutes(date.minute)+" tomar " + med
	            e=Event(med,date,Snips.usr,False,'')
	            if(not Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                Snips.addEvent(e)
	                Snips.log(e,Snips.usr,'','Añadir_Evento','')
	                Snips.scheduler.add_job(recordatorio, 'date', run_date=date,id=str(e.fecha)+','+e.med+','+e.user,args=['default',e,False,Snips])
	            else:
	                msg='Evento a crear ya existe'
	                Snips.log(None,'','','Error',msg)
	        else:
	            msg='La fecha introducida ya ha pasado. Vuelve a introducir el comando'
        else:
	        msg='Fecha errónea. Vuelve a introducir el comando'
    else:
        session=intentMessage.session_id
        if(intentMessage.slots.Fecha): 
            fecha = intentMessage.slots.Fecha.first().value
            fecha=fecha [ :fecha.index('+')-1 ]
            date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
        else:
            fecha=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0).strftime("%Y-%m-%d %H:%M")
            date=datetime.strptime(fecha,"%Y-%m-%d %H:%M")

        med = intentMessage.slots.Medicamento.first().value
        if(not intentMessage.slots.cantidad):
            veces=1
        else:
            veces= int(intentMessage.slots.cantidad.first().value)
        if (veces==0):
            msg='No se puede crear un evento repetitivo con cantidad  igual a 0.'
        else:
            frecuencia=intentMessage.slots.Repeticion.first().value
            if(frecuencia=='diariamente'):
                msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' todos los dias empezando '+str(fecha)
                e=Event(med,date,Snips.usr,True,'1 dia')
                if(not Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion diaria,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/1',hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True,Snips])
	                Snips.addEvent(e)
	                Snips.log(e,Snips.usr,'','Añadir_Evento','')
                else:
                    msg='Evento a crear ya existe' 
                    Snips.log(None,'','','Error',msg)
            elif(frecuencia=='dia'):
                if(veces>30):
                    msg="No se puede crear un evento repetitivo con cant mayor a 30 días."
                else:
                    msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' dias empezando '+str(fecha)
                    e=Event(med,date,Snips.usr,True,str(veces)+' dia')
                    if(not Snips.ExistsEvent(e)):
	                    e.IncrementarVeces()
	                    Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion cada '+str(veces)+' dias,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/'+str(veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True,Snips])             
	                    Snips.addEvent(e)
	                    Snips.log(e,Snips.usr,'','Añadir_Evento','')
                    else:
                        msg='Evento a crear ya existe' 	 
                        Snips.log(None,'','','Error',msg)                  
            elif(frecuencia=='mes'):
                if(veces>11):
                    msg="No se puede crear un evento repetitivo con cant igual o mayor que 11 meses"
                else:
                    msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' meses empezando '+str(fecha)
                    e=Event(med,date,Snips.usr,True,str(veces)+' mes')
                    if(not Snips.ExistsEvent(e)):
	                    e.IncrementarVeces()
	                    Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion '+str(veces)+' meses ,'+med+','+Snips.usr,year=date.year,month=str(date.month)+'/'+str(veces),day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True,Snips]) 
	                    Snips.addEvent(e)
	                    Snips.log(e,Snips.usr,'','Añadir_Evento','')
                    else:
                        msg='Evento a crear ya existe' 	
                        Snips.log(None,'','','Error',msg)                 
            elif(frecuencia=='semana'):
                if(veces>30):
                    msg="No se puede crear un evento repetitivo con cant mayor a 30 semanas."
                else:
                    msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' semanas empezando '+str(fecha)
                    e=Event(med,date,Snips.usr,True,str(veces)+' semana')
                    if(not Snips.ExistsEvent(e)):
	                    e.IncrementarVeces()
	                    Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion ' +str(veces)+' semanas,'+med+','+Snips.usr,year=date.year,month=date.month,day=str(date.day)+'/'+str(7*veces),hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True,Snips]) 
	                    Snips.addEvent(e)
	                    Snips.log(e,Snips.usr,'','Añadir_Evento','')
                    else:
                        msg='Evento a crear ya existe'
                        Snips.log(None,'','','Error',msg)                    
            elif(frecuencia=='hora'):
                if(veces>23):
                    msg="No se puede crear un evento repetitivo con cant sea 23 o más."
                else:
                    msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' horas empezando '+str(fecha)
                    e=Event(med,date,Snips.usr,True,str(veces)+' hora')
                    if(not Snips.ExistsEvent(e)):
	                    e.IncrementarVeces() 
	                    Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion '+str(veces)+' horas,'+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour=str(date.hour)+'/'+str(veces),minute=date.minute, replace_existing=True, args=['default',e,True,Snips]) 
	                    Snips.addEvent(e)
	                    Snips.log(e,Snips.usr,'','Añadir_Evento','')
                    else:
                        msg='Evento a crear ya existe' 	    
                        Snips.log(None,'','','Error',msg)                
            elif(frecuencia=='desayuno'):#HORA-1
                msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en el desayuno'
                e=Event(med,date,Snips.usr,True,'desayuno')
                if(not Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion Desayuno'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='8/1',minute=0, replace_existing=True, args=['default',e,True,Snips]) 
	                Snips.addEvent(e)
	                Snips.log(e,Snips.usr,'','Añadir_Evento','')
                else:
                    msg='Evento a crear ya existe'
                    Snips.log(None,'','','Error',msg) 	                
            elif(frecuencia=='comida'):#HORA-1
                msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en la comida'
                e=Event(med,date,Snips.usr,True,'comida')
                if(not Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion Comida'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='13/1',minute=0, replace_existing=True, args=['default',e,True,Snips]) 
	                Snips.addEvent(e)
	                Snips.log(e,Snips.usr,'','Añadir_Evento','')
                else:
                    msg='Evento a crear ya existe'
                    Snips.log(None,'','','Error',msg) 	              
            elif(frecuencia=='cena'): #HORA-1
                msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' en la cena'
                e=Event(med,date,Snips.usr,True,'cena')
                if(not Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion Cena'+','+med+','+Snips.usr,year=date.year,month=date.month,day=date.day,hour='20/1',minute=0, replace_existing=True, args=['default',e,True,Snips]) 
	                Snips.addEvent(e)
	                Snips.log(e,Snips.usr,'','Añadir_Evento','')
                else:
                    msg='Evento a crear ya existe'
                    Snips.log(None,'','','Error',msg) 	                
            else:
                msg=Snips.usr+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' '+frecuencia+' empezando '+str(fecha)
                e=Event(med,date,Snips.usr,True,str(veces)+' '+frecuencia)
                if(not Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                Snips.scheduler.add_job(recordatorio, 'cron',id='Repeticion semanal cada '+frecuencia+','+med+','+Snips.usr,day_of_week=Snips.dia_sem(frecuencia),year=date.year,month=date.month,day=date.day,hour=date.hour,minute=date.minute, replace_existing=True, args=['default',e,True,Snips]) 
	                Snips.addEvent(e)
	                Snips.log(e,Snips.usr,'','Añadir_Evento','')
                else:
                    msg='Evento a crear ya existe' 
                    Snips.log(None,'','','Error',msg)
    hermes.publish_end_session(intentMessage.session_id, msg)

#Intent cambiar usuario
def subscribe_user_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_user(hermes, intentMessage, conf)

def action_wrapper_user(hermes, intentMessage,conf):
    global Snips
    user = intentMessage.slots.user.first().value
    if(Snips.existUser(user)):
        if(Snips.UserActive()!=user):
            msg="Cambio de usuario a "+user
            Snips.changeActiveUsers(user)
            Snips.log(None,user,'','Cambio_Usuario','')
        else:
            msg=msg="El usuario "+user+" ya es el actual"
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
        Snips.log(None,user,'','Añadir_Usuario','')
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
    
def exist_Job1(job):
    enc=False
    if(Snips.scheduler1.get_jobs()):
        for x in Snips.scheduler1.get_jobs():
            if(x.__eq__(job)):
                return True
    return enc 

def exist_Job(job):
    enc=False
    if(Snips.scheduler.get_jobs()):
        for x in Snips.scheduler.get_jobs():
            if(x.__eq__(job)):
                return True
    return enc

def subscribe_confirmar_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_Confirmar(hermes, intentMessage, conf)

def action_wrapper_Confirmar(hermes, intentMessage,conf):
    global Snips   
    #msg="Evento aceptado por "+e.user
    #msg="Evento aceptado por "+Snips.usr
    Snips.log(None,Snips.usr,'Voz','Evento aceptado','')
    event=lastEventReminderByUser()
    print(event.__str__())
    if(event):
        if(Snips.eventActive(event)):
            msg='Aceptando '+event.__str__()
            if(not event.rep):
                Snips.FinishEvent(event)
                job='Evento no repetitivo: recordando tomar '+event.med+' a '+event.user
            else:
                Snips.NingunaVez(event)
                job='Evento repetitivo: recordando tomar '+event.med+' a '+event.user+' cada '+event.when 
            if(exist_Job1(job)):
                Snips.scheduler1.remove_job(job)
                hermes.publish_end_session(intentMessage.session_id, msg)
        else:
            hermes.publish_end_session(intentMessage.session_id, 'No existe ningún recordatorio a confirmar')
    else:
        hermes.publish_end_session(intentMessage.session_id, 'No existe ningún recordatorio a confirmar')


def subscribe_Negar_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_Negar(hermes, intentMessage, conf)

def action_wrapper_Negar(hermes, intentMessage,conf):
    msg="Evento no aceptado por "+Snips.usr+" se te volverá ha avisar en 20 segundos"
    Snips.log(None,Snips.usr,'','Evento no aceptado','')
    hermes.publish_end_session(intentMessage.session_id, msg)

def subscribe_Borrar_callback(hermes, intentMessage):
    #print('Borrando evento_callback')
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_Borrar(hermes, intentMessage, conf)

def action_wrapper_Borrar(hermes, intentMessage,conf):
    #print('Borrando evento')
    if(not intentMessage.slots.Repeticion):
        session=intentMessage.session_id
        if(intentMessage.slots.Fecha):
	        fecha = intentMessage.slots.Fecha.first().value
	        fecha=fecha [ :fecha.index('+')-1 ] 
	        date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
	        med = intentMessage.slots.Medicamento.first().value 
	        msg=Snips.usr+" está borrando el recordatorio para el día  " + str(date.day) + " de " + str(date.month) + " del " + str(date.year) + " a las " + str(date.hour) + minutes(date.minute)+" tomar " + med
	        e=Event(med,date,Snips.usr,False,'')
	        if(Snips.ExistsEvent(e)):
		        e.IncrementarVeces()
		        print('Evento a borrar: tomar '+str(e))
		        Snips.borrarEvento(e)
		        Snips.log(e,Snips.usr,'','Borrar_Evento','')
		        job=fecha+','+e.med+','+e.user
		        if(exist_Job(job)):
		            Snips.scheduler.remove_job(job)

		        job='Evento no repetitivo: recordando tomar '+e.med+' a '+e.user
		        if(exist_Job1(job)):
		            Snips.scheduler1.remove_job(job)
	        else:
		        msg='Evento a borrar no existe'
		        Snips.log(None,'','','Error',msg)  
        else:
            msg='Fecha errónea. Vuelve a introducir el comando'
        hermes.publish_end_session(intentMessage.session_id, msg)
    else:
        print('Borrando evento rep')
        session=intentMessage.session_id
        if(intentMessage.slots.Fecha): 
            fecha = intentMessage.slots.Fecha.first().value
            fecha=fecha [ :fecha.index('+')-1 ]
            date=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
        else:
            fecha=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0).strftime("%Y-%m-%d %H:%M")
            date=datetime.strptime(fecha,"%Y-%m-%d %H:%M")

        med = intentMessage.slots.Medicamento.first().value
        if(not intentMessage.slots.cantidad):
            veces=1
        else:
            veces= int(intentMessage.slots.cantidad.first().value)
        if (veces==0):
            msg='No se puede borrar un evento repetitivo con cantidad igual a 0.'
        else:
            frecuencia=intentMessage.slots.Repeticion.first().value

            if(frecuencia=='diariamente'):
                msg=Snips.usr+" está borrando un recordatorio para tomar "+med+' todos los dias empezando '+str(fecha)
                e=Event(med,date,Snips.usr,True,'1 dia')
                print(e)
                if(Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                job='Repeticion diaria,'+med+','+Snips.usr
	                Snips.borrarEvento(e)
	                Snips.log(e,Snips.usr,'','Borrar_Evento','')
	                if(exist_Job(job)):
	                    Snips.scheduler.remove_job(job)

	                job='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when
	                if(exist_Job1(job)):
	                    Snips.scheduler1.remove_job(job)
                else:
                    msg='Evento a borrar no existe' 
                    Snips.log(None,'','','Error',msg)  

            elif(frecuencia=='dia'):
                if(veces>30):
                    msg="No se puede borrar un evento repetitivo con cant mayor a 30 días."
                else:
                    msg=Snips.usr+" está borrando un recordatorio para tomar "+med+' cada '+str(veces)+' dias empezando '+str(fecha)
                    e=Event(med,date,Snips.usr,True,str(veces)+' dia')
                    if(Snips.ExistsEvent(e)):
	                    e.IncrementarVeces()
	                    job='Repeticion cada '+str(veces)+' dias,'+med+','+Snips.usr
	                    Snips.borrarEvento(e)
	                    Snips.log(e,Snips.usr,'','Borrar_Evento','')
	                    if(exist_Job(job)):
	                        Snips.scheduler.remove_job(job)

	                    job='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when
	                    if(exist_Job1(job)):
	                        Snips.scheduler1.remove_job(job) 
                    else:
                        msg='Evento a borrar no existe' 
                        Snips.log(None,'','','Error',msg)  

            elif(frecuencia=='mes'):
                if(veces>11):
                    msg="No se puede borrar un evento repetitivo con cant igual o mayor que 11 meses"
                else:
                    msg=Snips.usr+" está borrando un recordatorio para tomar "+med+' cada '+str(veces)+' meses empezando '+str(fecha)
                    e=Event(med,date,Snips.usr,True,str(veces)+' mes')
                    if(Snips.ExistsEvent(e)):
	                    e.IncrementarVeces()
	                    job='Repeticion '+str(veces)+' meses ,'+med+','+Snips.usr
	                    Snips.borrarEvento(e)
	                    Snips.log(e,Snips.usr,'','Borrar_Evento','')
	                    if(exist_Job(job)):
	                        Snips.scheduler.remove_job(job)

	                    job='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when
	                    if(exist_Job1(job)):
	                        Snips.scheduler1.remove_job(job)
                    else:
                        msg='Evento a borrar no existe'  
                        Snips.log(None,'','','Error',msg)  	                       
            elif(frecuencia=='semana'):
                if(veces>30):
                    msg="No se puede borrar un evento repetitivo con cant mayor a 30 semanas."
                else:
                    msg=Snips.usr+" está borrando un recordatorio para tomar "+med+' cada '+str(veces)+' semanas empezando '+str(fecha)
                    e=Event(med,date,Snips.usr,True,str(veces)+' semana')
                    if(Snips.ExistsEvent(e)):
	                    e.IncrementarVeces()
	                    job='Repeticion ' +str(veces)+' semanas,'+med+','+Snips.usr
	                    Snips.borrarEvento(e)
	                    Snips.log(e,Snips.usr,'','Borrar_Evento','')
	                    if(exist_Job(job)):
	                        Snips.scheduler.remove_job(job)

	                    job='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when
	                    if(exist_Job1(job)):
	                        Snips.scheduler1.remove_job(job)
                    else:
                        msg='Evento a borrar no existe'
                        Snips.log(None,'','','Error',msg)       

            elif(frecuencia=='hora'):
                if(veces>23):
                    msg="No se puede borrar un evento repetitivo con cant sea 23 horas o más."
                else:
                    msg=Snips.usr+" está borrando un recordatorio para tomar "+med+' cada '+str(veces)+' horas empezando '+str(fecha)
                    e=Event(med,date,Snips.usr,True,str(veces)+' hora')
                    if(Snips.ExistsEvent(e)):
	                    e.IncrementarVeces() 
	                    job='Repeticion '+str(veces)+' horas,'+med+','+Snips.usr
	                    Snips.borrarEvento(e)
	                    Snips.log(e,Snips.usr,'','Borrar_Evento','')
	                    if(exist_Job(job)):
	                        Snips.scheduler.remove_job(job)

	                    job='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when
	                    if(exist_Job1(job)):
	                        Snips.scheduler1.remove_job(job)
                    else:
                        msg='Evento a borrar no existe' 
                        Snips.log(None,'','','Error',msg)  
				            
            elif(frecuencia=='desayuno'):#HORA-1
                msg=Snips.usr+" está borrando un recordatorio para tomar "+med+' en el desayuno'
                e=Event(med,date,Snips.usr,True,'desayuno')
                if(Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                job='Repeticion Desayuno'+','+med+','+Snips.usr
	                Snips.borrarEvento(e)
	                Snips.log(e,Snips.usr,'','Borrar_Evento','')
	                if(exist_Job(job)):
	                    Snips.scheduler.remove_job(job)

	                job='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when
	                if(exist_Job1(job)):
	                    Snips.scheduler1.remove_job(job) 
                else:
                    msg='Evento a borrar no existe'
                    Snips.log(None,'','','Error',msg)        

            elif(frecuencia=='comida'):#HORA-1
                msg=Snips.usr+" está borrando un recordatorio para tomar "+med+' en la comida'
                e=Event(med,date,Snips.usr,True,'comida')
                if(Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                job='Repeticion Comida'+','+med+','+Snips.usr
	                Snips.borrarEvento(e)
	                Snips.log(e,Snips.usr,'','Borrar_Evento','')
	                if(exist_Job(job)):
	                    Snips.scheduler.remove_job(job)

	                job='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when
	                if(exist_Job1(job)):
	                    Snips.scheduler1.remove_job(job)
                else:
                    msg='Evento a borrar no existe' 
                    Snips.log(None,'','','Error',msg)  

            elif(frecuencia=='cena'): #HORA-1
                msg=Snips.usr+" está borrando un recordatorio para tomar "+med+' en la cena'
                e=Event(med,date,Snips.usr,True,'cena')
                if(Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                job='Repeticion Cena'+','+med+','+Snips.usr
	                Snips.borrarEvento(e)
	                Snips.log(e,Snips.usr,'','Borrar_Evento','')
	                if(exist_Job(job)):
	                    Snips.scheduler.remove_job(job)

	                job='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when
	                if(exist_Job1(job)):
	                    Snips.scheduler1.remove_job(job)
                else:
                    msg='Evento a borrar no existe' 
                    Snips.log(None,'','','Error',msg)        
            else:
                msg=Snips.usr+" está borrando un recordatorio para tomar "+med+' cada '+str(veces)+' '+frecuencia+' empezando '+str(fecha)
                e=Event(med,date,Snips.usr,True,str(veces)+' '+frecuencia)
                if(Snips.ExistsEvent(e)):
	                e.IncrementarVeces()
	                job='Repeticion semanal cada '+frecuencia+','+med+','+Snips.usr
	                Snips.borrarEvento(e)
	                Snips.log(e,Snips.usr,'','Borrar_Evento','')
	                if(exist_Job(job)):
	                    Snips.scheduler.remove_job(job)

	                job='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when
	                if(exist_Job1(job)):
	                    Snips.scheduler1.remove_job(job)
                else:
                    msg='Evento a borrar no existe' 
                    Snips.log(None,'','','Error',msg)  

        hermes.publish_end_session(intentMessage.session_id, msg)

def say(intentMessage,text):
    with Hermes(mqtt_options=MqttOptions()) as mqttClient:
        mqttClient.publish_start_session_notification(intentMessage, text,None) 
        
def recordatorio(intentMessage,e,Repetitivo,Snips):
    print('Evento detectado para : %s' % datetime.now())
    if(e.user==Snips.usr):
        say(intentMessage,e.user+' te toca tomarte '+e.med)
        Snips.log(e,Snips.usr,'','Recordatorio','')
        if(e.rep):
        	Snips.scheduler1.add_job(recordatorioTomar, 'interval', seconds=40,id='Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when,args=[e,intentMessage,Snips])
        else:
            Snips.scheduler1.add_job(recordatorioTomar, 'interval', seconds=40,id='Evento no repetitivo: recordando tomar '+e.med+' a '+e.user,args=[e,intentMessage,Snips])

   

def recordatorioTomar(e,intentMessage,Snips):
    if(Snips.eventActive(e)):
        if(e.user==Snips.usr):
            with Hermes(mqtt_options=MqttOptions()) as mqttClient:  
                if(e.veces<6):
                    Snips.log(e,Snips.usr,'','Recordatorio','')
                    mqttClient.publish_start_session_action(site_id=intentMessage,
                    session_init_text=e.user+'¿ te has tomado ' +e.med+'?',
                    session_init_intent_filter=["caguilary:Confirmar","caguilary:Negar"],
                    session_init_can_be_enqueued=True,
                    session_init_send_intent_not_recognized=True,
                    custom_data=None)
                    msg=""
                    print(e.user+'¿te has tomado ' +e.med+'?:Vez '+str(e.veces))
                    Snips.Incrementar(e) 
                    e.IncrementarVeces()    
                    mqttClient.publish_end_session(intentMessage, msg)  
                else:
                    msg=e.user+' ha ignorado el evento tomar '+e.med
                    say(intentMessage,msg)
                    if(not e.rep):
                        Snips.FinishEvent(e)
                    else:
                        Snips.NingunaVez(e)
                    if(e.rep):
                        Snips.scheduler1.remove_job('Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when)
                    else:
                        Snips.scheduler1.remove_job('Evento no repetitivo: recordando tomar '+e.med+' a '+e.user)
                    mqttClient.publish_end_session(intentMessage, msg)
        else:
            print("Usuario actual distinto al del evento")
            if(e.rep):
                Snips.scheduler1.remove_job('Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when)
            else:
                Snips.scheduler1.remove_job('Evento no repetitivo: recordando tomar '+e.med+' a '+e.user)
    else:
        print("El evento ya ha sido confirmado")
        if(e.rep):
            Snips.scheduler1.remove_job('Evento repetitivo: recordando tomar '+e.med+' a '+e.user+' cada '+e.when)
        else:
            Snips.scheduler1.remove_job('Evento no repetitivo: recordando tomar '+e.med+' a '+e.user)

class button(threading.Thread):
    BUTTON = 12
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON, GPIO.IN)
    def __init__(self):
        with Hermes(mqtt_options=MqttOptions()) as h:
           threading.Thread.__init__(self)
        
    def say(intentMessage,text):
        mqttClient.publish_start_session_notification(intentMessage, text,None) 

    def exist_Job(self,job):
        enc=False
        if(Snips.scheduler1.get_jobs()):
            for x in Snips.scheduler1.get_jobs():
                if(x.__eq__(job)):
                    return True
        return enc
 
    def run(self):
        while True:
            state = GPIO.input(self.BUTTON)
            if state:
                global Snips   
                #msg="Evento aceptado por "+e.user
                #msg="El último evento recordado ha sido aceptado por "+Snips.usr
                Snips.log(None,Snips.usr,'Botón','Evento aceptado','')
                event=lastEventReminderByUser()
                print(event.__str__())
                if(event):
                    if(Snips.eventActive(event)):
                        print('Activo')
                        msg='Aceptando '+event.__str__()
                        if(not event.rep):
                            #print('No repetitivo')
                            Snips.FinishEvent(event)
                            job='Evento no repetitivo: recordando tomar '+event.med+' a '+event.user
                        else:
                            #print('Repetitivo')
                            Snips.NingunaVez(event) 
                            job='Evento repetitivo: recordando tomar '+event.med+' a '+event.user+' cada '+event.when

                        if(self.exist_Job(job)):
                            Snips.scheduler1.remove_job(job)
                            say('default', msg)
                    else:
                        say('default', 'No existe ningún recordatorio a confirmar')
                else:
                    say('default', 'No existe ningún recordatorio a confirmar')                
                        

            time.sleep(1)

if __name__ == '__main__':
    mqtt_opts=MqttOptions()
    global_variables()
    thread1 = button()
    thread1.start()

        
    with Hermes(mqtt_options=mqtt_opts) as h:
        h\
        .subscribe_intent("caguilary:Anadir", subscribe_Anadir_callback) \
        .subscribe_intent("caguilary:user", subscribe_user_callback) \
        .subscribe_intent("caguilary:Confirmar", subscribe_confirmar_callback) \
        .subscribe_intent("caguilary:Negar", subscribe_Negar_callback) \
        .subscribe_intent("caguilary:Anadir_usuario", subscribe_AnadirUsuario_callback) \
        .subscribe_intent("caguilary:userActivo", subscribe_CheckUsuario_callback) \
        .subscribe_intent("caguilary:Borrar_Evento", subscribe_Borrar_callback) \
        .start()
