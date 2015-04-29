import sys
import csv
import os
import copy
import codecs
from bs4 import BeautifulSoup as soup


### ASSIGN IN THE SCRIPT - If not using drag and drop or command line
cardshtml = "The Next Web Europe 2015 - C" + ".html" # The directory and name HTML File

#If using command line or drag and drop, use arguments passed from the CL or dropped filed
try:
    if sys.argv[1] != None:
        cardshtml = sys.argv[1]
    if sys.argv[2] != None:
        cardscsv = sys.argv[2]
except IndexError:
    pass

event = os.path.basename(cardshtml) # Get the event name, remove absolute path prefix
if event.endswith('.html'): event = event[:-5] # Remove .html suffix
cardscsv = event + ".csv" # The directory and name of the outputted CSV, here we set it to the event name

def cards2csv(cardshtml, cardscsv):

    businesscards = open(cardshtml,'r').read()
    html = soup(businesscards)

    # This block will work out the priority of the cards in the exported HTML
    priorityCodes = [" - A", " - B", " - C"]
    if event.endswith(priorityCodes[0]):
        priority = "A"
    elif event.endswith(priorityCodes[1]):
        priority = "B"
    elif event.endswith(priorityCodes[2]):
        priority = "C"
    else:
        priority = "No priority specified"

    # This block will get the name and remove opening and trailing white space
    if event.count("-") == 2:
        inputters_name = event.split("-")[1] #The name is put inbetween two dashes i.e. TechCrunch - Joe Blogs - B
        if inputters_name[0] == " ":
            inputters_name = inputters_name.strip(" ") # If trailing opeing space, remove it
    else:
        inputters_name = "Inputter of card is unknown"
            
    cards = [ ]

    csv_row = {
        "event" : event,
        "priority" : priority,
        "inputtersname": inputters_name,
        "firstname" : "",
        "lastname" : "",
        "position" : "",
        "company" : "",
        "mobile" : "",
        "telephone" : "",
        "linkedin" : "",
        "fax" : "",
        "twitter" : "",
        "email" : "",
        "address" : "",
        "notes" : ""
    }

    #Dictionaries don't preserve order so we must state the order we want outputted - OrderedDict may overcome this?
    csv_fields = [
        "event",
        "priority",
        "inputtersname",
        "firstname",
        "lastname" ,
        "position" ,
        "company",
        "mobile",
        "telephone",
        "linkedin",
        "fax",
        "twitter",
        "email",
        "address",
        "notes"
        ]

    for contact in html.find_all('div', style=True):

        #Go through contacts, avoid duplicates with divs x-evernote:contact-title or x-evernote:contact-org
        if "x-evernote:contact" in contact['style'] and "x-evernote:contact-" not in contact['style']:
            row = copy.copy(csv_row)
            
            for link in contact.find_all('a', href=True):
                if "mailto:" in link['href']:
                    if "@" in link.text and "." in link.text:
                        #check it's a valid email
                        row['email'] = link.text.encode('utf-8')
                if "www.linkedin.com" in link['href']:
                    row['linkedin'] = link['href'].encode('utf-8')
                
                if "maps.google.com" in link['href']:
                    row['address'] = link.text.encode('utf-8')

            for span in contact.find_all('span', style=True):
                #print span.get_text()
                #nameStyle = "x-evernote:display-as; -evernote-editable:field;"
                #altNameStyle = "x-evernote:display-as; -evernote-editable:field;
                if "x-evernote:display-as;" in span['style']:
                    name = span.text.strip("Dr. ").encode('utf-8').split(" ")
                    #print name
                    row['firstname'] = name[0] #first name
                    if len(name) == 2:
                        row['lastname'] = name[1] #last name
                        #print row['lastname']
                    elif len(name) == 3:
                        row['lastname'] = unicode(name[1] + " " + name[2])
                        #print row['lastname']
                    else:
                        row['lastname'] = ""
                   
                if "x-evernote:contact-title;" in span['style']:
                    row['position'] = span.text.encode('utf-8')
             
                if "x-evernote:contact-org;" in span['style']:
                    row['company'] = span.text.encode('utf-8')
        
            for div in contact.find_all('div', style=True):
                if "x-evernote:phone;" in div['style']:
                    
                    if "mobile" in div.text:
                        row['mobile'] = div.text.replace("mobile", "").replace(" ", "").replace("\n", "").encode('utf-8')
                    
                    if "phone" in div.text:
                        row['telephone'] = div.text.replace("phone", "").replace(" ", "").replace("\n", "").encode('utf-8')
                        
                    if "fax" in div.text:
                        row['fax'] = div.text.replace("fax", "").replace(" ", "").replace("\n", "").encode('utf-8')
                        
                if "x-evernote:twitter;" in div['style']:
                    row['twitter'] = div.a.text.encode('utf-8')
                    
                if "x-evernote:note-body;" in div['style']:
                    if len(div.contents) > 0:
                        #get the text from the div. Remove excessive white space from the paragraph
                        notes = ' '.join(div.get_text().split()).encode('utf-8') 
                        print notes
                        row['notes'] =  notes
                
            cards.append(row)
            

    #Write to the CSV file1
    try:
        with open(cardscsv, 'wb') as csvfile:
            csvfile.write(codecs.BOM_UTF8) # ESSENTIAL FOR PROPER UTF-8 ENCODING - DO NOT REMOVE
            fieldnames = csv_fields
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for card in cards:
                writer.writerow(card)
 
                print "Writing :", card['firstname'], card['lastname'], "to", cardscsv
            print "Cards written to: ", cardscsv
    except IOError:
        print "IO error, the csv may already be open or being operated on"

### Run

if __name__ == "__main__":
    cards2csv(cardshtml, cardscsv)
