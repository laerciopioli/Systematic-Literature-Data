import csv
import matplotlib.pyplot as plt
import numpy as np
import glob
import plotly.graph_objs as go
import plotly.io as pio
import plotly
import pandas as pd
import math
import seaborn as sb
import re
import os
import subprocess



#bibtex_key = row[0]
#title = row[1]

#selection_criteria = row[2]
#Extract -> Print

#status = row[3]
#Print

#comments = row[4]
#[1]-[2]-[3]
#[4]-[5]-[6]
#Extract ->Create->Print

#Extract -> Total e ByCriteria

# Normalmente os Extracts são pré calculados, ai dependendo da escolha se calcula o Calculate e depois os prints



script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, '/home/laercio/github/ReadingParsifal/Figs/')
#sample_file_name = "sample

if not os.path.isdir(results_dir):
    os.makedirs(results_dir)


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
dict_H2H_ReachedObject = {}
dict_H2S_ReachedObject = {}
dict_H2SS_ReachedObject = {}
dict_S2S_ReachedImprovedObject = {}
dict_S2S_ReachedImplementedObject = {}
dict_S2H_ReachedImprovedObject = {}
dict_S2SS_ReachedImprovedObject = {}
dict_ARCH_improvedObject = {}


characters_to_remove = "[]()&"
papersToVerify = []

duplicated = 0
accepted = 0
rejected = 0
cont = 0


def CleanVariable(benchmark):
    for character in characters_to_remove:
        benchmark = benchmark.replace(character, "")
    return benchmark

def ExtractStatus(status, comments, selection_criteria):
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

    plt.rcParams.update({'font.size': 15.0})
    explode = (0, 0.1, 0.05)  # only "explode" the 2nd slice (i.e. 'Hogs')
    colors = ['red', 'green', 'yellow']
    fig1, ax1 = plt.subplots(figsize=(7, 7))
    ax1.pie(qtdLabels, explode=explode, autopct='%1.1f%%', shadow=True, wedgeprops=dict(width=1.0, edgecolor='white'), startangle=270, colors=colors)
    plt.legend(labels=labels, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 12}, bbox_transform=plt.gcf().transFigure)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Overall Papers Classification')
    title = 'OverallPapersClassification'
    plt.tight_layout()
    var = "{}/01printStatus_" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/01printStatus", shell=True)
    plt.savefig(var.format(results_dir+"/01printStatus"))
    plt.show()

def ExtractBenchmark(benchmarks):
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
                CreateInsertHeadAndTailBenchmark(head, tails)

            elif letter == "&" and word != "": #'ING&SFS&TPCH&GLIMPSEINDEX&CLAMAV&OLTP(TPC-C)&TAR&UNTAR]'
                word = CleanVariable(word)
                CreateInsertOnlyHeadBenchmark(word) #apos inserir um benchmark preciso zerar a variavel
                word =""
        if word != None and word!= "]": #this case is when there are a las benchmark
            word = CleanVariable(word)
            CreateInsertOnlyHeadBenchmark(word)

    else: # There is no tail in this benchmark, add it imediatelly.
        benchmarks = benchmarks.split('&')
        for i, bench in enumerate(benchmarks):
            bench = CleanVariable(bench)
            benchmarks[i] = bench
        #benchmarks = CleanVariables(benchmarks, tail) #in this case, chamaleon returns an array of benchmarks
        for benchmark in benchmarks:
            CreateInsertOnlyHeadBenchmark(benchmark)
def CreateInsertHeadAndTailBenchmark(head, tails):
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
def CreateInsertOnlyHeadBenchmark(benchmark): #this function receives an unique benchmak to be appened to the dictionary
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
def printBenchmarksChart():
    plt.rcParams.update({'font.size': 8.0})
    benchname = []
    benchvalue= []
    for key, value in dict_benchmarks.items():
        for item in sorted(value):
            if item > 3 and item != 152:
                benchvalue.append(item)
                benchname.append(key)

    plt.rcParams.update({'font.size': 12.0})
    y_pos = np.arange(len(benchname))
    fig1, ax1 = plt.subplots(figsize=(10, 7))
    plt.bar(y_pos, benchvalue, align='center', alpha=0.5)
    plt.xticks(y_pos, benchname, rotation=85, ha='center',size=10)
    for i, v in enumerate(benchvalue):
        plt.text(i, v, str(v), color='red', size=8, ha='center')
    plt.tight_layout()
    plt.xlabel('Benchmarks and Traces')
    plt.ylabel('Quantity')
    plt.title('Benchmarks Occurrences')
    title = 'BenchmarksOccurrences'
    plt.tight_layout()
    var = "{}/06printBenchmarksChart" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/06printBenchmarksChart", shell=True)
    plt.savefig(var.format(results_dir + "/06printBenchmarksChart"))
    plt.show()


    benchname = []
    benchvalue = []
    color = []

    for mainBenchmark, subbenchmaks in dict_benchmarks.items():
        for mainBenchmarkQtd, traces in subbenchmaks.items():
            if mainBenchmarkQtd > 3 and mainBenchmarkQtd != 152:
                benchvalue.append(mainBenchmarkQtd)
                benchname.append(mainBenchmark)
                color.append("red")
                for key, value in traces.items():
                    if value > 3:
                        benchname.append(mainBenchmark+"_"+key)
                        benchvalue.append(value)
                        color.append("blue")


    y_pos = np.arange(len(benchname))
    fig1, ax1 = plt.subplots(figsize=(15, 10))
    plt.bar(y_pos, benchvalue, align='center', alpha=0.5)
    plt.xticks(y_pos, benchname, rotation=85, ha='center', size=10)
    for i, v in enumerate(benchvalue):
        plt.text(i, v, str(v), color='black', size=8, ha='center')

    sb.barplot(x=benchname, y=benchvalue, palette=color, color=color)
    plt.tight_layout()
    ax1.xaxis.label.set_size(200)
    plt.xlabel('Benchmarks and Traces', fontsize=10)
    plt.ylabel('Quantity', fontsize=10)
    plt.title('Benchmarks and Traces Occurrences')
    title='BenchmarksAndTracesOccurrences'
    plt.tight_layout()
    var = "{}/06printBenchmarksChart" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/06printBenchmarksChart", shell=True)
    plt.savefig(var.format(results_dir + "/06printBenchmarksChart"))
    plt.show()

def ExtractANDCreateDict_Power(power,selection_criteria):
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
def printPowerChart():
    labelYesNo = []
    for key, value in dict_power.items():
        if key == "Y":
            yes = value
        else:
            no = value
    labelYesNo.append(no)
    labelYesNo.append(yes)

    plt.rcParams.update({'font.size': 14.0})
    labels = 'Does Not Consider Energy', 'Consider Energy'
    explode = (0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    colors = ['red', 'green']
    fig1, ax1 = plt.subplots(figsize=(7, 7))
    ax1.pie(labelYesNo, explode=explode, autopct='%1.1f%%', shadow=True, wedgeprops=dict(width=1.0, edgecolor='white'), startangle=270, colors=colors)
    plt.legend(labels=labels, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 12}, bbox_transform=plt.gcf().transFigure, title="Power Concerning")
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Papers With Power Consideration')
    title = 'PapersWithPowerConsideration'
    plt.tight_layout()
    var = "{}/02printPowerChart" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/02printPowerChart", shell=True)
    plt.savefig(var.format(results_dir + "/02printPowerChart"))
    plt.show()

def printPowerChartByCriteria(): # {'S2SS-IO -Soft-2-improve-IO-on-Storage-Systems': {'Y': 12, 'N': 197}, 'H2H-IO -Hard-2-improve-IO-on-Hardware': {'Y': 10, 'N': 2}, 'S2H-IO -Soft-2-improve-IO-on-Hardware': {'Y': 10, 'N': 106}, 'ARCHITECTURE': {'Y': 11, 'N': 71}, 'S2S-IO -Soft-2-improve-IO-on-Software': {'Y': 5, 'N': 102}, 'H2SS-IO -Hardw-2-improve-IO-on-Storage-Systems': {'Y': 1, 'N': 15}, 'H2S-IO -Hard-2-improve-IO-on-Software': {'Y': 1, 'N': 8}}
    labels = []
    colors =[]
    labels2 = ['Yes', 'No']
    percent=[]

    for criteria,value in dict_powerByCriteria.items():
        if "H2SS-IO" in criteria:
            for letter,val in value.items():
                if letter == 'Y':
                    yes = int(val)
                elif letter == 'N':
                    no=int(val)
            total=yes+no
            xyes=(yes*100)/total
            xno =(no*100)/total
            percent.append(round(xyes,0))
            percent.append(round(xno,0))
            labels.append("H2SS-IO")
            colors.append("green")

    for criteria, value in dict_powerByCriteria.items():
        if "S2SS-IO" in criteria:
            for letter,val in value.items():
                if letter == 'Y':
                    yes = int(val)
                elif letter == 'N':
                    no=int(val)
            total=yes+no
            xyes=(yes*100)/total
            xno =(no*100)/total
            percent.append(round(xyes,0))
            percent.append(round(xno,0))
            labels.append("S2SS-IO")
            colors.append("red")

    for criteria, value in dict_powerByCriteria.items():
        if "S2H-IO" in criteria:
            for letter,val in value.items():
                if letter == 'Y':
                    yes = int(val)
                elif letter == 'N':
                    no=int(val)
            total=yes+no
            xyes=(yes*100)/total
            xno =(no*100)/total
            percent.append(round(xyes,0))
            percent.append(round(xno,0))
            labels.append("S2H-IO")
            colors.append("tomato")

    for criteria, value in dict_powerByCriteria.items():
        if "S2S-IO" in criteria:
            for letter,val in value.items():
                if letter == 'Y':
                    yes = int(val)
                elif letter == 'N':
                    no=int(val)
            total=yes+no
            xyes=(yes*100)/total
            xno =(no*100)/total
            percent.append(round(xyes,0))
            percent.append(round(xno,0))
            labels.append("S2S-IO")
            colors.append("salmon")

    for criteria, value in dict_powerByCriteria.items():
        if "ARCHITECTURE" in criteria:
            for letter,val in value.items():
                if letter == 'Y':
                    yes = int(val)
                elif letter == 'N':
                    no=int(val)
            total=yes+no
            xyes=(yes*100)/total
            xno =(no*100)/total
            percent.append(round(xyes,0))
            percent.append(round(xno,0))
            labels.append("ARCHITECTURE")
            colors.append("yellow")

    for criteria, value in dict_powerByCriteria.items():
        if "H2H-IO" in criteria:
            for letter,val in value.items():
                if letter == 'Y':
                    yes = int(val)
                elif letter == 'N':
                    no=int(val)
            total=yes+no
            xyes=(yes*100)/total
            xno =(no*100)/total
            percent.append(round(xyes,0))
            percent.append(round(xno,0))
            labels.append("H2H-IO")
            colors.append("lightgreen")

    for criteria, value in dict_powerByCriteria.items():
        if "H2S-IO" in criteria:
            for letter,val in value.items():
                if letter == 'Y':
                    yes = int(val)
                elif letter == 'N':
                    no=int(val)
            total=yes+no
            xyes=(yes*100)/total
            xno =(no*100)/total
            percent.append(round(xyes,0))
            percent.append(round(xno,0))
            labels.append("H2S-IO")
            colors.append("olive")

    plt.rcParams.update({'font.size': 11.0})
    plt.subplots(figsize=(8, 8))
    plt.pie([1,1,1,1,1,1,1], radius=1,
            colors=colors,
            labels=labels,
            pctdistance=0.85, shadow=True, labeldistance=0.99,
            wedgeprops=dict(width=0.3, edgecolor='white'),startangle=40)

    plt.pie(percent, radius=0.7,
            colors=['xkcd:green','xkcd:red','xkcd:green','xkcd:red','xkcd:green','xkcd:red','xkcd:green','xkcd:red','xkcd:green','xkcd:red',
                    'xkcd:green','xkcd:red','xkcd:green','xkcd:red'],
            wedgeprops=dict(width=0.3, edgecolor='white'), labels=percent,
            pctdistance=0.9, labeldistance=0.7, shadow=True,startangle=40)
    plt.legend(labels=labels2, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 15},bbox_transform=plt.gcf().transFigure, title="Power Concerning")
    plt.axis('equal')
    plt.title('Papers With Power Consideration \n According to the Classification Model')
    title = 'PapersWithPowerConsiderationInnerAccordingtotheClassificationModelOuter'
    plt.tight_layout()
    var = "{}/03printPowerChartByCriteria" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/03printPowerChartByCriteria", shell=True)
    plt.savefig(var.format(results_dir + "/03printPowerChartByCriteria"))
    plt.show()

def ExtractImprovedObject(improvedObject,selection_criteria):
    global cont
    if selection_criteria == "H2H-IO -Hard-2-improve-IO-on-Hardware":
        #[on-chip access control memory-STT-RAM- (ACM)SSD(FeSSD)]-[SSD[DiskSim]]-[SSD&STT-RAM]
        CreateDict_H2H_improvedObject(improvedObject)
    elif selection_criteria == "H2S-IO -Hard-2-improve-IO-on-Software":
        #[Determine the Hardware Choice(DRAM)]-[File System(HDFS)]-[DRAM]
        #print("teste")
        ExtractDict_H2S_improvedObject(improvedObject)
    elif selection_criteria == "H2SS-IO -Hardw-2-improve-IO-on-Storage-Systems":
        #[DMA cache technique (DDC)]-[Storage System[FPGA Emulation Platform]]-[Memory&cache]
        ExtractDict_H2SS_improvedObject(improvedObject)
        #print("teste")
    elif selection_criteria == "S2S-IO -Soft-2-improve-IO-on-Software":
        #[non-blocking API extensions]-[Memcached[Libmemcached APIs]]-[SSD&Memory]
        cont +=1
        ExtractS2SDevices(improvedObject)
        #print("teste", cont)
    elif selection_criteria == "S2H-IO -Soft-2-improve-IO-on-Hardware":
        #[I/O link over-clocking]-[SSD[nf][rd(Altera Stratix IV GX FPGA PCle)]-[SSD]
        ExtractS2HDevices(improvedObject)
    elif selection_criteria == "S2SS-IO -Soft-2-improve-IO-on-Storage-Systems":
        # [writeback scheme(DFW)]-[Stotrage System[File System(EXT3)][rsee(1m2d)]]-[HDD&SSD]
        ExtractS2SSDevices(improvedObject)
    elif selection_criteria == "ARCHITECTURE":
        #[duplication-aware flash cache architecExtractH2HDevices(improvedObject)ture (DASH)]-[Cloud[rsee(1m)]]-[Flash&HDD]
        ExtractARCH(improvedObject)


def CreateDict_H2H_improvedObject(improvedObject):
    if improvedObject not in dict_H2H_ReachedObject:
        dict_H2H_ReachedObject[improvedObject] = 1
    else:
        val = dict_H2H_improvedObject[improvedObject]
        dict_H2H_ReachedObject[improvedObject] = val + 1
def print_H2H_ReachedObject():
    labels = []
    qtdLabels = []

    for device, value in dict_H2H_ReachedObject.items():
        labels.append(device)
        qtdLabels.append(value)
    plt.rcParams.update({'font.size': 13.0})
    fig1, ax1 = plt.subplots(figsize=(15, 8))
    ax1.pie(qtdLabels, labels=labels, autopct='%1.1f%%', shadow=True, startangle=270)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Improved Hardware Class by Hardware')
    title = 'ImprovedHardwareClassbyHardware'
    plt.tight_layout()
    var = "{}/08printH2HReachedObject" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/08printH2HReachedObject", shell=True)
    plt.savefig(var.format(results_dir + "/08printH2HReachedObject"))
    plt.show()


def ExtractDict_H2S_improvedObject(improvedObject): #[File System(HDFS)]
    word = ""
    especifiedObj = ""
    letter2 =""
    j = -1
    object = improvedObject.upper()
    #if "(" in object:  # devo fazer o tratamento com o parenteses
    for i, letter in enumerate(object):
        if letter != "(" and letter != "&" and i > j:
            word = word + letter  # word vai ser ou um head de um benchmark ou benchmark
        elif letter == "(":  # extract the tails
            improvedObjclass = word
            word = ""
            j = i + 1
            while object[j] != ")":  # trick to extract the tail
                letter2 = object[j]
                especifiedObj = especifiedObj + letter2
                j += 1
            letter2 = ""
            especifiedObjs = especifiedObj.split('&')
            especifiedObj = ""
            improvedObjclass = CleanVariable(improvedObjclass)
            for i, subespecifiedObj in enumerate(especifiedObjs):  # clean the vector of tails
                subespecifiedObj = CleanVariable(subespecifiedObj)
                especifiedObjs[i] = subespecifiedObj
            CreateDict_H2S_improvedObject(improvedObjclass, especifiedObjs)
def CreateDict_H2S_improvedObject(improvedObjclass, especifiedObjs):
    if improvedObjclass not in dict_H2S_ReachedObject.keys(): #adiciono HEAD com 1 ocorrencia, adiciono seus tais com 1 ocorrencia
        first = {1:{}}
        dict_H2S_ReachedObject[improvedObjclass] = first
        for obj in especifiedObjs:
            for occurrence,benchs in dict_H2S_ReachedObject[improvedObjclass].items():
                if obj not in benchs.keys():  # insert an new elemento into the subs
                    aux = {obj:1}
                    benchs.update(aux) #adiciona o head para adicionar os Keys
    else: # atualizo o valor do head, verifico se existe o tail, se existir atualizo valor do TAIL, se não existir, insiro o TAIL com ocorrencia = 1
        dict_old = dict_H2S_ReachedObject[improvedObjclass]
        dict_new = {}
        for occurrence, benchs in dict_old.items():
            occurrence += 1
            for obj in especifiedObjs:
                if obj not in benchs.keys():  # insert an new elemento into the subs
                    aux = {obj: 1}
                    benchs.update(aux)
                else:
                    for occurrenceSub, bench in benchs.items():
                        if occurrenceSub == obj:
                            bench += 1
                            aux2={occurrenceSub:bench}
                            benchs.update(aux2)

                #atualiza com benchs e occurrence
                dict_new = {occurrence:benchs}
                dict_H2S_ReachedObject[improvedObjclass] = dict_new
def print_H2S_ReachedObject():
    improvedObjClassName =[]
    improvedClassQtd =[]
    improvedSpecificObjName = []
    improvedSpecificObjQtd = []


    for improvedObjclass, especifiedObjs in dict_H2S_ReachedObject.items():
        improvedObjClassName.append(improvedObjclass)
        for classQtd, especifiedObjsSub in especifiedObjs.items():
            improvedClassQtd.append(classQtd)
            for specificObj, qtdEspecificObj in especifiedObjsSub.items():
                improvedSpecificObjName.append(specificObj)
                improvedSpecificObjQtd.append(qtdEspecificObj)

    percentObjClass = []
    percentObjSpecific = []
    total = 0

    #Calculate Obj Class Percentage
    for x in improvedClassQtd:
        total += int(x)
    for val in improvedClassQtd:
        percentage = (val * 100) / total
        percentObjClass.append(round(percentage, 1))

    # {'DATABASE': {1: {'IBM SOLIDDB': 1}}, 'IN-MEMORY KEY-VALUE STORE': {1: {'MEMCACHE': 1}}, 'APPLICATION': {1: {'GENOME SEARCH': 1}},
    # 'FRAMEWORK': {2: {'SPARK': 1, 'HADOOP MAPREDUCE': 1}}, 'FILE SYSTEM': {2: {'HDFS': 2}}}
    # ['DATABASE', 'IN-MEMORY KEY-VALUE STORE', 'APPLICATION', 'FRAMEWORK', 'FILE SYSTEM']   #improvedObjClassName
    # i  [1, 1, 1, 2, 2] quantidade de vezes que apareceu a aplicação.                          #improvedClassQtd
    # ['IBM SOLIDDB', 'MEMCACHE', 'GENOME SEARCH', 'SPARK', 'HADOOP MAPREDUCE', 'HDFS']      #improvedSpecificObjName
    # j  [1, 1, 1, 1, 1, 2]                                                                     #improvedSpecificObjQtd

    cont = 0
    item = 1
    for i, j in zip(improvedClassQtd, improvedSpecificObjQtd):  # o tamanho de J deve ser sempre igual ao tamanho de i
        if i > j:  # tem dois databases diferentes
            #calcula variavel cont que conterá a quantidade de valores do vetor improvedSpecificObjQtd  que correspondem ao vetor improvedClassQtd
            while i >= j:
                cont += 1
                j += 1
            addpercent = 1 / cont #adicione a quantidade de Cont com o valor ADDPERCENT
            while item <= cont:
                percentObjSpecific.append(addpercent)
                item+=1
        elif i == j:  # um elemento correspondente de cada vetor
            percentObjSpecific.append(1)

    plt.rcParams.update({'font.size': 13.0})
    plt.subplots(figsize=(11, 9))
    plt.pie(improvedClassQtd, radius=1, pctdistance=0.85, shadow=True, autopct='%.2f%%',
            wedgeprops=dict(width=0.3, edgecolor='white'),startangle=40)

    plt.pie(improvedSpecificObjQtd, radius=0.7, labels=improvedSpecificObjName, wedgeprops=dict(width=0.3, edgecolor='white'),# autopct='%.2f%%',
             pctdistance=0.9, labeldistance=0.6, shadow=True,startangle=40, textprops = dict(rotation_mode = 'anchor', va='center', ha='left'))
    plt.legend(labels=improvedObjClassName, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 11},
               bbox_transform=plt.gcf().transFigure, title="Improved Class")
    plt.axis('equal')
    plt.title('H2S - Software Class Improved by Hardware')
    title = 'H2SSoftwareClassImprovedbyHardware'
    plt.tight_layout()
    var = "{}/09printH2SReachedObject" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/09printH2SReachedObject", shell=True)
    plt.savefig(var.format(results_dir + "/09printH2SReachedObject"))
    plt.show()

def ExtractDict_H2SS_improvedObject(improvedObject): #[File System(HDFS)]
    # improved place/implanted place/evaluated environment
    #Storage Systems[Storage System][rsee(1s)]   ----   Storage System[Storage System][rsee(1c16n)]
    word = ""
    environmentType =''
    letter2 =""
    j = -1
    object = improvedObject.upper()
    object = object.split('[')
    improvedGeneralObjClass=object[0]
    improvedSpecificObjPlace=object[1]
    improvedObjEnv=object[2]
    #Extracting environment Class (RSEE) and EnvironmentType (1S)
    for i, letter in enumerate(improvedObjEnv):
        if letter != "(" and letter != "&" and i > j:
            word = word + letter  # word vai ser ou um head de um benchmark ou benchmark
        elif letter == "(":  # extract the tails
            environmentClass = word
            word = ""
            j = i + 1
            while improvedObjEnv[j] != ")":  # trick to extract the tail
                letter2 = improvedObjEnv[j]
                environmentType = environmentType + letter2
                j += 1
            letter2 = ""
            improvedGeneralObjClass=CleanVariable(improvedGeneralObjClass)
            improvedSpecificObjPlace=CleanVariable(improvedSpecificObjPlace)
            environmentClass=CleanVariable(environmentClass)
            environmentType=CleanVariable(environmentType)
            CreateDict_H2SS_improvedObject(improvedGeneralObjClass, improvedSpecificObjPlace, environmentClass, environmentType)
def CreateDict_H2SS_improvedObject(improvedGeneralObjClass, improvedSpecificObjPlace, environmentClass, environmentType):
    global dict_H2SS_ReachedObject
    #GENERALOBJCLASS :{STORAGE SYSTEM:1},
    #SPECIFICOBJCLASS: {STORAGE SYSTEM: 1, XXXSSS: 1},
    #ENVIRONMENTCLASS :{RSEE:1, RHEE:1, SSEE:1}
    #ENVIRONMENTYPE: {1pc: 1, 1c: 1, 1s: 1}

    #We insert one prefix into the environment type to plot the graphic according to these environment class
    envPrefix= ""
    if "RS" in environmentClass:
        envPrefix = "rs"
    elif "RH" in environmentClass:
        envPrefix = "rh"
    elif "SS" in environmentClass:
        envPrefix = "ss"
    environmentType = envPrefix+environmentType



    if "GENERALOBJCLASS" not in dict_H2SS_ReachedObject.keys():
        first = {}
        dict_H2SS_ReachedObject["GENERALOBJCLASS"] = first
    subdict = dict_H2SS_ReachedObject["GENERALOBJCLASS"]
    if improvedGeneralObjClass not in subdict.keys():
        val ={improvedGeneralObjClass: 1}
        subdict.update(val)
    else:
        del dict_H2SS_ReachedObject["GENERALOBJCLASS"]
        for key, value in subdict.items():
            if key == improvedGeneralObjClass:
                val = value
                val += 1
                dict_H2SS_ReachedObject["GENERALOBJCLASS"] = {}
                obj = {improvedGeneralObjClass: val}
                subdict.update(obj)
                dict_H2SS_ReachedObject["GENERALOBJCLASS"] = subdict


    if "SPECIFICOBJCLASS" not in dict_H2SS_ReachedObject.keys():
        first = {}
        dict_H2SS_ReachedObject["SPECIFICOBJCLASS"] = first
    subdict = dict_H2SS_ReachedObject["SPECIFICOBJCLASS"]
    if improvedSpecificObjPlace not in subdict.keys():
        val = {improvedSpecificObjPlace: 1}
        subdict.update(val)
    else:
        del dict_H2SS_ReachedObject["SPECIFICOBJCLASS"]
        for key, value in subdict.items():
            if key == improvedSpecificObjPlace:
                val = value
                val += 1
                dict_H2SS_ReachedObject["SPECIFICOBJCLASS"] = {}
                obj = {improvedSpecificObjPlace: val}
                subdict.update(obj)
                dict_H2SS_ReachedObject["SPECIFICOBJCLASS"] = subdict


    if "ENVIRONMENTCLASS" not in dict_H2SS_ReachedObject.keys():
        first = {}
        dict_H2SS_ReachedObject["ENVIRONMENTCLASS"] = first
    subdict = dict_H2SS_ReachedObject["ENVIRONMENTCLASS"]
    if environmentClass not in subdict.keys():
        val = {environmentClass: 1}
        subdict.update(val)
    else:
        del dict_H2SS_ReachedObject["ENVIRONMENTCLASS"]
        for key, value in subdict.items():
            if key == environmentClass:
                val = value
                val += 1
                dict_H2SS_ReachedObject["ENVIRONMENTCLASS"] = {}
                obj = {environmentClass: val}
                subdict.update(obj)
                dict_H2SS_ReachedObject["ENVIRONMENTCLASS"] = subdict


    if "ENVIRONMENTYPE" not in dict_H2SS_ReachedObject.keys():
        first = {}
        dict_H2SS_ReachedObject["ENVIRONMENTYPE"] = first
    subdict = dict_H2SS_ReachedObject["ENVIRONMENTYPE"]
    if environmentType not in subdict.keys():
        val = {environmentType: 1}
        subdict.update(val)
    else:
        del dict_H2SS_ReachedObject["ENVIRONMENTYPE"]
        for key, value in subdict.items():
            if key == environmentType:
                val = value
                val += 1
                dict_H2SS_ReachedObject["ENVIRONMENTYPE"] = {}
                obj = {environmentType: val}
                subdict.update(obj)
                dict_H2SS_ReachedObject["ENVIRONMENTYPE"] = subdict
def printDict_H2SS_improvedObject():
    # 'GENERALOBJCLASS': {'STORAGE SYSTEMS': 10}
    # 'SPECIFICOBJCLASS': {'PXA255]': 1, 'STORAGE SYSTEM]': 7, 'FPGA EMULATION PLATFORM]': 1, 'EXYNOS 5420 BOARD]': 1},
    # 'ENVIRONMENTCLASS': {'SSEE': 3, 'RSEE': 7},
    # 'ENVIRONMENTYPE': {'1S': 2, 'SP': 1, 'DRAMSIM2': 1, 'NF': 1, 'PXA255': 1, '1C16N': 1, 'PCM SIMULATOR': 1, '1PC': 2},

    objClass = []
    objClassQtd = []
    speObjClass =[]
    speObjQtd = []
    envClass = []
    envClassQtd = []
    envType =[]
    envTypeQtd =[]



    for key, value in dict_H2SS_ReachedObject.items():
        if key == "GENERALOBJCLASS":
            for objectClass, objectClassQtd in value.items():
                objClass.append(objectClass)
                objClassQtd.append(objectClassQtd)

    for key, value in dict_H2SS_ReachedObject.items():
        if key == "SPECIFICOBJCLASS":
            for specificObjectClass, specificObjectQtd in value.items():
                speObjClass.append(specificObjectClass)
                speObjQtd.append(specificObjectQtd)

    for key, value in dict_H2SS_ReachedObject.items():
        if key == "ENVIRONMENTCLASS":
            for environmentClass, environmentClassQtd in value.items():
                envClass.append(environmentClass)
                envClassQtd.append(environmentClassQtd)

    for key, value in dict_H2SS_ReachedObject.items():
        if key == "ENVIRONMENTYPE":
            for environmentType, environmentTypeQtd in value.items():
                envType.append(environmentType)
                envTypeQtd.append(environmentTypeQtd)
        #fazer a leitura letra a letra para inserir em um vetor os elementos que condizem com cada typo de ambiente

    # GENERALOBJCLASS
    labels = objClass
    qtdLabels = objClassQtd
    plt.rcParams.update({'font.size': 15.0})
    colors = ['dodgerblue']
    fig1, ax1 = plt.subplots(figsize=(7, 7))
    ax1.pie(qtdLabels, autopct='%1.1f%%', shadow=True, startangle=270, colors=colors,# explode=explode,
            wedgeprops=dict(width=0.5, edgecolor='white'))  # explode=explode,
    plt.legend(labels=labels, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 12},
               bbox_transform=plt.gcf().transFigure, title="Improved Object Class")
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('H2SS - General Object Improved Class')
    title = 'H2SSGeneralObjectImprovedClass'
    plt.tight_layout()
    var = "{}/10printDictH2SSimprovedObject" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/10printDictH2SSimprovedObject", shell=True)
    plt.savefig(var.format(results_dir + "/10printDictH2SSimprovedObject"))
    plt.show()




    #ENVIRONMENTCLASS
    labels2 = []
    labels = envClass
    if labels[0] == "RSEE":
        labels2=["RSEE - Real Small","SSEE - Software Simulated"]
        colors = ['green', 'red']
    else:
        labels2 == ["SSEE - Software Simulated", "RSEE - Real Small"]
        colors = ['red', 'green']

    qtdLabels = envClassQtd
    explode = (0.2, 0.0)
    fig1, ax1 = plt.subplots(figsize=(7, 7))
    ax1.pie(qtdLabels,  autopct='%1.1f%%', shadow=True, startangle=270, colors=colors, explode=explode, wedgeprops=dict(width=0.5, edgecolor='white'))# explode=explode,
    plt.legend(labels=labels2, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 9}, bbox_transform=plt.gcf().transFigure, title="Evaluated Environment")
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('H2SS - Class of Evaluated Environment')
    title = 'H2SSClassofEvaluatedEnvironment'
    plt.tight_layout()
    var = "{}/10printDictH2SSimprovedObject" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/10printDictH2SSimprovedObject",
                    shell=True)
    plt.savefig(var.format(results_dir + "/10printDictH2SSimprovedObject"))
    plt.show()

    # SPECIFICOBJCLASS
    labels = speObjClass
    qtdLabels = speObjQtd
    fig1, ax1 = plt.subplots(figsize=(7, 7))
    ax1.pie(qtdLabels, autopct='%1.1f%%', shadow=True, startangle=270, #colors=colors,# explode=explode,
            wedgeprops=dict(width=0.5, edgecolor='white'))  # explode=explode,
    plt.legend(labels=labels, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 9},
               bbox_transform=plt.gcf().transFigure, title="Improved Class")
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Specific Improved Object Class')
    title = 'SpecificImprovedObjectClass'
    plt.tight_layout()
    var = "{}/10printDictH2SSimprovedObject" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/10printDictH2SSimprovedObject",
                    shell=True)
    plt.savefig(var.format(results_dir + "/10printDictH2SSimprovedObject"))
    plt.show()


    # ENVIRONMENTYPE
    #labels = envType
    colors = []
    for env in labels:
        if "rs" in env:
            colors.append("green")
        elif "ss" in env:
            colors.append("red")
    qtdLabels = envTypeQtd
    labelsEvaluatedEnvironment = ["SS - Software Simulated",
                                  "RS - Real Small",
                                  "C - Cluster\nN - Node\nS - Server\nPC - Personal Computer\nD - Disk\nSd - Solid Disk",
                                  "M - Machine",
                                  "NF - Not Found",
                                  "V - Virtual",
                                  "FLM - Flash Memory",
                                  "FD - Flash Disk",
                                  "VM - Virtual Machine"
                                  ]

    plt.rcParams.update({'font.size': 8.0})
    plt.subplots(figsize=(8,9))
    clrs = ['red' if ("ss" in x) else 'green' for x in envType]
    sb.barplot(x=envType, y=envTypeQtd, palette=clrs, color=clrs)
    #sb.tsplot(data=envType, time="timepoint", unit="subject", condition="ROI", value="BOLD signal")

    plt.legend(labels=labelsEvaluatedEnvironment, bbox_to_anchor=(1.05, 1), loc=1, prop={'size': 8}, borderaxespad=0., title="Environment Class")
    plt.title('Hardware Infrastructure Used To Evaluation')
    title = 'HardwareInfrastructureUsedToEvaluation'
    plt.tight_layout()
    var = "{}/10printDictH2SSimprovedObject" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/10printDictH2SSimprovedObject",
                    shell=True)
    plt.savefig(var.format(results_dir + "/10printDictH2SSimprovedObject"))
    plt.show()


def ExtractS2SDevices(improvedObject):
    object = improvedObject.upper()
    object = re.split('[()]', object)

    improvedGeneralObjClass = object[0]
    improvedSpecificObjPlace = object[1]
    implementedObj = object[2]

    improvedGeneralObjClass = CleanVariable(improvedGeneralObjClass)
    improvedSpecificObjPlace = CleanVariable(improvedSpecificObjPlace)
    implementedObj = CleanVariable(implementedObj)

    CreateDict_S2S_improvedObject(improvedGeneralObjClass,improvedSpecificObjPlace)
    CreateDict_S2S_implementedObject(improvedGeneralObjClass, implementedObj)
def CreateDict_S2S_improvedObject(improvedGeneralObjClass,improvedSpecificObjPlace):
    #print("improvedGeneralObjClass ->", improvedGeneralObjClass, "\nimprovedSpecificObjPlace ->",improvedSpecificObjPlace,"\nimplementedObj ->",implementedObj)
    #improvedGeneralObjClass -> FILE SYSTEM
    #improvedSpecificObjPlace -> ORANGEFS
    #implementedObj -> ORANGEFS

    #Verifica se a classe de objeto está no dicionario
    if improvedGeneralObjClass not in dict_S2S_ReachedImprovedObject.keys():
        first = {}
        dict_S2S_ReachedImprovedObject[improvedGeneralObjClass] = first

    #faz BKP do VALUE do dicionario
    subdict = dict_S2S_ReachedImprovedObject[improvedGeneralObjClass]
    del dict_S2S_ReachedImprovedObject[improvedGeneralObjClass]

    #Faz a inserção da mesma CLASSE de objeto acima, e adiciona um valor para ela.
    if improvedGeneralObjClass not in subdict.keys():
        aux1 ={improvedGeneralObjClass: 1}
        subdict.update(aux1)
    else:
        val1 = subdict[improvedGeneralObjClass]
        val1 += 1
        obj = {improvedGeneralObjClass: val1}
        subdict.update(obj)
    # Faz a inserção da mesma SPECIFIC OBJECT de objeto acima, e adiciona um valor para ela.
    if improvedSpecificObjPlace not in subdict.keys():
        aux2 = {improvedSpecificObjPlace: 1}
        subdict.update(aux2)
    else:
        val2 = subdict[improvedSpecificObjPlace]
        val2 += 1
        obj = {improvedSpecificObjPlace: val2}
        subdict.update(obj)

    dict_S2S_ReachedImprovedObject[improvedGeneralObjClass] = {}
    dict_S2S_ReachedImprovedObject[improvedGeneralObjClass] = subdict
def CreateDict_S2S_implementedObject(improvedGeneralObjClass, implementedObj):
    #print("improvedGeneralObjClass ->", improvedGeneralObjClass, "\nimprovedSpecificObjPlace ->",improvedSpecificObjPlace,"\nimplementedObj ->",implementedObj)
    #improvedGeneralObjClass -> FILE SYSTEM
    #improvedSpecificObjPlace -> ORANGEFS
    #implementedObj -> ORANGEFS

    if improvedGeneralObjClass == "APPLICATIONS":
        print(improvedGeneralObjClass)
        print(implementedObj)
        #print(improvedSpecificObjPlace)

    #Verifica se a classe de objeto está no dicionario
    if improvedGeneralObjClass not in dict_S2S_ReachedImplementedObject.keys():
        first = {}
        dict_S2S_ReachedImplementedObject[improvedGeneralObjClass] = first

    #faz BKP do VALUE do dicionario
    subdict = dict_S2S_ReachedImplementedObject[improvedGeneralObjClass]
    del dict_S2S_ReachedImplementedObject[improvedGeneralObjClass]

    #Faz a inserção da mesma CLASSE de objeto acima, e adiciona um valor para ela.
    if improvedGeneralObjClass not in subdict.keys():
        aux1 ={improvedGeneralObjClass: 1}
        subdict.update(aux1)
    else:
        val1 = subdict[improvedGeneralObjClass]
        val1 += 1
        obj = {improvedGeneralObjClass: val1}
        subdict.update(obj)
    # Faz a inserção da mesma SPECIFIC OBJECT de objeto acima, e adiciona um valor para ela.
    if implementedObj not in subdict.keys():
        aux2 = {implementedObj: 1}
        subdict.update(aux2)
    else:
        val2 = subdict[implementedObj]
        val2 += 1
        obj = {implementedObj: val2}
        subdict.update(obj)



    dict_S2S_ReachedImplementedObject[improvedGeneralObjClass] = {}
    dict_S2S_ReachedImplementedObject[improvedGeneralObjClass] = subdict
def printDict_S2S_improvedObject():
#<class 'dict'>: {'OPERATIONAL SYSTEM': {'OPERATIONAL SYSTEM': 6, 'LINUX': 6}, 'FRAMEWORK': {'HADOOP': 2, 'FRAMEWORK': 6, 'FLAME-MR': 1, 'SPARK': 3}
    improvedGeneralObjClass = []
    improvedGeneralObjClassQtd = []
    improvedSpecificObjPlace = []
    improvedSpecificObjPlaceQtd = []

    for impGeneralObjClass, especificObjs in dict_S2S_ReachedImprovedObject.items():
        improvedGeneralObjClass.append(impGeneralObjClass)
        for impGenObjCla, impGenObjClaQtd in especificObjs.items():
            if impGenObjCla == impGeneralObjClass:
                improvedGeneralObjClassQtd.append(impGenObjClaQtd)
            else:
                improvedSpecificObjPlace.append(impGenObjCla)
                improvedSpecificObjPlaceQtd.append(impGenObjClaQtd)

    plt.rcParams.update({'font.size': 10.0})
    plt.subplots(figsize=(12,9))
    plt.pie(improvedGeneralObjClassQtd, radius=1, labels=improvedGeneralObjClass, pctdistance=0.85, labeldistance=0.99, shadow=True, autopct='%.2f%%', wedgeprops=dict(width=0.3, edgecolor='white'), startangle=180)
    plt.rcParams.update({'font.size': 7.0})
    patches, texts = plt.pie(improvedSpecificObjPlaceQtd, radius=0.7, labels=improvedSpecificObjPlace,rotatelabels = 270, wedgeprops=dict(width=0.3, edgecolor='white'), pctdistance=5, labeldistance=0.8, shadow=True, startangle=180,
            textprops=dict(rotation_mode='anchor', va='center', ha='left'))
    join = []
    plt.rcParams.update({'font.size': 10.0})
    for t in texts:
        t.set_horizontalalignment('center')

    for a,b in zip(improvedGeneralObjClass, improvedGeneralObjClassQtd):
        join.append(str(a)+" ="+str(b))
    for a,b in zip(improvedSpecificObjPlace,improvedSpecificObjPlaceQtd):
        join.append(str(a)+" ="+str(b))

    plt.legend(labels=join, bbox_to_anchor=(1, 0),loc="lower right", prop={'size': 8},bbox_transform=plt.gcf().transFigure)
    plt.axis('equal')
    plt.title('S2S - Improved Object Class and its Specific Improved Component')
    title = 'S2SImprovedObjectClassOutanditsSpecificImprovedComponentInner'
    plt.tight_layout()
    var = "{}/11printDictS2SimprovedObject" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/11printDictS2SimprovedObject", shell=True)
    plt.savefig(var.format(results_dir + "/11printDictS2SimprovedObject"))
    plt.show()
def printDict_S2S_implementedObject():
#<class 'dict'>: {'OPERATIONAL SYSTEM': {'OPERATIONAL SYSTEM': 6, 'LINUX': 6}, 'FRAMEWORK': {'HADOOP': 2, 'FRAMEWORK': 6, 'FLAME-MR': 1, 'SPARK': 3}
    improvedGeneralObjClass = []
    improvedGeneralObjClassQtd = []
    improvedSpecificObjPlace = []
    improvedSpecificObjPlaceQtd = []

    for impGeneralObjClass, especificObjs in dict_S2S_ReachedImplementedObject.items():
        improvedGeneralObjClass.append(impGeneralObjClass)
        for impGenObjCla, impGenObjClaQtd in especificObjs.items():
            if impGenObjCla == impGeneralObjClass:
                improvedGeneralObjClassQtd.append(impGenObjClaQtd)
            else:
                improvedSpecificObjPlace.append(impGenObjCla)
                improvedSpecificObjPlaceQtd.append(impGenObjClaQtd)

    plt.rcParams.update({'font.size': 10.0})
    plt.subplots(figsize=(12,9))
    plt.pie(improvedGeneralObjClassQtd, radius=1, labels=improvedGeneralObjClass, pctdistance=0.85, labeldistance=0.99, shadow=True, wedgeprops=dict(width=0.3, edgecolor='white'), startangle=180)
    plt.rcParams.update({'font.size': 7.0})
    patches, texts = plt.pie(improvedSpecificObjPlaceQtd, radius=0.9, labels=improvedSpecificObjPlace,rotatelabels = 270, wedgeprops=dict(width=0.3, edgecolor='white'), pctdistance=5, labeldistance=0.8, shadow=True, startangle=180,
            textprops=dict(rotation_mode='anchor', va='center', ha='left'))
    join = []
    plt.rcParams.update({'font.size': 10.0})
    for t in texts:
        t.set_horizontalalignment('center')

    for a,b in zip(improvedGeneralObjClass, improvedGeneralObjClassQtd):
        join.append(str(a)+" ="+str(b))
    for a,b in zip(improvedSpecificObjPlace,improvedSpecificObjPlaceQtd):
        join.append(str(a)+" ="+str(b))

    plt.legend(labels=join, bbox_to_anchor=(1, 0),loc="lower right", prop={'size': 6},bbox_transform=plt.gcf().transFigure)
    plt.axis('equal')
    plt.title('S2S - Improved Object Class and its Implemented Object Class')
    title = 'S2SImprovedObjectClassOutanditsImplementedObjectClassInner'
    plt.tight_layout()
    var = "{}/11printDictS2SimprovedObject" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/11printDictS2SimprovedObject", shell=True)
    plt.savefig(var.format(results_dir + "/11printDictS2SimprovedObject"))
    plt.show()

def ExtractS2HDevices(improvedObject):
    deviceSpecific=[]
    deviceClass=""
    improvedGeneralObjClass=""
    implementedSpecificObjPlace = ""
    implementedSpecificObjPlaceVet=[]
    UsedDeviceOnExperimentVet =""


    object = improvedObject.upper()
    object = re.split('; |, |\*|[[]', object)

    improvedGeneralObjClass = object[0]
    implementedSpecificObjPlace = object[1]
    UsedDeviceOnExperimentVet = object[2]


    UsedDeviceOnExperimentVet = UsedDeviceOnExperimentVet.split('(')
    deviceClass = UsedDeviceOnExperimentVet[0]
    del UsedDeviceOnExperimentVet[0]
    deviceSpecificAUX = UsedDeviceOnExperimentVet
    for i in deviceSpecificAUX:
        aux = CleanVariable(i)
        deviceSpecific.append(aux)

    improvedGeneralObjClass = CleanVariable(improvedGeneralObjClass)


    implementedSpecificObjPlace = re.split('[()]', implementedSpecificObjPlace)
    for i in implementedSpecificObjPlace:
        if i != "]":
            aux = CleanVariable(i)
            implementedSpecificObjPlaceVet.append(aux)

    deviceClass = CleanVariable(deviceClass)

    CreateDict_S2H_improvedObject(improvedGeneralObjClass,implementedSpecificObjPlaceVet,deviceClass,deviceSpecific)
def CreateDict_S2H_improvedObject(improvedGeneralObjClass,implementedSpecificObjPlaceVet,deviceClass,deviceSpecific):
# ----------------------------------------------improvedGeneralObjClass----------------------------------------------
    #improvedGeneralObjClass -> SSD
    #implementedSpecificObjPlaceVet -> [simulator, SSDsim]
    #deviceClass -> RD or SD
    #deviceSpecific

    #Verifica se a classe de objeto está no dicionario
    if "improvedGeneralObjClass" not in dict_S2H_ReachedImprovedObject.keys():
        first = {}
        dict_S2H_ReachedImprovedObject["improvedGeneralObjClass"] = first

    #faz BKP do VALUE do dicionario
    subdict = dict_S2H_ReachedImprovedObject["improvedGeneralObjClass"]
    del dict_S2H_ReachedImprovedObject["improvedGeneralObjClass"]

    #Faz a inserção da mesma CLASSE de objeto acima, e adiciona um valor para ela.
    if improvedGeneralObjClass not in subdict.keys():
        aux1 ={improvedGeneralObjClass: 1}
        subdict.update(aux1)
    else:
        val1 = subdict[improvedGeneralObjClass]
        val1 += 1
        obj = {improvedGeneralObjClass: val1}
        subdict.update(obj)

    dict_S2H_ReachedImprovedObject["improvedGeneralObjClass"] = {}
    dict_S2H_ReachedImprovedObject["improvedGeneralObjClass"] = subdict


    if len(implementedSpecificObjPlaceVet) == 2:
        objClass = implementedSpecificObjPlaceVet[0]
        objSpecific = implementedSpecificObjPlaceVet[1]
    else:
        objClass = implementedSpecificObjPlaceVet[0]
        objSpecific = "WithoutClass"
        print(title)
        print(title)

#----------------------------------------------implementedSpecificObjPlace----------------------------------------------
    # Faz a inserção da SPECIFIC OBJECT
    if "implementedSpecificObjPlace" not in dict_S2H_ReachedImprovedObject.keys():
        first = {}
        dict_S2H_ReachedImprovedObject["implementedSpecificObjPlace"] = first

    subdict = dict_S2H_ReachedImprovedObject["implementedSpecificObjPlace"]
    del dict_S2H_ReachedImprovedObject["implementedSpecificObjPlace"]


    # Verifica se a classe de objeto está no dicionario
    if objClass not in subdict.keys():
        first = {}
        subdict[objClass] = first

    # faz BKP do VALUE do dicionario
    subsubdict = subdict[objClass]
    del subdict[objClass]

    # Adiciona tanto a classe quanto sua especificação no mesmo nível do subsub dict ----  {'SIMULATOR': {'SIMULATOR': 1, 'PCMSIM': 1}} ----
    #                                                                                         subdict       subsubdict dictionary
    if objClass not in subsubdict.keys():
        aux1 = {objClass: 1}
        subsubdict.update(aux1)
    else:
        val1 = subsubdict[objClass]
        val1 += 1
        obj = {objClass: val1}
        subsubdict.update(obj)
    # Faz a inserção da mesma SPECIFIC OBJECT de objeto acima, e adiciona um valor para ela.
    if objSpecific not in subsubdict.keys():
        aux2 = {objSpecific: 1}
        subsubdict.update(aux2)
    else:
        val2 = subsubdict[objSpecific]
        val2 += 1
        obj = {objSpecific: val2}
        subsubdict.update(obj)

    subdict[objClass] = {}
    subdict[objClass] = subsubdict

    dict_S2H_ReachedImprovedObject["implementedSpecificObjPlace"] = subdict

#------------------------------------------------deviceClas and deviceSpecific -----------------------------------------

    #if implementedSpecificObjPlaceVet == "GENERAL-HARDWARE":
        #print(title)
        #print(title)
    #print(deviceSpecific)

    if "deviceClass" not in dict_S2H_ReachedImprovedObject.keys():
       first = {}
       dict_S2H_ReachedImprovedObject["deviceClass"] = first

    subdict = dict_S2H_ReachedImprovedObject["deviceClass"]
    del dict_S2H_ReachedImprovedObject["deviceClass"]

    # Verifica se a classe de objeto está no dicionario
    if deviceClass not in subdict.keys():
        first = {}
        subdict[deviceClass] = first

    # faz BKP do VALUE do dicionario
    subsubdict = subdict[deviceClass]
    del subdict[deviceClass]

    if deviceClass not in subsubdict.keys():
       aux1 = {deviceClass: 1}
       subsubdict.update(aux1)
    else:
       val1 = subsubdict[deviceClass]
       val1 += 1
       obj = {deviceClass: val1}
       subsubdict.update(obj)

    for deviceSpecific in deviceSpecific:
        if deviceSpecific not in subsubdict.keys():
           aux2 = {deviceSpecific: 1}
           subsubdict.update(aux2)
        else:
           val2 = subsubdict[deviceSpecific]
           val2 += 1
           obj = {deviceSpecific: val2}
           subsubdict.update(obj)

    subdict[deviceClass] = {}
    subdict[deviceClass] = subsubdict
    dict_S2H_ReachedImprovedObject["deviceClass"] = subdict
def printDict_S2H_improvedObject():
    #[(PGC)] - [SSD[simulator(MSRsim)][sd(MSRsim)]] - [SSD]
    #[garbage collector] - [N] - [SPC(Financial) & Cello & TPC(TPC - H) & OpenMail]

    for element, subdict_S2H_ReachedImprovedObject in dict_S2H_ReachedImprovedObject.items():
        improvedGeneralObjClass = []
        improvedGeneralObjClassQtd = []
        improvedSpecificObjPlace = []
        improvedSpecificObjPlaceQtd = []


        if element == "improvedGeneralObjClass":
            colors = []
            plt.rcParams['font.size'] = 7
            for impGeneralObjClass, classQtd in subdict_S2H_ReachedImprovedObject.items():
                improvedGeneralObjClass.append(impGeneralObjClass)
                improvedGeneralObjClassQtd.append(classQtd)
                if impGeneralObjClass == "FLASH MEMORY":
                    colors.append("pink")
                elif impGeneralObjClass == "SPM":
                    colors.append("deeppink")
                elif impGeneralObjClass == "SSD":
                    colors.append("red")
                elif impGeneralObjClass == "FLASH":
                    colors.append("pink")
                elif impGeneralObjClass == "SCM":
                    colors.append("tomato")
                elif impGeneralObjClass == "DRAM-SSD":
                    colors.append("darkviolet")
                elif impGeneralObjClass == "XILINX ZYNQ":
                    colors.append("cornflowerblue")
                elif impGeneralObjClass == "GPU":
                    colors.append("purple")
                elif impGeneralObjClass == "NVM":
                    colors.append("yellow")
                elif impGeneralObjClass == "PCM":
                    colors.append("gold")
                elif impGeneralObjClass == "SCRATCHPAD MEMORY":
                    colors.append("black")
                elif impGeneralObjClass == "MEMORY":
                    colors.append("blue")
                elif impGeneralObjClass == "HDD":
                    colors.append("green")
                elif impGeneralObjClass == "DRAM":
                    colors.append("blue")
                elif impGeneralObjClass == "H-SMR":
                    colors.append("grey")
                elif impGeneralObjClass == "OSD":
                    colors.append("orange")


            plt.rcParams.update({'font.size': 15.0})
            fig1, ax1 = plt.subplots(figsize=(9,9))
            ax1.pie(improvedGeneralObjClassQtd, colors=colors, autopct='%1.1f%%', pctdistance=0.9, radius=1,
                    counterclock=False, wedgeprops=dict(width=1.0, edgecolor='white'),
                    shadow=True, startangle=10,  labeldistance=1.05)  # , wedgeprops = { 'linewidth': 1, "edgecolor" :"k" })
            plt.legend(labels=improvedGeneralObjClass, bbox_to_anchor=(1, 0), prop={'size': 10}, loc="lower right",
                       bbox_transform=plt.gcf().transFigure)

            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            #ax1.set_title('Accepted Papers Grouped by Selection Criteria')
            plt.title('S2H - Improved Device')
            title = 'S2HImprovedDevice'
            plt.tight_layout()
            var = "{}/12printDictS2HimprovedObject" + title + ".png"
            subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/12printDictS2HimprovedObject", shell=True)
            plt.savefig(var.format(results_dir + "/12printDictS2HimprovedObject"))
            plt.show()

        #-----------------------------------------------------------------------

        if element == "implementedSpecificObjPlace":
            plt.rcParams['font.size'] = 7
            for impGeneralObjClass, especificObjs in subdict_S2H_ReachedImprovedObject.items():
                improvedGeneralObjClass.append(impGeneralObjClass)
                for impGenObjCla, impGenObjClaQtd in especificObjs.items():
                    if impGenObjCla == impGeneralObjClass:
                        improvedGeneralObjClassQtd.append(impGenObjClaQtd)
                    else:
                        improvedSpecificObjPlace.append(impGenObjCla)
                        improvedSpecificObjPlaceQtd.append(impGenObjClaQtd)
            # plt.pie([1, 1, 1, 1, 1, 1, 1], radius=1, colors=colors, labels=labels, pctdistance=0.85, shadow=True, labeldistance=0.99, wedgeprops=dict(width=0.3, edgecolor='white'), startangle=40)

            plt.rcParams.update({'font.size': 11.0})
            plt.subplots(figsize=(11,9))
            plt.pie(improvedGeneralObjClassQtd, radius=1, labels=improvedGeneralObjClass, pctdistance=0.94, labeldistance=0.99, shadow=True,
                    autopct='%.2f%%', wedgeprops=dict(width=0.3, edgecolor='white'), startangle=180)
            plt.rcParams.update({'font.size': 7.0})
            patches, texts = plt.pie(improvedSpecificObjPlaceQtd, radius=0.7, labels=improvedSpecificObjPlace, rotatelabels=270,
                                     wedgeprops=dict(width=0.3, edgecolor='white'), pctdistance=5, labeldistance=0.8,
                                     shadow=True, startangle=180,
                                     textprops=dict(rotation_mode='anchor', va='center', ha='left'))
            join = []
            plt.rcParams.update({'font.size': 10.0})
            for t in texts:
                t.set_horizontalalignment('center')
            for a, b in zip(improvedGeneralObjClass, improvedGeneralObjClassQtd):
                join.append(str(a) + " =" + str(b))
            for a, b in zip(improvedSpecificObjPlace, improvedSpecificObjPlaceQtd):
                join.append(str(a) + " =" + str(b))
            plt.legend(labels=join, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 7},
                       bbox_transform=plt.gcf().transFigure)#, title="Power Concerning")
            plt.axis('equal')
            plt.title('S2H - Implemented Object')
            title = 'S2HImplementedObject'
            plt.tight_layout()
            var = "{}/12printDictS2HimprovedObject" + title + ".png"
            subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/12printDictS2HimprovedObject",
                            shell=True)
            plt.savefig(var.format(results_dir + "/12printDictS2HimprovedObject"))
            plt.show()

        if element == "deviceClass":
            print("printando o subdict pra ver se está certo",subdict_S2H_ReachedImprovedObject)
            #These code below corrects the dictionary because we were surprised by the new devices included into the vector. To correct and separate the devices these code is necessary.
            dictdeviceUpdate = {}
            subdictdeviceUpdate = {}
            totalClaSum = 0
            for impGeneralObjClass, especificObjs in subdict_S2H_ReachedImprovedObject.items():
                for impGenObjCla, impGenObjClaQtd in especificObjs.items():             #if é igual  //  if contem "_" se tiver somar um no total e dividir os elementos e cadd ao novo dicionario
                    if "_" in impGenObjCla:
                        # devo dividir os elementos
                        impGenObjClas = impGenObjCla.split('_')
                        print(impGenObjClas, len(impGenObjClas), "x", impGenObjClaQtd )
                        #todos os elementos divididos vão receber a quantidade impGenObjClaQtd
                        for i in range(impGenObjClaQtd):
                            for el in impGenObjClas:
                                #verificar se o elemento existe no dicionario se existir, atualiza o value, se não existir, crie com o numero 1
                                if el not in subdictdeviceUpdate.keys():
                                    aux1 = {el: impGenObjClaQtd}
                                    subdictdeviceUpdate.update(aux1)
                                else:
                                    val1 = subdictdeviceUpdate[el]
                                    val1 += 1
                                    obj = {el: val1}
                                    subdictdeviceUpdate.update(obj)
                        #print(impGenObjClas, len(impGenObjClas))
                        totalClaSum += (len(impGenObjClas) * impGenObjClaQtd)  - ( 1 * impGenObjClaQtd)
                    elif "_" not in impGenObjCla and impGenObjCla != impGeneralObjClass and impGenObjCla != "NOT FOUND":
                        if impGenObjCla not in subdictdeviceUpdate.keys():
                            aux1 = {impGenObjCla: impGenObjClaQtd}
                            subdictdeviceUpdate.update(aux1)
                        else:
                            val1 = subdictdeviceUpdate[impGenObjCla]
                            val1 += impGenObjClaQtd
                            obj = {impGenObjCla: val1}
                            subdictdeviceUpdate.update(obj)
                    elif impGenObjCla == "NOT FOUND":
                        if impGenObjCla not in subdictdeviceUpdate.keys():
                            aux1 = {impGenObjCla: impGenObjClaQtd}
                            subdictdeviceUpdate.update(aux1)
                #atualiza a quantidade total de elementos da classe, isso é necessario pq um objeto X_Z de tamanho 1 deve se transformar em dois objetos de tamanho 1, X e Z.
                for impGenObjCla, impGenObjClaQtd in especificObjs.items():
                    if impGenObjCla == impGeneralObjClass:
                        totalClaSum += impGenObjClaQtd
                        obj = {impGenObjCla:totalClaSum}
                        subdictdeviceUpdate.update(obj)
                dictdeviceUpdate[impGeneralObjClass]= subdictdeviceUpdate
                subdictdeviceUpdate ={}
                totalClaSum = 0

            #Agora devo fazer o processo de inserção com o novo dicionario DICTDEVICEUPDATE.
            improvedGeneralObjClass = []
            improvedGeneralObjClassQtd = []
            improvedSpecificObjPlace = []
            improvedSpecificObjPlaceQtd = []

            plt.rcParams['font.size'] = 7
            for impGeneralObjClass, especificObjs in dictdeviceUpdate.items():
                improvedGeneralObjClass.append(impGeneralObjClass)
                for impGenObjCla, impGenObjClaQtd in especificObjs.items():
                    if impGenObjCla == impGeneralObjClass:
                        improvedGeneralObjClassQtd.append(impGenObjClaQtd)
                    else:
                        improvedSpecificObjPlace.append(impGenObjCla)
                        improvedSpecificObjPlaceQtd.append(impGenObjClaQtd)

            plt.rcParams.update({'font.size': 11.0})
            plt.subplots(figsize=(11,9))
            plt.pie(improvedGeneralObjClassQtd, radius=1, labels=improvedGeneralObjClass, pctdistance=0.98, shadow=True, labeldistance=0.85 , autopct='%.2f%%', wedgeprops=dict(width=0.3, edgecolor='white'), startangle=180)
            plt.rcParams.update({'font.size': 7.0})
            patches, texts = plt.pie(improvedSpecificObjPlaceQtd, radius=0.8, labels=improvedSpecificObjPlace,
                                     rotatelabels=270,
                                     wedgeprops=dict(width=0.3, edgecolor='white'), pctdistance=5, labeldistance=0.8,
                                     shadow=True, startangle=180,
                                     textprops=dict(rotation_mode='anchor', va='center', ha='left'))

            join = []
            plt.rcParams.update({'font.size': 10.0})
            for t in texts:
                t.set_horizontalalignment('center')
            for a, b in zip(improvedGeneralObjClass, improvedGeneralObjClassQtd):
                join.append(str(a) + " =" + str(b))
            for a, b in zip(improvedSpecificObjPlace, improvedSpecificObjPlaceQtd):
                join.append(str(a) + " =" + str(b))

            # verify if wxists the string "_" into the keys, if exists we shoud split and update the keys values into the dicts
            plt.legend(labels=join, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 6},
                       bbox_transform=plt.gcf().transFigure)#, title="Power Concerning")
            plt.axis('equal')
            plt.title('S2H - Class Of Experimented Device on the Evaluation Process')
            title = 'S2HClassOfExperimentedDeviceonEvaluationProcess'
            plt.tight_layout()
            var = "{}/12printDictS2HimprovedObject" + title + ".png"
            subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/12printDictS2HimprovedObject",
                            shell=True)
            plt.savefig(var.format(results_dir + "/12printDictS2HimprovedObject"))
            plt.show()

def ExtractS2SSDevices(improvedObject):
    StorageDomainVet = []
    implementedSpecificObjPlaceVet = []
    EnvironmentVet = []

    object = improvedObject.upper()
    object = re.split('; |, |\*|[[]', object)

    if "-" in object[0]:
        StorageDomainAUX= object[0]
        StorageDomainAUX = StorageDomainAUX.split('-')
    else:
        StorageDomainAUX = object[0]


    if type(StorageDomainAUX) == list:
        for i in StorageDomainAUX:
            aux = CleanVariable(i)
            StorageDomainVet.append(aux)
    else:
        StorageDomainVet.append(CleanVariable(StorageDomainAUX))
    del StorageDomainAUX


    implementedSpecificObjPlaceAUX = object[1]
    implementedSpecificObjPlaceAUX = re.split('; |, |\*|[(]', implementedSpecificObjPlaceAUX)
    for i in implementedSpecificObjPlaceAUX:
        aux = CleanVariable(i)
        implementedSpecificObjPlaceVet.append(aux)
    del implementedSpecificObjPlaceAUX


    EnvironmentAUX = object[2]
    if "&" in EnvironmentAUX:
        EnvironmentAUX = EnvironmentAUX.split('&')
        for element in EnvironmentAUX:
            element = re.split('; |, |\*|[(]', element)
            EnvironmentVet.append(element)
    else:
        EnvironmentAUX = re.split('; |, |\*|[(]', EnvironmentAUX)
        for i in EnvironmentAUX:
            aux = CleanVariable(i)
            EnvironmentVet.append(aux)
        del EnvironmentAUX

    CreateDict_S2SS_improvedObject(StorageDomainVet, implementedSpecificObjPlaceVet, EnvironmentVet)
def CreateDict_S2SS_improvedObject(StorageDomainVet, implementedSpecificObjPlaceVet, EnvironmentVet):
    #['STORAGE SYSTEM', 'RAID'] ['EMULATOR', 'MICROSOFTSSDSIM'] ['SSEE', 'MICROSOFTSSDSIM']
    #['HPC'] ['NF', 'NOT FOUND'] ['RHEE', '1C_64N']

    # improvedGeneralObjClass -> STORAGE System
    # implementedSpecificObjPlaceVet -> [simulator, SSDsim]
    # deviceClass -> RD or SD
    # deviceSpecific

    # Verifica se a classe de objeto está no dicionario
    if "improvedGeneralObjClass" not in dict_S2SS_ReachedImprovedObject.keys():
        first = {}
        dict_S2SS_ReachedImprovedObject["improvedGeneralObjClass"] = first

    # faz BKP do VALUE do dicionario
    subdict = dict_S2SS_ReachedImprovedObject["improvedGeneralObjClass"]
    del dict_S2SS_ReachedImprovedObject["improvedGeneralObjClass"]

    # Faz a inserção da mesma CLASSE de objeto acima, e adiciona um valor para ela.
    for StorageDomain in StorageDomainVet:
        if StorageDomain not in subdict.keys():
            aux1 = {StorageDomain: 1}
            subdict.update(aux1)
        else:
            val1 = subdict[StorageDomain]
            val1 += 1
            obj = {StorageDomain: val1}
            subdict.update(obj)

    dict_S2SS_ReachedImprovedObject["improvedGeneralObjClass"] = {}
    dict_S2SS_ReachedImprovedObject["improvedGeneralObjClass"] = subdict

#--------------------------------------------------------------------------------
# Faz a inserção da SPECIFIC OBJECT
    if "implementedSpecificObjPlace" not in dict_S2SS_ReachedImprovedObject.keys():
        first = {}
        dict_S2SS_ReachedImprovedObject["implementedSpecificObjPlace"] = first

    subdict = dict_S2SS_ReachedImprovedObject["implementedSpecificObjPlace"]
    del dict_S2SS_ReachedImprovedObject["implementedSpecificObjPlace"]


    objClass = implementedSpecificObjPlaceVet[0]
    objSpecific = implementedSpecificObjPlaceVet[1]

    if "2C_9N_16N" in EnvironmentVet:
        print(title)
        print(title)


    # Verifica se a classe de objeto está no dicionario
    if objClass not in subdict.keys():
        first = {}
        subdict[objClass] = first

    # faz BKP do VALUE do dicionario
    subsubdict = subdict[objClass]
    del subdict[objClass]

    # Adiciona tanto a classe quanto sua especificação no mesmo nível do subsub dict ----  {'SIMULATOR': {'SIMULATOR': 1, 'PCMSIM': 1}} ----
    #                                                                                         subdict       subsubdict dictionary
    if objClass not in subsubdict.keys():
        aux1 = {objClass: 1}
        subsubdict.update(aux1)
    else:
        val1 = subsubdict[objClass]
        val1 += 1
        obj = {objClass: val1}
        subsubdict.update(obj)
    # Faz a inserção da mesma SPECIFIC OBJECT de objeto acima, e adiciona um valor para ela.
    if objSpecific not in subsubdict.keys():
        aux2 = {objSpecific: 1}
        subsubdict.update(aux2)
    else:
        val2 = subsubdict[objSpecific]
        val2 += 1
        obj = {objSpecific: val2}
        subsubdict.update(obj)

    subdict[objClass] = {}
    subdict[objClass] = subsubdict

    dict_S2SS_ReachedImprovedObject["implementedSpecificObjPlace"] = subdict


#----------------------------------------------------------------
#faz o Environment
    deviceSpecifics = []
    deviceClass =""
    t = EnvironmentVet[0]
    if type(t) == str:
        deviceClass = EnvironmentVet[0]
        deviceClass =CleanVariable(deviceClass)
        deviceSpecifics = EnvironmentVet[1:]
    else:
        for vet in EnvironmentVet:
            for i in vet:
                if "EE" in i:
                    deviceClass = i
                    deviceClass = CleanVariable(deviceClass)
                elif "EE" not in i:
                    i = CleanVariable(i)
                    deviceSpecifics.append(i)

    # Verifica se a classe de objeto está no dicionario
    if "deviceClass" not in dict_S2SS_ReachedImprovedObject.keys():
        first = {}
        dict_S2SS_ReachedImprovedObject["deviceClass"] = first

    subdict = dict_S2SS_ReachedImprovedObject["deviceClass"]
    del dict_S2SS_ReachedImprovedObject["deviceClass"]

    # Verifica se a classe de objeto está no dicionario
    if deviceClass not in subdict.keys():
        first = {}
        subdict[deviceClass] = first

    # faz BKP do VALUE do dicionario
    subsubdict = subdict[deviceClass]
    del subdict[deviceClass]

    if deviceClass not in subsubdict.keys():
        aux1 = {deviceClass: 1}
        subsubdict.update(aux1)
    else:
        val1 = subsubdict[deviceClass]
        val1 += 1
        obj = {deviceClass: val1}
        subsubdict.update(obj)

    for deviceSpecific in deviceSpecifics:
        if deviceSpecific not in subsubdict.keys():
            aux2 = {deviceSpecific: 1}
            subsubdict.update(aux2)
        else:
            val2 = subsubdict[deviceSpecific]
            val2 += 1
            obj = {deviceSpecific: val2}
            subsubdict.update(obj)

    subdict[deviceClass] = {}
    subdict[deviceClass] = subsubdict
    dict_S2SS_ReachedImprovedObject["deviceClass"] = subdict
def printDict_S2SS_improvedObject():
    print(dict_S2SS_ReachedImprovedObject)
    for element, subdict_S2SS_ReachedImprovedObject in dict_S2SS_ReachedImprovedObject.items():
        improvedGeneralObjClass = []
        improvedGeneralObjClassQtd = []
        improvedSpecificObjPlace = []
        improvedSpecificObjPlaceQtd = []

        if element == "improvedGeneralObjClass":
            plt.rcParams['font.size'] = 7
            for impGeneralObjClass, classQtd in subdict_S2SS_ReachedImprovedObject.items():
                improvedGeneralObjClass.append(impGeneralObjClass)
                improvedGeneralObjClassQtd.append(classQtd)

            plt.rcParams.update({'font.size': 10.0})
            fig1, ax1 = plt.subplots(figsize=(9,9))
            ax1.pie(improvedGeneralObjClassQtd, autopct='%1.1f%%', pctdistance=0.9, radius=1,
                    counterclock=False, wedgeprops=dict(width=0.5, edgecolor='white'),
                    shadow=True, startangle=10, labeldistance=1.05)
            plt.legend(labels=improvedGeneralObjClass, bbox_to_anchor=(1, 0), prop={'size': 10}, loc="lower right", bbox_transform=plt.gcf().transFigure)


            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            ax1.set_title('S2SS - Improved General Object Class(NÂO USAR)')
            title = "S2SSImprovedGeneralObjectClass"
            plt.tight_layout()
            var = "{}/13printDictS2SSimprovedObject" + title + ".png"
            subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/13printDictS2SSimprovedObject",
                            shell=True)
            plt.savefig(var.format(results_dir + "/13printDictS2SSimprovedObject"))
            plt.show()

    #-------------------------------------------------------------------------------------------------
        if element == "implementedSpecificObjPlace":
            # Agora devo fazer o processo de inserção com o novo dicionario DICTDEVICEUPDATE.
            improvedGeneralObjClass = []
            improvedGeneralObjClassQtd = []
            improvedSpecificObjPlace = []
            improvedSpecificObjPlaceQtd = []

            plt.rcParams['font.size'] = 7
            for impGeneralObjClass, especificObjs in subdict_S2SS_ReachedImprovedObject.items():
                improvedGeneralObjClass.append(impGeneralObjClass)
                for impGenObjCla, impGenObjClaQtd in especificObjs.items():
                    if impGenObjCla == impGeneralObjClass:
                        improvedGeneralObjClassQtd.append(impGenObjClaQtd)
                    else:
                        improvedSpecificObjPlace.append(impGenObjCla)
                        improvedSpecificObjPlaceQtd.append(impGenObjClaQtd)

            plt.rcParams.update({'font.size': 11.0})
            plt.subplots(figsize=(11, 10))
            plt.pie(improvedGeneralObjClassQtd, radius=1, labels=improvedGeneralObjClass, pctdistance=0.92, labeldistance=0.99, shadow=True,autopct='%.2f%%', wedgeprops=dict(width=0.3, edgecolor='white'), startangle=180)
            plt.rcParams.update({'font.size': 7.0})
            patches, texts = plt.pie(improvedSpecificObjPlaceQtd, radius=0.9, labels=improvedSpecificObjPlace, rotatelabels=270, wedgeprops=dict(width=0.3, edgecolor='white'),
                                     pctdistance=5, labeldistance=0.8,shadow=True, startangle=180, textprops=dict(rotation_mode='anchor', va='center', ha='left'))
            join = []
            for t in texts:
                t.set_horizontalalignment('center')
            for a, b in zip(improvedGeneralObjClass, improvedGeneralObjClassQtd):
                join.append(str(a) + " =" + str(b))
            for a, b in zip(improvedSpecificObjPlace, improvedSpecificObjPlaceQtd):
                join.append(str(a) + " =" + str(b))

            plt.rcParams.update({'font.size': 11.0})
            plt.legend(labels=join, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 5.5},
                       bbox_transform=plt.gcf().transFigure, title="Object Value")
            plt.axis('equal')
            plt.title('S2SS - Implemented Specific Object Place')
            title = "S2SSImplementedSpecificObjectPlace"
            plt.tight_layout()
            var = "{}/13printDictS2SSimprovedObject" + title + ".png"
            subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/13printDictS2SSimprovedObject",
                            shell=True)
            plt.savefig(var.format(results_dir + "/13printDictS2SSimprovedObject"))
            plt.show()

    #-----------------------------------------------------------------------------------------------------------
        if element == "deviceClass":
            # Agora devo fazer o processo de inserção com o novo dicionario DICTDEVICEUPDATE.
            improvedGeneralObjClass = []
            improvedGeneralObjClassQtd = []
            improvedSpecificObjPlace = []
            improvedSpecificObjPlaceQtd = []
            # plt.pie([1, 1, 1, 1, 1, 1, 1], radius=1, colors=colors, labels=labels, pctdistance=0.85, shadow=True, labeldistance=0.99, wedgeprops=dict(width=0.3, edgecolor='white'), startangle=40)
            plt.rcParams['font.size'] = 7
            for impGeneralObjClass, especificObjs in subdict_S2SS_ReachedImprovedObject.items():
                improvedGeneralObjClass.append(impGeneralObjClass)
                for impGenObjCla, impGenObjClaQtd in especificObjs.items():
                    if impGenObjCla == impGeneralObjClass:
                        improvedGeneralObjClassQtd.append(impGenObjClaQtd)
                    else:
                        improvedSpecificObjPlace.append(impGenObjCla)
                        improvedSpecificObjPlaceQtd.append(impGenObjClaQtd)

            labels = improvedGeneralObjClass
            qtdLabels = improvedGeneralObjClassQtd
            plt.rcParams.update({'font.size': 15.0})
            fig1, ax1 = plt.subplots(figsize=(9,9))
            ax1.pie(qtdLabels, autopct='%1.1f%%', shadow=True, startangle=270, wedgeprops=dict(width=0.5, edgecolor='white'))
            plt.legend(labels=labels, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 13}, bbox_transform=plt.gcf().transFigure, title="Improved Class")
            ax1.axis('equal')
            plt.title('S2SS - Class of Used Environment on the Experimentation')
            title = "S2SSClassofUsedEnvironmentontheExperimentation"
            plt.tight_layout()
            var = "{}/13printDictS2SSimprovedObject" + title + ".png"
            subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/13printDictS2SSimprovedObject",
                            shell=True)
            plt.savefig(var.format(results_dir + "/13printDictS2SSimprovedObject"))
            plt.show()

            for impGeneralObjClass, especificObjs in subdict_S2SS_ReachedImprovedObject.items():
                improvedSpecificObjPlace = []
                improvedSpecificObjPlaceQtd = []
                Classe = ""
                if impGeneralObjClass != "NF":
                    Classe = impGeneralObjClass
                    for impGenObjCla, impGenObjClaQtd in especificObjs.items():
                        if impGenObjCla != impGeneralObjClass:
                            improvedSpecificObjPlace.append(impGenObjCla)
                            improvedSpecificObjPlaceQtd.append(impGenObjClaQtd)

                    labels = improvedSpecificObjPlace
                    qtdLabels = improvedSpecificObjPlaceQtd
                    fig1, ax1 = plt.subplots(figsize=(14,10))
                    ax1.pie(qtdLabels, autopct='%1.1f%%', labels=labels, shadow=True, startangle=270, pctdistance=0.90, labeldistance=1, wedgeprops=dict(width=0.5, edgecolor='white'))  # explode=explode,
                    plt.legend(labels=labels, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 11},
                               bbox_transform=plt.gcf().transFigure, title="Improved Class")
                    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                    plt.title("S2SS - " + Classe + " Environments Used on the Experimentation")
                    title = "S2SS"+Classe+"EnvironmentsUsedonEvaluations"
                    plt.tight_layout()
                    var = "{}/13printDictS2SSimprovedObject" + title + ".png"
                    subprocess.call(
                        "mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/13printDictS2SSimprovedObject",
                        shell=True)
                    plt.savefig(var.format(results_dir + "/13printDictS2SSimprovedObject"))
                    plt.show()


                    labels = improvedSpecificObjPlace
                    qtdLabels = improvedSpecificObjPlaceQtd
                    y_pos = np.arange(len(labels))
                    fig1, ax1 = plt.subplots(figsize=(13, 10))
                    plt.bar(y_pos, qtdLabels, align='center', alpha=0.5)
                    plt.xticks(y_pos, labels, rotation=85, ha='center', size=11)
                    for i, v in enumerate(qtdLabels):
                        plt.text(i, v, str(v), color='black', size=8, ha='center')

                    sb.barplot(x=labels, y=qtdLabels)
                    plt.tight_layout()
                    ax1.xaxis.label.set_size(200)
                    plt.xlabel(Classe+" Objects", fontsize=12)
                    plt.ylabel('Quantity', fontsize=12)
                    title = "S2SS" + Classe + "UsedEnvironmentOP02"
                    plt.tight_layout()
                    var = "{}/13printDictS2SSimprovedObject" + title + ".png"
                    subprocess.call(
                        "mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/13printDictS2SSimprovedObject",
                        shell=True)
                    plt.savefig(var.format(results_dir + "/13printDictS2SSimprovedObject"))
                    plt.show()


def ExtractARCH(improvedObject):
    StorageDomainVet = []
    EnvironmentVet = []

    if title == "WHOBBS: An Object-Based Distributed Hybrid Storage Providing Block Storage for Virtual Machines":
        print("wait")
        print("wait")
    object = improvedObject.upper()
    object = re.split('; |, |\*|[[]', object)

    StorageDomainAUX = object[0]
    StorageDomainAUX = StorageDomainAUX.split('&')
    if type(StorageDomainAUX) == list:
        for i in StorageDomainAUX:
            aux = CleanVariable(i)
            StorageDomainVet.append(aux)
    else:
        StorageDomainVet.append(CleanVariable(StorageDomainAUX))
    del StorageDomainAUX


    EnvironmentAUX = object[1]
    if "&" in EnvironmentAUX:
        EnvironmentAUX = EnvironmentAUX.split('&')
        for element in EnvironmentAUX:
            element = re.split('; |, |\*|[(]', element)
            EnvironmentVet.append(element)
    else:
        EnvironmentAUX = re.split('; |, |\*|[(]', EnvironmentAUX)
        for i in EnvironmentAUX:
            aux = CleanVariable(i)
            EnvironmentVet.append(aux)
        del EnvironmentAUX

    CreateDict_ARCH_improvedObject(StorageDomainVet, EnvironmentVet)
def CreateDict_ARCH_improvedObject(StorageDomainVet, EnvironmentVet):
    # Verifica se a classe de objeto está no dicionario
    if "StorageDomain" not in dict_ARCH_improvedObject.keys():
        first = {}
        dict_ARCH_improvedObject["StorageDomain"] = first

    # faz BKP do VALUE do dicionario
    subdict = dict_ARCH_improvedObject["StorageDomain"]
    del dict_ARCH_improvedObject["StorageDomain"]

    # Faz a inserção da mesma CLASSE de objeto acima, e adiciona um valor para ela.
    for StorageDomain in StorageDomainVet:
        if StorageDomain not in subdict.keys():
            aux1 = {StorageDomain: 1}
            subdict.update(aux1)
        else:
            val1 = subdict[StorageDomain]
            val1 += 1
            obj = {StorageDomain: val1}
            subdict.update(obj)

    dict_ARCH_improvedObject["StorageDomain"] = {}
    dict_ARCH_improvedObject["StorageDomain"] = subdict

    # ----------------------------------------------------------------
    # faz o Environment
    deviceSpecifics = []
    deviceClass = ""
    t = EnvironmentVet[0]
    if type(t) == str:
        deviceClass = EnvironmentVet[0]
        deviceClass = CleanVariable(deviceClass)
        deviceSpecifics = EnvironmentVet[1:]
    else:
        for vet in EnvironmentVet:
            for i in vet:
                if "EE" in i:
                    deviceClass = i
                    deviceClass = CleanVariable(deviceClass)
                elif "EE" not in i:
                    i = CleanVariable(i)
                    deviceSpecifics.append(i)

    #if "1D1SD" in deviceSpecifics:
        #print(title)
        #print(title)
    # Verifica se a classe de objeto está no dicionario
    if "deviceClass" not in dict_ARCH_improvedObject.keys():
        first = {}
        dict_ARCH_improvedObject["deviceClass"] = first

    subdict = dict_ARCH_improvedObject["deviceClass"]
    del dict_ARCH_improvedObject["deviceClass"]

    # Verifica se a classe de objeto está no dicionario
    if deviceClass not in subdict.keys():
        first = {}
        subdict[deviceClass] = first

    # faz BKP do VALUE do dicionario
    subsubdict = subdict[deviceClass]
    del subdict[deviceClass]

    if deviceClass not in subsubdict.keys():
        aux1 = {deviceClass: 1}
        subsubdict.update(aux1)
    else:
        val1 = subsubdict[deviceClass]
        val1 += 1
        obj = {deviceClass: val1}
        subsubdict.update(obj)

    for deviceSpecific in deviceSpecifics:
        if deviceSpecific not in subsubdict.keys():
            aux2 = {deviceSpecific: 1}
            subsubdict.update(aux2)
        else:
            val2 = subsubdict[deviceSpecific]
            val2 += 1
            obj = {deviceSpecific: val2}
            subsubdict.update(obj)

    subdict[deviceClass] = {}
    subdict[deviceClass] = subsubdict
    dict_ARCH_improvedObject["deviceClass"] = subdict
def printDict_ARCH_improvedObject():
    for element, subdict_ARCH_improvedObject in dict_ARCH_improvedObject.items():
        improvedGeneralObjClass = []
        improvedGeneralObjClassQtd = []

        if element == "StorageDomain":
            plt.rcParams.update({'font.size': 15.0})
            for impGeneralObjClass, classQtd in subdict_ARCH_improvedObject.items():
                improvedGeneralObjClass.append(impGeneralObjClass)
                improvedGeneralObjClassQtd.append(classQtd)

            fig1, ax1 = plt.subplots(figsize=(10, 10))
            ax1.pie(improvedGeneralObjClassQtd, autopct='%1.1f%%', pctdistance=0.9, radius=1,
                    counterclock=False, wedgeprops=dict(width=0.5, edgecolor='white'),
                    shadow=True, startangle=10, labeldistance=1.05)
            plt.legend(labels=improvedGeneralObjClass, bbox_to_anchor=(1, 0), prop={'size': 13}, loc="lower right",
                       bbox_transform=plt.gcf().transFigure)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            ax1.set_title('Architecture Storage Domain')
            title = "ArchitectureStorageDomain"
            plt.tight_layout()
            var = "{}/printDictARCHStorageDomain" + title + ".png"
            subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/ARCH", shell=True)
            plt.savefig(var.format(results_dir + "/ARCH"))
            plt.show()

        # -----------------------------------------------------------------------------------------------------------
        if element == "deviceClass":
            # Agora devo fazer o processo de inserção com o novo dicionario DICTDEVICEUPDATE.
            improvedGeneralObjClass = []
            improvedGeneralObjClassQtd = []
            improvedSpecificObjPlace = []
            improvedSpecificObjPlaceQtd = []


            for impGeneralObjClass, especificObjs in subdict_ARCH_improvedObject.items():
                improvedGeneralObjClass.append(impGeneralObjClass)
                for impGenObjCla, impGenObjClaQtd in especificObjs.items():
                    if impGenObjCla == impGeneralObjClass:
                        improvedGeneralObjClassQtd.append(impGenObjClaQtd)
                    else:
                        improvedSpecificObjPlace.append(impGenObjCla)
                        improvedSpecificObjPlaceQtd.append(impGenObjClaQtd)
            labels = improvedGeneralObjClass
            qtdLabels = improvedGeneralObjClassQtd
            plt.rcParams.update({'font.size': 15.0})
            fig1, ax1 = plt.subplots(figsize=(10,10))
            ax1.pie(qtdLabels, autopct='%1.1f%%', shadow=True, startangle=270,  # colors=colors,# explode=explode,
                    wedgeprops=dict(width=0.5, edgecolor='white'))  # explode=explode,
            plt.legend(labels=labels, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 15},
                       bbox_transform=plt.gcf().transFigure)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.title('Architecture - Environment Class Used on the Experimentation')
            plt.tight_layout()
            title = "ArchtectureClassEnvironment"
            var = "{}/printDictARCHEnvironment" + title + ".png"
            subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/ARCH", shell=True)
            plt.savefig(var.format(results_dir + "/ARCH"))
            plt.show()

            #plt.pie([1, 1, 1, 1, 1, 1, 1], radius=1, colors=colors, labels=labels, pctdistance=0.85, shadow=True, labeldistance=0.99, wedgeprops=dict(width=0.3, edgecolor='white'), startangle=40)

            for impGeneralObjClass, especificObjs in subdict_ARCH_improvedObject.items():
                improvedSpecificObjPlace = []
                improvedSpecificObjPlaceQtd = []
                Classe = ""
                if impGeneralObjClass != "NF":
                    Classe = impGeneralObjClass
                    for impGenObjCla, impGenObjClaQtd in especificObjs.items():
                        if impGenObjCla != impGeneralObjClass:
                            improvedSpecificObjPlace.append(impGenObjCla)
                            improvedSpecificObjPlaceQtd.append(impGenObjClaQtd)
                    labels = improvedSpecificObjPlace
                    qtdLabels = improvedSpecificObjPlaceQtd
                    fig1, ax1 = plt.subplots(figsize=(13, 10))
                    ax1.pie(qtdLabels, autopct='%1.1f%%', labels=labels, shadow=True, startangle=270, labeldistance=0.99, wedgeprops=dict(width=0.5, edgecolor='white'))
                    plt.legend(labels=labels, bbox_to_anchor=(1, 0), loc="lower right", prop={'size': 12},
                               bbox_transform=plt.gcf().transFigure, title="Improved Class")
                    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                    plt.title("Archtecture - Specific Experimented Environment of "+Classe+" Class")
                    plt.tight_layout()
                    title = "ArchtectureSpecificExperimentedEnvironmentof"+Classe+"Class"
                    var = "{}/printDictARCHEnvironmentPie" + title + ".png"
                    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/ARCH", shell=True)
                    plt.savefig(var.format(results_dir+"/ARCH"))
                    plt.show()

                    #colors = []
                    labels = improvedSpecificObjPlace
                    qtdLabels = improvedSpecificObjPlaceQtd
                    y_pos = np.arange(len(labels))
                    fig1, ax1 = plt.subplots(figsize=(10,10))
                    plt.bar(y_pos, qtdLabels, align='center', alpha=0.5, width=0.5)
                    plt.xticks(y_pos, labels, rotation=75, ha='center', size=11)
                    for i, v in enumerate(qtdLabels):
                        plt.text(i, v, str(v), color='red', size=8, ha='center')

                    plt.tight_layout()
                    plt.title("Archtecture Specific Class " + Classe + " Used Environment")
                    plt.xlabel(Classe + " Objects", fontsize=11)
                    plt.ylabel('Quantity', fontsize=11)
                    title = "Archtecture" + Classe + "UsedEnvironmentOP02"
                    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/ARCH", shell=True)
                    var = "{}/printDictARCHEnvironmentBar" + title + ".png"
                    plt.savefig(var.format(results_dir+"/ARCH"))
                    plt.show()

def ExtractSelectioCriteria(selection_criteria):
    if selection_criteria not in dict_selectionCriteria:
        dict_selectionCriteria[selection_criteria] = 1
    else:
        val = dict_selectionCriteria[selection_criteria]
        dict_selectionCriteria[selection_criteria] = val + 1
def printSelectioCriteria():
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

    plt.rcParams.update({'font.size': 14.0})
    explode = (0.1, 0.2, 0.3, 0.0, 0.0, 0.0, 0.0)
    fig1, ax1 = plt.subplots(figsize=(7,7))
    ax1.pie(Criteriavalue, colors=colors, explode=explode, autopct='%1.1f%%', pctdistance=0.3, radius=1, counterclock=False,wedgeprops=dict(width=1.0, edgecolor='white'),
            shadow=True, startangle=10, labeldistance=1.05)  # , wedgeprops = { 'linewidth': 1, "edgecolor" :"k" })
    plt.legend(labels=Criterianame,bbox_to_anchor=(1, 0), prop={'size': 12}, loc="lower right", bbox_transform=plt.gcf().transFigure)

    ax1.axis('equal')
    ax1.set_title('Accepted Papers According to the Selection Criteria')
    title = 'AcceptedPapersAccordingtotheSelectionCriteria'
    plt.tight_layout()
    var = "{}/07printSelectioCriteria" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/07printSelectioCriteria", shell=True)
    plt.savefig(var.format(results_dir + "/07printSelectioCriteria"))
    plt.show()


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
def printDevicesChart():
    #explode = (0.01, 0.025, 0.015, 0.02, 0.03, 0.04, 0.05, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.015)
    explode = (0.01, 0.025, 0.015, 0.02, 0.03, 0.04, 0.05, 0.02, 0.03, 0.04, 0.05, 0.06, 0.10, 0.14, 0.17, 0.015)
    CreateDevicesChartByCriteria(dict_devices, title, explode)
def printDevicesChartByCriteria():
    explode = None
    for criteria, value in dict_devicesByCriteria.items():
        if criteria == "H2H-IO -Hard-2-improve-IO-on-Hardware":
            title = "H2H-IO"
            CreateDevicesChartByCriteria(value,title,explode)
        elif criteria == "H2S-IO -Hard-2-improve-IO-on-Software":
            title  = "H2S-IO"
            CreateDevicesChartByCriteria(value, title, explode)
        elif criteria == "H2SS-IO -Hardw-2-improve-IO-on-Storage-Systems":
            title  = "H2SS-IO"
            CreateDevicesChartByCriteria(value, title, explode)
        elif criteria == "S2S-IO -Soft-2-improve-IO-on-Software":
            title  = "S2S-IO"
            CreateDevicesChartByCriteria(value, title, explode)
        elif criteria == "S2H-IO -Soft-2-improve-IO-on-Hardware":
            title  = "S2H-IO"
            CreateDevicesChartByCriteria(value, title, explode)
        elif criteria == "S2SS-IO -Soft-2-improve-IO-on-Storage-Systems":
            title  = "S2SS-IO"
            CreateDevicesChartByCriteria(value, title, explode)
        elif criteria == "ARCHITECTURE":
            title  = "ARCHITECTURE"
            CreateDevicesChartByCriteria(value, title, explode)
def CreateDevicesChartByCriteria(dict_devices,title,explode):
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
        plt.rcParams.update({'font.size': 12.0})
        fig, ax = plt.subplots(figsize=(8, 9))
        plt.title(title+' - Most Considered Devices According to the Classification')
        data = qtdDevices
        ax.pie(data, colors=colors, wedgeprops=dict(width=0.5), pctdistance=1.1, radius=1, counterclock=False,
                               shadow=False, startangle=60, labeldistance=1.1,autopct='%1.1f%%')

        plt.legend(devices, bbox_to_anchor=(1, 0), loc="lower right", bbox_transform=plt.gcf().transFigure)
        plt.gca().axis("equal")
        title = title+'MostConsideredDevicesAccordingtotheClassification'
        plt.tight_layout()
        var = "{}/05printDevicesChartByCriteria" + title + ".png"
        subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/05printDevicesChartByCriteria", shell=True)
        plt.savefig(var.format(results_dir + "/05printDevicesChartByCriteria"))
        plt.show()

    else:
        explode =  explode
        plt.rcParams.update({'font.size': 14.0})
        fig1, ax1 = plt.subplots(figsize=(8, 8))
        ax1.pie(qtdDevices, colors=colors, explode=explode, pctdistance=1.0, radius=1, counterclock=False,
                shadow=False, startangle=180, labeldistance=1.05, wedgeprops={'linewidth': 0.19, "edgecolor": "k"},autopct='%1.1f%%')
        plt.legend(devices, bbox_to_anchor=(1, 0), prop={'size': 11}, loc="lower right", bbox_transform=plt.gcf().transFigure)

        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax1.set_title('Most Considered Storage Devices on the Papers')
        title = 'MostConsideredDevices'
        plt.tight_layout()
        var = "{}/04printDevicesChart" + title + ".png"
        subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/04printDevicesChart", shell=True)
        plt.savefig(var.format(results_dir + "/04printDevicesChart"))
        plt.show()

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
        ExtractANDCreateDict_Power(power,selection_criteria)
        #print(power)
        benchmarks = line[5]
        ExtractBenchmark(benchmarks)
        #print("proxima linha \n")

def menu():
    escolha = int(input(''' Choose an option to print please!!

1 - printStatus(1x)
2 - printPowerChart(1x)
3 - printPowerChartByCriteria(1x)
4 - printDevicesChart(1x)
5 - printDevicesChartByCriteria(7x)
6 - printBenchmarksChart(2x)
7 - printSelectioCriteria(1x)
8 - print_H2H_ReachedObject(1x)
9 - print_H2S_ReachedObject(1x)
10- printDict_H2SS_improvedObject(4x)
11- printDict_S2S_improvedObject(1x)
12- printDict_S2H_improvedObject(3x)
13- printDict_S2SS_improvedObject(9x)
14- printDict_ARCH_improvedObject(8x)
15- 
0 - Para voltar ao menu
Escolha: \n''' ))

    if escolha == 1:
        print("accepted", accepted)
        print("duplicated", duplicated)
        print("rejected", rejected)
        printStatus()
        menu()
        pass
    elif escolha == 2:
        printPowerChart()
        menu()
        pass
    elif escolha == 3:
        printPowerChartByCriteria()
        menu()
        pass
    elif escolha == 4:
        printDevicesChart()
        menu()
        pass
    elif escolha == 5:
        printDevicesChartByCriteria()
        menu()
        pass
    elif escolha == 6:
        printBenchmarksChart()
        menu()
        pass
    elif escolha == 7:
        printSelectioCriteria()
        menu()
        pass
    elif escolha == 8:
        print_H2H_ReachedObject()
        menu()
        pass
    elif escolha == 9:
        print_H2S_ReachedObject()
        menu()
        pass
    elif escolha == 10:
        printDict_H2SS_improvedObject()
        menu()
        pass
    elif escolha == 11:
        printDict_S2S_improvedObject()
        printDict_S2S_implementedObject()
        menu()
        pass
    elif escolha == 12:
        printDict_S2H_improvedObject()
        menu()
        pass
    elif escolha == 13:
        printDict_S2SS_improvedObject()
        menu()
        pass
    elif escolha == 14:
        printDict_ARCH_improvedObject()
        menu()
        pass
    elif escolha == 15:

        menu()
        pass

    elif escolha == 0:
        print("\nEND!")
        pass
for f in filenames:
    path = "/home/laercio/github/ReadingParsifal/" + f

    with open(path) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        data = {}
        for row in readCSV:
            bibtex_key = row[0]
            title = row[1]
            selection_criteria = row[2]
            status = row[3]
            comments = row[4]
#bibtex_key	title	selection_criteria	status	comments
            ExtractStatus(status, comments, selection_criteria)
menu()

