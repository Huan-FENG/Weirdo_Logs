import sys
import ConfigParser
import os
import string
import types
import time
from analyze_ologs_dir import UndoTask
from config import configuration

__TEMP_SENDTYPE_LOG__ = 'sendtype_log.temp'
__TEMP_RECIEVETYPE_LOG__ = 'recivetype_log.temp'
__TEMP_LOG__ = 'log.temp'

__READ_SENDTYPE_LOG_PERTME__ = 20
__READ_RECIEVETYPE_LOG_PERTME__ = 20
__CHECK_NEXT_LOG_COUNT__ = 20

__RECHECK_STATUS__ = False
''' data before 2014-5-23 need recheck to 1-cellur|2-wifi, means set VAR=True'''

''' ID || type || time || urlbase || urlparms || urlbodyparms || responsedata || status '''
''' ID || duration || type || timestart || timefinished || urlbase || urlparms || urlbodyparms || responsedata || status '''
 

def check_undo_task_list():
    print 'CHECK UNDO TASK LIST!'
    instance_undo_task = UndoTask()
    todo_task_path = instance_undo_task.get_todo_task_path()
    return todo_task_path

def generate_temp_logs(taskpath):
    taskkey = os.path.basename(os.path.dirname(taskpath))
    print taskkey
    configs = configuration()

    try:
        ologfile_obj = open(taskpath, 'r')
    except IOError:
        print'== ERROR: OPEN FAILED! (' + taskpath + ')'
    else:
        log_file_root = configs.get_log_path()

        file_temp_send_log = __TEMP_SENDTYPE_LOG__
        file_temp_send_log_obj = open(os.path.join(log_file_root, file_temp_send_log), 'w+')
        file_temp_recieved_log = __TEMP_RECIEVETYPE_LOG__
        file_temp_recieved_log_obj = open(os.path.join(log_file_root, file_temp_recieved_log), 'w+')

        global send_log_count
        global recieved_log_count
        send_log_count = 0
        recieved_log_count = 0
        
        for current_line, line in enumerate(ologfile_obj):
            if line.split('\t')[0] == 'ID':
                continue
    
            send_log_count = send_log_count + 1
            togenerate_log = line.split('\t')
            if (__RECHECK_STATUS__):
                status = togenerate_log[-1]
                if (status == '1\n'):
                    togenerate_log[-1] = '2\n'
                if (status == '2\n'):
                    togenerate_log[-1] = '1\n'
            if (len(togenerate_log[2]) == 10):
                togenerate_log[2]=togenerate_log[2]+'000'
            if togenerate_log[1] == 'data':
                recieved_log_count = recieved_log_count + 1
                send_log_count = send_log_count - 1
                file_temp_recieved_log_obj.write('\t'.join(togenerate_log))
            else:
                togenerate_log.insert(1, 'duration')
                togenerate_log.insert(4, 'timefinished')
                file_temp_send_log_obj.write('\t'.join(togenerate_log))
        ologfile_obj.close()
        file_temp_send_log_obj.close()
        file_temp_recieved_log_obj.close()
        print '== SEND LOG COUNT: ' + str(send_log_count) + '\tRECIEVED LOG COUNT: ' + str(recieved_log_count)

def generate_task_log(taskkey):
    
    configs = configuration()
    log_file_root = configs.get_log_path()

    'clear temp file'
    log_temp_file_path = os.path.join(log_file_root, __TEMP_LOG__)
    if (os.path.isfile(log_temp_file_path)):
        os.remove(log_temp_file_path)

    'init relative var'
    global failed_sendlog_count
    failed_sendlog_count = 0
    global failed_recievedlog_count
    failed_recievedlog_count = 0

    sendlog_offset = 0
    sendlogs = []
    print 'READ FIRST ' + str(__READ_SENDTYPE_LOG_PERTME__) + ' SEND LOGS FROM OFFSET ' + str(sendlog_offset)
    read_send_log_dict = read_temp_log(__TEMP_SENDTYPE_LOG__, sendlog_offset)
    sendlogs.extend(read_send_log_dict.get('lines'))
    sendlog_offset = read_send_log_dict.get('offset')

    recievedlog_offset = 0
    recievedlogs = []
    print 'READ FIRST ' + str(__READ_RECIEVETYPE_LOG_PERTME__) + ' RECIEVED LOGS FROM OFFSET ' + str(recievedlog_offset)
    read_recieved_log_dict = read_temp_log( __TEMP_RECIEVETYPE_LOG__, recievedlog_offset)
    recievedlogs.extend(read_recieved_log_dict.get('lines'))
    recievedlog_offset = read_recieved_log_dict.get('offset')

    while (True):
        if (len(recievedlogs) == 0):
            print 'READ NEXT ' + str(__READ_RECIEVETYPE_LOG_PERTME__) + ' RECIEVED LOGS FROM OFFSET ' + str(recievedlog_offset)
            read_recieved_log_dict = read_temp_log( __TEMP_RECIEVETYPE_LOG__, recievedlog_offset)
            if (len(read_recieved_log_dict.get('lines')) == 0):
                print '== NO MORE RECIEVED LOGS!'
                write_temp_log_without_check(sendlogs, log_temp_file_path)
                print '== COMPARE FINISHED!'
                os.remove 
                break
            else:
                recievedlogs.extend(read_recieved_log_dict.get('lines'))
                recievedlog_offset = read_recieved_log_dict.get('offset')
            
        recievedlog = recievedlogs[0]
        logID = recievedlog[0]
        send_log_founded = False
        for sendlog in sendlogs:
            if (sendlog[0] == logID and sendlog[1] == 'duration'):
                sendlog[4] = recievedlog[2]
                sendlog[8] = recievedlog[6]
                sendlog[1] = str(float(recievedlog[2])-float(sendlog[3]))
                ''' print 'PRETREAMTMENT COMPLETED LOG ID : '+ sendlog[0]'''
                send_log_founded = True
                break
        if (send_log_founded == True):
            del recievedlogs[0]
            if (len(recievedlogs) == 0):
                write_temp_log(sendlogs, log_temp_file_path)
        else:
            print 'READ NEXT ' + str(__READ_SENDTYPE_LOG_PERTME__) + ' SEND LOGS FROM OFFSET ' + str(sendlog_offset)
            read_send_log_dict = read_temp_log(__TEMP_SENDTYPE_LOG__, sendlog_offset)
            if (len(read_send_log_dict.get('lines')) == 0):
                print '== NO MORE SEND LOGS!'
                print '== UNKNOWN RECIEVED LOG: ID = ' + logID
                del recievedlogs[0]
            else:
                sendlog_offset = read_send_log_dict.get('offset')
                sendlogs.extend(read_send_log_dict.get('lines'))
    
def write_log(taskkey):
    
    configs = configuration()
    log_file_root = configs.get_log_path()
    log_file_path = os.path.join(log_file_root, taskkey)
    temp_log_file_path = os.path.join(log_file_root, __TEMP_LOG__)

    file_log = open(log_file_path, 'a')
    if (os.path.isfile(temp_log_file_path) == True):
        file_temp_log = open(temp_log_file_path, 'r')
        for line in file_temp_log:
            file_log.write(line)
        file_temp_log.close()
        os.remove(temp_log_file_path)
    else:
        print 'THERE IS NO TEMP LOGS'
    file_log.close()

def write_temp_log(sendlogs, logpath):

    global check_next_log_count
    task_log_obj = open(logpath, 'a')
    while True:
        if (len(sendlogs) == 0):
            break
        if (sendlogs[0][1] != 'duration'):
            task_log_obj.write('\t'.join(sendlogs[0]))
            del sendlogs[0]
        else:
            checklogcount = 0
            for i in range(1, len(sendlogs)-1):
                if (sendlogs[i][1] != 'duration'):
                    checklogcount = checklogcount + 1
            if (checklogcount > check_next_log_count):
                print '== FOUND FAILED SEND LOG ID: ' + str(sendlogs[0][0])
                global failed_sendlog_count
                failed_sendlog_count = failed_sendlog_count + 1
                task_log_obj.write('\t'.join(sendlogs[0]))
                del sendlogs[0]
            else:
                '''cannot decide whether it is a failed send log!'''
                break
    task_log_obj.close()

def write_temp_log_without_check(sendlogs, logpath):
    
    if (len(sendlogs) == 0):
        return
    task_log_obj = open(logpath, 'a')
    for sendlog in sendlogs:
        if (sendlog[1] == 'duration'):
            print '== FOUND FAILED SEND LOG ID: ' + str(sendlog[0])
            global failed_sendlog_count
            failed_sendlog_count = failed_sendlog_count + 1
        task_log_obj.write('\t'.join(sendlog))
    task_log_obj.close()
            
def read_temp_log(temp_log, offset):

    if temp_log == __TEMP_SENDTYPE_LOG__:
        maxcount = __READ_SENDTYPE_LOG_PERTME__
    else:
        maxcount = __READ_RECIEVETYPE_LOG_PERTME__
        
    configs = configuration()
    log_file_root = configs.get_log_path()
    file_temp_log = open(os.path.join(log_file_root, temp_log), 'r')
    file_temp_log.seek(offset, 0)

    count = 0
    lines_array = []
    while count < maxcount:
        temp = file_temp_log.readline()
        if (temp ==  ''):
            break
        templog = temp.split('\t')
        lines_array.append(templog)
        count = count + 1
    newoffset = file_temp_log.tell()
    templogsdict = {}
    templogsdict['offset'] = newoffset
    templogsdict['lines'] = lines_array
    file_temp_log.close()
    return templogsdict

def del_temp_logs():

    configs = configuration()
    log_file_root = configs.get_log_path()
    if os.path.isfile(os.path.join(log_file_root, __TEMP_SENDTYPE_LOG__)):
        os.remove(os.path.join(log_file_root, __TEMP_SENDTYPE_LOG__))
                      
    if os.path.isfile(os.path.join(log_file_root,  __TEMP_RECIEVETYPE_LOG__)):
        os.remove(os.path.join(log_file_root, __TEMP_RECIEVETYPE_LOG__))
                      
    if os.path.isfile(os.path.join(log_file_root, __TEMP_LOG__)):
        os.remove(os.path.join(log_file_root, __TEMP_LOG__))
    

def check_pretreatment_correction():
    global send_log_count
    global recieved_log_count
    global failed_sendlog_count
    global failed_recievedlog_count

    if failed_recievedlog_count:
        print 'MATCH FAILED! [' + str(failed_recievedlog_count) + \
        ' RECIEVED LOG DIDNOT FIND MATCH'
        return False

    if (send_log_count-recieved_log_count != failed_sendlog_count):
        print 'MATCH FAILED! [SEND LOG(' + str(send_log_count) + ') - RECIEVED LOG(' + \
        str(recieved_log_count) + ') != FAILED SEND LOG(' + str(failed_sendlog_count) + ')]'
        return False

    print 'MATCH COMPELETED! [SEND LOG(' + str(send_log_count) + ') | RECIEVED LOG(' + \
        str(recieved_log_count) + ') | FAILED SEND LOG(' + str(failed_sendlog_count) + ')'
    
    return True
    
if __name__ == '__main__':

    print '========== READY TO PRETREATMENT ==========\n'

    total_log_count = 0
    failed_sendlog_count = 0
    failed_recievedlog_count = 0
    send_log_count = 0
    recieved_log_count = 0
    check_next_log_count = __CHECK_NEXT_LOG_COUNT__
    pretreatment_finished = False
    while (pretreatment_finished == False):
        todo_task_path = check_undo_task_list()
        if type(todo_task_path) is types.StringType:
            print '= THERE IS TASK TO DO! ' + todo_task_path
            print '= START TO DO THE TASK AFTER 10 SECENDS!'
            time.sleep(3)
            '''do the task'''
            print '\nSTEP 0 : GENERATE TEMP LOGS (RECIEVED LOGS && SEND LOGS)'
            generate_temp_logs(todo_task_path)

            print '\nSTEP 1 : MATCH TEMP LOGS'
            taskkey = os.path.basename(os.path.dirname(todo_task_path))
            generate_task_log(taskkey)

            print '\nSTEP 2: CHECK PRETREATMENT CORRECTION'
            for i in range (0, 3):
                if (check_pretreatment_correction() == False):
                    print 'PRETREATMTNET INCORRECT!'
                    print '\nBACK TO STEP 1: MATCH TEMP LOGS (10 SECENDS LATER)'

                    time.sleep(10)
                    check_next_log_count = check_next_log_count + 20
                    generate_task_log(taskkey)
                else:
                    break
            
            if (check_pretreatment_correction() == True):
                print 'PRETREATMTNET CORRECT!'
                print '\nSTEP 3: APPEND CORRECTED TEMP LOGS INTO LOGS'
            else:
                print 'PRETREATMENT STILL INCORRECT!'
                print 'STOP CORRECTION CHECK!'
                print '\nSTEP 3: APPEND TEMP LOGS INTO LOGS'
            write_log(taskkey)
                        
            instance_undotask = UndoTask()
            instance_undotask.finished_task_at_path(todo_task_path)
            total_log_count = total_log_count + send_log_count
            '''pretreatment_finished = True'''
        else:
            print '= THERE IS NO TASK LEFT!\n'
            print 'CHECK LATEST TASKS!'
            execfile('analyze_ologs_dir.py')
            todo_task_path = check_undo_task_list()
            if type(todo_task_path) is types.NoneType:
                print '= THERE IS NO NEW UNDO TASK!\n'
                del_temp_logs()
                pretreatment_finished = True
    print '= TOTAL LOG PRETREATED: ' + str(total_log_count)
    print '========== PRETREATMENT FINIESHED =========='
