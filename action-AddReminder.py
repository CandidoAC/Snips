#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
from datetime import datetime

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

def minutes(i):
	switcher={
        0:"",
        15:" y cuarto",
        30:" y media",
        45:" menos cuarto",
		}
	return switcher.get(i," y " + str(i))
def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
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
    msg="Añadiendo recordatorio para el día  " + str(date.day) + " de " + str(date.month) + " del " + str(date.year) + " a las " + str(date.hour) + minutes(date.minute)+" tomar " + med
    hermes.publish_end_session(intentMessage.session_id, msg)

#Intent cambiar usuario
def subscribe_user_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper_user(hermes, intentMessage, conf)

def action_wrapper_user(hermes, intentMessage,conf):
    user = intentMessage.slots.user.first().value
   
    msg="Cambio de usuario a "+user
    hermes.publish_end_session(intentMessage.session_id, msg)



if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("caguilary:Anadir", subscribe_Anadir_callback) \
         .start()
        h.subscribe_intent("caguilary:user", subscribe_user_callback) \
         .start()