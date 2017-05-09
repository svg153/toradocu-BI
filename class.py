#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import copy
import errno
import json
import os
import re
from collections import Counter

import matplotlib.pyplot as plt


def silentremove(filename):
    # http://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def paramTagAnalisis(cond):
    tipos = {}
    ocu = {'==', '!=', '>=', '<=', 'true', 'false', 'null'}

    for o in ocu:
        n = cond.count(o)
        if n != 0:
            if o in tipos:
                tipos[o] = tipos[o] + n
            else:
                tipos.update({o: n})

    # < y > regex con texto a los lados
    # funciones con regex

    typo = '<'
    reg = 'r\'[a-zA-Z_0-9]*' + typo + '[a-zA-Z_0-9]*'
    ocur = re.findall(reg, cond)
    n = len(ocur)
    if n != 0:
        if typo in tipos:
            tipos[typo] = tipos[typo] + n
        else:
            tipos.update({typo: n})

    typo = '>'
    reg = 'r\'[a-zA-Z_0-9]*' + typo + '[a-zA-Z_0-9]*'
    ocur = re.findall(reg, cond)
    n = len(ocur)
    if n != 0:
        if typo in tipos:
            tipos[typo] = tipos[typo] + n
        else:
            tipos.update({typo: n})

    functions_list = re.findall(r'\.[a-zA-Z_0-9]*\(', cond)
    for f in functions_list:
        f_name = f[1:-1]
        if f_name in tipos:
            tipos[f_name] = tipos[f_name] + 1
        else:
            tipos.update({f_name: 1})

    return tipos


def tiposGraph(title, tipos):
    # http://stackoverflow.com/questions/36009049/plotting-a-graph-from-a-list-of-information-in-python
    # http://matplotlib.org/1.2.1/examples/pylab_examples/barh_demo.html
    data = Counter(tipos)
    xaxis = range(len(data))

    keys_freq = []
    values_freq = []

    # Rank depending on frequency
    for key, value in data.most_common()[::-1]:
        keys_freq.append(key)
        values_freq.append(value)

    fig = plt.figure()

    plt.title(title)

    plt.barh(xaxis, values_freq, align='center')
    plt.yticks(xaxis, keys_freq)
    locs, labels = plt.yticks()
    plt.setp(labels)
    plt.grid(True)
    plt.ylabel('type')
    plt.xlabel('ocurs')

    fig.tight_layout()
    fig.savefig('jsons_' + title + '.png', dpi=fig.dpi)


condname = 'condition'
out_template = {'throws': {'n': 0, 'c': 0, '%c': 0.0, 'tipos': {}}, 'params': {'n': 0, 'c': 0, '%c': 0.0, 'tipos': {}},
                'return': {'n': 0, 'c': 0, '%c': 0.0, 'tipos': {}}}

errorfiles = os.getcwd() + '/errorfiles.txt'
errorfiles_out = open(errorfiles, 'w')

goaldirpath = os.getcwd() + '/jsons'

goals_out_name = goaldirpath + '_BI.json'
silentremove(goals_out_name)
goals_out = open(goals_out_name, 'w')

goals_out_temp = copy.deepcopy(out_template)

for file in os.listdir(goaldirpath):
    filepath = goaldirpath + os.sep + file
    if os.path.isdir(filepath):
        packagedirpath = filepath

        package_out_name = packagedirpath + '_BI.json'
        package_name = file
        silentremove(package_out_name)
        package_out = open(package_out_name, 'w')

        package_out_temp = copy.deepcopy(out_template)

        for file2 in os.listdir(packagedirpath):
            file2path = packagedirpath + os.sep + file2

            if os.path.isfile(file2path) and not file2path.endswith("_BI.json"):
                classfilepath = file2path
                # print('-------------------------------------')
                # print(classfilepath)
                # print('-------------------------------------')

                with open(classfilepath) as data_file:

                    try:
                        data = json.load(data_file)
                    except json.decoder.JSONDecodeError as e:
                        line = str(classfilepath) + '\n'
                        errorfiles_out.write(line)
                        continue

                    classfile_out_name = classfilepath[:-5] + '_BI.json'

                    silentremove(classfile_out_name)
                    classfile_out = open(classfile_out_name, 'w')

                    classfile_out_temp = copy.deepcopy(out_template)

                    for n in data:
                        # n tiene la info de cada metodo

                        if 'throwsTags' in n and n['throwsTags'] != []:
                            type = 'throws'
                            for d in n['throwsTags']:
                                classfile_out_temp[type]['n'] = classfile_out_temp[type]['n'] + 1
                                package_out_temp[type]['n'] = package_out_temp[type]['n'] + 1
                                goals_out_temp[type]['n'] = goals_out_temp[type]['n'] + 1
                                cond = d[condname]
                                if cond != '':
                                    classfile_out_temp[type]['c'] = classfile_out_temp[type]['c'] + 1
                                    package_out_temp[type]['c'] = package_out_temp[type]['c'] + 1
                                    goals_out_temp[type]['c'] = goals_out_temp[type]['c'] + 1
                                    # pprint(type + " : " + cond)
                                    classfile_out_temp[type]['tipos'] = paramTagAnalisis(cond)
                                    package_out_temp[type]['tipos'] = Counter(
                                        package_out_temp[type]['tipos']) + Counter(classfile_out_temp[type]['tipos'])
                                    goals_out_temp[type]['tipos'] = Counter(goals_out_temp[type]['tipos']) + Counter(
                                        classfile_out_temp[type]['tipos'])
                                    # print(classfilepath + " : " + type + " : " + cond + " : " + str(classfile_out_temp[type]['tipos']))

                        if 'paramTags' in n and n['paramTags'] != []:
                            type = 'params'
                            for d in n['paramTags']:
                                classfile_out_temp[type]['n'] = classfile_out_temp[type]['n'] + 1
                                package_out_temp[type]['n'] = package_out_temp[type]['n'] + 1
                                goals_out_temp[type]['n'] = goals_out_temp[type]['n'] + 1
                                cond = d[condname]
                                if cond != '':
                                    classfile_out_temp[type]['c'] = classfile_out_temp[type]['c'] + 1
                                    package_out_temp[type]['c'] = package_out_temp[type]['c'] + 1
                                    goals_out_temp[type]['c'] = goals_out_temp[type]['c'] + 1
                                    # pprint(type + " : " + cond)
                                    classfile_out_temp[type]['tipos'] = paramTagAnalisis(cond)
                                    package_out_temp[type]['tipos'] = Counter(
                                        package_out_temp[type]['tipos']) + Counter(classfile_out_temp[type]['tipos'])
                                    goals_out_temp[type]['tipos'] = Counter(goals_out_temp[type]['tipos']) + Counter(
                                        classfile_out_temp[type]['tipos'])

                        if 'returnTag' in n:
                            type = 'return'
                            cond = n['returnTag'][condname]
                            classfile_out_temp[type]['n'] = classfile_out_temp[type]['n'] + 1
                            package_out_temp[type]['n'] = package_out_temp[type]['n'] + 1
                            goals_out_temp[type]['n'] = goals_out_temp[type]['n'] + 1
                            if cond != '':
                                classfile_out_temp[type]['c'] = classfile_out_temp[type]['c'] + 1
                                package_out_temp[type]['c'] = package_out_temp[type]['c'] + 1
                                goals_out_temp[type]['c'] = goals_out_temp[type]['c'] + 1
                                # pprint(type + " : " + cond)
                                if '?' in cond:
                                    cond = cond.split('?')
                                    cond = str(cond[1])
                                classfile_out_temp[type]['tipos'] = paramTagAnalisis(cond)
                                package_out_temp[type]['tipos'] = Counter(package_out_temp[type]['tipos']) + Counter(
                                    classfile_out_temp[type]['tipos'])
                                goals_out_temp[type]['tipos'] = Counter(goals_out_temp[type]['tipos']) + Counter(
                                    classfile_out_temp[type]['tipos'])

                    classfile_out_temp['throws']['%c'] = classfile_out_temp['throws']['c'] / \
                                                         classfile_out_temp['throws']['n'] if \
                    classfile_out_temp['throws']['n'] != 0 else 0
                    classfile_out_temp['params']['%c'] = classfile_out_temp['params']['c'] / \
                                                         classfile_out_temp['params']['n'] if \
                    classfile_out_temp['params']['n'] != 0 else 0
                    classfile_out_temp['return']['%c'] = classfile_out_temp['return']['c'] / \
                                                         classfile_out_temp['return']['n'] if \
                    classfile_out_temp['return']['n'] != 0 else 0

                    #%c Para cada clase.

                    classfile_out.write(json.dumps(classfile_out_temp, indent=2, sort_keys=True))
                    classfile_out.close()

                    classfile_out_temp['throws']['n'] = 0
                    classfile_out_temp['throws']['c'] = 0
                    classfile_out_temp['params']['n'] = 0
                    classfile_out_temp['params']['c'] = 0
                    classfile_out_temp['return']['n'] = 0
                    classfile_out_temp['return']['c'] = 0


            else:
                continue

        package_out_temp['throws']['%c'] = package_out_temp['throws']['c'] / package_out_temp['throws']['n'] if \
        package_out_temp['throws']['n'] != 0 else 0
        package_out_temp['params']['%c'] = package_out_temp['params']['c'] / package_out_temp['params']['n'] if \
        package_out_temp['params']['n'] != 0 else 0
        package_out_temp['return']['%c'] = package_out_temp['return']['c'] / package_out_temp['return']['n'] if \
        package_out_temp['return']['n'] != 0 else 0

        #%c Para cada paquete

        package_out.write(json.dumps(package_out_temp, indent=2, sort_keys=True))
        package_out.close()


        # png con el ranking por paquete

        tiposGraph(str(package_name) + '_return', package_out_temp['return']['tipos'])
        tiposGraph(str(package_name) + '_throws', package_out_temp['throws']['tipos'])
        tiposGraph(str(package_name) + '_params', package_out_temp['params']['tipos'])

        package_out_temp['throws']['n'] = 0
        package_out_temp['throws']['c'] = 0
        package_out_temp['params']['n'] = 0
        package_out_temp['params']['c'] = 0
        package_out_temp['return']['n'] = 0
        package_out_temp['return']['c'] = 0


goals_out_temp['throws']['%c'] = goals_out_temp['throws']['c'] / goals_out_temp['throws']['n'] if \
goals_out_temp['throws']['n'] != 0 else 0
goals_out_temp['params']['%c'] = goals_out_temp['params']['c'] / goals_out_temp['params']['n'] if \
goals_out_temp['params']['n'] != 0 else 0
goals_out_temp['return']['%c'] = goals_out_temp['return']['c'] / goals_out_temp['return']['n'] if \
goals_out_temp['return']['n'] != 0 else 0

goals_out.write(json.dumps(goals_out_temp, indent=2, sort_keys=True))
goals_out.close()
errorfiles_out.close()

goals_out_temp['throws']['n'] = 0
goals_out_temp['throws']['c'] = 0
goals_out_temp['params']['n'] = 0
goals_out_temp['params']['c'] = 0
goals_out_temp['return']['n'] = 0
goals_out_temp['return']['c'] = 0

tiposGraph('throws', goals_out_temp['throws']['tipos'])
tiposGraph('params', goals_out_temp['params']['tipos'])
tiposGraph('return', goals_out_temp['return']['tipos'])
