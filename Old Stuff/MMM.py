import random
from collections import Counter
numbers = [] #Empty list which does not have any numbers stored in it
loop = True
print('|_List cleared!_|') #Lets user know the list has been cleared
numbers.clear() #Clears the list from the previous values which are still stored from the last test
inp = str(input('What is your name? ')) #Used for the procedure down below


def name(hello): #Procedure name, takes the given name in inp, and uses it for all of the code below. Refers to the user's name when printing out to be more formal
    print(hello + ', for reference here is your list down below. \n')
    print(*numbers, sep = ',') #Prints the list which is all seperated by commas
    print('\n' + hello + ', your number of items in this list: ' + str(count))
    print(hello + ', your median for this list is: ' + str(median))
    print(hello + ', your mean for this list is: ' + str(mean))
    
while loop: #While loop will only break when the user is finished entering their numbers, which can be done so by entering letters or anything else other than a number
	try:
		user = float(input(('Input your following numbers here, one by one, to find the mean, median, range, and mode of them.\nIf you are done with this, enter anything other than a number to break the loop.\nEnter your number(s): ')))
		numbers.append(user) #Adds the users latest response to the list
		

	except ValueError as e: #Breaks the loop when this error is encounterd
		print('\nI will assume you have entered all your numbers.')
		break
try:
	count = len(numbers) 
	numbers.sort()

	if count % 2 == 0:
		med = numbers[count//2]
		med2 = numbers[count//2-1]
		median = (med + med2)/2
	else:
		median = numbers[count//2]
	mean = sum(numbers)/count
	mode = Counter(numbers)
	damode = dict(mode)
	actualmode = [x for x, k in damode.items() if k == max(list(mode.values()))] 

	if len(mode) == count:
		damode = "There is no mode for this list." #If there is no mode, prints this
	else:
		damode = "The mode(s) for this list are: " + ','.join(map(str, actualmode)) #Prints all the modes in the list

	name(inp) #Procedure being used here, easier to use it instead of typing individual print blocks
	print(damode)
	

except IndexError as e: #If the user does not enter anything, the list cannot have any median, mode, or mean, so this except block solves it with the IndexError clause
	print('The list was empty, no calculations could be performed.')