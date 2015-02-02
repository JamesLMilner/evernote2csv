import sys
import csv
import os
import copy
from bs4 import BeautifulSoup as soup

### ASSIGN IN THE SCRIPT
cardshtml = "tchtml3.html" # The directory and name HTML File
cardscsv = "cards.csv" # The directory and name of the outputted CSV

try:
    if sys.argv[1] != None:
        cardshtml = sys.argv[1]
    if sys.argv[2] != None:
        cardscsv = sys.argv[2]
except IndexError:
    pass
    

def cards2csv(cardshtml, cardscsv):

    businesscards = open(cardshtml,'r').read()
    html = soup(businesscards)
    event = os.path.basename(cardshtml)
    if event.endswith('.html'):
        event = event[:-5]
    
    cards = [ ]

    csv_row = {
        "event" : event,
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
    }

    #Dictionaries don't preserve order so we must state the order we want out
    csv_fields = [
        "event",
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
        "address"
        ]

 
    for contact in html.find_all('div', style=True):

        #Go through contacts, avoid duplicates with divs x-evernote:contact-title or x-evernote:contact-org
        if "x-evernote:contact" in contact['style'] and "x-evernote:contact-" not in contact['style']:
            row = copy.copy(csv_row)
            
            for link in contact.find_all('a', href=True):
                if "mailto:" in link['href']:
                    if "@" in link.text and "." in link.text:
                        #check it's a valid email
                        row['email'] = link.text
                if "www.linkedin.com" in link['href']:
                    row['linkedin'] = link['href']
                
                if "maps.google.com" in link['href']:
                    row['address'] = link.text

            for span in contact.find_all('span', style=True):
                if "x-evernote:display-as; -evernote-editable:field;" in span['style']:
                    row['firstname'] = span.text.split(" ")[0] #first name 
                    row['lastname'] = span.text.split(" ")[1] #last name
                   
                if "x-evernote:contact-title; -evernote-editable:field;" in span['style']:
                    row['position'] = span.text
             
                if "x-evernote:contact-org; -evernote-editable:field;" in span['style']:
                    row['company'] = span.text
        
            for div in contact.find_all('div', style=True):
                if "x-evernote:phone; -evernote-editable:phone;" in div['style']:
                    
                    if "mobile" in div.text:
                        row['mobile'] = div.text.replace("mobile", "").replace(" ", "").replace("\n", "")
                    
                    if "phone" in div.text:
                        row['telephone'] = div.text.replace("phone", "").replace(" ", "").replace("\n", "")
                        
                    if "fax" in div.text:
                        row['fax'] = div.text.replace("fax", "").replace(" ", "").replace("\n", "")
                        
                if "x-evernote:twitter;" in div['style']:
                    row['twitter'] = div.a.text
            #print row
            cards.append(row)
            

    #Write to the CSV file1
    try:
        with open(cardscsv, 'wb') as csvfile:
            fieldnames = csv_fields
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for card in cards:
                writer.writerow(card)
                print "Writing :", card['firstname'], card['lastname'], "to", cardscsv
            print "Cards written to: ", cardscsv
    except IOError:
        print "IO error, the csv may already be open or being operatded on"

### Run

if __name__ == "__main__":
    cards2csv(cardshtml, cardscsv)
