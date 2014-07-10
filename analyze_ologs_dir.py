import sys
import os
import config
from config import configuration

class UndoTask:
    def __init__(self):
        return

    def get_todo_task_path(self):
        return get_undo_task(0)

    def finished_task_at_path(self, path):
        delete_undo_task_at_path(path)
        add_completed_task_at_path(path)

def add_completed_task_at_path(path):
    instance_config = configuration()
    root_path = instance_config.get_oringal_log_path()
    toadd_task = path.replace(root_path + '\\', '')
    file_completed_task_list = instance_config.get_completed_task_list_path()
    try:
        file_obj = open(file_completed_task_list, 'a+')
    except IOError:
        print '=== ERROR: OPEN FAILED!(' + file_completed_task_list + ')'
    else:
        print '=== ADDING COMPLETED TASK TO LIST! (' + toadd_task + ')'
        toadd_task = toadd_task + '\n'
        file_obj.write(toadd_task)
        file_obj.close()
        
def read_completed_tasks_list():
    completed_task_list = []
    global configs
    file_completed_task_list = configs.get_completed_task_list_path()
    print '= READ COMPLETED TASK LIST FILE: ' + file_completed_task_list
    try:
        file_obj = open(file_completed_task_list, 'r')
    except IOError:
        print '=== ERROR: OPEN FAILED!(' + file_completed_task_list + ')'
    else:
        print '=== START READING!'
        completed_task_list = file_obj.readlines()
        file_obj.close()
        print ''.join(completed_task_list)
        print '=== READING COMPLETED!'
    return completed_task_list

def add_undo_task(task_key, task_name):
    global undo_task_dict
    if undo_task_dict.has_key(task_key):
        undo_task_dict[task_key].append(task_name)
    else:
        tasks = [task_name]
        undo_task_dict[task_key] = tasks

def get_undo_task(index):
    instance_config = configuration()
    file_undo_task_list = instance_config.get_undo_task_list_path()
    try:
        file_obj = open(file_undo_task_list, 'r')
    except IOError:
        print '=== ERROR: OPEN FAILED!(' + file_undo_task_list + ')'
    else:
        for line_count, line in enumerate(file_obj):
            if line_count == index:
                path = os.path.join(instance_config.get_oringal_log_path(), line).strip('\n')
                print 'undo task = '+ path
                return path
            
def delete_undo_task_at_path(path):
    
    instance_config = configuration()
    root_path = instance_config.get_oringal_log_path()
    todelete_task = path.replace(root_path + '\\', '')
    todelete_task = todelete_task + '\n'

    file_undo_task_list = instance_config.get_undo_task_list_path()
    try:
        file_obj = open(file_undo_task_list, 'r')
    except IOError:
        print '=== ERROR: OPEN FAILED!(' + file_undo_task_list + ')'
    else:
        lines = file_obj.readlines()
        file_obj.close()
        if lines.count(todelete_task)>0:
            lines.remove(todelete_task)
            try:
                file_obj = open(file_undo_task_list, 'w')
            except IOError:
                print '=== ERROR: OPEN FAILED!(' + file_undo_task_list + ')'
            else:
                file_obj.write(''.join(lines))
                file_obj.close()

def write_undo_task_list():
    global configs
    file_undo_task_list = configs.get_undo_task_list_path()
    total_count = 0
    try:
        file_obj = open(file_undo_task_list, 'w+')
    except IOError:
        print '=== ERROR: OPEN FAILED!(' + file_undo_task_list + ')'
    else:
        global undo_task_dict
        for key, value in undo_task_dict.items():
            total_count = total_count + len(value)
            print key + '\n'
            for v in value:
                print '\t | '+ v
            task_string = '\n'.join(value) + '\n'
            file_obj.writelines(task_string)
        file_obj.close()
        print '=== UNDO TASK LIST SAVED(TOTAL: ' + str(total_count) + ')\n'

if __name__ == '__main__':
    
    print 'STEP 0 : READ CONFIGUARTIONS'
    configs = configuration()
    configs.print_configs()
    
    undo_task_dict = {}
    print '\nSTEP 1 : READ COMPLETED TASK LIST'
    completed_task_list = read_completed_tasks_list()
    
    print '\nSTEP 2 : CHECK LATEST UPLOADED TASKS'
    ologs_dir = configs.get_oringal_log_path()

    for root, dirs, files, in os.walk(ologs_dir, True):
        for name in files:
            checking_task_key = os.path.basename(root)
            checking_task_name = os.path.join(checking_task_key, name)
            print '= CHECKING TASK: ' + checking_task_name
            checking_task_name = checking_task_name + '\n'
            if completed_task_list.count(checking_task_name) == 0:
                print '=== NEW TASK ---> ADDING UNDO TASK'
                add_undo_task(checking_task_key, checking_task_name.strip('\n'))

    print '= CHECKING COMPLETED'
    print '\nSTEP 3 : SAVE UNDO TASK LIST'
    write_undo_task_list()
    
    
                
