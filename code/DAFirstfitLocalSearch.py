'''
This file is the main file of first fit and the local search
Two other file is related to this file

loaddata.py is the file to load the problem data to the computer.
save4.py is the file to save the machine state and the log file to the related directory. 
'''

import numpy as np
import datetime
import random
import copy
import matplotlib.pyplot as plt

import loaddata
import save4 as zzlsave

num_of_breakappcon = 0
num_ins = 100


def InitStatus(data_block):
    # this function init the status of every machine with 0
    # you can view the machine status with cod status[i], i is the int number of machine.

    # the tatuse
    app_cons, app_resources, instan_deploy, machine_resources = data_block

    status = {}
    status['list_ins2machine'] = {}
    list_S_ins = list(instan_deploy)
    for ins in list_S_ins:
        status['list_ins2machine'][ins] = -1

    # init machine states one by one
    for i in range(6000):
        cpu = np.zeros((98))
        mem = np.zeros((98))
        dis = 0
        M = 0
        P = 0
        PM = 0
        status[i+1] = {'cpu': cpu, 'mem': mem,
                       'disk': dis, 'M': M, 'P': P, 'PM': PM, 'hasapps': []}

    return status


def Evaluate(status, machine_resources):
    # this function evaluate all the machine state and return the score

    score_list = []
    above_score = 0
    for i in range(1, 6001):
        roof = machine_resources[i]['cpu']
        c_score = 0
        for j in range(98):
            if status[i]['disk'] == 0:
                c_score += 0
            else:
                c = status[i]['cpu'][j] / roof
                score_list.append(c)
                c_score += 1 + 10 * (np.exp(max(0, c-0.5)) - 1)
        c_score /= 98
        above_score += c_score
    return above_score, score_list


def LoadData():
    # this function load the data in loaddata.py
    # and the detail is shown in it

    app_cons = loaddata.LoadAppConstraint()
    app_resources = loaddata.LoadAppResources(9338)
    instan_deploy = loaddata.LoadInstanDeploy()
    machine_resources = loaddata.LoadMachineResources()

    return app_cons, app_resources, instan_deploy, machine_resources


def Ins2Machine(data_bolck, S_ins):
    # this function Find the machine serial number corresponding to the instance serial number
    # and return it

    app_cons, app_resources, instan_deploy, machine_resources = data_bolck
    S_mach = instan_deploy[S_ins]['machine']
    return S_mach


def Ins2App(S_ins, data_block):
    # this function Find the app serial number corresponding to the instance serial number
    # and return it

    app_cons, app_resources, instan_deploy, machine_resources = data_block
    S_app = instan_deploy[S_ins]['app']
    return S_app


def App2Need(S_app, data_block):
    # this function Find the app resource need corresponding to the app serial number
    # and return it

    app_cons, app_resources, instan_deploy, machine_resources = data_block
    app_need = app_resources[S_app]
    return app_need


def GetMachineStatus(status, S_mach):
    # this function Find the machine state dictionary corresponding to the machine serial number
    # and return it

    MachineStatue = status[S_mach]

    return MachineStatue


def Machine2Ins(machine_status):
    # this function Find the list of instance corresponding to the machine state
    # and return it

    apps = machine_status['hasapps']
    Ins = []
    for app in apps:
        Ins.append(app[0])
    return Ins


def Ins2Need(data_block, S_ins):
    # this function Find the app resource need corresponding to the instance serial number
    # and return it

    S_app = Ins2App(S_ins, data_block)
    need = App2Need(S_app, data_block)

    return need


def Mach2Reso(data_block, S_mach):
    # this function Find the machine resource corresponding to the serial number
    # and return it

    app_cons, app_resources, instan_deploy, machine_resources = data_block

    current_machine_resources = machine_resources[S_mach]
    return current_machine_resources


def PutIns2Machine(data_block, status, S_ins, S_mach):
    # this function put instance S_ins to machine S_mach
    # refresh the state and return it

    res_need = Ins2Need(data_block, S_ins)
    aim_machine_status = status[S_mach]
    S_app = Ins2App(S_ins, data_block)

    aim_machine_status['cpu'] = aim_machine_status['cpu'] + res_need['cpu']
    aim_machine_status['mem'] = aim_machine_status['mem'] + res_need['mem']
    aim_machine_status['disk'] = aim_machine_status['disk'] + res_need['disk']
    aim_machine_status['P'] = aim_machine_status['P'] + res_need['P_roof']
    aim_machine_status['PM'] = aim_machine_status['PM'] + res_need['PM_roof']
    aim_machine_status['M'] = aim_machine_status['M'] + res_need['M_roof']

    dict_of_has_app = aim_machine_status['hasapps']
    dict_of_has_app.append([S_app, S_ins])
    status['list_ins2machine'][S_ins] = S_mach

    return status


def GetOutInsFromMachine(data_block, status, S_ins, S_mach):
    # this function take out instance S_ins machine machine S_mach
    # refresh the state and return it

    res_need = Ins2Need(data_block, S_ins)
    aim_machine_status = status[S_mach]
    S_app = Ins2App(S_ins, data_block)

    aim_machine_status['cpu'] = aim_machine_status['cpu'] - res_need['cpu']
    aim_machine_status['mem'] = aim_machine_status['mem'] - res_need['mem']
    aim_machine_status['disk'] = aim_machine_status['disk'] - res_need['disk']
    aim_machine_status['P'] = aim_machine_status['P'] - res_need['P_roof']
    aim_machine_status['PM'] = aim_machine_status['PM'] - res_need['PM_roof']
    aim_machine_status['M'] = aim_machine_status['M'] - res_need['M_roof']

    fromhasapps = aim_machine_status['hasapps']
    for i in range(len(fromhasapps)):
        if fromhasapps[i][0] == S_app:
            fromhasapps.pop(i)
            break

    status['list_ins2machine'][S_ins] = -1
    return status


def Stat_app(hasapp_list):
    # This function counts the hasapp list for use in judging conflicts below.

    stat_dict = {}
    for i in range(len(hasapp_list)):
        S_app = hasapp_list[i][0]
        if S_app in stat_dict:
            hasapp = stat_dict[S_app]
            hasapp[0] += 1
        else:
            stat_dict[S_app] = [1, hasapp_list[i][1]]

    return stat_dict


def CheckAppCons(information, machine_status, app_cons):
    # Check if there is a conflict between apps in the current state
    # if there are conflict return the conflict information.

    breakset = set()

    hasapp_list = machine_status['hasapps']
    # a dictionary of apps and quantities currently running on the machine
    dict_has_apps = Stat_app(hasapp_list)
    for app1 in dict_has_apps:  # traversing this dictionary
        # app1 = app1list[0]
        if app1 in app_cons:
            dict_of_limit_app = app_cons[app1]  # get one app restrain
            for app2 in dict_has_apps:  # In contrast to other elements
                if app1 == app2:
                    add = 1
                else:
                    add = 0
                if app2 in dict_of_limit_app and \
                        dict_of_limit_app[app2] + add < dict_has_apps[app2][0]:

                    information = information + '_applimit:app1 ' + \
                        str(app1)+' only accommodate '+str(dict_of_limit_app[app2]) + \
                        ' app2 '+str(app2)+' ins '+str(dict_has_apps[app2][1]) + \
                        ', but has '+str(dict_has_apps[app2][0]) + '\n'
                    breakset.add(dict_has_apps[app2][1])

    return information, breakset


def CheckOverflow(information, machine_status, cmachine_resources, app_cons, alpha=0.5):
    # Check if there is a overflow in the current state
    # if there are overflow, return the conflict information.

    if max(machine_status['cpu']) > alpha * cmachine_resources['cpu']:
        information = information + '_cpu max is ' + str(cmachine_resources['cpu']) + 'but use '+str(
            max(machine_status['cpu']))+'\n'
    if max(machine_status['mem']) > cmachine_resources['mem']:
        information = information + 'mem max is ' + str(cmachine_resources['mem']) + 'but use '+str(
            max(machine_status['mem']))+'\n'
    if machine_status['disk'] > cmachine_resources['disk']:
        information = information + 'disk max is ' + str(cmachine_resources['disk']) + 'but use '+str(
            machine_status['disk'])+'\n'
    if machine_status['P'] > cmachine_resources['P_roof']:
        information = information + 'P_roof max is ' + str(cmachine_resources['P_roof']) + 'but use '+str(
            machine_status['P'])+'\n'
    if machine_status['PM'] > cmachine_resources['PM_roof']:
        information = information + 'PM_roof max is ' + str(cmachine_resources['PM_roof']) + 'but use '+str(
            machine_status['PM'])+'\n'
    if machine_status['M'] > cmachine_resources['M_roof']:
        information = information + 'M_roof max is ' + str(cmachine_resources['M_roof']) + 'but use '+str(
            machine_status['M'])+'\n'

    return information


def CheckMachineState(data_block, statue, S_mach):
    # check the state of machine S_machine, include the overflow and conflict
    # if there are some bad state, return the information

    app_cons, app_resources, instan_deploy, machine_resources = data_block

    machine_status = statue[S_mach]
    information, breakset = CheckAppCons(":", machine_status, app_cons)
    current_machine_resources = Mach2Reso(data_block, S_mach)
    information = CheckOverflow(
        information, machine_status, current_machine_resources, app_cons)

    if information == ':':
        out = 1
    else:
        out = 0

    return out, information


def PutIns2RandomMach(status, data_block, machinelist, lenmachinelist, S_ins):
    # put instance S_ins to a random machine.
    # and return the serious of this machine.

    random_mach_list = random.sample(machinelist, lenmachinelist)
    for S_mach in random_mach_list:
        status = PutIns2Machine(data_block, status, S_ins, S_mach)
        out, information = CheckMachineState(
            data_block, status, S_mach)
        if out == 1:
            # movehistory.append([S_ins, S_mach])
            # print("{}: put ins {} to Mach {}".format(i, S_ins, S_mach))
            succ = 1
            break
        else:
            GetOutInsFromMachine(data_block, status, S_ins, S_mach)
            # print(information)
        if S_mach == random_mach_list[-1]:
            succ = 0
            # input('cantfind')

    return succ, S_mach


def GetMostBadIns(machine_status):
    # get this instance serious to remove

    S_ins = machine_status['hasapps'][0][1]

    return S_ins


def LoadStep1(status, data_block, machinelist, movehistory):
    # this function is used to loading the working apps
    # the input is the initialized status and the data block
    # the output is the statues after loading the working app and the
    # moving trace of conflicting ins.

    print("start step 1")
    app_cons, app_resources, instan_deploy, machine_resources = data_block
    ins_to_machine = status['list_ins2machine']
    list_ins = list(instan_deploy)

    for i in range(len(list_ins)):
        S_ins = list_ins[i]
        S_mach_ins_to = instan_deploy[S_ins]['machine']
        if S_mach_ins_to != -1:
            status = PutIns2Machine(data_block, status, S_ins, S_mach_ins_to)
            ins_to_machine[S_ins] = S_mach_ins_to

    return status, movehistory


def LoadStep2(status, data_block, machinelist, movehistory):
    # this function is used to check the app conflict
    # the input is the initialized status and the data block
    # the output is the statues after loading the working app and the
    # moving trace of conflicting ins.

    print("start step 2")
    lenmachinelist = len(machinelist)
    app_cons, app_resources, instan_deploy, machine_resources = data_block

    for S_mach in machinelist:

        machine_status = status[S_mach]
        information, breakset = CheckAppCons(':', machine_status, app_cons)
        while information != ':':
            S_ins = breakset.pop()
            status = GetOutInsFromMachine(data_block, status, S_ins, S_mach)
            succ, new_mach = PutIns2RandomMach(
                status, data_block, machinelist, lenmachinelist, S_ins)
            if succ == 1:
                movehistory.append([S_ins, new_mach])
                # print("LoadStep2 : put ins {} to Mach {}".format(S_ins, S_mach))
            else:
                input('cant find')
            machine_status = status[S_mach]
            information, breakset = CheckAppCons(':', machine_status, app_cons)
    return status, movehistory

    # pass


def LoadStep3(status, data_block, machinelist, movehistory):
    # this function is used to check the machine overflow
    # the input is the initialized status and the data block
    # the output is the statues after loading the working app and the
    # moving trace of conflicting ins.

    print("start step 3")
    lenmachinelist = len(machinelist)
    app_cons, app_resources, instan_deploy, machine_resources = data_block

    for S_mach in machinelist:

        machine_status = status[S_mach]
        current_machine_resources = Mach2Reso(data_block, S_mach)
        information = CheckOverflow(
            ':', machine_status, current_machine_resources, app_cons)

        while information != ':':
            S_ins = GetMostBadIns(machine_status)
            status = GetOutInsFromMachine(data_block, status, S_ins, S_mach)
            succ, new_mach = PutIns2RandomMach(
                status, data_block, machinelist, lenmachinelist, S_ins)
            if succ == 1:
                movehistory.append([S_ins, new_mach])
                # print("LoadStep3 : put ins {} to Mach {}".format(S_ins, S_mach))
            else:
                input('cant find')
            machine_status = status[S_mach]
            information = CheckOverflow(
                ':', machine_status, current_machine_resources, app_cons)
    return status, movehistory


def LoadStep4(status, data_block, machinelist, movehistory):
    # this function is used to schedule the other instance
    # the input is the initialized status and the data block
    # the output is the statues after loading the working app and the
    # moving trace of conflicting ins.

    print("start step 4")
    app_cons, app_resources, instan_deploy, machine_resources = data_block
    list_ins = list(instan_deploy)
    sorted_ins_list = zzlsave.LoadSortIns('./savetxt.txt')
    lenmachinelist = len(machinelist)

    for i in range(len(list_ins)):
        
        if i % (len(list_ins) // 100 ) == 1:
            print("step process {} percent".format(i/len(list_ins)))
        
        num_of_try = -1
        S_ins = int(sorted_ins_list[i, 0])
        S_mach = Ins2Machine(data_block, S_ins)
        if S_mach == -1:
            succ, S_mach = PutIns2RandomMach(
                status, data_block, machinelist, lenmachinelist, S_ins)
            if succ == 1:
                movehistory.append([S_ins, S_mach])
                # print("{}: put ins {} to Mach {}".format(i, S_ins, S_mach))
            else:
                input('cant find')

    return status, movehistory


def EmptyMach(status, data_block, S_mach, machinelist, movehistory):

    lenmachinelist = len(machinelist)
    machine_status = status[S_mach]
    hasapp_list = copy.deepcopy(machine_status['hasapps'])
    for app, S_ins in hasapp_list:
        succ, mach = PutIns2RandomMach(
            status, data_block, machinelist, lenmachinelist, S_ins)
        if succ == 1:
            out = 1
            status = GetOutInsFromMachine(data_block, status, S_ins, S_mach)
            movehistory.append([S_ins, mach])
            # print("EmptyMach: put ins {} to Mach {}".format(S_ins, S_mach))
        else:
            out = 0

    return out, status, movehistory


def GenerateAnswer(move, score, nowTime):

    f_sub = open('./code/submit/'+str(score) + 'submit'+nowTime+'.csv', 'w')
    for item in move:
        print('inst_'+str(item[0])+',machine_'+str(item[1]), file=f_sub)


def main():

    app_cons, app_resources, instan_deploy, machine_resources = LoadData()
    data_block = [app_cons, app_resources, instan_deploy, machine_resources]

    nowTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    status = InitStatus(data_block)
    machine_list = [i for i in range(1, 6001)]
    movehistory = []

    status, movehistory = LoadStep1(
        status, data_block, machine_list, movehistory)
    status, movehistory = LoadStep2(
        status, data_block, machine_list, movehistory)
    status, movehistory = LoadStep3(
        status, data_block, machine_list, movehistory)
    status, movehistory = LoadStep4(
        status, data_block, machine_list, movehistory)

    above_score, score_list = Evaluate(status, machine_resources)
    GenerateAnswer(movehistory, above_score, nowTime)
    print(above_score)

    for i in range(1, 200):
        machine_list.remove(i)
        # machine_list.pop(0)
        copystatus = copy.deepcopy(status)
        copymovehistory = copy.deepcopy(movehistory)
        out, status, movehistory = EmptyMach(
            status, data_block, i, machine_list, movehistory)
        if out == 0:
            machine_list.append(i)
            status = copystatus
            movehistory = copymovehistory
            # break

    above_score, score_list = Evaluate(status, machine_resources)
    GenerateAnswer(movehistory, above_score, nowTime)
    print(above_score)


if __name__ == '__main__':
    # st = Statusload('/home/utry2/Documents/研究生/研究生学习/学科竞赛/Tianchi/TIANCHI-Server-scheduling-2018-7-3/zzl/statussave/status_2018-07-15_09:54:24_afterloading.txt')
    main()
