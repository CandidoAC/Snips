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
from Eventos import Snips
from Evento import Evento
import threading
import RPi.GPIO as GPIO

configuracion_formato_codificacion = "utf-8"
Configuracion_inicial = "config.ini"


class boton(threading.Thread):
    BOTON = 12
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BOTON, GPIO.IN)

    def __init__(self):
        with Hermes(mqtt_options=MqttOptions()) as h:
            threading.Thread.__init__(self)

    def say(MensajeIntent, texto):
        mqttClient.publish_start_session_notification(MensajeIntent, texto, None)

    def existe_Trabajo(self, trabajo):
        enc = False
        if (Snips.planificador1.get_jobs()):
            for x in Snips.planificador1.get_jobs():
                if (x.__eq__(trabajo)):
                    return True
        return enc

    def run(self):
        while True:
            estado = GPIO.input(self.BOTON)
            if estado:
                global Snips
                Snips.log(None, Snips.usuario, 'Botón', 'Evento aceptado', '')
                evento = ultimoEventoRecordatorioPorUsuario()
                print(evento.__str__())
                if (evento):
                    if (Snips.EventoActivo(evento)):
                        print('Activo')
                        mensaje = 'Aceptando ' + evento.__str__()
                        if (not evento.rep):
                            # print('No repetitivo')
                            Snips.EventoFinalizado(evento)
                            trabajo = 'Evento no repetitivo: recordando tomar ' + evento.med + ' a ' + evento.usuario
                        else:
                            # print('Repetitivo')
                            Snips.NingunaVez(evento)
                            trabajo = 'Evento repetitivo: recordando tomar ' + evento.med + ' a ' + evento.usuario + ' cada ' + evento.cuando

                        if (self.existe_Trabajo(trabajo)):
                            Snips.planificador1.remove_job(trabajo)
                            say('default', mensaje)
                    else:
                        say('default', 'No existe ningún recordatorio a confirmar')
                else:
                    say('default', 'No existe ningún recordatorio a confirmar')

            time.sleep(1)


def global_variables():
    global Recordatorio,e,Snips
    Snips = Snips()


def minutos(i):
    switcher={
        0:"",
        15:" y cuarto",
        30:" y media",
        45:" menos cuarto",
        }
    return switcher.get(i," y " + str(i))

def existe_Trabajo(trabajo):
    enc=False
    if(Snips.planificador.get_jobs()):
        for x in Snips.planificador.get_jobs():
            if(x.__eq__(trabajo)):
                return True
    return enc

def existe_Trabajo1(trabajo):
    enc=False
    if(Snips.planificador1.get_jobs()):
        for x in Snips.planificador1.get_jobs():
            if(x.__eq__(trabajo)):
                return True
    return enc


#Intent Añadir mdicamento
def subscribir_Anadir_llamada(hermes, MesajeIntent):
    conf = SnipsConfigParser.read_configuration_file(Configuracion_inicial)
    controlador_accion_Anadir_Evento(hermes, MesajeIntent, conf)

def controlador_accion_Anadir_Evento(hermes, MensajeIntent, conf):
    global Snips
    #print(str(MensajeIntent.slots.Repeticion))
    if(not MensajeIntent.slots.Repeticion):
        session=MensajeIntent.session_id
        if(MensajeIntent.slots.Fecha):
            fecha = MensajeIntent.slots.Fecha.first().value
            fecha=fecha [ :fecha.index('+')-1 ]
            FechaObjecto=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
            if(datetime.now() < FechaObjecto):
                med = MensajeIntent.slots.Medicamento.first().value
                mensaje= Snips.usuario +" está añadiendo un recordatorio para el día  " + str(FechaObjecto.day) + " de " + str(FechaObjecto.month) + " del " + str(FechaObjecto.year) + " a las " + str(FechaObjecto.hour) + minutos(FechaObjecto.minute) + " tomar " + med
                e=Evento(med, FechaObjecto, Snips.usuario, False, '')
                if(not Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    Snips.anadirEvento(e)
                    Snips.log(e,Snips.usr,'','Añadir_Evento','')
                    Snips.planificador.add_job(recordatorio, 'date', run_date=FechaObjecto, id=str(e.fecha)+','+e.med+','+e.usuario, args=['default', e, False, Snips])
                else:
                    mensaje='Evento a crear ya existe'
                    Snips.log(None,'','','Error',mensaje)
            else:
                mensaje='La fecha introducida ya ha pasado. Vuelve a introducir el comando'
        else:
            mensaje='Fecha errónea. Vuelve a introducir el comando'
    else:
        session=MensajeIntent.session_id
        if(MensajeIntent.slots.Fecha):
            fecha = MensajeIntent.slots.Fecha.first().value
            fecha=fecha [ :fecha.index('+')-1 ]
            FechaObjecto=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
        else:
            fecha=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0).strftime("%Y-%m-%d %H:%M")
            FechaObjecto=datetime.strptime(fecha,"%Y-%m-%d %H:%M")

        med = MensajeIntent.slots.Medicamento.first().value
        if(not MensajeIntent.slots.cantidad):
            veces=1
        else:
            veces= int(MensajeIntent.slots.cantidad.first().value)
        if (veces==0):
            mensaje='No se puede crear un evento repetitivo con cantidad  igual a 0.'
        else:
            frecuencia=MensajeIntent.slots.Repeticion.first().value
            if(frecuencia=='diariamente'):
                mensaje=Snips.usuario+" está añadiendo un recordatorio para tomar "+med+' todos los dias empezando '+str(fecha)
                e=Evento(med, FechaObjecto, Snips.usuario, True, '1 dia')
                if(not Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    Snips.planificador.add_job(recordatorio, 'cron',id='Repeticion diaria,'+med+','+Snips.usuario,year=FechaObjecto.year,month=FechaObjecto.month,day=str(FechaObjecto.day)+'/1',hour=FechaObjecto.hour,minute=FechaObjecto.minute, replace_existing=True, args=['default',e,True,Snips])
                    Snips.anadirEvento(e)
                    Snips.log(e,Snips.usuario,'','Añadir_Evento','')
                else:
                    mensaje='Evento a crear ya existe'
                    Snips.log(None,'','','Error',mensaje)
            elif(frecuencia=='dia'):
                if(veces>30):
                    mensaje="No se puede crear un evento repetitivo con cant mayor a 30 días."
                else:
                    mensaje=Snips.usuario+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' dias empezando '+str(fecha)
                    e=Evento(med, FechaObjecto, Snips.usuario, True, str(veces) + ' dia')
                    if(not Snips.ExisteEvento(e)):
                        e.IncrementarVeces()
                        Snips.planificador.add_job(recordatorio, 'cron',id='Repeticion cada '+str(veces)+' dias,'+med+','+Snips.usuario,year=FechaObjecto.year,month=FechaObjecto.month,day=str(FechaObjecto.day)+'/'+str(veces),hour=FechaObjecto.hour,minute=FechaObjecto.minute, replace_existing=True, args=['default',e,True,Snips])
                        Snips.anadirEvento(e)
                        Snips.log(e,Snips.usuario,'','Añadir_Evento','')
                    else:
                        mensaje='Evento a crear ya existe'
                        Snips.log(None,'','','Error',mensaje)
            elif(frecuencia=='mes'):
                if(veces>11):
                    mensaje="No se puede crear un evento repetitivo con cant igual o mayor que 11 meses"
                else:
                    mensaje=Snips.usuario+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' meses empezando '+str(fecha)
                    e=Evento(med, FechaObjecto, Snips.usuario, True, str(veces) + ' mes')
                    if(not Snips.ExisteEvento(e)):
                        e.IncrementarVeces()
                        Snips.planificador.add_job(recordatorio, 'cron',id='Repeticion '+str(veces)+' meses ,'+med+','+Snips.usuario,year=FechaObjecto.year,month=str(FechaObjecto.month)+'/'+str(veces),day=FechaObjecto.day,hour=FechaObjecto.hour,minute=FechaObjecto.minute, replace_existing=True, args=['default',e,True,Snips])
                        Snips.anadirEvento(e)
                        Snips.log(e,Snips.usuario,'','Añadir_Evento','')
                    else:
                        mensaje='Evento a crear ya existe'
                        Snips.log(None,'','','Error',mensaje)
            elif(frecuencia=='semana'):
                if(veces>30):
                    mensaje="No se puede crear un evento repetitivo con cant mayor a 30 semanas."
                else:
                    mensaje=Snips.usuario+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' semanas empezando '+str(fecha)
                    e=Evento(med, FechaObjecto, Snips.usuario, True, str(veces) + ' semana')
                    if(not Snips.ExisteEvento(e)):
                        e.IncrementarVeces()
                        Snips.planificador.add_job(recordatorio, 'cron',id='Repeticion ' +str(veces)+' semanas,'+med+','+Snips.usuario,year=FechaObjecto.year,month=FechaObjecto.month,day=str(FechaObjecto.day)+'/'+str(7*veces),hour=FechaObjecto.hour,minute=FechaObjecto.minute, replace_existing=True, args=['default',e,True,Snips])
                        Snips.anadirEvento(e)
                        Snips.log(e,Snips.usuario,'','Añadir_Evento','')
                    else:
                        mensaje='Evento a crear ya existe'
                        Snips.log(None,'','','Error',mensaje)
            elif(frecuencia=='hora'):
                if(veces>23):
                    mensaje="No se puede crear un evento repetitivo con cant sea 23 o más."
                else:
                    mensaje=Snips.usuario+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' horas empezando '+str(fecha)
                    e=Evento(med, FechaObjecto, Snips.usuario, True, str(veces) + ' hora')
                    if(not Snips.ExisteEvento(e)):
                        e.IncrementarVeces()
                        Snips.planificador.add_job(recordatorio, 'cron',id='Repeticion '+str(veces)+' horas,'+med+','+Snips.usuario,year=FechaObjecto.year,month=FechaObjecto.month,day=FechaObjecto.day,hour=str(FechaObjecto.hour)+'/'+str(veces),minute=FechaObjecto.minute, replace_existing=True, args=['default',e,True,Snips])
                        Snips.anadirEvento(e)
                        Snips.log(e,Snips.usuario,'','Añadir_Evento','')
                    else:
                        mensaje='Evento a crear ya existe'
                        Snips.log(None,'','','Error',mensaje)
            elif(frecuencia=='desayuno'):#HORA-1
                mensaje=Snips.usuario+" está añadiendo un recordatorio para tomar "+med+' en el desayuno'
                e=Evento(med, FechaObjecto, Snips.usuario, True, 'desayuno')
                if(not Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    Snips.planificador.add_job(recordatorio, 'cron',id='Repeticion Desayuno'+','+med+','+Snips.usuario,year=FechaObjecto.year,month=FechaObjecto.month,day=FechaObjecto.day,hour='8/1',minute=0, replace_existing=True, args=['default',e,True,Snips])
                    Snips.anadirEvento(e)
                    Snips.log(e,Snips.usuario,'','Añadir_Evento','')
                else:
                    mensaje='Evento a crear ya existe'
                    Snips.log(None,'','','Error',mensaje)
            elif(frecuencia=='comida'):#HORA-1
                mensaje=Snips.usuario+" está añadiendo un recordatorio para tomar "+med+' en la comida'
                e=Evento(med, FechaObjecto, Snips.usuario, True, 'comida')
                if(not Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    Snips.planificador.add_job(recordatorio, 'cron',id='Repeticion Comida'+','+med+','+Snips.usuario,year=FechaObjecto.year,month=FechaObjecto.month,day=FechaObjecto.day,hour='13/1',minute=0, replace_existing=True, args=['default',e,True,Snips])
                    Snips.anadirEvento(e)
                    Snips.log(e,Snips.usuario,'','Añadir_Evento','')
                else:
                    mensaje='Evento a crear ya existe'
                    Snips.log(None,'','','Error',mensaje)
            elif(frecuencia=='cena'): #HORA-1
                mensaje=Snips.usuario+" está añadiendo un recordatorio para tomar "+med+' en la cena'
                e=Evento(med, FechaObjecto, Snips.usuario, True, 'cena')
                if(not Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    Snips.planificador.add_job(recordatorio, 'cron',id='Repeticion Cena'+','+med+','+Snips.usuario,year=FechaObjecto.year,month=FechaObjecto.month,day=FechaObjecto.day,hour='20/1',minute=0, replace_existing=True, args=['default',e,True,Snips])
                    Snips.anadirEvento(e)
                    Snips.log(e,Snips.usuario,'','Añadir_Evento','')
                else:
                    mensaje='Evento a crear ya existe'
                    Snips.log(None,'','','Error',mensaje)
            else:
                mensaje=Snips.usuario+" está añadiendo un recordatorio para tomar "+med+' cada '+str(veces)+' '+frecuencia+' empezando '+str(fecha)
                e=Evento(med, FechaObjecto, Snips.usuario, True, str(veces) + ' ' + frecuencia)
                if(not Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    Snips.planificador.add_job(recordatorio, 'cron',id='Repeticion semanal cada '+frecuencia+','+med+','+Snips.usuario,day_of_week=Snips.dia_sem(frecuencia),year=FechaObjecto.year,month=FechaObjecto.month,day=FechaObjecto.day,hour=FechaObjecto.hour,minute=FechaObjecto.minute, replace_existing=True, args=['default',e,True,Snips])
                    Snips.anadirEvento(e)
                    Snips.log(e,Snips.usr,'','Añadir_Evento','')
                else:
                    mensaje='Evento a crear ya existe'
                    Snips.log(None,'','','Error',mensaje)
    hermes.publish_end_session(MensajeIntent.session_id, mensaje)

def subscribir_Borrar_llamada(hermes, MensajeIntent):
    conf = SnipsConfigParser.read_configuration_file(Configuracion_inicial)
    controlador_accion_Borrar(hermes, MensajeIntent, conf)

def controlador_accion_Borrar(hermes, MensajeIntent, conf):
    if(not MensajeIntent.slots.Repeticion):
        sesion=MensajeIntent.session_id
        if(MensajeIntent.slots.Fecha):
            fecha = MensajeIntent.slots.Fecha.first().value
            fecha=fecha [ :fecha.index('+')-1 ]
            fechaObjecto=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
            med = MensajeIntent.slots.Medicamento.first().value
            mensaje= Snips.usuario +" está borrando el recordatorio para el día  " + str(fechaObjecto.day) + " de " + str(fechaObjecto.month) + " del " + str(fechaObjecto.year) + " a las " + str(fechaObjecto.hour) + minutos(fechaObjecto.minute) + " tomar " + med
            e=Evento(med, fechaObjecto, Snips.usuario, False, '')
            if(Snips.ExisteEvento(e)):
                e.IncrementarVeces()
                print('Evento a borrar: tomar '+str(e))
                Snips.borrarEvento(e)
                Snips.log(e,Snips.usuario,'','Borrar_Evento','')
                job=fecha+','+e.med+','+e.usuario
                if(existe_Trabajo(job)):
                    Snips.planificador.remove_job(job)

                job='Evento no repetitivo: recordando tomar '+e.med+' a '+e.usuario
                if(existe_Trabajo1(job)):
                    Snips.planificador1.remove_job(job)
            else:
                mensaje='Evento a borrar no existe'
                Snips.log(None,'','','Error',mensaje)
        else:
            mensaje='Fecha errónea. Vuelve a introducir el comando'
        hermes.publish_end_session(MensajeIntent.session_id, mensaje)
    else:
        print('Borrando evento rep')
        sesion=MensajeIntent.session_id
        if(MensajeIntent.slots.Fecha):
            fecha = MensajeIntent.slots.Fecha.first().value
            fecha=fecha [ :fecha.index('+')-1 ]
            fechaObjecto=datetime.strptime(fecha,"%Y-%m-%d %H:%M:%S")
        else:
            fecha=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0).strftime("%Y-%m-%d %H:%M")
            fechaObjecto=datetime.strptime(fecha,"%Y-%m-%d %H:%M")

        med = MensajeIntent.slots.Medicamento.first().value
        if(not MensajeIntent.slots.cantidad):
            veces=1
        else:
            veces= int(MensajeIntent.slots.cantidad.first().value)
        if (veces==0):
            mensaje='No se puede borrar un evento repetitivo con cantidad igual a 0.'
        else:
            frecuencia=MensajeIntent.slots.Repeticion.first().value

            if(frecuencia=='diariamente'):
                mensaje=Snips.usuario+" está borrando un recordatorio para tomar "+med+' todos los dias empezando '+str(fecha)
                e=Evento(med, fechaObjecto, Snips.usuario, True, '1 dia')
                print(e)
                if(Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    job='Repeticion diaria,'+med+','+Snips.usuario
                    Snips.borrarEvento(e)
                    Snips.log(e,Snips.usuario,'','Borrar_Evento','')
                    if(existe_Trabajo(job)):
                        Snips.planificador.remove_job(job)

                    job='Evento repetitivo: recordando tomar ' + e.med +' a ' + e.usuario + ' cada ' + e.cuando
                    if(existe_Trabajo1(job)):
                        Snips.planificador1.remove_job(job)
                else:
                    mensaje='Evento a borrar no existe'
                    Snips.log(None,'','','Error',mensaje)

            elif(frecuencia=='dia'):
                if(veces>30):
                    mensaje="No se puede borrar un evento repetitivo con cant mayor a 30 días."
                else:
                    mensaje=Snips.usuario+" está borrando un recordatorio para tomar "+med+' cada '+str(veces)+' dias empezando '+str(fecha)
                    e=Evento(med, fechaObjecto, Snips.usuario, True, str(veces) + ' dia')
                    if(Snips.ExisteEvento(e)):
                        e.IncrementarVeces()
                        job='Repeticion cada '+str(veces)+' dias,'+med+','+Snips.usuario
                        Snips.borrarEvento(e)
                        Snips.log(e,Snips.usuario,'','Borrar_Evento','')
                        if(existe_Trabajo(job)):
                            Snips.planificador.remove_job(job)

                        job='Evento repetitivo: recordando tomar ' + e.med +' a ' + e.usuario + ' cada ' + e.cuando
                        if(existe_Trabajo1(job)):
                            Snips.planificador1.remove_job(job)
                    else:
                        mensaje='Evento a borrar no existe'
                        Snips.log(None,'','','Error',mensaje)

            elif(frecuencia=='mes'):
                if(veces>11):
                    mensaje="No se puede borrar un evento repetitivo con cant igual o mayor que 11 meses"
                else:
                    mensaje=Snips.usuario+" está borrando un recordatorio para tomar "+med+' cada '+str(veces)+' meses empezando '+str(fecha)
                    e=Evento(med, fechaObjecto, Snips.usuario, True, str(veces) + ' mes')
                    if(Snips.ExisteEvento(e)):
                        e.IncrementarVeces()
                        job='Repeticion '+str(veces)+' meses ,'+med+','+Snips.usuario
                        Snips.borrarEvento(e)
                        Snips.log(e,Snips.usuario,'','Borrar_Evento','')
                        if(existe_Trabajo(job)):
                            Snips.planificador.remove_job(job)

                        job='Evento repetitivo: recordando tomar ' + e.med +' a ' + e.usuario + ' cada ' + e.cuando
                        if(existe_Trabajo1(job)):
                            Snips.planificador1.remove_job(job)
                    else:
                        mensaje='Evento a borrar no existe'
                        Snips.log(None,'','','Error',mensaje)
            elif(frecuencia=='semana'):
                if(veces>30):
                    mensaje="No se puede borrar un evento repetitivo con cant mayor a 30 semanas."
                else:
                    mensaje=Snips.usuario+" está borrando un recordatorio para tomar "+med+' cada '+str(veces)+' semanas empezando '+str(fecha)
                    e=Evento(med, fechaObjecto, Snips.usuario, True, str(veces) + ' semana')
                    if(Snips.ExisteEvento(e)):
                        e.IncrementarVeces()
                        job='Repeticion ' +str(veces)+' semanas,'+med+','+Snips.usuario
                        Snips.borrarEvento(e)
                        Snips.log(e,Snips.usuario,'','Borrar_Evento','')
                        if(existe_Trabajo(job)):
                            Snips.planificador.remove_job(job)

                        job='Evento repetitivo: recordando tomar ' + e.med +' a ' + e.usuario + ' cada ' + e.cuando
                        if(existe_Trabajo1(job)):
                            Snips.planificador1.remove_job(job)
                    else:
                        mensaje='Evento a borrar no existe'
                        Snips.log(None,'','','Error',mensaje)

            elif(frecuencia=='hora'):
                if(veces>23):
                    mensaje="No se puede borrar un evento repetitivo con cant sea 23 horas o más."
                else:
                    mensaje=Snips.usuario+" está borrando un recordatorio para tomar "+med+' cada '+str(veces)+' horas empezando '+str(fecha)
                    e=Evento(med, fechaObjecto, Snips.usuario, True, str(veces) + ' hora')
                    if(Snips.ExisteEvento(e)):
                        e.IncrementarVeces()
                        job='Repeticion '+str(veces)+' horas,'+med+','+Snips.usuario
                        Snips.borrarEvento(e)
                        Snips.log(e,Snips.usuario,'','Borrar_Evento','')
                        if(existe_Trabajo(job)):
                            Snips.planificador.remove_job(job)

                        job='Evento repetitivo: recordando tomar ' + e.med +' a ' + e.usuario + ' cada ' + e.cuando
                        if(existe_Trabajo1(job)):
                            Snips.planificador1.remove_job(job)
                    else:
                        mensaje='Evento a borrar no existe'
                        Snips.log(None,'','','Error',mensaje)

            elif(frecuencia=='desayuno'):#HORA-1
                mensaje=Snips.usuario+" está borrando un recordatorio para tomar "+med+' en el desayuno'
                e=Evento(med, fechaObjecto, Snips.usuario, True, 'desayuno')
                if(Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    job='Repeticion Desayuno'+','+med+','+Snips.usuario
                    Snips.borrarEvento(e)
                    Snips.log(e,Snips.usuario,'','Borrar_Evento','')
                    if(existe_Trabajo(job)):
                        Snips.planificador.remove_job(job)

                    job='Evento repetitivo: recordando tomar ' + e.med +' a ' + e.usuario + ' cada ' + e.cuando
                    if(existe_Trabajo1(job)):
                        Snips.planificador1.remove_job(job)
                else:
                    mensaje='Evento a borrar no existe'
                    Snips.log(None,'','','Error',mensaje)

            elif(frecuencia=='comida'):#HORA-1
                mensaje=Snips.usuario+" está borrando un recordatorio para tomar "+med+' en la comida'
                e=Evento(med, fechaObjecto, Snips.usuario, True, 'comida')
                if(Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    job='Repeticion Comida'+','+med+','+Snips.usuario
                    Snips.borrarEvento(e)
                    Snips.log(e,Snips.usuario,'','Borrar_Evento','')
                    if(existe_Trabajo(job)):
                        Snips.planificador.remove_job(job)

                    job='Evento repetitivo: recordando tomar ' + e.med +' a ' + e.usuario + ' cada ' + e.cuando
                    if(existe_Trabajo1(job)):
                        Snips.planificador1.remove_job(job)
                else:
                    mensaje='Evento a borrar no existe'
                    Snips.log(None,'','','Error',mensaje)

            elif(frecuencia=='cena'): #HORA-1
                mensaje=Snips.usuario+" está borrando un recordatorio para tomar "+med+' en la cena'
                e=Evento(med, fechaObjecto, Snips.usuario, True, 'cena')
                if(Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    job='Repeticion Cena'+','+med+','+Snips.usuario
                    Snips.borrarEvento(e)
                    Snips.log(e,Snips.usuario,'','Borrar_Evento','')
                    if(existe_Trabajo(job)):
                        Snips.planificador.remove_job(job)

                    job='Evento repetitivo: recordando tomar ' + e.med +' a ' + e.usuario + ' cada ' + e.cuando
                    if(existe_Trabajo1(job)):
                        Snips.planificador1.remove_job(job)
                else:
                    mensaje='Evento a borrar no existe'
                    Snips.log(None,'','','Error',mensaje)
            else:
                mensaje=Snips.usuario+" está borrando un recordatorio para tomar "+med+' cada '+str(veces)+' '+frecuencia+' empezando '+str(fecha)
                e=Evento(med, fechaObjecto, Snips.usuario, True, str(veces) + ' ' + frecuencia)
                if(Snips.ExisteEvento(e)):
                    e.IncrementarVeces()
                    job='Repeticion semanal cada '+frecuencia+','+med+','+Snips.usuario
                    Snips.borrarEvento(e)
                    Snips.log(e,Snips.usuario,'','Borrar_Evento','')
                    if(existe_Trabajo(job)):
                        Snips.planificador.remove_job(job)

                    job='Evento repetitivo: recordando tomar ' + e.med +' a ' + e.usuario + ' cada ' + e.cuando
                    if(existe_Trabajo1(job)):
                        Snips.planificador1.remove_job(job)
                else:
                    mensaje='Evento a borrar no existe'
                    Snips.log(None,'','','Error',mensaje)

        hermes.publish_end_session(MensajeIntent.session_id, mensaje)

def subscribir_Confirmar_llamada(hermes, MensajeIntent):
    conf = SnipsConfigParser.read_configuration_file(Configuracion_inicial)
    controlador_accion_Confirmar(hermes, MensajeIntent, conf)

def controlador_accion_Confirmar(hermes, MensajeIntent, conf):
    global Snips
    Snips.log(None,Snips.usuario,'Voz','Evento aceptado','')
    evento=ultimoEventoRecordatorioPorUsuario()
    print(evento.__str__())
    if(evento):
        if(Snips.EventoActivo(evento)):
            mensaje='Aceptando '+evento.__str__()
            if(not evento.rep):
                Snips.EventoFinalizado(evento)
                job='Evento no repetitivo: recordando tomar '+evento.med+' a '+evento.usuario
            else:
                Snips.NingunaVez(evento)
                job='Evento repetitivo: recordando tomar ' + evento.med +' a ' + evento.usuario + ' cada ' + evento.cuando
            if(existe_Trabajo1(job)):
                Snips.planificador1.remove_job(job)
                hermes.publish_end_session(MensajeIntent.session_id, mensaje)
        else:
            hermes.publish_end_session(MensajeIntent.session_id, 'No existe ningún recordatorio a confirmar')
    else:
        hermes.publish_end_session(MensajeIntent.session_id, 'No existe ningún recordatorio a confirmar')


def subscribir_Negar_llamada(hermes, MensajeIntent):
    conf = SnipsConfigParser.read_configuration_file(Configuracion_inicial)
    controlador_accion_Negar(hermes, MensajeIntent, conf)

def controlador_accion_Negar(hermes, MensajeIntent, conf):
    msg="Evento no aceptado por "+Snips.usr+" se te volverá ha avisar en 20 segundos"
    Snips.log(None,Snips.usuario,'','Evento no aceptado','')
    hermes.publish_end_session(MensajeIntent.session_id, msg)

def subscribir_Anadir_usuario_llamada(hermes, MensajeIntent):
    conf = SnipsConfigParser.read_configuration_file(Configuracion_inicial)
    controlador_accion_anadir_usuario(hermes, MensajeIntent, conf)

def controlador_accion_anadir_usuario(hermes, MensajeIntent, conf):
    global Snips
    usuario = MensajeIntent.slots.usuario.first().value
    if(not Snips.existeUsuario(usuario)):
        mensaje="Añadiendo usuario "+usuario +' y cambio a dicho usuario'
        Snips.anadirUsuario(usuario)
        Snips.cambiarUsuarioActivo(usuario)
        Snips.log(None,usuario,'','Añadir_Usuario','')
    else:
        mensaje="El usuario "+usuario+" ya existe"
    hermes.publish_end_session(MensajeIntent.session_id, mensaje)

#Intent cambiar usuario
def subscribir_Cambiar_usuario_llamada(hermes, MensajeIntent):
    conf = SnipsConfigParser.read_configuration_file(Configuracion_inicial)
    controlador_accion_Cambiar_usuario(hermes, MensajeIntent, conf)

def controlador_accion_Cambiar_usuario(hermes, MensajeIntent, conf):
    global Snips
    usuario = MensajeIntent.slots.usuario.first().value
    if(Snips.existeUsuario(usuario)):
        if(Snips.usuarioActivo()!=usuario):
            mensaje="Cambio de usuario a "+usuario
            Snips.cambiarUsuarioActivo(usuario)
            Snips.log(None,usuario,'','Cambio_Usuario','')
        else:
            mensaje="El usuario "+usuario+" ya es el actual"
    else:
        mensaje="El usuario "+usuario+" no existe"
    hermes.publish_end_session(MensajeIntent.session_id, mensaje)


def subscribir_Comprobar_usuario_llamada(hermes, MensajeIntent):
    conf = SnipsConfigParser.read_configuration_file(Configuracion_inicial)
    controlador_accion_comprobar_usuario(hermes, MensajeIntent, conf)

def controlador_accion_comprobar_usuario(hermes, MensajeIntent, conf):
    global Snips
    msg="El usuario activo es "+Snips.usuario
    hermes.publish_end_session(MensajeIntent.session_id, msg)

def ultimoEventoRecordatorioPorUsuario():
        aux = None
        with open('/home/pi/Reporte.csv', 'r') as csvfile:
            lector = csv.DictReader(csvfile)
            encabecazados = lector.fieldnames
            listaRec = []
            for columna in lector:
                # print(row[headers[2]])
                if (columna['Nombre_Usuario'] == Snips.usuario and columna['Tipo'] == 'Recordatorio'):
                    listaRec.append(columna)
            print(*listaRec)
            for columna in listaRec:
                if (columna['¿Repetitivo?'] == 'Si'):
                    e = Evento(columna['Medicamento'], datetime.strptime(columna['Fecha'], "%Y-%m-%d %H:%M:%S"),
                               columna['Nombre_Usuario'], True, columna['Frecuencia'])
                    print(e)
                    if (Snips.EventoActivo(e)):
                        aux = e
                else:
                    e = Evento(columna['Medicamento'], datetime.strptime(columna['Fecha'], "%Y-%m-%d %H:%M:%S"),
                               columna['Nombre_Usuario'], False, None)
                    print(e)
                    if (Snips.EventoActivo(e)):
                        aux = e
            print('Va a aceptar ' + aux.__str__())
            if (aux):
                return aux
            else:
                return None


def say(MensajeIntent, texto):
    with Hermes(mqtt_options=MqttOptions()) as clienteMQTT:
        clienteMQTT.publish_start_session_notification(MensajeIntent, texto, None)
        
def recordatorio(MensajeIntent, e, Repetitivo, Snips):
    print('Evento detectado para : %s' % datetime.now())
    if(e.usuario==Snips.usuario):
        say(MensajeIntent, e.usuario + ' te toca tomarte ' + e.med)
        Snips.log(e,Snips.usuario,'','Recordatorio','')
        if(e.rep):
            Snips.planificador1.add_job(recordatorioTomar, 'interval', seconds=20, id='Evento repetitivo: recordando tomar '+e.med+' a '+e.usuario+' cada '+e.cuando, args=[e, MensajeIntent, Snips])
        else:
            Snips.planificador1.add_job(recordatorioTomar, 'interval', seconds=20, id='Evento no repetitivo: recordando tomar '+e.med+' a '+e.usuario, args=[e, MensajeIntent, Snips])

   

def recordatorioTomar(e,intentMessage,Snips):
    if(Snips.EventoActivo(e)):
        if(e.usuario==Snips.usuario):
            with Hermes(mqtt_options=MqttOptions()) as clienteMQTT:
                if(e.veces<6):
                    Snips.log(e,Snips.usuario,'','Recordatorio','')
                    clienteMQTT.publish_start_session_action(site_id=intentMessage,
                    session_init_text=e.usuario+'¿ te has tomado ' +e.med+'?',
                    session_init_intent_filter=["caguilary:Confirmar","caguilary:Negar"],
                    session_init_can_be_enqueued=True,
                    session_init_send_intent_not_recognized=True,
                    custom_data=None)
                    mensaje=""
                    print(e.usuario+'¿te has tomado ' +e.med+'?:Vez '+str(e.veces))
                    Snips.Incrementar(e) 
                    e.IncrementarVeces()    
                    clienteMQTT.publish_end_session(intentMessage, mensaje)
                else:
                    mensaje=e.usuario+' ha ignorado el evento tomar '+e.med
                    say(intentMessage,mensaje)
                    if(not e.rep):
                        Snips.EventoFinalizado(e)
                    else:
                        Snips.NingunaVez(e)
                    if(e.rep):
                        Snips.planificador1.remove_job('Evento repetitivo: recordando tomar '+e.med+' a '+e.usuario+' cada '+e.cuando)
                    else:
                        Snips.planificador1.remove_job('Evento no repetitivo: recordando tomar '+e.med+' a '+e.usuario)
                    clienteMQTT.publish_end_session(intentMessage, mensaje)
        else:
            print("Usuario actual distinto al del evento")
            if(e.rep):
                Snips.planificador1.remove_job('Evento repetitivo: recordando tomar '+e.med+' a '+e.usuario+' cada '+e.cuando)
            else:
                Snips.planificador1.remove_job('Evento no repetitivo: recordando tomar '+e.med+' a '+e.usuario)
    else:
        print("El evento ya ha sido confirmado")
        if(e.rep):
            Snips.planificador1.remove_job('Evento repetitivo: recordando tomar '+e.med+' a '+e.usuario+' cada '+e.cuando)
        else:
            Snips.planificador1.remove_job('Evento no repetitivo: recordando tomar '+e.med+' a '+e.usuario)


if __name__ == '__main__':
    opciones_MQTT=MqttOptions()
    global_variables()
    HiloBoton = boton()
    HiloBoton.start()

        
    with Hermes(mqtt_options=opciones_MQTT) as h:
        h\
        .subscribe_intent("caguilary:Anadir_Evento", subscribir_Anadir_llamada) \
        .subscribe_intent("caguilary:Cambiar_Usuario", subscribir_Cambiar_usuario_llamada) \
        .subscribe_intent("caguilary:Confirmar", subscribir_Confirmar_llamada) \
        .subscribe_intent("caguilary:Negar", subscribir_Negar_llamada) \
        .subscribe_intent("caguilary:Anadir_usuario", subscribir_Anadir_usuario_llamada) \
        .subscribe_intent("caguilary:usuario_Activo", subscribir_Comprobar_usuario_llamada) \
        .subscribe_intent("caguilary:Borrar_Evento", subscribir_Borrar_llamada) \
        .start()
