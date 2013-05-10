#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson
import MeCab
import re
#from multiprocessing import Pool

filter_list = ['AKB']
#link_pattern = re.compile("http(s)?://([\w-]+\.)+[\w-]+(/[\w- ./?%&=]*)?")
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
    __all_words = []
    __election_words = []
    def __init__ (self):
        pass

    def isAboutElection(self,words_list):
        if "選挙" in words_list:
            for filter_word in filter_list:
                if filter_word in words_list:
                    return False
            return True

    def extractToElection(self,words_list):
        for word in words_list:
            if word in self.__election_words:
                pass
            else:
                self.__election_words.append(word)
                if word in self.__all_words:
                    self.__all_words.append(word)
                else:
                    pass

    def extractToAll(self,words_list):
        for word in words_list:
            if word in self.__all_words:
                pass
            else:
                self.__all_words.append(word)

    def showElectionList(self):
        for word in self.__election_words:
            print word + ' ',
        print 
        
    def showAllList(self):
        for word in self.__all_words:
            print word + ' ',
        print

    def writeElectionList(self,output):
        for word in self.__election_words:
            output.write(word+' ')
        output.write('\n')

    def writeAllList(self,output):
        for word in self.__all_words:
            output.write(word+' ')
        output.write('\n')
        
def main():
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
    #dist.showElectionList()
    dist.writeElectionList(output)
    input.close()
    output.close()

if __name__ == '__main__':
    import sys
    argv = sys.argv
    main()
