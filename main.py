#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
import sys, os
import gzip
import copy

from distributer import Distributer
import naturalLanguage

query_list = ['賛成','反対']

def function1(line):
    dist = Distributer()
    tweet_text = naturalLanguage.setTweet(line)
    if dist.isAboutElection(tweet_text,query_list):
        dist.extractToElection(tweet_text)
    else:
        dist.extractToAll(tweet_text)
    return list(set(dist.passElection() )) 
    
def function2(line,relevant_word_list):
    appearance_list = []
    tweet_text =naturalLanguage.setTweet(line)
    for query in relevant_word_list:
        for word in tweet_text:
            if word.find(query)!=-1:
                appearance_list.append(query)
                break
    return list(set(appearance_list)) 
    
def writeAppearanceDict(output,dictionary,total_tweet):
    print 'データを出力します'
    output.write(str(total_tweet) + '\n')
    for key,value in sorted(dictionary.items(),key=lambda x:x[1],reverse=True):
        output.write(key + '\t' + str(value) + '\n')
        
def listToDict(list,dictionary):
    """['A','B','C','A','D','C','C','B','A']
       {'A':3, 'B':2, 'C':3, 'D':1}"""
    for word in list:
        if word in dictionary.keys():
            dictionary[word] += 1
        else:
            dictionary[word] = 1
 
if __name__ == '__main__':
    argv = sys.argv
    Input = gzip.open(argv[1], 'r')
    output1 = open(argv[2], 'w')
    output2 = open(argv[3], 'w') 
    total_tweet = sum(1 for line in Input)
    print argv[1] + 'は' + str(total_tweet) + '行あります'

    print '関連語抽出処理を開始します'
    Input.seek(0)
    relevant_dict = {}
    for line in Input:
        temp_list = function1(line)
        listToDict(temp_list,relevant_dict)
            
    writeAppearanceDict(output1,relevant_dict,total_tweet)
    

    print '関連語登場回数測定を開始します'
    Input.seek(0)
    appear_rate_dict = {}
    for line in Input:
        temp_list = function2(line,relevant_dict)
        listToDict(temp_list,appear_rate_dict)
        
    writeAppearanceDict(output2,appear_rate_dict,total_tweet)
 
    Input.close()
    output1.close()
    output2.close()
    
###############################################################################
