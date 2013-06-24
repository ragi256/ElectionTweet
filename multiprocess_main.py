#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
import sys, os
import time
import gzip
import copy
import decimal
import logging
import multiprocessing 

from distributer import Distributer
import naturalLanguage

query_list = ['賛成','反対']

def function1(line,queue,counter,tenth):
    dist = Distributer()
    tweet_text = naturalLanguage.setTweet(line)
    if dist.isAboutElection(tweet_text,query_list):
        dist.extractToElection(tweet_text)
    else:
        dist.extractToAll(tweet_text)
    progress(counter,tenth)
    queue.put(list(set(dist.passElection() )) )
    
def function2(line,queue,relevant_word_list,counter,tenth):
    appearance_list = []
    tweet_text =naturalLanguage.setTweet(line)
    for query in relevant_word_list:
        for word in tweet_text:
            if word.find(query)!=-1:
                appearance_list.append(query)
                break
    progress(counter,tenth)
    queue.put(list(set(appearance_list)) )
    
def progress(counter,tenth):
    if counter.value%tenth == 0:
        prog = "%s" % ("=" * (counter.value/tenth) + ">")
        print prog + '\r',
    counter.value += 1

def setDictProcess(queue,conn,flag):
    dic = {}
    flag.value = True
    while flag.value:
        if queue.empty():
            time.sleep(0.01)
        else:
            word_list = queue.get()
            listToDict(word_list,dic)
    conn.send(dic)
    
def writeProbabilityDict(output,dictionary,total_tweet,string):
    print 'データを出力します'
    probability_dict = {}
    for key,value in dictionary.items():
        probability_dict[key] = decimal.Decimal(value) / total_tweet
    writeOutput(output,probability_dict,string)

def writeOutput(output,dictionary,top_line):
    counter = 0
    output.write(top_line)
    for key,value in sorted(dictionary.items(),key=lambda x:x[1],reverse=True):
        counter += 1
        output.write(str(counter) + ':' + key + '\n\t\t' + str(value) +'\n')
    output.write('\n')

def listsToDict(lists,dictionary):
    """[ ['A','B','C'],['D','A','B'],['A','A','A'] ]
       {'A':5, 'B':2, 'C':1, 'D':1}"""
    for list in lists:
        listToDict(list,dictionary)
        
def listToDict(list,dictionary):
    """['A','B','C','A','D','C','C','B','A']
       {'A':3, 'B':2, 'C':3, 'D':1}"""
    for word in list:
        if word in dictionary.keys():
            dictionary[word] += 1
        else:
            dictionary[word] = 1

def exceptionMessage(e):
    print '=== エラー内容 ==='
    print 'type:' + str(type(e))
    print 'args:' + str(e.args)
    print 'message:' + e.message
    print 'e自身:' + str(e)
 
if __name__ == '__main__':
    argv = sys.argv
    starttime = time.time()
    Input = gzip.open(argv[1], 'r')
#    Input = open(argv[1], 'r')
    output1 = open(argv[2], 'w')
    output2 = open(argv[3], 'w') 
    total_tweet = sum(1 for line in Input)
    print argv[1] + 'は' + str(total_tweet) + '行あります'
    tenth = total_tweet / 10   
    queue = multiprocessing.Queue()
    result_receiver,result_sender = multiprocessing.Pipe()
    counter = multiprocessing.Value('i',0)
    flag = multiprocessing.Value('i',0)
    print '関連語抽出処理を開始します'
    Input.seek(0)
    try:
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(logging.WARNING)

        set_dic_process = multiprocessing.Process(name='setDict',
                                                  target=setDictProcess,
                                                  args=(queue,result_sender,flag))
        set_dic_process.start()
                
        process = [multiprocessing.Process(target=function1,
                                           args=(line,queue,counter,tenth))
                   for line in Input]
        for p in process:
            p.start()

        flag.value = False
        relevant_dict = result_receiver.recv()
        for p in process:
            p.join()
        set_dic_process.join()

    except Exception as e:
        exceptionMessage(e)
        for p in process:
            p.terminate()
        print 'プログラムを終了します'
        sys.exit()
            
    write_line = "======== relevant word & query tweet appear probability ========\n"
    writeProbabilityDict(output1,relevant_dict,total_tweet,write_line)
    
    counter.value = 0
    print '関連語登場回数測定を開始します'
    Input.seek(0)
    try:
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(logging.WARNING)

        set_dic_process = multiprocessing.Process(name='setDict',
                                                  target=setDictProcess,
                                                  args=(queue,result_sender,flag))
        keys = relevant_dict.keys()
        del relevant_dict
        set_dic_process.start()
        process = [multiprocessing.Process(target=function2,
                                           args=(line,queue,keys,counter,tenth))
                   for line in Input]
        for p in process:
            p.start()

        flag.value = False
        appear_rate_dict = result_receiver.recv()
        for p in process:
            p.join()
        set_dic_process.join()
        

    except Exception as e:
        exceptionMessage(e)
        for p in process:
            p.terminate()
        print 'プログラムを終了します'
        sys.exit()
        
    write_line = "======== relevant word all tweet  appear probability ========\n"
    writeProbabilityDict(output2,appear_rate_dict,total_tweet,write_line)
 
    Input.close()
    output1.close()
    output2.close()
    
    endtime = time.time()
    print "time.time:" + str(endtime-starttime)

###############################################################################
