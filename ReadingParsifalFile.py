import csv
import matplotlib.pyplot as plt
import numpy as np
import glob
import plotly.graph_objs as go
import plotly.io as pio
import plotly
import pandas as pd
import math


plotly.io.orca.config.executable = '/home/laercio/anaconda3/bin/orca'

plt.rcParams.update({'font.size': 10.0})
filenames = sorted(glob.glob('articles.csv'))
filenames = filenames[0:3]

dict_environments = {
    "x": [],
    "y": []
}

dict_selectionCriteria = {}
dict_devices = {}
dict_devicesByCriteria={}
dict_benchmarks = {}
dict_power = {"Y":0,"N":0}
dict_powerByCriteria = {}




characters_to_remove = "[]()&"

papersToVerify = []

duplicated = 0
accepted = 0
rejected = 0


testando = "MICROSOFT"


def ExtractDevice(devices,selection_criteria):
    device = devices.split('&')
    for dispositive in device:
        dispositive = dispositive.upper()
        if dispositive == "DRAM" or dispositive == "RAM" or dispositive == "MEMORY" or dispositive == "DRAM(WIDEIO2)" or dispositive == "DRAM(LPDDR4)":
            dispositive = "DRAM"
        if "M.2" in dispositive or dispositive == "M.2(NVME)" or dispositive == "M.2(SSD)":
            dispositive = "M.2"
        if  dispositive == "PCM" or dispositive == "PRAM" or dispositive == "PCME" or dispositive == "PCRAM" or dispositive == "OUM":
            dispositive = "PCM"
        if  dispositive == "FERAM" or dispositive == "F-RAM" or dispositive == "FRAM":
            dispositive = "FERAM"
        if  dispositive == "FLASH" or dispositive == "NAND FLASH" or dispositive == "NAND":
            dispositive = "FLASH"

        #insert all devices into dict_devices dictionary
        if dispositive not in dict_devices:
            dict_devices[dispositive] = 1
        else:
            cont = int(dict_devices[dispositive])
            dict_devices[dispositive] = cont + 1

        #insert all devices into dict_devicesByCriteria according to the classification criteria.
        if selection_criteria not in dict_devicesByCriteria:
            dict_devicesByCriteria[selection_criteria]= {}
            if dispositive not in dict_devicesByCriteria[selection_criteria]:
                dict_devicesByCriteria[selection_criteria][dispositive] = 1
            else:
                cont = int(dict_devicesByCriteria[selection_criteria][dispositive])
                dict_devicesByCriteria[selection_criteria][dispositive] = cont + 1
        elif dispositive not in dict_devicesByCriteria[selection_criteria]:
            dict_devicesByCriteria[selection_criteria][dispositive] = 1
        else:
            cont = int(dict_devicesByCriteria[selection_criteria][dispositive])
            dict_devicesByCriteria[selection_criteria][dispositive] = cont + 1

def CleanVariable(benchmark):
    for character in characters_to_remove:
        benchmark = benchmark.replace(character, "")
    return benchmark



def InsertHeadAndTailBenchmark(head, tails):
    if head not in dict_benchmarks.keys(): #adiciono HEAD com 1 ocorrencia, adiciono seus tais com 1 ocorrencia
        first = {1:{}}
        dict_benchmarks[head] = first
        for tail in tails:
            for occurrence,benchs in dict_benchmarks[head].items():
                if tail not in benchs.keys():  # insert an new elemento into the subs
                    aux = {tail:1}
                    benchs.update(aux) #adiciona o head para adicionar os Keys
    else: # atualizo o valor do head, verifico se existe o tail, se existir atualizo valor do TAIL, se não existir, insiro o TAIL com ocorrencia = 1
        dict_old = dict_benchmarks[head]
        dict_new = {}
        for occurrence, benchs in dict_old.items():
            occurrence += 1
            for tail in tails:
                if tail not in benchs.keys():  # insert an new elemento into the subs
                    aux = {tail: 1}
                    benchs.update(aux)
                else:
                    for occurrenceSub, bench in benchs.items():
                        if occurrenceSub == tail:
                            bench += 1
                            aux2={occurrenceSub:bench}
                            benchs.update(aux2)

                #atualiza com benchs e occurrence
                dict_new = {occurrence:benchs}
                dict_benchmarks[head] = dict_new


def InsertOnlyHeadBenchmark(benchmark): #this function receives an unique benchmak to be appened to the dictionary
    '''
    if testando in benchmark:
        print(title)
        print("teste")
    '''

    if benchmark not in dict_benchmarks.keys(): #se o benchmark não está nas chaves eu somente insiro
        dict_benchmarks[benchmark]= {}
        dict_benchmarks[benchmark][1]={}
    #else: # se o benchmark está nas chaves devo ver se ele é cabeça de chave
    elif benchmark in dict_benchmarks.keys():
        valueTypeTest = dict_benchmarks[benchmark]
        for occurrence, benchs in valueTypeTest.items():
            # atualiza com benchs e occurrence
            occurrence += 1
            dict_new = {occurrence:benchs}
            dict_benchmarks[benchmark]=dict_new



def ExtractBenchmark(benchmarks,title):
    #[Linux(wc&grep)&App(Sphinx-3)&specific]
    '''
    if title == "Simultaneous Evaluation of Multiple I/O Strategies":
        print("verificar no corte do benchmark")
    '''
    head = ""
    tail = ""
    word = ""
    j = -1
    benchmarks = benchmarks.upper()
    if "(" in benchmarks: #devo fazer o tratamento com o parenteses
        for i, letter in enumerate(benchmarks):  #benchmarks tem tudo 'LINUX(WC&GREP)&APP(SPHINX-3)&SPECIFIC]' 'twitter&kron28&LINUX(WC&GREP)&kron30&kron32&wdc'
            if letter != "(" and letter != "&" and i > j:
                word = word + letter  #word vai ser ou um head de um benchmark ou benchmark
            elif letter == "(": #extract the tails
                head = word
                word = ""
                j = i + 1
                while benchmarks[j] != ")": #trick to extract the tail
                    letter2 = benchmarks[j]
                    tail = tail+letter2
                    j += 1
                letter2 = ""
                tails = tail.split('&')
                tail = ""
                head = CleanVariable(head)
                for i, subtail in enumerate(tails): #clean the vector of tails
                    subtail = CleanVariable(subtail)
                    tails[i] = subtail
                InsertHeadAndTailBenchmark(head, tails)

            elif letter == "&" and word != "": #'ING&SFS&TPCH&GLIMPSEINDEX&CLAMAV&OLTP(TPC-C)&TAR&UNTAR]'
                word = CleanVariable(word)
                InsertOnlyHeadBenchmark(word) #apos inserir um benchmark preciso zerar a variavel
                word =""
        if word != None and word!= "]": #this case is when there are a las benchmark
            word = CleanVariable(word)
            InsertOnlyHeadBenchmark(word)

    else: # There is no tail in this benchmark, add it imediatelly.
        benchmarks = benchmarks.split('&')
        for i, bench in enumerate(benchmarks):
            bench = CleanVariable(bench)
            benchmarks[i] = bench
        #benchmarks = CleanVariables(benchmarks, tail) #in this case, chamaleon returns an array of benchmarks
        for benchmark in benchmarks:
            InsertOnlyHeadBenchmark(benchmark)




def ExtractPower(power,selection_criteria):
    if "Y" in power:
        cont = dict_power['Y']
        dict_power['Y'] = cont + 1
    elif "N" in power:
        cont = dict_power['N']
        dict_power['N'] = cont + 1


    if selection_criteria not in dict_powerByCriteria:
        dict_powerByCriteria[selection_criteria]= {"Y":0,"N":0}
    if "Y" in power:
        cont = dict_powerByCriteria[selection_criteria]["Y"]
        dict_powerByCriteria[selection_criteria]["Y"] = cont + 1
    elif "N" in power:
        cont = dict_powerByCriteria[selection_criteria]["N"]
        dict_powerByCriteria[selection_criteria]["N"] = cont + 1


def ExtractSelectioCriteria(selection_criteria):
    if selection_criteria not in dict_selectionCriteria:
        dict_selectionCriteria[selection_criteria] = 1
    else:
        val = dict_selectionCriteria[selection_criteria]
        dict_selectionCriteria[selection_criteria] = val + 1

def ExtractImprovedObject(improvedObject,selection_criteria):
    for selection_criteria, value in dict_devicesByCriteria.items():
        if selection_criteria == "H2H-IO -Hard-2-improve-IO-on-Hardware":
            #[on-chip access control memory-STT-RAM- (ACM)SSD(FeSSD)]-[SSD[DiskSim]]-[SSD&STT-RAM]
            CreateDevicesChart(value,title,explode)
        elif selection_criteria == "H2S-IO -Hard-2-improve-IO-on-Software":
            #[Determine the Hardware Choice(DRAM)]-[File System(HDFS)]-[DRAM]
            CreateDevicesChart(value, title, explode)
        elif selection_criteria == "H2SS-IO -Hardw-2-improve-IO-on-Storage-Systems":
            #[DMA cache technique (DDC)]-[Storage System[FPGA Emulation Platform]]-[Memory&cache]
            CreateDevicesChart(value, title, explode)
        elif selection_criteria == "S2S-IO -Soft-2-improve-IO-on-Software":
            #[non-blocking API extensions]-[Memcached[Libmemcached APIs]]-[SSD&Memory]
            CreateDevicesChart(value, title, explode)
        elif selection_criteria == "S2H-IO -Soft-2-improve-IO-on-Hardware":
            #[I/O link over-clocking]-[SSD[nf][rd(Altera Stratix IV GX FPGA PCle)]-[SSD]
            CreateDevicesChart(value, title, explode)
        elif selection_criteria == "S2SS-IO -Soft-2-improve-IO-on-Storage-Systems":
            # [writeback scheme(DFW)]-[Stotrage System[File System(EXT3)][rsee(1m2d)]]-[HDD&SSD]
            CreateDevicesChart(value, title, explode)
        elif selection_criteria == "ARCHITECTURE":
            #[duplication-aware flash cache architecture (DASH)]-[Cloud[rsee(1m)]]-[Flash&HDD]
            CreateDevicesChart(value, title, explode)

def ExtractComments(comment, title, selection_criteria):
    comment = comment.replace("]\n[", "]-[");
    line = comment.split(']-[')
    if len(line) < 6:
        papersToVerify.append(title)
    else:
        text = line[0]
        #print(text)
        improvedObject = line[1]
        ExtractImprovedObject(improvedObject,selection_criteria)
        devices = line[2]
        ExtractDevice(devices, selection_criteria)
        concerning = line[3]
        #print(concerning)
        power = line[4]
        ExtractPower(power,selection_criteria)
        #print(power)
        benchmarks = line[5]
        ExtractBenchmark(benchmarks,title)
        #print("proxima linha \n")

def verifyStatus(status, comments, selection_criteria):
    global duplicated
    global accepted
    global rejected

    if status == "Duplicated":
        duplicated += 1
    elif status == "Accepted":
        accepted += 1
        ExtractComments(comments, title, selection_criteria)
        ExtractSelectioCriteria(selection_criteria)
    elif status == "Rejected":
        rejected += 1


def printStatus():
    global duplicated
    global accepted
    global rejected

    labels = ['Reject', 'Accepted', 'Duplicated']
    qtdLabels = [rejected, accepted, duplicated]

    explode = (0, 0.1, 0.05)  # only "explode" the 2nd slice (i.e. 'Hogs')
    colors = ['red', 'green', 'yellow']
    fig1, ax1 = plt.subplots()
    ax1.pie(qtdLabels, labels=labels, explode=explode, autopct='%1.1f%%', shadow=True, startangle=270, colors=colors)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()

def printEnergyChart(dict_power):
    labelYesNo = []
    for key, value in dict_power.items():
        if key == "Y":
            yes = value
        else:
            no = value
    labelYesNo.append(no)
    labelYesNo.append(yes)

    labels = 'Without Energy\nEfficiency Consideration', 'With Energy\nEfficiency\nConsideration'
    explode = (0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    colors = ['red', 'green']
    fig1, ax1 = plt.subplots()
    ax1.pie(labelYesNo, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=270, colors=colors)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()

def printBenchmarksChart(dict_benchmarks):
    plt.rcParams.update({'font.size': 8.0})
    benchname = []
    benchvalue= []
    for key, value in dict_benchmarks.items():
        for item in sorted(value):
            if item > 3 and item != 162:
                benchvalue.append(item)
                benchname.append(key)

    y_pos = np.arange(len(benchname))
    plt.bar(y_pos, benchvalue, align='center', alpha=0.5)
    plt.xticks(y_pos, benchname, rotation=85, ha='center',size=7)
    for i, v in enumerate(benchvalue):
        plt.text(i, v, str(v), color='red', size=8, ha='center')
    plt.xlabel('Workload', fontsize=10)
    plt.ylabel('Occurence Number')
    plt.title('Programming language usage')
    plt.tight_layout()

    plt.show()

    ''' 
    y_pos = np.arange(len(benchvalue))
    plt.barh(y_pos, benchvalue, align='center', alpha=0.5)
    plt.yticks(y_pos, benchname)
    for i, v in enumerate(benchvalue):
        plt.text(v, i, str(v), color='red', va='center',size=8)

    plt.xlabel('Usage')
    plt.ylabel('XXXXXXXXXXXXXXXXXxx')
    plt.title('Programming language usage')

    plt.show()
    '''
    '''
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=benchname,
        y=benchvalue,
        name='Primary Product',
        marker_color='indianred'
    ))
    fig.update_layout(title='Least Used Feature', title_font_size=30, xaxis_title='Workloads', yaxis_title='Occurence Number')
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.show()

    '''

def printSelectioCriteria(dict_selectionCriteria):
    plt.rcParams.update({'font.size': 8.0})
    Criterianame = []
    Criteriavalue = []

    colors = []


    for key, value in dict_selectionCriteria.items():
        if key == "H2H-IO -Hard-2-improve-IO-on-Hardware":
            Criterianame.append("H2H-IO")
            Criteriavalue.append(value)
            colors.append("lightgreen")

    for key, value in dict_selectionCriteria.items():
        if key == "H2S-IO -Hard-2-improve-IO-on-Software":
            Criterianame.append("H2S-IO")
            Criteriavalue.append(value)
            colors.append("olive")

    for key, value in dict_selectionCriteria.items():
        if key == "H2SS-IO -Hardw-2-improve-IO-on-Storage-Systems":
            Criterianame.append("H2SS-IO")
            Criteriavalue.append(value)
            colors.append("green")

    for key, value in dict_selectionCriteria.items():
        if key == "S2S-IO -Soft-2-improve-IO-on-Software":
            Criterianame.append("S2S-IO")
            Criteriavalue.append(value)
            colors.append("salmon")

    for key, value in dict_selectionCriteria.items():
        if key == "S2H-IO -Soft-2-improve-IO-on-Hardware":
            Criterianame.append("S2H-IO")
            Criteriavalue.append(value)
            colors.append("tomato")

    for key, value in dict_selectionCriteria.items():
        if key == "S2SS-IO -Soft-2-improve-IO-on-Storage-Systems":
            Criterianame.append("S2SS-IO")
            Criteriavalue.append(value)
            colors.append("red")

    for key, value in dict_selectionCriteria.items():
        if key == "ARCHITECTURE":
            Criterianame.append("Arch")
            Criteriavalue.append(value)
            colors.append("yellow")

    explode = (0.1, 0.2, 0.3, 0.0, 0.0, 0.0, 0.0)
    fig1, ax1 = plt.subplots(figsize=(4,4))
    ax1.pie(Criteriavalue, colors=colors, labels=Criterianame, explode=explode, autopct='%1.1f%%', pctdistance=0.3, radius=1, counterclock=False,
            shadow=True, startangle=10, labeldistance=1.05)  # , wedgeprops = { 'linewidth': 1, "edgecolor" :"k" })
    #plt.legend(bbox_to_anchor=(1, 0), loc="lower right", bbox_transform=plt.gcf().transFigure)

    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.set_title('Accepted Papers Grouped by Selection Criteria')
    plt.tight_layout()
    plt.show()

def printDevicesChart(dict_devices):
    explode = (0.01, 0.025, 0.015, 0.02, 0.03, 0.04, 0.05, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.015)
    title = "Most Used Devices"
    CreateDevicesChart(dict_devices, title, explode)

def printDevicesChartByCriteria(dict_devicesByCriteria):
    explode = None
    for criteria, value in dict_devicesByCriteria.items():
        if criteria == "H2H-IO -Hard-2-improve-IO-on-Hardware":
            title = "H2H-IO"
            CreateDevicesChart(value,title,explode)
        elif criteria == "H2S-IO -Hard-2-improve-IO-on-Software":
            title  = "H2S-IO"
            CreateDevicesChart(value, title, explode)
        elif criteria == "H2SS-IO -Hardw-2-improve-IO-on-Storage-Systems":
            title  = "H2SS-IO"
            CreateDevicesChart(value, title, explode)
        elif criteria == "S2S-IO -Soft-2-improve-IO-on-Software":
            title  = "S2S-IO"
            CreateDevicesChart(value, title, explode)
        elif criteria == "S2H-IO -Soft-2-improve-IO-on-Hardware":
            title  = "S2H-IO"
            CreateDevicesChart(value, title, explode)
        elif criteria == "S2SS-IO -Soft-2-improve-IO-on-Storage-Systems":
            title  = "S2SS-IO"
            CreateDevicesChart(value, title, explode)
        elif criteria == "ARCHITECTURE":
            title  = "ARCH"
            CreateDevicesChart(value, title, explode)

def CreateDevicesChart(dict_devices,title,explode):
    devices = []
    qtdDevices = []
    colors = []

    for dev, count in dict_devices.items():
        if dev == "CACHE":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("pink")

    for dev, count in dict_devices.items():
        if dev == "SPM":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("deeppink")

    for dev, count in dict_devices.items():
        if dev == "SSD":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("red")

    for dev, count in dict_devices.items():
        if dev == "FLASH":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("crimson")

    for dev, count in dict_devices.items():
        if dev == "M.2":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("firebrick")

    for dev, count in dict_devices.items():
        if dev == "SCM":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("tomato")

    for dev, count in dict_devices.items():
        if dev == "DRAM-SSD":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("darkviolet")

    for dev, count in dict_devices.items():
        if dev == "DRAM":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("blue")

    for dev, count in dict_devices.items():
        if dev == "SDRAM":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("cornflowerblue")

    for dev, count in dict_devices.items():
        if dev == "SRAM":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("slateblue")

    for dev, count in dict_devices.items():
        if dev == "NVRAM":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("yellow")

    for dev, count in dict_devices.items():
        if dev == "PCM":
            devices.append(dev + "/PRAM")
            qtdDevices.append(count)
            colors.append("gold")

    for dev, count in dict_devices.items():
        if dev == "STT-RAM":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("orange")

    for dev, count in dict_devices.items():
        if dev == "TAPE":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("black")

    for dev, count in dict_devices.items():
        if dev == "FERAM":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("royalblue")

    for dev, count in dict_devices.items():
        if dev == "HDD":
            devices.append(dev)
            qtdDevices.append(count)
            colors.append("green")

    if explode == None:
        fig, ax = plt.subplots(figsize=(5, 5))
        plt.title('Most Used Devices in ' + title)
        data = qtdDevices
        wedges, texts = ax.pie(data, colors=colors, wedgeprops=dict(width=0.5), pctdistance=0.3, radius=1, counterclock=False,
                               shadow=False, startangle=60, labeldistance=1.1)#,autopct='%1.1f%%')

        plt.legend(wedges, devices, bbox_to_anchor=(1, 0), loc="lower right", bbox_transform=plt.gcf().transFigure)
        plt.gca().axis("equal")
        plt.tight_layout()
        plt.show()
    else:
        explode =  explode
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        ax1.pie(qtdDevices, colors=colors, explode=explode, pctdistance=0.3, radius=1, counterclock=False,
                shadow=False, startangle=180, labeldistance=1.05, wedgeprops={'linewidth': 0.19, "edgecolor": "k"})  # ,autopct='%1.1f%%')
        plt.legend(devices, bbox_to_anchor=(1, 0), loc="lower right", bbox_transform=plt.gcf().transFigure)

        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax1.set_title('Most Used Devices')
        plt.tight_layout()
        plt.show()



for f in filenames:
    path = "/home/laercio/github/ReadingParsifal/" + f

    with open(path) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        data = {}
        for row in readCSV:
            '''
            bibtex_key = row[0]
            title = row[1]
            author = row[2]
            journal = row[3]
            year = row[4]
            source = row[5]
            pages = row[6]
            volume = row[7]
            abstract = row[8]
            document_type = row[9]
            doi = row[10]
            url = row[11]
            affiliation = row[12]
            author_keywords = row[13]
            keywords = row[14]
            publisher = row[15]
            issn = row[16]
            language = row[17]
            note = row[18]
            selection_criteria = row[19]
            created_at = row[20]
            updated_at = row[21]
            created_by = row[22]
            updated_by = row[23]
            status = row[24]
            comments = row[25]
            '''
            bibtex_key = row[0]
            title = row[1]
            selection_criteria = row[2]
            status = row[3]
            comments = row[4]

            verifyStatus(status, comments, selection_criteria)




print("accepted", accepted)
print("duplicated", duplicated)
print("rejected", rejected)
#printStatus() #print the Reject, Accepted and Duplicated quantity of papers

print(dict_power)
#printEnergyChart(dict_power)

print(dict_devices.items())
print(dict_devicesByCriteria.items())
#printDevicesChart(dict_devices)
#printDevicesChartByCriteria(dict_devicesByCriteria)


print("dict_benchmark size ->", len(dict_benchmarks),dict_benchmarks.items())
#printBenchmarksChart(dict_benchmarks)
#printSelectioCriteria(dict_selectionCriteria)


print("papers to verify --->>>",papersToVerify)








#https://kite.com/python/answers/how-to-remove-specific-characters-from-a-string-in-python