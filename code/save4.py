import loaddata
import numpy as np
import datetime
import random
import copy
import matplotlib.pyplot as plt


def SaveMove(label, move, nowTime):

    savemove = np.array(move)
    np.savetxt('./zzl/statussave/move_'+nowTime +
               '_'+label+'.txt', savemove, fmt="%d")


def LoadMove(path):
    allpath = './zzl/statussave/move_'+path+'.txt'
    loadmove = np.loadtxt(allpath, dtype=int)
    return loadmove.tolist()


def LoadSortIns(infilename):
    aal = np.loadtxt(infilename)
    return aal


def SaveStatus(status, label, nowTime):

    f = open('./zzl/statussave/status_'+nowTime+'_'+label+'.txt', 'w')

    for i in range(1, 1+len(status)):
        for j in range(98):
            if j != 97:
                print(status[i]['cpu'][j], end=',', file=f)
            else:
                print(status[i]['cpu'][j], file=f)
        for j in range(98):
            if j != 97:
                print(status[i]['mem'][j], end=',', file=f)
            else:
                print(status[i]['mem'][j], file=f)
        print(status[i]['disk'], file=f)
        print(status[i]['M'], file=f)
        print(status[i]['P'], file=f)
        print(status[i]['PM'], file=f)

        print('hasapps:', end='', file=f)
        hasapp = status[i]['hasapps']
        if len(hasapp) == 0:
            print('', file=f)
        for j in range(len(hasapp)):
            if j != len(hasapp)-1:
                print(hasapp[j], end=',', file=f)
            else:
                print(hasapp[j], file=f)
    input('ok')
    f.close()

    return './zzl/statussave/status_'+str(nowTime)+'_'+label+'.txt'


def LoadStatus(path):
    status = {}
    f = open(
        './zzl/statussave/status_'+path+'.txt', 'r')
    for machinei in range(1, 6001):
        cpus = f.readline().split(',')
        listcpu = []
        for cpu in cpus:
            listcpu.append(float(cpu))
        cpu = np.array(listcpu)

        mems = f.readline().split(',')
        listmem = []
        for mem in mems:
            listmem.append(float(mem))
        mem = np.array(listmem)

        disk = int(f.readline())
        M = int(f.readline())
        P = int(f.readline())
        PM = int(f.readline())

        hasapps0 = f.readline()
        hasapps1 = hasapps0.split(':')[1]
        if len(hasapps1) > 3:
            hasapps2 = hasapps1.split(',')
            hasapp = []
            for i in range(int(len(hasapps2) / 2)):
                hasapp.append(
                    [int(hasapps2[i*2].split('[')[1]), int(hasapps2[i*2+1].split(']')[0])])

        status[machinei] = {'cpu': cpu, 'mem': mem,
                            'disk': disk, 'M': M, 'P': P, 'PM': PM, 'applimit': {}, 'hasapps': hasapp}

    return status


def SaveInsToMachine(label, ins_to_machine, nowTime):

    f = open('./zzl/statussave/ins2machine_' +
             nowTime+'_'+label+'.txt', 'w')
    f.write(str(ins_to_machine))
    f.close()


def LoadInsToMachine(path):
    f = open(
        './zzl/statussave/ins2machine_'+path+'.txt', 'r')
    a = f.read()
    ins_to_machine = eval(a)
    f.close()
    return ins_to_machine


def SaveAll(label, ins_to_machine, status, move):

    nowTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    SaveInsToMachine(label, ins_to_machine, nowTime)
    SaveStatus(status, label, nowTime)
    SaveMove(label, move, nowTime)
    return nowTime


def LoadAll(time, label):
    path = time+'_'+label
    ins_to_machine = LoadInsToMachine(path)
    move = LoadMove(path)
    status = LoadStatus(path)

    return ins_to_machine, move, status
