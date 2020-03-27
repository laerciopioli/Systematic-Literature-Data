import csv
import matplotlib.pyplot as plt
import numpy as np
import glob

plt.rcParams.update({'font.size': 6.50})
filenames = sorted(glob.glob('articles.csv'))
filenames = filenames[0:3]

dict_environments = {
    "x": [],
    "y": []
}

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


testando = "ROCKSDB"
#

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


def VerifyDuplicityBenchmarks(benchmark):
    benchmark = benchmark.upper()
    if benchmark == "FINANCIAL2" or benchmark == "FINANCIAL-2" or benchmark == "SPC-FINANCIAL1" or benchmark == "FIN2":
        benchmark = "SPC-FINANCIAL2"
    if benchmark == "FINANCIAL1" or benchmark == "FINANCIAL-1" or benchmark == "FIN1":
        benchmark = "SPC(FINANCIAL1)"
    return benchmark



def InsertHeadAndTailBenchmark(head, tails):
    global testando
    if testando in head or testando in tails:
        print(title)
        print("teste")


    if head not in dict_benchmarks.keys():
        dict_benchmarks[head] = {} #adiciona o head para adicionar os Keys


    val = dict_benchmarks[head]
    if type(val) == int: # se for o valor for do tipo int quer dizer que foi inserido a chave [head] e o valor é um numero, logo update nesse numero e ignora os parenteses
        cont = int(dict_benchmarks[head])
        dict_benchmarks[head] = cont + 1
    elif type(val) == dict: #atualiza o elemento e o numero dentro do dicionário.
        for trace in tails:
            if trace not in dict_benchmarks.values():
                dict_benchmarks[head][trace] = 1
            else:
                cont = int(dict_benchmarks[head][trace])
                dict_benchmarks[head][trace] = cont + 1



def InsertOnlyHeadBenchmark(benchmark): #this function receive an benchmaks to be appened to the dictionary
    global testando
    if testando in benchmark:
        print(title)
        print("teste")


    if benchmark not in dict_benchmarks.keys(): #se o benchmark não está nas chaves eu somente insiro
        dict_benchmarks[benchmark] = 1
    #else: # se o benchmark está nas chaves devo ver se ele é cabeça de chave
    elif benchmark in dict_benchmarks.keys():
        valueTypeTest = dict_benchmarks[benchmark]
        if type(valueTypeTest) == int: #significa que o valor do benchmark é um inteiro, logo key,value é benchmark,number
            cont = int(dict_benchmarks[benchmark])
            dict_benchmarks[benchmark] = cont + 1
        elif type(valueTypeTest) == dict: # o tipo da variavel eh dict
            papersToVerify.append(title)



def ExtractBenchmark(benchmarks,title):
    #[Linux(wc&grep)&App(Sphinx-3)&specific]
    #logo primeiro devo dar o split em parenteses e depois em &
    if title == "Simultaneous Evaluation of Multiple I/O Strategies":
        print("verificar no corte do benchmark")
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
    else:
        print(title)
        print("verify")

    if selection_criteria not in dict_powerByCriteria:
        dict_powerByCriteria[selection_criteria]= {"Y":0,"N":0}
    if "Y" in power:
        cont = dict_powerByCriteria[selection_criteria]["Y"]
        dict_powerByCriteria[selection_criteria]["Y"] = cont + 1
    elif "N" in power:
        cont = dict_powerByCriteria[selection_criteria]["N"]
        dict_powerByCriteria[selection_criteria]["N"] = cont + 1



def ExtractComments(comment, title, selection_criteria):
    comment = comment.replace("]\n[", "]-[");
    line = comment.split(']-[')
    if len(line) < 6:
        papersToVerify.append(title)
    else:
        text = line[0]
        #print(text)
        improvedObject = line[1]
        devices = line[2]
        ExtractDevice(devices, selection_criteria)
        concerning = line[3]
        #print(concerning)
        power = line[4]
        ExtractPower(power,selection_criteria)
        #print(power)
        benchmarks = line[5]
        print(title)
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
    elif status == "Rejected":
        rejected += 1
    else:
        print("A DIFFERENT STATUS IS the HEADER IS ALLOWED ONLY FOR HEADERS TITLE")
        print(title)


print(dict_devices)
print(dict_devicesByCriteria)

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
print("PAPERS to VERIFY", len(papersToVerify), papersToVerify)

print(dict_devices.items())
print(dict_devicesByCriteria.items())
print(dict_benchmarks.items())
print(len(dict_benchmarks))
print(dict_power)
print(dict_powerByCriteria)
print("papers to verify --->>>",papersToVerify)

#Prepare the data
line1 = plt.plot(["xx"])
line2 = plt.plot(["32/Seq","32/Ran","64/Seq","64/Ran"])

plt.ylabel('ydeddddddddddddddd')
plt.xlabel('xxxxxxxxxxxxxxxxxxxxxxxx')

# Add a legend
plt.legend()

# Show the plot
plt.show()

#https://kite.com/python/answers/how-to-remove-specific-characters-from-a-string-in-python