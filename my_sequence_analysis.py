import sys
import os
import string
import time
import copy
import types
import shutil
import ConfigParser
import random
from config import configuration

__VAR_TIME_INTERVAL__ = 60*10
__VAR_MAX_SERIAL_LENGTH__ = 5
__FN_RESULTS_LIST__ = 'result'
__FN_DISPLAY_RESULTS_LIST__ = 'result.txt'
__MY_VAR_ROOT_PATH__ = 'my'

class MySequenceAnalysis:
    def __init__(self):
        return
    def serial_generate(self, task, logpath):
        serial_generate(task, logpath)
    def reset_serial_analysis_enviroment(self, task):
        reset_serial_analysis_enviroment(task)


def reset_serial_analysis_enviroment(task):
    config = configuration()
    env_path = os.path.join(config.get_log_analysis_path(), task, __MY_VAR_ROOT_PATH__)
    if (os.path.isdir(env_path)):
        shutil.rmtree(env_path)
    os.makedirs(env_path)

def serial_generate(task, logpath):

    print '===== PREPARE TO EXCUTE MY SERIAL ANALYSIS ====='

    global lut_api_key
    config = configuration()
    lut_api_key = config.read_LUT(1)

    global serial_list_dict
    serial_list_dict = read_serial_list(task)
    temp_info = [[],0.0]

    print 'LOG TO ANALYSIS: ' + logpath
    if (os.path.exists(logpath)):
        print 'CALCULATING ... '
        'step 1 - form the api serial'
        file_log = open(logpath, 'r')
        for line in file_log:
            arrays = line.split('\t')
            temp = api_serial(arrays, temp_info)
            'step 2 - calculate orrurence of in each api serial'
            if (isinstance(temp, types.NoneType)):
                continue
            calculate_serial_orrurence(temp[0])
            temp_info = temp

        'step 3 - calculate probability'
        calculate_serial_probability(task)
        
        print 'CALCULATE COMPLETED!'
        print 'SAVING RESULTS ...'
        save_serial_list(task, serial_list_dict)
        config.save_LUT(lut_api_key)
        print 'SAVE COMPLETED!'
        print '===== ANLAYSIS COMPLETED ====='
        
    else:
        print 'ERROR: OPEN FILE FAILED!'
'-----------------------------------------------------------------------------------------'
def read_serial_list(task):
    serial_list_dict = {}
    configs = configuration()
    root = configs.get_log_analysis_path()
    serial_list_path = os.path.join(root, task, __MY_VAR_ROOT_PATH__,__FN_RESULTS_LIST__)
    if (os.path.isfile(serial_list_path) == True):
        file_serial_list = open(serial_list_path, 'r')
        for line in file_serial_list:
            arrays = line.split('=')
            serial = arrays[0]
            values = arrays[1].split('|')
            serial_list_dict[serial] = values
        file_serial_list.close()
    return serial_list_dict

def save_serial_list(task, serial_list_dict):
    configs = configuration()
    root = configs.get_log_analysis_path()
    serial_list_path = os.path.join(root, task, __MY_VAR_ROOT_PATH__,__FN_RESULTS_LIST__)
    serial_display_path = os.path.join(root, task, __MY_VAR_ROOT_PATH__, __FN_DISPLAY_RESULTS_LIST__)
    
    file_result = open(serial_list_path, 'w')
    file_result_display = open(serial_display_path, 'w')

    for key, value in serial_list_dict.items():
        
        'write serial result into file /serial.txt/ for later dispaly'
        linekey = key
        '''print linekey'''
        file_result_display.write(linekey)
        '''print '-----'''
        file_result_display.write('\n-----\n')
        linevalue = ''
        if (type(value) is types.ListType):
            for v in value:
                linevalue = linevalue + str(v) + '|'
            linevalue = linevalue.strip('|')
        else:
            linevalue = str(value)
        '''print linevalue'''
        file_result_display.write(linevalue)
        '''print '=========='''
        file_result_display.write('\n==========\n')

        'write serial result into file /serial/ for later use'
        serial_to_write = key + '=' + linevalue
        file_result.write(serial_to_write + '\n')
    file_result_display.close()
    file_result.close()
    
'------------------------------------------------------------------------'

def api_serial(logarray, temp_info):
    ''' ID || duration || type || timestart || timefinished \
    || urlbase || urlparms || urlbodyparms || responsedata || status '''

    api_serial = copy.deepcopy(temp_info[0])
    last_log_starttime = copy.deepcopy(temp_info[1])

    'process the log'
    'omit logs when \
                - 1. not a api link \
                - 2. failed request'
                
    'cut into serial when \
                - 1. timestart between two logs above __TIME_INTERVAL__ sec \
                - X 2. meet the POST type request'

    key = logarray[5]
    if (key.find('https://api') == -1):
        return
    duration = logarray[1]
    if (duration == 'duraiton'):
        return

    '-- check -1'
    current_log_starttime = int(logarray[3])
    '---- calculate the interval'
    if (last_log_starttime != 0):
        interval = current_log_starttime - last_log_starttime
        if interval > __VAR_TIME_INTERVAL__*1000:
            api_serial = []

    if (lut_api_key.has_key(key)):
        alapi = lut_api_key.get(key)
    else:
        largest_alph = ord('A')-1
        for api, alph in lut_api_key.items():
            if (ord(alph)>largest_alph):
                largest_alph = ord(alph)
        alapi = chr(largest_alph+1)
        lut_api_key[key] = alapi
            
    api_serial.append(alapi)
    temp_info = [api_serial, current_log_starttime]
    print temp_info[0]
    return temp_info

def calculate_serial_orrurence(api_serial):
    
    global serial_list_dict
    s_list = copy.deepcopy(api_serial)
    for i in range(0, len(api_serial)):
        pre_serial = '\t'.join(s_list)
        if (serial_list_dict.has_key(pre_serial)):
            serial_list_dict[pre_serial][0] = str(int(serial_list_dict[pre_serial][0]) + 1)
        else:
            serial_list_dict[pre_serial] = [1]
        del s_list[0]

def calculate_serial_probability(task):
    global serial_list_dict
    if (len(serial_list_dict) == 0):
        serial_list_dict = read_serial_list(task)
    for key, value in serial_list_dict.items():
        keyarray = key.split('\t')
        percentage = '0.00%'
        if (type(value) is types.ListType):
            v = int(value[0])
        else:
            v = int(value)
            value = [value]
        if (len(keyarray)>1):
            del keyarray[-1]
            pre_serial_key = '\t'.join(keyarray)
            if (serial_list_dict.has_key(pre_serial_key)):
                pre_serial_value = serial_list_dict.get(pre_serial_key)
                if (type(pre_serial_value) is types.ListType):
                    vpre = int(pre_serial_value[0])
                else:
                    vpre = int(pre_serial_value)
                percentage = format(float(v)/float(vpre), '.2%')
        if (len(value)<2):
            value.append(percentage)
        else:
            value[1] = percentage
        serial_list_dict[key] = value
        '''newvalue = [v, percentage]
        serial_list_dict[key] = newvalue'''
    print 'CALCULATED SERIAL PROBABILITY BELOW:'
    save_serial_list(task, serial_list_dict)
'----------------------------------------------------------------------------------'

def cut_tail(task):

    print '===== PREPARE TO CUTTING TAIL ====='
    global serial_list_dict
    serial_list_dict = read_serial_list(task)
    '{A : appear_times, appear_percentage_after_pre_serial}'

    serials = {}
    'CUT THE APPEARENCE TIME OF 1 AND PERCENTAGE OF 100%'
    'CUT THE REPLICATED SERIAL - ABC IF THERE IS ABCD'
    for key, values in serial_list_dict.items():
        if (values[0] == '1' and values[1] == '100.00%\n'):
            '''print 'FOUND TAIL!'
            print key
            print values
            print '-----'''
            continue
        elif (len(values) == 3 and values[2] == 'COUNTED'):
            continue
        else:
            keyarray = key.split('\t')
            valuearray = copy.deepcopy(values)
            for i in range(0, len(keyarray) - 1):
                del keyarray[-1]
                newkey = '\t'.join(keyarray)
                toaddv1 = '0,'
                toaddv2 = '0%,'
                if serial_list_dict.has_key(newkey):
                    vs = serial_list_dict.get(newkey)
                    if (len(vs) != 3):
                        vs.append('COUNTED')
                        serial_list_dict[newkey] = vs
                    toaddv1 = vs[0] + ','
                    toaddv2 = vs[1].strip('\n') + ','
                valuearray[0] = toaddv1 + valuearray[0]
                valuearray[1] = toaddv2 + valuearray[1]
                serials[key] = valuearray

    time.sleep(1)
    print '===== CUTTING TAIL COMPLETED===== '
    '''for key, values in serials.items():
        print key
        print values
        print '-----'''
    return serials

'-------------------------------------------------------------------------------------'

def predict_task(task, serials):
    global lut_api_key
    config = configuration()
    lut_api_key = config.read_LUT(1)

    task_log_path = os.path.join(config.get_log_analysis_path(), task, task)
    try:
        task_log_file = open(task_log_path, 'r')
    except:
        print 'OPEN LOG FILE FAILED! (' + task_log_file + ')'
    else:
        api_serial = []
        last_time = 0
        predict_count = 0
        predict_hitted = 0
        total_api_count = 0
        next_api_key = ''

        random_hitted = 0
        for line in task_log_file:
            linearray = line.split('\t')
            api = linearray[5]
            
            'check whether it is a api'
            if (lut_api_key.has_key(api)):
                apikey = lut_api_key[api]
            else:
                continue
            
            'check whether time out'         
            if (last_time > 0):
                if (int(linearray[3]) - last_time > __VAR_TIME_INTERVAL__*1000):
                    api_serial = []
                else:
                    'it is a valid api, check whether predict hitted!'
                    total_api_count = total_api_count + 1
                    if (next_api_key != ''):
                        random_next_api = chr(random.randint(ord('A'), ord('A')+len(lut_api_key)-1))
                        if (apikey == random_next_api):
                            random_hitted = random_hitted + 1
                    
                    if (apikey == next_api_key):
                        predict_hitted = predict_hitted + 1
                        '''print 'PREDICT HITTED!'''
            next_api_key = ''
            last_time = int(linearray[3])

            api_serial.append(apikey)
            predict = prediction(api_serial, serials)
            if (predict != False):
                predict_count = predict_count + 1
                next_api_key = predict
                
        task_log_file.close()
        print '===== PREDICT TASK COMPLETED ====='
        time.sleep(2)
        print 'TOTAL API COUNT:' + str(total_api_count)
        print 'PREDICTED COUNT:' + str(predict_count)
        print 'PREDICTED HITTED COUNT:' + str(predict_hitted)
        print 'RANDOM HITTED COUNT:' + str(random_hitted)
        
def prediction(api_serial, serials):
    
    prediction_set = {}
    for i in range(0, len(api_serial)):
        for key, values in serials.items():
            if (key.startswith('\t'.join(api_serial))):
                keyarray = key.split('\t')
                if (len(keyarray) > len(api_serial)):
                    
                    api = keyarray[len(api_serial)]
                    percentage = float((values[1].strip('\n').split(','))[len(api_serial)].strip('%'))
                    if (prediction_set.has_key(api) and percentage < float(prediction_set[api])):
                        continue
                    prediction_set[api] = str(percentage)
        del api_serial[0]
                    
    max_percentage = 0.0
    max_key = ''
    for key, value in prediction_set.items():
        if (float(value)>max_percentage):
            max_percentage = float(value)
            max_key = key
    '''print predicted next key:  + max_key
    print predicted percentage:  + str(max_percentage) + %'''
    if (float(max_percentage) > 50.0):
        return max_key
    else:
        return False

if __name__ == '__main__':
    
    print '===== WELCOME TO MY SERIAL ANALYSIS STUDIO ====='
    configs = configuration()
    waiting_tasks = os.listdir(configs.get_log_analysis_path())

    exit_studio = False
    while (exit_studio == False):
        print 'TASKS BELOW:'
        print '0 - CANCEL'
        i = 1
        for task in waiting_tasks:
            print str(i) + ' - ' + task
            i = i + 1
        task_number = input('PLEASE CHOOSE THE NUMBER OF TASK: ')
        if (task_number == 0):
            break
        if (task_number < i+1):
            task = waiting_tasks[task_number-1]
            print 'STARTING ANALYZE TASK:' + task
            time.sleep(2)
            serials = cut_tail(task)
            
            print 'EXPERIMENT THE PREDICTION...'
            time.sleep(2)
            predict_task(task, serials)
            
            print '===== ANLAYSIS COMPLETED ====='
            confirm = raw_input('===== CONTINUE ANALYSIS MORE TASK? (Y/N)\n')
            if (confirm.upper() != Y):
                exit_studio = True
    print '===== EXIT MY SERIAL ANALYSIS STUDIO ====='
