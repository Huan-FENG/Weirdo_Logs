import sys
import os
import string
import time
import copy
import types
import ConfigParser
from config import configuration
from log_analysis import SerialList

__MAX_SERIAL_COUNT__ = 5

if __name__ == '__main__':
    print '========== SERIAL ANALYSIS =========='
    configs = configuration()
    log_file_root = configs.get_log_analysis_path()
    waiting_tasks = os.listdir(log_file_root)

    serial_list = SerialList()
    serials = {}
    for task in waiting_tasks:
        print '===== FOR TASK: '+ task
        serial_list_dict = serial_list.get_serial_list(task)
        print '===== FIRST ANALYSIS: SEQUENCE AND PROPERBILITY ====='
        for i in range(0, __MAX_SERIAL_COUNT__):
            print 'FOR THE TIME:' + str(i)
            time.sleep(2)
            for key, values in serial_list_dict.items():
                keyarray = key.split('\t')
                if (len(keyarray) == (__MAX_SERIAL_COUNT__-i)):
                    if (len(values) == 3 and values[2] == '0'):
                        continue
                    '''print '---------------'
                    print '\n'.join(keyarray)'''
                    for j in range(0, __MAX_SERIAL_COUNT__-i-1):
                        del keyarray[-1]
                        newkey = '\t'.join(keyarray)
                        toaddv1 = '0,'
                        toaddv2 = '0%,'
                        if serial_list_dict.has_key(newkey):
                            vs = serial_list_dict.get(newkey)
                            if (len(vs) != 3):
                                vs.append('0')
                                serial_list_dict[newkey] = vs
                            toaddv1 = vs[0] + ','
                            toaddv2 = vs[1].strip('\n') + ','
                        values[0] = toaddv1 + values[0]
                        values[1] = toaddv2 + values[1]
                    '''print values[0]
                    print values[1]'''
                    serials[key] = values

    print '============'
    for key, values in serials.items():
        print '------'
        print '\n'.join(key.split('\t'))
        print '--'
        print values[0]
        print values[1]
                    
                    
                
            
        
