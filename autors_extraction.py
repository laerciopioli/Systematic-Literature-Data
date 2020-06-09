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


script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, '/home/laercio/github/ReadingParsifal/Figs/')

if not os.path.isdir(results_dir):
    os.makedirs(results_dir)

#plotly.io.orca.config.executable = '/home/laercio/anaconda3/bin/orca'

filenames = sorted(glob.glob('Extract_autors.csv'))
filenames = filenames[0:3]

author_dict = {}

qtd_author =[]
qtd_publication = []



def sum_each_author_qt(authorow):
    authors = authorow.split('and')
    for autor in authors:
        if autor not in author_dict.keys():
            author_dict[autor] = 1
        else:
            aux = author_dict[autor]
            aux += 1
            obj = {autor:aux}
            author_dict.update(obj)


def print_extractingAutors():
    print(author_dict)
    a1_sorted_keys = sorted(author_dict, key=author_dict.get, reverse=False)
    for r in a1_sorted_keys:
        print(r, author_dict[r])
        qtd = sum(value == author_dict[r] for value in author_dict.values())

        if author_dict[r] not in qtd_author:
            qtd_author.append(author_dict[r])
            qtd_publication.append(qtd)

    print(qtd_author)
    print(qtd_publication)

    #plt.plot(qtd_author, qtd_publication, 'bo-')
    plt.scatter(qtd_author, qtd_publication)
    for x, y in zip(qtd_author, qtd_publication):
        label = "{:.0f}".format(y)

        plt.annotate(label,  # this is the text
                     (x, y),  # this is the point to label
                     textcoords="offset points",  # how to position the text
                     xytext=(0, 10),  # distance from text to points (x,y)
                     ha='center')  # horizontal alignment can be left, right or center

    #1
    # plt.title("Relation Between Authors and Publication Quantity")
    title = 'RelationBetweenAuthorsandPublicationQuantity'
    plt.grid(True)
    plt.xlabel(u'Number of Publication')
    plt.ylabel(u'Number of Authors')
    plt.xscale

    var = "{}/Plot" + title + ".png"
    subprocess.call("mkdir -m 755 -p /home/laercio/github/ReadingParsifal/Figs/Plot",
                    shell=True)
    plt.savefig(var.format(results_dir + "/Plot"))

    plt.show()



def menu():
    escolha = int(input(''' Choose an option to print please!!
1 - extract_autors
0 - quit
Escolha: \n''' ))

    if escolha == 1:
        print("Extracting Autrs")
        print_extractingAutors()
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
            author = row[0]
            sum_each_author_qt(author)
            #fazer função que da split no autor e adiciona em um dicionario
        menu()

