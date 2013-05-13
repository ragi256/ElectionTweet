#!/usr/bin/python
# -*- coding: utf-8 -*-

class Distributer(object):
    """ 分配器。与えられたクエリのリストがツイート文に含まれているかで分配
        並列処理ではオブジェクトを共有してもメンバの辞書はリセットされるので
        返り値をなんとか利用するしかない"""
    __all_words = {}
    __election_words = {}
    def __init__ (self):
        pass

    def isAboutElection(self,words_list,query_list):
        for query in query_list:
            for word in words_list:
                if word.count(query)!=0:
                    return True
        return False
                    
#            if query in words_list:
#                for filter_word in filter_list:
#                    if filter_word in words_list:
#                        return False

    def extractToElection(self,words_list):
        All = self.__all_words
        Election = self.__election_words
        for word in words_list:
            if word in Election:
                Election[word] += 1
            else:
                Election[word] = 1
                if word in All:
                    All[word] += 1
                else:
                    All[word] = 1
                    

    def extractToAll(self,words_list):
        All = self.__all_words
        for word in words_list:
            if word in All:
                All[word] += 1
            else:
                All[word] = 1

    def showElectionKeys(self):
        """ 並列処理では使えない"""
        for word in self.__election_words.keys():
            print word + ' ',
        print
        
    def showAllKeys(self):
        """ 並列処理では使えない"""
        for word in self.__all_words.keys():
            print word + ' ',
        print

    def writeDict(self,output,ElectionOrAll):
        """ 並列処理では使えない"""
        if ElectionOrAll=="Election":
            dictionary = self.__election_words
        else:
            dictionary = self.__all_words
        for key,value in sorted(dictionary.items(),key=lambda x:x[1],reverse=True):
            output.write(key + ':' + str(value) + '  ',)
        output.write('\n')
        
    def passElection(self):
        return self.__election_words

    def passAll(self):
        return self.__all_words
