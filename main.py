#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson
import MeCab
import re
import time
#from multiprocessing import Pool

filter_list = ['AKB']
link_pattern = re.compile ('(https?://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+)')

def preformat(line):
    """一行を受け取り形態素解析をしてリストを返す"""
    tagger = MeCab.Tagger('')
    encoded_line = line.encode('utf-8')
    node = tagger.parseToNode(encoded_line)
    keywords =[]
    while node:
        genkei = node.feature.split(",")[6]
        if genkei == "*":
            keywords.append(node.surface)
        else:
            keywords.append(genkei)
        node = node.next
    return keywords

def httpFilter(line):
    if "http" in line:
        temp = line
        line = link_pattern.sub(u"", temp)
    return line

class Distributer(object):
    """ テスト段階、そのうち外部モジュールに切るかも """
    __all_words = {}
    __election_words = {}
    def __init__ (self):
        pass

    def isAboutElection(self,words_list):
        if "選挙" in words_list:
            for filter_word in filter_list:
                if filter_word in words_list:
                    return False
            return True

    def extractToElection(self,words_list):
        All = self.__all_words
        Election = self.__election_words
        for word in words_list:
            if word in Election:
                Election[word] += 1
            else:
                Election[word] = 0
                if word in All:
                    All[word] += 1
                else:
                    All[word] = 0
                    

    def extractToAll(self,words_list):
        All = self.__all_words
        for word in words_list:
            if word in All:
                All[word] += 1
            else:
                All[word] = 0

    def showElectionKeys(self):
        for word in self.__election_words.keys():
            print word + ' ',
        print 
        
    def showAllKeys(self):
        for word in self.__all_words.keys():
            print word + ' ',
        print

    def writeDict(self,output,ElectionOrAll):
        if ElectionOrAll=="Election":
            dictionary = self.__election_words
        else:
            dictionary = self.__all_words
        for key,value in sorted(dictionary.items(),key=lambda x:x[1],reverse=True):
            output.write(key + ':',)
            output.write(str(value),)
            output.write('  ',)
        output.write('\n')
        
def main():
    starttime = time.clock()
    input = open(argv[1], 'r')
    output= open(argv[2], 'w')
    dist = Distributer()
    for line in input:
        tweet = simplejson.loads(line,"utf-8")
        tweet["text"] = httpFilter(tweet["text"])
        tweet_text = preformat(tweet["text"])
        if dist.isAboutElection(tweet_text):
            dist.extractToElection(tweet_text)
        else:
            dist.extractToAll(tweet_text)
    dist.showElectionKeys()
    output.write("\n========== words around Election ==========\n")
    dist.writeDict(output,"Election")
    # output.write("\n========== all words ==========\n")
    # dist.writeDict(output,"All")
    input.close()
    output.close()
    endtime = time.clock()
    print endtime-starttime
    
if __name__ == '__main__':
    import sys
    argv = sys.argv
    main()
