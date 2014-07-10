import sys
import os
import types

__CONFIG_PATH__ = 'config'
__ORINGAL_LOG_PATH__ = 'ORINGAL_LOG_PATH'
__UNDO_TASK_LIST_PATH__ = 'UNDO_TASK_LIST_PATH'
__COMPLETED_TASK_LIST_PATH__ = 'COMPLETED_TASK_LIST_PATH'
__LOG_PATH__ = 'LOG_PATH'
__LOG_ANALYSIS_PATH__ = 'LOG_ANALYSIS_PATH'
__LUT_PATH__ = 'LUT_PATH'

class configuration:
    config = {}
    def __init__(self):
        global config
        config = read_config()

    def get_oringal_log_path(self):
        global config
        return config.get(__ORINGAL_LOG_PATH__)

    def get_undo_task_list_path(self):
        global config
        return config.get(__UNDO_TASK_LIST_PATH__)

    def get_completed_task_list_path(self):
        global config
        return config.get(__COMPLETED_TASK_LIST_PATH__)

    def get_log_path(self):
        global config
        return config.get(__LOG_PATH__)

    def get_log_analysis_path(self):
        global config
        return config.get(__LOG_ANALYSIS_PATH__)
    
    def print_configs(self):
        global config
        for key, value in config.items():
            print key + '=' + value
            
    def read_LUT(self, api_as_key):
        return read_LUT(api_as_key)

    def save_LUT(self, lut):
        return save_LUT(lut)
    

def read_LUT(api_as_key):
    config_dict = read_config()
    lut_path = os.path.join(config_dict.get(__LOG_ANALYSIS_PATH__), \
                            config_dict.get(__LUT_PATH__))
    try:
        file_obj = open(lut_path, 'r')
    except IOError:
        print '=== ERROR: READ LUT FAILED! (' + lut_path + ')'
    else:
        lut = {}
        for line in file_obj:
            arrays = line.strip('\n').split('=')
            if (api_as_key == 1):
                lut[arrays[1]] = arrays[0]
            else:
                lut[arrays[0]] = arrays[1]
        file_obj.close()
        return lut
    
def save_LUT(lut):
    config_dict = read_config()
    lut_path = os.path.join(config_dict.get(__LOG_ANALYSIS_PATH__), \
                            config_dict.get(__LUT_PATH__))
    try:
        file_obj = open(lut_path, 'w')
    except IOError:
        print '=== ERROR: SAVE LUT FAILED! (' + lut_path + ')'
    else:    
        for key, value in lut.items():
            linetowrite = key + '=' + value + '\n'
            if (len(value) == 1):
                linetowrite = value + '=' + key + '\n'
            file_obj.writelines(linetowrite)
        file_obj.close()

def read_config():
    config_dict = {}
    try:
        file_obj = open(__CONFIG_PATH__, 'r')
    except IOError:
        print '=== ERROR: OPEN CONFIG FILE FAILED!(' + __CONFIG_PATH__ + ')'
    else:
        for line in file_obj:
            arrays = line.split('=')
            config_dict[arrays[0]] = arrays[1].strip('\n')
    return config_dict
    
def init_config():
    config_dict = {}
    config_dict[__ORINGAL_LOG_PATH__] = 'ologs'
    config_dict[__UNDO_TASK_LIST_PATH__] = 'undo_task_list.txt'
    config_dict[__COMPLETED_TASK_LIST_PATH__ ] = 'completed_task_list.txt'
    config_dict[__LOG_PATH__] = 'logs'
    config_dict[__LOG_ANALYSIS_PATH__] = 'analysis'
    
    if (os.path.isdir('ologs') == False):
        os.makedirs('ologs')
    if (os.path.isdir('logs') == False):
        os.makedirs('logs')
    try:
        file_obj = open(__CONFIG_PATH__, 'w+')
    except IOError:
        print '=== ERROR: OPEN CONFIG FILE FAILED!(' + __CONFIG_PATH__ + ')'
    else:
        for key, value in config_dict.items():
            string = key + '=' + value + '\n'
            file_obj.writelines(string)
        file_obj.close()

if __name__ == '__main__':
    '''if os.path.isfile(__CONFIG_PATH__) == False:'''
    init_config()
