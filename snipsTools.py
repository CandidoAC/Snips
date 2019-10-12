#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import configparser

"""
Clase con las herrmientas de Snips, dada por la misma empresa
"""

CONFIGURATION_ENCODING_FORMAT = "utf-8"
class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name : option for option_name, \
                          option in self.items(section)} for section in self.sections()}

    @staticmethod
    def read_configuration_file(configuration_file):
        try:
            with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as file_conf:
                conf_parser = SnipsConfigParser()
                conf_parser.readfp(file_conf)
                return conf_parser.to_dict()
        except (IOError, configparser.Error) as error:
            print(error)
            return dict()

    @staticmethod
    def write_configuration_file(configuration_file, data):
        conf_parser = SnipsConfigParser()
        for key in list(data.keys()):
            conf_parser.add_section(key)
            for inner_key in list(data[key].keys()):
                conf_parser.set(key, inner_key, data[key][inner_key])
        try:
            with open(configuration_file, 'w') as file_conf:
                conf_parser.write(file_conf)
                return True
        except (IOError, configparser.Error) as error:
            print(error)
            return False