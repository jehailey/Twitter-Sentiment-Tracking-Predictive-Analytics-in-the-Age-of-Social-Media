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


# trump_vector: (-1, 1) -1 negative, 1 positive
# (key, value) = (doc#, degree)
trump_vector = {}

# store lists of hashtag for trump
trump_word_hash = {}

# dictionary from training data 
train_dict = {}



# MAIN()
#
# Read in the file
# Call each line 
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
	print len(trump_vector)
	num_pro_and_con(line_num)
	write_label(line_num)

	file.close()


# HASHTAG_POLARITY_DETECTION
#
# Return: True (if hashtag gave enough evidence)
#		  False (if further investigation needed)
#
# Find the hashtag, figure out whether pro or anti trump or 
# neutral (ambiguous) and insert asociative value into each vector
def hashtag_weighting(line_num, hash_word, words): 

	hashtag_exist = False
	
	regex_t = re.compile(r'fortrump', re.IGNORECASE)

	for tag in hash_word:  # check trump hashtags 
		if trump_word_hash.has_key(tag): 	
			if trump_vector.has_key(line_num): 
				trump_vector[line_num] += trump_word_hash[tag]*5
			else: 
				trump_vector[line_num] = trump_word_hash[tag]*5		
			hashtag_exist = True 

		# handing "#__fortrump" hashtag 
		if regex_t.findall(tag): 	 
			if trump_vector.has_key(line_num):
				trump_vector[line_num] += 5
			else: 
				trump_vector[line_num] = 5		
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

	# find #trump text and look for +/- 4 indexing 
	regex = re.compile(r'Trump|republic', re.IGNORECASE)
	if regex.findall(hash_word):
		ambi_hash = trump_region_weighting(hash_index, line_num, words)

	return ambi_hash 


# TERM_WEIGHTING
# 
# Parameters: text 
# 
# Extract common words, identify either clinton/hilary or Trump
# Use positive/negative dictionary to weight 
def term_weighting(line_num, words): 

	if special_anti_trump(line_num, words):
		return True 

	kwd_vect_t = [] 
	Trump_words = ["trump", "republic", "donald"]

	# find the index for all keywords 
	for index in range(len(words)):  
		if words[index] in Trump_words: 
			kwd_vect_t.append(index) # find all index for trump

	# if empty index, then 1. neutral? (yes, cause its almost impossible)
	if len(kwd_vect_t) == 0: 
		return False 

	# region weighting by keyword 
	for index in kwd_vect_t:
		trump_region_weighting(index, line_num, words)

	# term weighting 
	if len(kwd_vect_t) != 0:
		for word in words:
			if word in train_dict:
				if trump_vector.has_key(line_num):
					trump_vector[line_num] += train_dict[word]
				else: 
					trump_vector[line_num] = train_dict[word]


# WRITE_LABEL
#
# write to the separate text file of label 
def write_label(line_num):

	file = open("label.txt", 'w')

	# label -1 as negative, 0 as ambiguous and 1 as positive 
	for i in range(1, line_num):
		if trump_vector.has_key(i):
			if trump_vector[i] > 0:
				file.write("1")
				file.write("\n")
			elif trump_vector[i] < 0:
				file.write("-1")
				file.write("\n")
			elif trump_vector[i] == 0: 
				file.write("0")
				file.write("\n")
		else:
			file.write("0")
			file.write("\n")
	file.close() 


# SPECIAL_ANTI_TRUMP
#
# Russia/Putin with words from anti-trump-Russia will be anti-trump
def special_anti_trump(line_num, words):

	# negative words when used with Russia, putin, then negative
	special_russia = {}
	for line in open("dictionary/anti-trump-russia.txt", 'r'):
		line = line.strip()
		special_russia[line] = -1 #since all negative words

	special_tax = ["returns", "ask", "leak", "release",
			"show", "bankruptcy", "trump" "pay"]
	# look through range of -3, 3 and find if russia or putin exist

	for index in range(len(words)):
		if words[index] == "putin" or words[index] == "russia":
			for i in range(-3,4):
				if (index + i) < len(words) and (index + i) > -1:
					if words[index + i] in special_russia:
						if trump_vector.has_key(line_num):
							trump_vector[line_num] += -5
						else: 
							trump_vector[line_num] = -5
						return True
		if words[index] == "tax":
			for i in range(-3,4):
				if (index + i) < len(words) and (index + i) > -1:
					if words[index + i] in special_tax:
						if trump_vector.has_key(line_num):
							trump_vector[line_num] += -5
						else: 
							trump_vector[line_num] = -5
						return True
					if words[index + i] == "lower":
						if trump_vector.has_key(line_num):
							trump_vector[line_num] += 5
						else: 
							trump_vector[line_num] = 5
						return True						
	return False


# NUM_PRO_AND_CON
#
# Parameters: line-num
#
# calculate the number of pro, anti for clinton and trump
# by finding positive or negative 
def num_pro_and_con(line_num):

	trump_pro = 0
	trump_anti = 0

	for i in range(line_num):
		if trump_vector.has_key(i):
			if trump_vector[i] > 0:
				trump_pro = trump_pro + 1
			elif trump_vector[i] < 0:
				trump_anti = trump_anti + 1

	trump = float(trump_pro + trump_anti)
	print "trump: ", trump_pro, trump_anti
	print "trump%: ", float(trump_pro/trump), float(trump_anti/trump)



# TRUMP_REGION_WEIGHTING
#  
# region weighting nearby the keywork (index)
def trump_region_weighting(index, line_num, words):

	found = False 
	for i in range(-3, 4):
		if (index + i) < len(words) and (index + i) > -1: 
			if words[index + i] in train_dict:	# if the word exists in train_dict
				if trump_vector.has_key(line_num):
					trump_vector[line_num] += return_weight(i) -1
				else: 
					trump_vector[line_num] = return_weight(i) -1 
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

	# read in all the pro/anti hashtags 
	for line in open("dictionary/pro-trump.txt", "r"):
		line = line.lower()
		trump_word_hash[line.strip()] = 1;

	for line in open("dictionary/anti-trump.txt", "r"):
		line = line.lower()
		trump_word_hash[line.strip()] = -1;



# OPEN_DICTIONARY
# 
# Read in positive/negative words 
# pro as positive, anti as negative 
def open_dictionary():

	file = open('train/Trump_tweets_sentiment.csv', 'r')	# open train file
	reader = csv.reader(file, delimiter = ',')
	negative = 0
	positive = 0 

	for row in reader:
		myre = re.compile(r"\w{4,}", re.UNICODE) 			# create list of words
		line = row[2].lower()
		words = myre.findall(line)

		for index in range(0, len(words)): 					# remove urls 
			if words[index] == "http" or words[index] == "https":
				words = [words[k] for k in range(0, index)]
				break

		value = 0
		if row[7] != "Sentiment": 							# create label list
			value = float(row[7])
		if value > 0: 										# normalize number of 
			if positive < 6000:							# positive and negative
				positive = positive + 1						# datasets 
				insert_words(words, value)
		elif value < 0:
			if negative < 6000:
				negative = negative + 1
				insert_words(words, value)

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

	# open all helpful hashtags 
	open_hashtag() 

	# open train data and train model 
	open_dictionary() 

	# call main function 
	main()



