#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
import sys, os
import gzip
import copy
import decimal 
    
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
    
    total = 0
    dic = {}
    for data in sys.argv[1:]:
        f = open(data)
        for line in f:
            words = line.strip("\n").split("\t")
            if len(words)==1:
                total += int(line)
            elif len(words)==2:
                word = words[0]
                number = int(words[1])
                if word in dic:
                    dic[word] += number
                else:
                    dic[word] = number
            else:
                print "形式が間違っていました。確認してください。"
                sys.exit()
    print total
    for word,number in sorted(dic.items(),key=lambda x:x[1],reverse=True):
        print word + "\t" + str(decimal.Decimal(number)/total)
#        print word + "\t" + str(number/total)
#        print word + "\t" + str(number)

###############################################################################
