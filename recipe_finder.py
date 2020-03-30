#!/usr/bin/env python3
# # -*- coding: utf-8 -*-
""" recipe finder program"""


import math
import re
import sys
import collections



def main_dialogue():


    info_in = sys.argv[1] # adminstrator will place the program in
    # import file
    recipe_file = open(info_in,"r").read()
    #to exit loop
    exitOut = False


    #-------------------------------internal testing--------------------------#


    #to be used for testing
    copy = recipe_file.lower()

    #remove noise
    c = re.sub(r'[*,"/.:á<>#=~ä!?%_@;()-]|[\']|[\[]'," ",copy)
    d = re.sub(r'[0-9]',"",copy)
    b_o_wList = set(d.split(' ')) # to eliminate duplicates
    clean = ' '.join(b_o_wList).split()#to remove spaces


    # add the file into a dictionary
    result_recipe_dictionary = toDictionary(recipe_file,1) #use the orignal for splitting purposes
    testing_recipe_dictionary = toDictionary(c,2) #will be displayed to user

    #Step 3: calculate tf-idf
    tf_idf_scores = tf_idf(clean,result_recipe_dictionary)




    #--------------------------------------begin diaglogue--------------------------------->#
    #display intro message
    print('\n'+"Hello and welcome to Grubby Recipe Finder!"+'\n'
          '\n'+ "Today, we are going to find a recipe based on "+
              "the things you already have at home."+ "\n" +"Let's get started!"+
              "\n" +"<----------------------------------------------------------------------------------------------------->"
              +"\n")


    #begin dialogue loop
    while exitOut is False:

        #Step 1: ask user to list ingredients they have
        user = input('\n'+" List ingredients that you have on hand (Please separate by a comma(,):" )

        #Step 2: create a list to save the responses
        u_ingre = user.split(",")

        print('\n'+"The items you listed were: "+'\n') #display items listed
        num = 1

        for i in range(len(u_ingre)):
            print(num,':',u_ingre[i],'\n')
            num+=1

        print('\n'+"Thank you! Now, let's match you with recipes that best accomedates your ingredients"+'\n')

        #step 4: Search result dictionary to match user inquiry
        rec_search = find_recipe(u_ingre,testing_recipe_dictionary)#returns a list of recipes found

        #match not found
        if len(rec_search) == 0:
            print("Hmm, it seems that we were unable to find a match")

        #Step 5: Pinpoint recipe for user
        else:
            results = found_recipe(testing_recipe_dictionary,rec_search,tf_idf_scores)
        #display results
            l = "".join(results[0])
            d = " ".join(results[1])
            print(l,d)

        #ask user for another query
        user = input('\n'+"Would you like to find another recipe?  ")
        if user == 'no':
            exitOut = True  #temporary -> will be changes as we go along
            print('\n'+"Thank for using our services, have a great day!"+'\n')
            print('\n'+"You have exited the program..............."+'\n')
        else:
            exitOut = False


    # <---------------------------end of dialogue-------------------------------------------->#


def found_recipe(recipe_dict,recipe_results,tdif_score):

    matchFound = None

    #ask user to choose between the options that are available
    print('\n'+"We have located some matches, let's match you with the best one!"+'\n')
    print('\n'+"Please answer 'yes' or 'no' to the options below"+'\n')

    for match in recipe_results:

        print(match)
        answer = input('\n'+"Do you like this recipe? "+'\n')

        if answer == 'yes':
            print('\n'+"Great! Now let's see if you have additional ingredients to make this recipe"+'\n'"RESULTS:"+'\n')

            #retrieve the instructions for the recipe
            instructions = recipe_dict[match]

            #find the top three scores to match the recipe and user items
            matchFound = locateScores(instructions,recipe_dict,tdif_score)

            if matchFound == True:
                print('\n'+"Excellent, you have all the ingredients needed. Here are your results"+'\n')
                #need match -> contains key/ name of recipe
                return match , recipe_dict[match]
            else:
                print('\n'+"I'm sorry that you don't have everything, let's look for another one"+'\n')

        elif answer == 'no':
            print('\n'+"I'm sorry, let's find something else for you"+'\n')


    return "We were unable to find something for you."# returns if no results have been found

def show(return_recipe_dict,match):

    for k,v in return_recipe_dict.items():

        if match == k:
            return k

#finds the top 3 ingredients needed to make the recipe
def locateScores(instructions,recipe_dict,tdif_score):
    #create a dictionary to hold scores
    score_dict = {}

    #convert instructions into a set to remove duplicates
    instructions_list = set(' '.join(instructions).split())

    #Next step - iterate through list and recipe_dict
    for item in instructions_list:
        for k,v in tdif_score.items():
            if item in k:
                score_dict[item] = v

    #retrieve if the user has items to creat it
    canCreate = return_score(score_dict)

    return canCreate

#check if the user has items or can subsitute it
def return_score(score_dict):

    hasItem = True
    mC = 0 #increments through the list

    #put scores in order
    score = collections.Counter(score_dict)
    #retrieve 3 highest scores
    maxItem = score.most_common(3)

    while hasItem == True and mC < len(maxItem):

        val = maxItem[mC]
        answer = input('\n'+"Do you have or can subsitute the following ingredient:"+val[0].upper()+'\n')

        if answer == 'yes':
            mC += 1
        elif answer == 'no':
            hasItem = False #exits the loop
        else:
            print('\n'+"I'm sorry, but that entry was not correct. Please try again."+'\n')

    return hasItem #returns boolean value


def find_recipe(on_hand,recipes):
    #create a list to return back results
    result = []

    for items in on_hand:
        for k,v in recipes.items():
            toString = " ".join(v) #converts into string to search the keyword of ingredients from user
            if items in toString:
                result.append(k) #if keyword match, add to the list
    return result


#convert file into dictionary
def toDictionary(recipeFile,type):
    recipe_dict = {}
    #used to split the array by it's type - lower or normal case
    if type == 1:
        s = "MMMMM----- Recipe via Meal-Master (tm) v8.05"
        x = "Yield: "

    #used to retrieve the title for the user
    elif type == 2:

        s = "mmmmm      recipe via meal master  tm  v8 05"
        x = "yield  "

    #phase 1: split the array by recipe and contents
    a = recipeFile.split(s)
    #split the file by the the serving size
    for value in a:
        b = value.split(x)
        c = b[0]
        d = b[1:]
        recipe_dict[c] = d

    return recipe_dict



#tf_idf
def tf_idf(bow,rec_dict):
    # create a dictionary to hold scores
    tf_idf = {}
    #calculate tf_idf and store into dictionaries
    tf_d = tf(bow,rec_dict)
    idf_d = idf(bow)

    #loop through the dictionaries and place final score
    for (k1,v1),(k2,v2) in zip(tf_d.items(),idf_d.items()):
        if k1 == k2:
            tf_idf[k1] = v1 * v2


    return tf_idf


#calculate tf
def tf(bow,rec_dict):
    #create a dictionary to hold the value of each word
    tf_dict = {}
    #create a word count to keep track
    wc = 0

    # create a nested loop to find # word of words in the recipe
    for word in bow:
        for key,val in rec_dict.items():
            if word in key or word in val:
                wc += 1
        if wc > 0:
            tf_dict[word] = 1 + math.log2(wc)
            wc = 0
        else:
            tf_dict[word] = 0
    return tf_dict


#calculate idf
def idf(b_o_wList):

    idf_d = {}
    wc = 0
    #get the total # of words in the file
    n = len(b_o_wList)
    b_d = collections.Counter(b_o_wList)

    for word in b_o_wList:
        for key in b_d.keys():
            if word in key:
                wc +=1
        if wc > 0:
            idf_d[word] = math.log2(n/wc)
            wc = 0
        else:
            idf_d[word] = 0
    return idf_d





main_dialogue()
