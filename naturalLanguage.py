#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson
import MeCab
import re

http_filter_pattern = re.compile ('(https?://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+)')
string_filter_pattern = re.compile (u'([0-9A-Za-z⺀-⿕ぁ-ヾ㐀-䶵一-龥豈-舘０-９Ａ-Ｚａ-ｚｦ-ﾝ]+)')
hinshi_list = ['名詞']#,'動詞','形容詞']

def stringFilter(line):
    line = http_filter_pattern.sub(" ", line)
    line = string_filter_pattern.findall(line)
    line = u"、".join(line)
    return line

def preformat(line):
    """一行を受け取り形態素解析をしてリストを返す
       連続した名詞はできるだけ長くなるように結合する
       見やすいように名詞であっても記号は取り除く"""
    tagger = MeCab.Tagger('')
    encoded_line = line.encode('utf-8')
    node = tagger.parseToNode(encoded_line)
    keywords =[]
    while node:
        node_f = node.feature.split(",")
        hinshi = node_f[0]
        genkei = node_f[6]
        if hinshi in hinshi_list:
            if genkei == "*":
                genkei = node.surface
            elif previous=='名詞' and hinshi=='名詞':
                genkei = keywords.pop() + genkei
            keywords.append(genkei)
        previous = hinshi
        node = node.next
    return keywords

def setTweet(line):
    tweet = simplejson.loads(line,"utf-8")
    tweet["text"] = stringFilter(tweet["text"])
    tweet_text = preformat(tweet["text"])[:-1]
    return tweet_text
