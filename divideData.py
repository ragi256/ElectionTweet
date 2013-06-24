#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
import sys, os
import gzip
 
if __name__ == '__main__':
    argv = sys.argv
    print '何分割？',
    number = input()
    Input = gzip.open(argv[1], 'rb')
    name = 'data'
    tail = '.txt.gz'
    total_tweet = sum(1 for line in Input)
    print argv[1] + 'は' + str(total_tweet) + '行あります'
    divide = (total_tweet / number) + 1
    Input.seek(0)
    counter = 0
    line_number = 0
    for line in Input:
        if line_number % divide == 0:
            print str(line_number/divide) + '-th writing'
            output = gzip.open(name + str(counter) + tail,'wb')
            counter += 1
        output.write(line)
        line_number += 1
 
    Input.close()


###############################################################################
