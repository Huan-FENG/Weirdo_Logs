import sys
import os
import string
import time
import copy
import types
import ConfigParser
from config import configuration
from my_sequence_analysis import MySequenceAnalysis

__TYPE_NEW_DATA__ = '1'
__TYPE_COLLECTED_DATA__ = '2'

__BASIC_KN_TOTAL__ = 'total'
__BASIC_KN_CELLUR__ = 'cellur'
__BASIC_KN_WIFI__ = 'wifi'
__BASIC_FN_RESULTS__ = 'basic_analysis_results.txt'
__BASIC_VAR_DURATION__ = 'AVERAGE DURATION'
__BASIC_VAR_TOTAL_COUNT__ = 'TOTAL REQUEST COUNT'
__BASIC_VAR_FAILED_COUNT__ = 'FAILED REQUEST COUNT'
__BASIC_VAR_FAILED_PERCENTAGE__ = 'FAILED REQUEST PERCENTAGE'


def basic_analysis_task(task, analysis_type):

    if (analysis_type == __TYPE_COLLECTED_DATA__):
        delete_basic_result(task)
    
    basic_analysis_initiation(task)

    configs = configuration()
    if (analysis_type == __TYPE_NEW_DATA__):
        task_log_path = os.path.join(configs.get_log_path(), task)
        log_path = os.path.join(os.path.join(configs.get_log_analysis_path(), task),task)
    if (analysis_type == __TYPE_COLLECTED_DATA__):
        task_log_path = os.path.join(os.path.join(configs.get_log_analysis_path(), task),task)

    try:
        file_task_log = open(task_log_path, 'r')
    except IOError:
        print 'ERROR: OPEN FAILED! (' + task_log_path + ')'
    else:
        for line in file_task_log:
            basic_analysis_for_line(line)
        file_task_log.close()
        
    basic_analysis_tofinished(task)     
    
        
def read_basic_result_as_result_dict(task):
    root_path = configs.get_log_analysis_path()
    task_root_path = os.path.join(root_path, task)   
    basic_result_path = os.path.join(task_root_path, __BASIC_FN_RESULTS__)
    basic_result_dict = {}
    if (os.path.isfile(basic_result_path) == True):
        file_basic_result = open(basic_result_path, 'r')
        for line in file_basic_result:
            arrays = line.split('=')
            '''if (arrays[0] == __ANALYSIS_SERIAL__):
                break'''
            basic_result_dict[arrays[0]] = arrays[1].strip('\n')
        file_basic_result.close()
    return basic_result_dict

def save_basic_result_dict(task, result_dict):
    root_path = configs.get_log_analysis_path()
    task_root_path = os.path.join(root_path, task)
    basic_result_path = os.path.join(task_root_path, __BASIC_FN_RESULTS__)
    file_basic_result = open(basic_result_path, 'w+')
    file_basic_result.write(__BASIC_VAR_DURATION__ + '=' + \
                      result_dict.get(__BASIC_VAR_DURATION__) + '\n')
    file_basic_result.write(__BASIC_VAR_TOTAL_COUNT__+ '=' + \
                      result_dict.get(__BASIC_VAR_TOTAL_COUNT__) + '\n')
    file_basic_result.write(__BASIC_VAR_FAILED_COUNT__+ '=' + \
                      result_dict.get(__BASIC_VAR_FAILED_COUNT__) + '\n')
    file_basic_result.write(__BASIC_VAR_FAILED_PERCENTAGE__ + '=' + \
                      result_dict.get(__BASIC_VAR_FAILED_PERCENTAGE__) + '\n')
    file_basic_result.close()

def delete_basic_result(task):
    root_path = configs.get_log_analysis_path()
    task_root_path = os.path.join(root_path, task)
    basic_result_path = os.path.join(task_root_path, __BASIC_FN_RESULTS__)
    if (os.path.exists(basic_result_path)):
        os.remove(basic_result_path)

def basic_analysis_initiation(task):
    global total_duration
    global total_request_count
    global failed_request_count

    average_duration = {__BASIC_KN_TOTAL__:0.0, __BASIC_KN_CELLUR__:0.0, __BASIC_KN_WIFI__:0.0}
    total_request_count = {__BASIC_KN_TOTAL__:0, __BASIC_KN_CELLUR__:0, __BASIC_KN_WIFI__:0}
    failed_request_count = {__BASIC_KN_TOTAL__:0, __BASIC_KN_CELLUR__:0, __BASIC_KN_WIFI__:0}

    basic_result_dict = read_basic_result_as_result_dict(task)
    
    if (len(basic_result_dict) != 0):
        averages = basic_result_dict.get(__BASIC_VAR_DURATION__).split('|')
        average_duration[__BASIC_KN_TOTAL__] = float(averages[0])
        average_duration[__BASIC_KN_CELLUR__] = float(averages[1])
        average_duration[__BASIC_KN_WIFI__] = float(averages[2])
        
        total_request_counts = basic_result_dict.get(__BASIC_VAR_TOTAL_COUNT__).split('|')
        total_request_count[__BASIC_KN_TOTAL__] = int(total_request_counts[0])
        total_request_count[__BASIC_KN_CELLUR__] = int(total_request_counts[1])
        total_request_count[__BASIC_KN_WIFI__] = int(total_request_counts[2])
        
        failed_request_counts = basic_result_dict.get(__BASIC_VAR_FAILED_COUNT__).split('|')
        failed_request_count[__BASIC_KN_TOTAL__] = int(failed_request_counts[0])
        failed_request_count[__BASIC_KN_CELLUR__] = int(failed_request_counts[1])
        failed_request_count[__BASIC_KN_WIFI__] = int(failed_request_counts[2])

    print 'AVERAGE_DURATEION = ' + str(average_duration.get(__BASIC_KN_TOTAL__)) + '|' + \
          str(average_duration.get(__BASIC_KN_CELLUR__)) + '|' + \
          str(average_duration.get(__BASIC_KN_WIFI__))
    print 'TOTAL_REQUEST_COUNT = ' + str(total_request_count.get(__BASIC_KN_TOTAL__)) + '|' + \
          str(total_request_count.get(__BASIC_KN_CELLUR__)) + '|' + \
          str(total_request_count.get(__BASIC_KN_WIFI__))
    print 'FAILED_REQUEST_COUNT = ' + str(failed_request_count.get(__BASIC_KN_TOTAL__)) + '|' + \
          str(failed_request_count.get(__BASIC_KN_CELLUR__)) + '|' + \
          str(failed_request_count.get(__BASIC_KN_WIFI__))
    
    total_duration[__BASIC_KN_TOTAL__] = (total_request_count.get(__BASIC_KN_TOTAL__) - \
                                          failed_request_count.get(__BASIC_KN_TOTAL__)) \
                                          *average_duration.get(__BASIC_KN_TOTAL__)
    total_duration[__BASIC_KN_CELLUR__] = (total_request_count.get(__BASIC_KN_CELLUR__) - \
                                               failed_request_count.get(__BASIC_KN_CELLUR__)) \
                                              *average_duration.get(__BASIC_KN_CELLUR__)
    total_duration[__BASIC_KN_WIFI__] = (total_request_count.get(__BASIC_KN_WIFI__) - \
                                             failed_request_count.get(__BASIC_KN_WIFI__)) \
                                              *average_duration.get(__BASIC_KN_WIFI__)

def basic_analysis_for_line(line):
    global total_duration
    global total_request_count
    global failed_request_count
    arrays = line.split('\t')
    
    'add into total count'
    total_request_count[__BASIC_KN_TOTAL__] = total_request_count.get(__BASIC_KN_TOTAL__) + 1
    if (arrays[9] == '1\n'):
        total_request_count[__BASIC_KN_CELLUR__] = total_request_count.get(__BASIC_KN_CELLUR__) + 1
    if (arrays[9] == '2\n'):
        total_request_count[__BASIC_KN_WIFI__] = total_request_count.get(__BASIC_KN_WIFI__) + 1
        
    duration = arrays[1]
    
    if (duration != 'duration' and float(duration)>0 and float(duration)<300000):
        'add into total duration to calculate average duration later'
        total_duration[__BASIC_KN_TOTAL__] = total_duration.get(__BASIC_KN_TOTAL__) + float(duration)
        if (arrays[9] == '1\n'):
            total_duration[__BASIC_KN_CELLUR__] = total_duration.get(__BASIC_KN_CELLUR__) + float(duration)
        if (arrays[9] == '2\n'):
            total_duration[__BASIC_KN_WIFI__] = total_duration.get(__BASIC_KN_WIFI__) + float(duration)
    else:
        'add into failed count'
        failed_request_count[__BASIC_KN_TOTAL__] = failed_request_count.get(__BASIC_KN_TOTAL__) + 1
        if (arrays[9] == '1\n'):
            failed_request_count[__BASIC_KN_CELLUR__] = failed_request_count.get(__BASIC_KN_CELLUR__) + 1
        if (arrays[9] == '2\n'):
            failed_request_count[__BASIC_KN_WIFI__] = failed_request_count.get(__BASIC_KN_WIFI__) + 1

        if (duration != 'duration'):
            if (float(duration)<=0):
                print 'ERROR!!!!!!! FOUND DURATION LESS THAN 0 SECOND'
            if (float(duration)>=300000):
                print 'ERROR!!!!! FOUND DURATION MORE THANE 5 MIN'

def basic_analysis_tofinished(task):
    
    global total_request_count
    global failed_request_count
    global total_duration
    
    result_dict = {}
    
    average_duration = {}
    average_duration[__BASIC_KN_TOTAL__] = total_duration.get(__BASIC_KN_TOTAL__)/ \
                                           (total_request_count.get(__BASIC_KN_TOTAL__) - \
                                            failed_request_count.get(__BASIC_KN_TOTAL__))
    if (total_duration.get(__BASIC_KN_CELLUR__) != 0.0):
        average_duration[__BASIC_KN_CELLUR__] = total_duration.get(__BASIC_KN_CELLUR__)/ \
                                                (total_request_count.get(__BASIC_KN_CELLUR__) - \
                                                 failed_request_count.get(__BASIC_KN_CELLUR__))
    else:
        average_duration[__BASIC_KN_CELLUR__] =0.0
    if (total_duration.get(__BASIC_KN_WIFI__) != 0.0):
        average_duration[__BASIC_KN_WIFI__] = total_duration.get(__BASIC_KN_WIFI__)/ \
                                              (total_request_count.get(__BASIC_KN_WIFI__) - \
                                               failed_request_count.get(__BASIC_KN_WIFI__))
    else:
        average_duration[__BASIC_KN_WIFI__] = 0.0
    
    result_dict[__BASIC_VAR_DURATION__] = str(average_duration.get(__BASIC_KN_TOTAL__)) + '|' + \
          str(average_duration.get(__BASIC_KN_CELLUR__)) + '|' + \
          str(average_duration.get(__BASIC_KN_WIFI__))
    result_dict[__BASIC_VAR_TOTAL_COUNT__] = str(total_request_count.get(__BASIC_KN_TOTAL__)) + '|' + \
          str(total_request_count.get(__BASIC_KN_CELLUR__)) + '|' + \
          str(total_request_count.get(__BASIC_KN_WIFI__))
    result_dict[__BASIC_VAR_FAILED_COUNT__] = str(failed_request_count.get(__BASIC_KN_TOTAL__)) + '|' + \
          str(failed_request_count.get(__BASIC_KN_CELLUR__)) + '|' + \
          str(failed_request_count.get(__BASIC_KN_WIFI__))

    percentage_cellur = 0.0
    if (failed_request_count.get(__BASIC_KN_CELLUR__) > 0.0):
        percentage_cellur = float(failed_request_count.get(__BASIC_KN_CELLUR__))/ \
                            float(total_request_count.get(__BASIC_KN_CELLUR__))*100.0
    percentage_wifi = 0.0
    if (failed_request_count.get(__BASIC_KN_WIFI__) > 0.0):
        percentage_wifi = float(failed_request_count.get(__BASIC_KN_WIFI__))/ \
                          float(total_request_count.get(__BASIC_KN_WIFI__))*100.0
    failed_percentage = str(float(failed_request_count.get(__BASIC_KN_TOTAL__))/ \
                            float(total_request_count.get(__BASIC_KN_TOTAL__))*100.0) + '%|'+ \
                      str(percentage_cellur) + '%|'+ \
                      str(percentage_wifi) + '%'
    result_dict[__BASIC_VAR_FAILED_PERCENTAGE__] = failed_percentage
    save_basic_result_dict(task, result_dict)

    print 'AVERAGE_DURATEION = ' + str(average_duration.get(__BASIC_KN_TOTAL__)) + '|' + \
          str(average_duration.get(__BASIC_KN_CELLUR__)) + '|' + \
          str(average_duration.get(__BASIC_KN_WIFI__))
    print 'TOTAL_REQUEST_COUNT = ' + str(total_request_count.get(__BASIC_KN_TOTAL__)) + '|' + \
          str(total_request_count.get(__BASIC_KN_CELLUR__)) + '|' + \
          str(total_request_count.get(__BASIC_KN_WIFI__))
    print 'FAILED_REQUEST_COUNT = ' + str(failed_request_count.get(__BASIC_KN_TOTAL__)) + '|' + \
          str(failed_request_count.get(__BASIC_KN_CELLUR__)) + '|' + \
          str(failed_request_count.get(__BASIC_KN_WIFI__))
    
def del_task(task):
    configs = configuration()
    log_file_root = configs.get_log_path()
    task_file_path = os.path.join(log_file_root, task)
    os.remove(task_file_path)

if __name__ == '__main__':

    print '========== LOG ANALYSIS =========='
    while True:
        print 'CHOOSE ANALYSIS TYPE'
        print __TYPE_NEW_DATA__ + ' -ANALYSIS NEW DATA'
        print __TYPE_COLLECTED_DATA__ + ' -REANALYSIS COLLECTED DATA'
        chosen_type = raw_input('PLEASE CHOOSE ANALYSIS TYPE: ')
        if (chosen_type == __TYPE_NEW_DATA__ or \
            chosen_type == __TYPE_COLLECTED_DATA__):
            break

    configs = configuration()
    if (chosen_type == __TYPE_NEW_DATA__):
        log_file_root = configs.get_log_path()
    if (chosen_type == __TYPE_COLLECTED_DATA__):
        log_file_root = configs.get_log_analysis_path()

    waiting_tasks = os.listdir(log_file_root)
    print waiting_tasks

    total_duration = {}
    total_request_count = {}
    failed_request_count = {}

    for task in waiting_tasks:
        if (chosen_type == __TYPE_COLLECTED_DATA__):
            confirm = raw_input('===== REANALYSIS TASK: ' + task + ' (Y/N)\n')
            if (confirm.upper() != 'Y'):
                continue
            while True:
                print '0 -ALL ANALYSIS'
                print '1 -BASIC ANALYSIS'
                print '2 -MY SERIAL ANALYSIS'
                print '3 -CANCEL'
                input_type = raw_input()
                if (input_type == '0'):
                    '''analysis_task(task, chosen_type)
                    calculate_serial_probability(task)'''
                    break
                elif (input_type == '1'):
                    basic_analysis_task(task, chosen_type)
                    break
                elif (input_type == '2'):
                    logpath = os.path.join(log_file_root, task, task)
                    my_sequence_analysis = MySequenceAnalysis()
                    my_sequence_analysis.reset_serial_analysis_enviroment(task)
                    my_sequence_analysis.serial_generate(task, logpath)
                    break
                elif (input_type == '3'):
                    print 'CANCEL ANALYSIS TASK!'
                    break
                else:
                    print 'PLEASE CHOOSE ANALYSIS TYPE:'
        else:
            print '===== ANALYSIS TASK: ' + task
            basic_analysis_task(task, chosen_type)
            logpath = os.path.join(log_file_root, task)
            my_sequence_analysis = MySequenceAnalysis()
            my_sequence_analysis.my_serial_generate(task, logpath)
    print '========== ANALYSIS COMPLETED =========='
