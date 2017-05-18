# Jeong eun Lee (jlee562)
# Arpan Ghosh (aghosh17)
# EN.600.466 Informational Retrieval and Web Agents  

# Python Script for Sentiment Analysis on given data

import sys
import math
import re
import os
import csv
import subprocess

# clinton_vector: (-1, 1) -1 negative, 1 positive
# (key, value) = (doc#, degree)
ambiguous_vector = {}

# clinton_vector: (-1, 1) -1 negative, 1 positive
# (key, value) = (doc#, degree)
clinton_vector = {}

# store lists of hashtag for clinton 
clinton_word_hash = {}

# dictionary from train doc
train_dict = {}



def main():

	line_num = 1
	count_1 = 1 

	try: 
		file = open(sys.argv[1], 'r')			# open file 
	except Exception as e: print(e)

	for row in file: 
		myre = re.compile(r"\w{4,}", re.UNICODE)
		myhash = re.compile(r"#[a-z]+", re.UNICODE)
		line = row.lower()
		words = myre.findall(line) 			# list of words 
		hash_word = myhash.findall(line)	# list of hashtags

		for index in range(0, len(words)): 
			if len(words[index]) < 3: 
				words.remove(words[index])
			if words[index] == "http" or words[index] == "https":	#remove url
				words = [words[k] for k in range(0, index)]
				break
		if hash_word:				# if hashtag can distinguish pro-or-anti trump
			hashtag_weighting(line_num, hash_word,words)
			count_1 = count_1 + 1
		else:						# if not, then term weight overall sentence 
			term_weighting(line_num, words)

		line_num = line_num + 1 	# count entire line number 

	print count_1, line_num
	print len(clinton_vector)
	num_pro_and_con(line_num)
	write_label(line_num)
	expand_train(line_num)
	file.close()


# HASHTAG_POLARITY_DETECTION
# 
# Return: True (if hashtag gave enough evidence)
#		  False (if further investigation needed)
#
# Find the hashtag, figure out whether clinton, trump, or 
# neutral (ambiguous) and insert asociative value into each vector
def hashtag_weighting(line_num, hash_word, words): 

	hashtag_exist = False
	
	regex_c = re.compile(r'forclinton | forhilary', re.IGNORECASE)

	for tag in hash_word: 	# check clinton hashtags 
		if clinton_word_hash.has_key(tag): 		
			if clinton_vector.has_key(line_num): 
				clinton_vector[line_num] += clinton_word_hash[tag]*5
			else: 
				clinton_vector[line_num] = clinton_word_hash[tag]*5
			hashtag_exist = True  

		# handing "#__forclinton" hashtag 
		if regex_c.findall(tag): 	 
			if clinton_vector.has_key(line_num): 
				clinton_vector[line_num] += 5 
			else: 
				clinton_vector[line_num] = 5		
			hashtag_exist = True 

	if hashtag_exist == False: 	# if ambiguous hashtag
		for word in hash_word:	
			if ambiguous_hashtag(line_num, word, words):
				hashtag_exist = True

	# if ambiguous, return false, else found, return true 
	return hashtag_exist


# AMBIGUOUS_HASHTAG
# 
# Parameters: hash_word, text 
# 
# If its not clearly pro or anti, like #election, #Trump, 
# then find words +/- 4 (region (term) weighting)
# and put into doc_vector and doc_simula only when not sure 
def ambiguous_hashtag(line_num, hash_word, words): # region weighting focus 

	ambi_hash = False

	hash_index = 0 
	for index in range(len(words)):
		if hash_word == words[index]:
			hash_index = index

	# find #clinton text and look for +/- 4 indexing 
	regex = re.compile(r'hilary|clinton|democrat', re.IGNORECASE)
	if regex.findall(hash_word):
		ambi_hash = clinton_region_weighting(hash_index, line_num, words)

	return ambi_hash 


# TERM_WEIGHTING
# 
# Parameters: text 
# 
# Extract common words, identify either clinton/hilary or Trump
# Use positive/negative dictionary to weight 
def term_weighting(line_num, words): 

	if special_anti_clinton(line_num, words):
		return True 

	kwd_vect_c = []
	Clinton_words = ["democrat", "clinton", "hilary", "hillary"]

	# find the index for all keywords 
	for index in range(len(words)):  
		if words[index] in Clinton_words:
			kwd_vect_c.append(index) # find all index for clinton 
	
	if len(kwd_vect_c) == 0:
		return False

	# region weighting by keyword 
	for index in kwd_vect_c:
		clinton_region_weighting(index, line_num, words)

	# term weighting 
	if len(kwd_vect_c) != 0:
		for word in words:
			if word in train_dict:
				if clinton_vector.has_key(line_num):
					clinton_vector[line_num] += train_dict[word]
				else: 
					clinton_vector[line_num] = train_dict[word]


# EXPAND_TRAIN
#
# write more train data 
def expand_train(line_num):

	infile = open(sys.argv[1], 'r')
	outfile= open('train/clinton_train.csv', 'a+')	# open train file
	reader = csv.reader(infile, delimiter = ',')
	writer = csv.writer(outfile)
	writer.writerow("")
	neg = 0 
	pos_line = []
	neg_line = []

	for val in clinton_vector.values():
		if val < -10:
			neg = neg+1

	print neg
	for i in range(1, neg/2):
		max_num = max(clinton_vector, key=lambda i: clinton_vector[i])
		if clinton_vector[max_num]< 0:
			break 
		del clinton_vector[max_num]
		pos_line.append(max_num)

	for i in range(1, neg/2):
		min_num = min(clinton_vector, key=lambda i: clinton_vector[i])
		if clinton_vector[min_num] > 0: 
			break
		del clinton_vector[min_num]
		neg_line.append(min_num)

	line_count = 1
	for row in reader:
		if line_count in pos_line:
			line = [row[0], '1']
			writer.writerow(line)
		elif line_count in neg_line:
			line = [row[0], '-1']
			writer.writerow(line)
		line_count = line_count + 1

	infile.close()
	outfile.close()
	return 


# WRITE_LABEL
#
# write to the separate text file of label 
def write_label(line_num):

	file = open("label.txt", 'w')

	# label -1 as negative, 0 as ambiguous and 1 as positive 
	for i in range(1, line_num):
		if clinton_vector.has_key(i):
			if clinton_vector[i] > 0:
				file.write("1")
				file.write("\n")
			elif clinton_vector[i] < 0:
				file.write("-1")
				file.write("\n")
			elif clinton_vector[i] == 0: 
				file.write("0")
				file.write("\n")
		else:
			file.write("0")
			file.write("\n")
	file.close() 


# SPECIAL_ANTI_CLINTON
#
# Russia/Putin with words from anti-trump-Russia will be anti-trump
def special_anti_clinton(line_num, words):

	# if Hilary/Clinton and emails appear at the same time, then anti-clinton
	special_clinton = ["liar", "crooked", "email", "corrupt", "rotten"]

	# look through range of -3, 3 and find if the above words exist with clinton
	for index in range(len(words)):
		if words[index] == "clinton" or words[index] == "hillary":
			for i in range(-3,4):
				if (index + i) < len(words) and (index + i) > -1:
					if words[index + i] in special_clinton:
						if clinton_vector.has_key(line_num):
							clinton_vector[line_num] += -5
						else: 
							clinton_vector[line_num] = -5
						return True
					
	return False


# NUM_PRO_AND_CON
#
# Parameters: line-num
#
# calculate the number of pro, anti for clinton and trump
# by finding positive or negative 
def num_pro_and_con(line_num):

	clinton_pro = 0
	clinton_anti = 0

	for i in range(line_num):
		if clinton_vector.has_key(i):
			if clinton_vector[i] > 0:
				clinton_pro = clinton_pro + 1
			else:
				clinton_anti = clinton_anti + 1

	clinton = float(clinton_pro + clinton_anti)

	print "clinton: ", clinton_pro, clinton_anti
	print "clinton%: ", float(clinton_pro/clinton), float(clinton_anti/clinton)


#CLINTON_REGION_WEIGHTING
#  
# region weighting nearby the keywork (index)
# with given index, word vector, and line number
def clinton_region_weighting(index, line_num, words):

	found = False 
	for i in range(-3, 4):
		if (index + i) < len(words) and (index + i) > -1: 
			if words[index + i] in train_dict: # if the word exists in train_dict
				if clinton_vector.has_key(line_num):
					clinton_vector[line_num] += return_weight(i) -1
				else: 
					clinton_vector[line_num] = return_weight(i)	-1
				found = True	

	return found 


# RETURN_WEIGHT
#
# Parameter index
#
# return the term weight in terms of index 
def return_weight(index):

	term_weight = 1 

	if index == 1: 
		term_weight = 5
	elif index == 2:
		term_weight = 4 
	elif index == 3:
		term_weight = 3
	elif index == 4:
		term_weight = 2

	return term_weight


# OPEN_HASHTAG
# 
# Read in Hashtag_comp text file 
# Store in clinton/trump word hash 
# pro as positive, anti as negative 
def open_hashtag():

	# read in all the pro/anti words 
	for line in open("dictionary/pro-clinton.txt", "r"):
		line = line.lower()
		clinton_word_hash[line.strip()] = 1;

	for line in open("dictionary/anti-clinton.txt", "r"):
		line = line.lower()
		clinton_word_hash[line.strip()] = -1;


# OPEN_DICTIONARY
# 
# Read in positive/negative words 
# pro as positive, anti as negative 
def open_dictionary():

	file = open('train/clinton_train.csv', 'r')	# open train file
	reader = csv.reader(file, delimiter = ',')
	negative = 0
	positive = 0 
	line_num = 0 

	for row in reader:
		myre = re.compile(r"\w{4,}", re.UNICODE) 			# create list of words
		if len(row) == 0:
			return 
		line = row[0].lower()
		words = myre.findall(line)

		for index in range(0, len(words)): 					# remove urls 
			if words[index] == "http" or words[index] == "https":
				words = [words[k] for k in range(0, index)]
				break
		value = float(row[1])								# create label list
		if value > 0: 										# normalize number of 
			if positive < 600000:							# positive and negative
				positive = positive + 1						# datasets 
				insert_words(words, value)
		elif value < 0:
			if negative < 600000:
				negative = negative + 1
				insert_words(words, value)			##### change this to cope with clinton model 
		line_num = line_num + 1
	train_dict.pop('trump', None)		# some keywords that 
	train_dict.pop('clinton', None)		# can skewe the model
	train_dict.pop('hillary', None)
	file.close()

	return 


# INSERT_WORDS 
#
# insert the value for each word in train_dict
def insert_words(words, value):

	for word in words:
		if train_dict.has_key(word):
			train_dict[word] += value
		else:
			train_dict[word] = value


if __name__ == "__main__": 

	# open all text and put it into hash/vector 
	open_hashtag() 
	open_dictionary() 

	# call main function 
	main()



