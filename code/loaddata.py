import numpy as np


def LoadAppConstraint():
    # This function trainslate the app constraint csv file to a list and matrix
    # the data in the list have the same data structure with the csv file
    # the matrix provide a continence way to retrieve.
    # for example if you wang to get the constaint between app 8361 and app 2163.
    # you can just use m_app_interference[8361,2163]

    f = open('./data/scheduling_preliminary_app_interference_20180606.csv')
    num_of_lines = len(f.readlines())
    f.close()
    f = open('./data/scheduling_preliminary_app_interference_20180606.csv')

    app_cons = {}

    for i in range(num_of_lines):
        current_line_txt = f.readline()
        items = current_line_txt.split(',')
        app1 = int(items[0].split('_')[1])
        app2 = int(items[1].split('_')[1])
        cons = int(items[2][:-1])

        if app1 in app_cons:
            app_dick = app_cons[app1]
            app_dick[app2] = cons
        else:
            app_cons[app1]={app2: cons} #= {'app2': app2, 'cons': cons}
    
    f.close()
    return app_cons


def LoadAppResources(num_of_app):
    # This function trainslate the app constraint csv file to a matrix
    # the matrix provide a continence way to retrieve.
    # for example if you wang to get the resources data of app 8361 .
    # you can just use resources[8361,:]

    resources = {}

    f = open('./data/scheduling_preliminary_app_resources_20180606.csv')
    for i in range(num_of_app):
        current_line = f.readline()
        if not current_line:
            break

        line_data = current_line.split(',')

        items = line_data[1].split('|')
        cpu = np.array([])
        for item in items:
            cpu = np.append(cpu, float(item))

        items = line_data[2].split('|')
        mem = np.array([])
        for item in items:
            mem = np.append(mem, float(item))

        disk = int(line_data[3])
        P_roof = int(line_data[4])
        M_roof = int(line_data[5])
        PM_roof = int(line_data[6])

        resources[i+1] = {'cpu': cpu, 'mem': mem, 'disk': disk,
                          'P_roof': P_roof, 'M_roof': M_roof, 'PM_roof': PM_roof}
    f.close()
    return resources


def LoadInstanDeploy():
    f = open('./data/scheduling_preliminary_instance_deploy_20180606.csv')
    num_of_lines = len(f.readlines())
    f.close()
    f = open('./data/scheduling_preliminary_instance_deploy_20180606.csv')

    dick_instan = {}

    for i in range(num_of_lines):
        current_line_txt = f.readline()
        items = current_line_txt.split(',')
        inst = int(items[0].split('_')[1])
        app = int(items[1].split('_')[1])
        if len(items[2]) > 3:
            machine = int(items[2].split('_')[1])
        else:
            machine = -1
        dick_instan[inst] = {'app': app, 'machine': machine}
    f.close()
    return dick_instan


def LoadMachineResources():
    f = open('./data/scheduling_preliminary_machine_resources_20180606.csv')
    num_of_lines = len(f.readlines())
    f.close()
    f = open('./data/scheduling_preliminary_machine_resources_20180606.csv')

    machine_resources = {}
    for i in range(num_of_lines):
        current_line_txt = f.readline()
        items = current_line_txt.split(',')
        machine = int(items[0].split('_')[1])
        cpu = int(items[1])
        mem = int(items[2])
        disk = int(items[3])
        P_roof = int(items[4])
        M_roof = int(items[5])
        PM_roof = int(items[6])
        machine_resources[machine] = {
            'cpu': cpu, 'mem': mem, 'disk': disk, 'P_roof': P_roof, 'M_roof': M_roof, 'PM_roof': PM_roof}
    f.close()
    return machine_resources


def main():
    # the main function is used to test other function code

    # LoadAppConstraint()
    app_cons = LoadAppConstraint()
    print(app_cons[106])
    # print(m_app_interference[8361, 2163])

    # LoadAppResources()
    resources = LoadAppResources(9338)
    print(resources[1])

    # LoadInstDeploy
    dick_instan = LoadInstanDeploy()
    print(dick_instan[23673]['app'])
    print(dick_instan[23673]['machine'])

    machine_resources = LoadMachineResources()
    print(machine_resources[15]['cpu'])


if __name__ == '__main__':
    main()
