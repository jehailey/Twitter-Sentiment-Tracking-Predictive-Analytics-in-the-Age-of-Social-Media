
import csv
import re
import os
import sys 


file = open(sys.argv[1], 'r')
reader = csv.reader(file, delimiter = ',')

count_n = 0
count_p = 0 
ambiguous = 0

# for every row, if positive, posfeat or if negative, negfeat 

for row in reader:
	value = row[1]
	if row[1] != 'i':
		value = float(row[1]) 
	if value > 0:
		count_p = count_p + 1
	elif value < 0:
		count_n = count_n + 1
	elif value == 0:
		ambiguous = ambiguous + 1


print "positive ", count_p
print "negative ", count_n
print "neutral ", ambiguous

file.close()
