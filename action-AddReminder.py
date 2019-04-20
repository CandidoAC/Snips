#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

def subscribe_intent_callback(hermes, intentMessage):
    fecha = intentMessage.slots.Fecha.first().value
    med = intentMessage.slots.Medicamento.first().value
    msg = "Okay, añadiendo recordatorio:tomar  " + med  + " el "+fecha
    hermes.publish_end_session(intentMessage.session_id, msg)





if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("caguilary:Anadir", subscribe_intent_callback) \
         .start()
