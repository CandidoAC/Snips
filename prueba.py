import csv
from datetime import datetime
import time

def t():
    global idFile
    idFile += 1
    time.sleep(5)

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

def Error(mensaje):
	date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	writer.writerow({'id': idFile,  'Fecha':date,'Tipo':'Error','Medicamento':'','Fecha_Evento':'','Nombre_Usuario':'','Error_output':mensaje})
	t()

if __name__ == '__main__':
	idFile=0
	with open('prueba.csv', 'a') as csvfile:
	    fieldnames = ['id', 'Fecha','Tipo','Medicamento','Fecha_Evento','Nombre_Usuario','Error_output']
	    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	    writer.writeheader()
	    add_Reminder('adiro','')
	    Reminder('adiro')
	    add_Reminder('aspirina','')
	    Error('Error:Snips no ha detectado la fecha')
	    Error('Error:Snips no ha detectado el nombre del Medicamento')
	    Reminder('Juan')
	    