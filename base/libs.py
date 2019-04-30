#!/usr/bin/python3k
# -*- coding: utf-8 -*-
###########################################################
# Feature: base lib 
# Author : Bing
# Version: 1.1
# Email  : kun1.huang@outlook.com
# Date   : 2016-11-24
###########################################################
from os import path
from os import listdir
import shutil
import csv
import pandas
import re
from itertools import combinations
from sqlite3 import connect as sqlite_conn

#get files from path
def get_files(path_str):
    """ get files"""
    filelist = []
    if path.isdir(path_str):
        dirs = listdir(path_str)
        for file in dirs:
            if path.isfile(file):
                filelist.append(file)
    elif path.isfile(path_str):
        filelist.append(path_str)

    return filelist
# get base name of f
def get_filename(file):
    """ get_filename """
    return path.basename(file)

# move file f to dest
def move_file(src, dest):
    """ move_file """
    fname = path.basename(src)
    return shutil.move(src, path.join(dest, fname))
# save dataset to mysql,dataset is result that query executed
def save_dataset_mysql(engine, dataset, table, cols, mode='append'):
    """ save_dataset_mysql """
    if dataset and table and engine:
        try:
            pdf = pandas.DataFrame(data=dataset, columns=cols)
            pdf.to_sql(table, engine, index=False, if_exists=mode)
            return True
        except Exception as ex:
            raise ex
    return False

#save dataset to csv,dataset is result that query executed
def save_dataset_csv(dataset, dest, mode='a'):
    """ save_dataset_csv """
    if dataset:
        try:
            cfile = open(dest, mode)
            writer = csv.writer(cfile)
            writer.writerows(dataset)
            cfile.close()
            return True
        except Exception as ex:
            raise ex

    return False

#load csv file to dic.the file must have two col.
def load_csv_dic(file):
    """ load_csv_dic """
    if csv and path.exists(file):
        try:
            dic = dict()
            csv_file = open(file)
            reader = csv.reader(csv_file)
            for line in reader:
                if line:
                    key, value = line
                    dic[key] = value
            csv_file.close()
            return dic
        except Exception as ex:
            raise ex

    return None

# load dataset to dic
def load_dataset_dic(data, columns, main_key=0, primary_key='imsi', sub_key='startdate'):
    """load_dataset_dic"""
    result = dict()
    print('convert data len %d' % len(data))
    if data and columns:
        for row in data:
            index_range = range(0, len(row))
            row_dic = {}
            for index in index_range:
                row_dic[columns[index]] = row[index]
            if row_dic:
                imsi = row_dic.get(primary_key)
                startdate = row_dic.get(sub_key)
                if imsi and startdate:
                    if not result.get(imsi):
                        result[imsi] = {}
                    result[imsi][startdate] = row_dic
    return result

# get index of the item in list
def get_list_item_index(array, item):
    """ get_list_item_index """
    try:
        index = array.index(item)
        return index
    except Exception as ex:
        print(ex)
        return -1


def reg_match(src, reg):
    """ reg_match """
    try:
        pattern = re.compile(reg)
        match = pattern.match(src)
        if match:
            return match.group()
        else:
            return None
    except Exception as ex:
        print(ex)
        return None

def get_dest_file(src_file, dest_dir):
    """ reg_match """
    fname = path.basename(src_file)
    if path.isdir(dest_dir):
        return path.join(dest_dir, fname)
    return dest_dir


def list_to_combinations(l,sort=False):
    if isinstance(l,list):
        comb = []
        res = []
        if sort:
            l.sort()
        for i in range(1,len(l)+1):
            comb.append(tuple(combinations(l,i)))
        if comb:
            for com in comb:
                for c in com:
                    res.append(list(c))
        return res

    return []

#
def load_dataset_sqlite(dataset, connection, table, cols):
    if dataset and connection and table and cols:
        try:
            pdf = pandas.DataFrame(data=dataset, columns=cols)
            pdf.to_sql(table, connection, index=False)
            return True
        except Exception as ex:
            raise ex

    return False

def is_table_exists(conn, table, database = None):
    sql = ""
    if conn and table:
        if database:
            sql = "show create table %s.%s;" % (database, table)
        else:
            sql = "show create table %s;" % (table)

        try:
            cur = conn.cursor()
            conn.execute(sql)
            return True
        except:
            return False
    return False
