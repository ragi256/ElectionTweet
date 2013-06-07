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
    #if dist.passElection() != []:
    #    print ",".join(dist.passElection())
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
    #if appearance_list != []:
    #    print ",".join(appearance_list)
    queue.put(list(set(appearance_list)) )
    
def progress(counter,tenth):
    if counter.value%tenth == 0:
        prog = "%s" % ("=" * (counter.value/tenth) + ">")
        print prog + '\r',
    counter.value += 1

def setDictProcess(queue,dic):
    word_list = queue.get()
    for word in word_list:
        if word in dic.keys():
            dic[word] += 1
        else:
            dic[word] = 1
    
def listsToDict(lists,dictionary):
    for list in lists:
        listToDict(list,dictionary)
        
def listToDict(list,dictionary):
        for word in list:
            if word in dictionary.keys():
                dictionary[word] += 1
            else:
                dictionary[word] = 1

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

def exceptionMessage(e):
    print '=== エラー内容 ==='
    print 'type:' + str(type(e))
    print 'args:' + str(e.args)
    print 'message:' + e.message
    print 'e自身:' + str(e)
 
if __name__ == '__main__':
    argv = sys.argv
    starttime = time.time()
    manager = multiprocessing.Manager()
    Input = gzip.open(argv[1], 'r')
    output1 = open(argv[2], 'w')
    output2 = open(argv[3], 'w') 
    total_tweet = sum(1 for line in Input)
    print argv[1] + 'は' + str(total_tweet) + '行あります'
    tenth = total_tweet / 10   
    queue = multiprocessing.Queue()
    
    counter = multiprocessing.Value('i',0)
    print '関連語抽出処理を開始します'
    Input.seek(0)
    ps = []
    try:
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(logging.WARNING)

        relevant_dict = manager.dict()
        set_dic_process = multiprocessing.Process(target=setDictProcess,
                                                  args=(queue,relevant_dict))
        set_dic_process.start()
        for line in Input:
#            if len(ps) < 20:
            p = multiprocessing.Process(target=function1,
                                        args=(line,queue,counter,tenth))
            p.start()
            ps.append(p)
            p.join()
        set_dic_process.join()
    except Exception as e:
        exceptionMessage(e)
        for p in ps:
            p.terminate()
        print 'プログラムを終了します'
        sys.exit()
            
    write_line = "======== relevant word & query tweet appear probability ========\n"
    writeProbabilityDict(output1,relevant_dict,total_tweet,write_line)
    
    counter.value = 0
    print '関連語登場回数測定を開始します'
    Input.seek(0)
    ps = []
    try:
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(logging.WARNING)

        appear_rate_dict = manager.dict()
        set_dic_process = multiprocessing.Process(target=setDictProcess,
                                                  args=(queue,relevant_dict))
        set_dic_process.start()
        for line in Input:
#            if len(ps) < 20:
            p = multiprocessing.Process(target=function2,
                                        args=(line,queue,
                                              relevant_dict.keys(),counter,tenth))
            p.start()
            ps.append(p)
            p.join()
        set_dic_process.join()
    except Exception as e:
        exceptionMessage(e)
        for p in ps:
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
