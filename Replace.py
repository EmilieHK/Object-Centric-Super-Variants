# creating a variable and storing the text 
# that we want to search 
search_text = ":pr_trigger"
  
# creating a variable and storing the text 
# that we want to add 
replace_text = "_pr_trigger"
  
# Opening our text file in read only 
# mode using the open() function 
with open(r'ReplaceText.txt', 'r') as file: 
  
    # Reading the content of the file 
    # using the read() function and storing 
    # them in a new variable 
    data = file.read() 
  
    # Searching and replacing the text 
    # using the replace() function 
    data = data.replace(search_text, replace_text) 
  
# Opening our text file in write only 
# mode to write the replaced content 
with open(r'ReplaceText.txt', 'w') as file: 
  
    # Writing the replaced data in our 
    # text file 
    file.write(data) 
  
# Printing Text replaced 
print("Text replaced") 