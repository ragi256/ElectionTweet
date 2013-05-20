#!/usr/bin/python
# -*- coding: utf-8 -*-

class Distributer(object):
    """ 分配器。与えられたクエリのリストがツイート文に含まれているかで分配
        クエリを含むならelection_wordsに追加。all_wordsは常に追加
        一回の処理ごとにリストはリセットされるものと想定して設計(Poolの処理でそうなってしまう)"""
    __all_words = []
    __election_words = []
    def __init__ (self):
        pass
    
    def reset(self):
        self.__all_words = []
        self.__election_words = []

    def isAboutElection(self,words_list,query_list):
        """連続した名詞は連結するため調べるword_listの要素を
           直接比較せず、要素の文字列の中に一致するものがあるか調べる"""
        for query in query_list:
            for word in words_list:
                if word.find(query)!=-1:
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
            if len(word.decode('utf-8'))!=1 and not word in Election:
                Election.append(word)
                if not word in All:
                    All.append(word)
                    

    def extractToAll(self,words_list):
        All = self.__all_words
        for word in words_list:
            if len(word.decode('utf-8'))!=1 and not word in All:
                All.append(word)

    def showElectionKeys(self):
        """ 並列処理では使えない"""
        for word in self.__election_words:
            print word + ' ',
        print
        
    def showAllKeys(self):
        """ 並列処理では使えない"""
        for word in self.__all_words:
            print word + ' ',
        print

    def writeDict(self,output,ElectionOrAll):
        """ 並列処理では使えない"""
        if ElectionOrAll=="Election":
            words_list = self.__election_words
        else:
            words_list = self.__all_words
        for word in words_list:
            output.write(word + " ",)
        output.write('\n')
        
    def passElection(self):
        self.__election_words = list(set(self.__election_words))
        return self.__election_words


    def passAll(self):
        self.__all_words = list(set(self.__all_words))                         
        return self.__all_words

