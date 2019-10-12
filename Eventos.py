#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Evento import Evento
from datetime import datetime
from BaseDeDatos import BaseDeDatos
from apscheduler.schedulers.background import BackgroundScheduler
import csv
import os
import time
import threading

class Snips(object):
    def __init__(self):
        self.fichero=__import__('action-Actions')
        self.usuario= ""
        self.idFichero=0
        self.nombreCampos = ['Fecha Creación', 'Id', 'Tipo', '¿Repetitivo?', 'Frecuencia', 'Fecha', 'Medicamento', 'Nombre_Usuario', 'Modo de aceptar', 'Salida_error']
        if(not os.path.exists('/home/pi/Reporte.csv')):
            with open('/home/pi/Reporte.csv', 'a+') as csvfile:
                escritor = csv.DictWriter(csvfile, fieldnames=self.nombreCampos)
                escritor.writeheader()
        self.planificador = BackgroundScheduler({'apscheduler.timezone': 'Europe/Madrid'})
        self.planificador1 = BackgroundScheduler({'apscheduler.timezone': 'Europe/Madrid'})
        self.BaseDeDatos=BaseDeDatos()
        self.planificador.start()
        self.planificador1.start()
        self.BaseDeDatos.conectarDB()
        self.BaseDeDatos.crearTabla()
        self.BaseDeDatos.insertarUsuario('default')
        self.usuario=self.BaseDeDatos.usuarioActivo()
        if(not self.usuario):
            self.BaseDeDatos.cambiarUsuarioActivo('default')
            self.usuario= 'default'
        self.crearRecordatorios(self.fichero)
        ActHilos=self.sincronizarEventos(self)
        ActHilos.start()
    
    def existe_Trabajo1(self, job):
        enc=False
        if(self.planificador1.get_jobs()):
            for x in self.planificador1.get_jobs():
                if(x.__eq__(job)):
                    return True
        return enc 

    def existe_Trabajo(self, job):
        enc=False
        if(self.planificador.get_jobs()):
            for x in self.planificador.get_jobs():
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
        self.idFichero+=1
        
        
    def log(self, e, usuario, Modo, Tipo, mensage):
        with open('/home/pi/Reporte.csv', 'a+') as csvfile:
            escritor = csv.DictWriter(csvfile, fieldnames=self.nombreCampos)
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if(e):
                if(e.rep):
                    escritor.writerow({'Fecha Creación':fecha,'Id': str(self.idFichero), 'Tipo':Tipo, '¿Repetitivo?': 'Si', 'Fecha':str(e.fecha), 'Frecuencia':e.cuando, 'Medicamento':e.med, 'Nombre_Usuario':e.usuario, 'Modo de aceptar': '', 'Salida_error': ''})
                else:
                    escritor.writerow({'Fecha Creación':fecha,'Id': str(self.idFichero), 'Tipo':Tipo, '¿Repetitivo?': 'No', 'Fecha':str(e.fecha), 'Frecuencia': '', 'Medicamento':e.med, 'Nombre_Usuario':e.usuario, 'Modo de aceptar': '', 'Salida_error': ''})
            else:
                escritor.writerow({'Fecha Creación':fecha,'Id': str(self.idFichero), 'Tipo':Tipo, '¿Repetitivo?': '', 'Fecha': '', 'Frecuencia': '', 'Medicamento': '', 'Nombre_Usuario':usuario, 'Modo de aceptar':Modo, 'Salida_error':mensage})
        self.t()

    def anadirEvento(self, evento):
        self.BaseDeDatos.insertarEvento(datetime.now(), evento)

    def anadirUsuario(self, usuario):
        self.BaseDeDatos.insertarUsuario(usuario)

    def existeUsuario(self, usuario):
        return self.BaseDeDatos.ExisteUsuario(usuario)

    def ExisteEvento(self, evento):
        return self.BaseDeDatos.ExisteEvento(evento, self.BaseDeDatos.IDUsuario(self.usuario))

    def Incrementar(self, evento):
        self.BaseDeDatos.IncrementarVeces(evento)

    def EventoFinalizado(self, e):
        self.BaseDeDatos.EventoFinalizado(e)

    def CambioUsuarioActivo(self, usuario):
        self.BaseDeDatos.cambiarUsuarioActivo(usuario)
        self.usuario=usuario

    def NingunaVez(self,e):
        self.BaseDeDatos.NingunaVeces(e)
    
    def UsusarioActivo(self):
        return self.BaseDeDatos.usuarioActivo()

    def EventoActivo(self, e):
        ID=self.BaseDeDatos.IDUsuario(self.usuario)
        if(e.rep):
            return self.BaseDeDatos.EventoEsActivo(e.med, e.fecha, ID, e.rep, e.cuando[e.cuando.index(' ') + 1:], int(e.cuando[:e.cuando.index(' ')]))
        else:
            return self.BaseDeDatos.EventoEsActivo(e.med, e.fecha, ID, e.rep, None, None)

    def borrarEvento(self,e):
        print(e)
        if(e.rep):
            if(' 'in e.cuando):
                self.BaseDeDatos.borrarEvento(e.med, e.fecha, e.usuario, e.rep, e.cuando[e.cuando.index(' ') + 1:], int(e.cuando[:e.cuando.index(' ')]))
            else:
                self.BaseDeDatos.borrarEvento(e.med, e.fecha, e.usuario, e.rep, e.cuando, '')
        else:
            self.BaseDeDatos.borrarEvento(e.med, e.fecha, e.usuario, e.rep, None, None)

    def crearRecordatorios(self, fichero):
        LEventos=self.BaseDeDatos.eventosActivos()
        for e in LEventos:
            if(e.rep):
                if(' 'in e.cuando.strip()):##Se hace el strip para borrar el blanco a la derecha en las comidas
                    Repeticion=e.cuando[e.cuando.index(' ')+1:]
                    veces=int(e.cuando[:e.cuando.index(' ')])
                    #print(Repeticion)
                else:
                    Repeticion=e.cuando

                if(not e.fecha is None):
                    fecha=e.fecha

                if(Repeticion=='dia'):
                    if(not self.existe_Trabajo('Repeticion cada ' + str(veces) + ' dias,' + e.med + ',' + e.usuario)):
                        self.planificador.add_job(fichero.recordatorio, 'cron', id='Repeticion cada ' + str(veces) + ' dias,' + e.med + ',' + e.usuario, year=fecha.year, month=fecha.month, day=str(fecha.day) + '/' + str(veces), hour=fecha.hour, minute=fecha.minute, replace_existing=True, args=['default', e, True, self])
                elif(Repeticion=='mes'):
                    if(not self.existe_Trabajo('Repeticion ' + str(veces) + ' meses ,' + e.med + ',' + e.usuario)):
                        self.planificador.add_job(fichero.recordatorio, 'cron', id='Repeticion ' + str(veces) + ' meses ,' + e.med + ',' + e.usuario, year=fecha.year, month=str(fecha.month) + '/' + str(veces), day=fecha.day, hour=fecha.hour, minute=fecha.minute, replace_existing=True, args=['default', e, True, self])
                elif(Repeticion=='semana'):
                    if(not self.existe_Trabajo('Repeticion cada ' + str(veces) + ' dias,' + e.med + ',' + e.usuario)):
                        self.planificador.add_job(fichero.recordatorio, 'cron', id='Repeticion' + str(veces) + ' semanas,' + e.med + ',' + e.usuario, year=fecha.year, month=fecha.month, day=str(fecha.day) + '/' + str(7 * veces), hour=fecha.hour, minute=fecha.minute, replace_existing=True, args=['default', e, True, self])
                elif(Repeticion=='hora'):
                    if(not self.existe_Trabajo('Repeticion ' + str(veces) + ' horas,' + e.med + ',' + e.usuario)):
                        self.planificador.add_job(fichero.recordatorio, 'cron', id='Repeticion ' + str(veces) + ' horas,' + e.med + ',' + e.usuario, year=fecha.year, month=fecha.month, day=fecha.day, hour=str(fecha.hour) + '/' + str(veces), minute=fecha.minute, replace_existing=True, args=['default', e, True, self])
                elif(Repeticion=='desayuno'):#HORA-1
                    if(not self.existe_Trabajo('Repeticion Desayuno' + ',' + e.med + ',' + e.usuario)):
                        self.planificador.add_job(fichero.recordatorio, 'cron', id='Repeticion Desayuno' + ',' + e.med + ',' + e.usuario, year=fecha.year, month=fecha.month, day=fecha.day, hour='8/1', minute=0, replace_existing=True, args=['default', e, True, self])
                elif(Repeticion=='comida'):#HORA-1
                    if(not self.existe_Trabajo('Repeticion Comida' + ',' + e.med + ',' + e.usuario)):
                        self.planificador.add_job(fichero.recordatorio, 'cron', id='Repeticion Comida' + ',' + e.med + ',' + e.usuario, year=fecha.year, month=fecha.month, day=fecha.day, hour='13/1', minute=0, replace_existing=True, args=['default', e, True, self])
                elif(Repeticion=='cena'): #HORA-1
                    if(not self.existe_Trabajo('Repeticion Desayuno' + ',' + e.med + ',' + e.usuario)):
                        self.planificador.add_job(fichero.recordatorio, 'cron', id='Repeticion Cena' + ',' + e.med + ',' + e.usuario, year=fecha.year, month=fecha.month, day=fecha.day, hour='20/1', minute=0, replace_existing=True, args=['default', e, True, self])
                else:
                    if(not self.existe_Trabajo('Repeticion semanal cada ' + Repeticion + ',' + e.med + ',' + e.usuario)):
                        self.planificador.add_job(fichero.recordatorio, 'cron', id='Repeticion semanal cada ' + Repeticion + ',' + e.med + ',' + e.usuario, day_of_week=self.dia_sem(Repeticion), year=fecha.year, month=fecha.month, day=fecha.day, hour=fecha.hour, minute=fecha.minute, replace_existing=True, args=['default', e, True, self])
                ahora=datetime.now()
                fechaE=e.fecha
                #print(str(ahora)+" y "+fechaE)
                if(ahora<fechaE):  
                    if(not self.existe_Trabajo1('Evento repetitivo: recordando tomar ' + e.med + ' a ' + e.usuario + ' cada ' + e.cuando)):
                        self.planificador1.add_job(fichero.recordatorioTomar, 'interval', seconds=20, id='Evento repetitivo: recordando tomar ' + e.med + ' a ' + e.usuario + ' cada ' + e.cuando, args=[e, 'default', self])
            else:
                if(not e.fecha is None):
                    fecha=e.fecha

                ahora=datetime.now()
                fechaE=e.fecha
                #print(str(ahora)+" y "+fechaE)
                if(ahora<fechaE):    
                    if(not self.existe_Trabajo(str(e.fecha) + ',' + e.med + ',' + e.usuario)):
                        self.planificador.add_job(fichero.recordatorio, 'date', run_date=fecha, id=str(e.fecha) + ',' + e.med + ',' + e.usuario, args=['default', e, False, self])
                else:
                    if(not self.existe_Trabajo1('Evento no repetitivo:recordando tomar ' + e.med + ' a ' + e.usuario)):
                        self.planificador1.add_job(fichero.recordatorioTomar, 'interval', seconds=20, id='Evento no repetitivo: recordando tomar ' + e.med + ' a ' + e.usuario, args=[e, 'default', self])

    class sincronizarEventos(threading.Thread):
        def __init__(self,Snips):
            threading.Thread.__init__(self)
            self.usuario=Snips.usuario
            self.Snips=Snips
        
        def run(self):
            while True:
                if(self.Snips.BaseDeDatos.HayActualizados()):
                    print('Actualizando threads')
                    self.Snips.crearRecordatorios(self.Snips.fichero)
                    self.Snips.BaseDeDatos.cambioANoActualizado()
                time.sleep(5)
