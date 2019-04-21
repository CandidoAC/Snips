#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)

def action_wrapper(hermes, intentMessage,conf):
    fecha = intentMessage.slots.Fecha.first().value
    med = intentMessage.slots.Medicamento.first().value
    #msg = "Okay, añadiendo recordatorio:tomar  " + med  + " el "+fecha
    msg="Hello"
    hermes.publish_end_session(intentMessage.session_id, msg)





if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("caguilary:Anadir", subscribe_intent_callback) \
         .start()
