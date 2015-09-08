#---------------------------------------------------------------------------------------------------
#Note Extraction Script designed by Paul Kasay at King's College London
#The script is meant to take a permalink url from a Tumblr post
#And extract the a complete set of note information for reblogs of a post
#---------------------------------------------------------------------------------------------------

from bs4 import BeautifulSoup
from bs4 import BeautifulStoneSoup
import urllib2
import re
import os
import os.path
import shutil
import time
import errno
from socket import error as socket_error

#Defining the initial function getnotes with the objective of:
#recording the blog information, isolating the <div> that contains the notes,
#and recording the unique id for loading further notes pages

def getnotes(url):
    #For ease of use and to be able to save progress, each new pass prints its start point and the URL
    print "Began parsing a new URL"
    print url

    #Due to server demands on tumblr, which can often result in server timeouts
    #As well as to be kind citizens and not overload any one site
    #We step back from URL calls, attempt the connection, and wait after it is denied to try again
    c = 0
    while True:
        print "Attempting Connection..."
        try:
            conn = urllib2.urlopen(url)
            page_source = conn.read()
            conn.close()
            print 'Successfully loaded URL!'
            break
        except socket_error as sock_tempt:
            print sock_tempt
            print "Waiting..."
            time.sleep(2)
            c += 1
            if c == 5:
                print "Did not manage to load the URL - Error!"
                break

    blog_name_info = url.split("/")                 #the url is split along the slashes
    blog_url = blog_name_info[2]                    #the main blog url is isolated
    blogname = blog_url.strip(".tumblr.com")        #and the name extracted
    post_number = blog_name_info[4]                 #the post number is saved as well

    #an already existing diretory is used - It collects the generated notes folders
    #the name of each new directory is structured as "Notes_from_<Blog> - <Post_Number>"
    #the file that will be written will be called "Notes"
    myDirectory = "/Users/isra/Desktop/notes"
    folderName = "Notes_from_" + blogname + "_" + post_number
    folderNew = myDirectory + "/" + folderName + "/"
    filename = "Notes"
    #if the collection folder does not exist, it is made
    #if the folder already exists then the script appends to the information already recorded
    if not os.path.exists(folderNew):
        os.mkdir(folderNew)

    #the Page Source from the URL is opened and stored as a BeautifulSoup object
    soup = BeautifulSoup(page_source)

    #--if the page has less than 50 notes, they will all be shown immediately
    #and thus the page will not have a "More Notes" button
    #---the presence of this button is checked for
    #and if it is not found in the page source
    #the notes section is isolated, then all items that have "reblog" are found
    #this list is then iterated over with added spacing for readability
    #and saved to the output file
    if "more_notes_link" not in page_source:
        small_notes_section = str(soup.find_all("ol",{"class":"notes"}))    #the notes div is isolated
        small_notes_soup = BeautifulSoup(small_notes_section)               #converted into a Soup object
        small_reblog = small_notes_soup.find_all("li",{"class":"reblog"})   #and each list item that is a reblog, as opposed to like, is saved


        #if the file already exists, the new information is appended
        #this allows the script to fail and still save all of the passes it was able to accomplish
        #and since we print out each url is generated and parsed, we can pick up where we left off
        if os.path.isfile(folderNew+filename+".txt"):
            outputFile = open(folderNew+filename+".txt", "a")
            for i in small_reblog:
                outputFile.write("\n"+str(i)+"\n")
        else:
            outputFile = open(folderNew+filename+".txt", "w")
            for i in small_reblog:
                outputFile.write("\n"+str(i)+"\n")

    #if the page has more than a certain number of notes (often more than 50), the first 25 or 50 will show
    #the rest will need to be requested from the tumblr API
    #--the function stored in the "More Notes" button is found and searched inside of
    #the variable uniqueID stores the token for the individual tumblr site
    #the post number and key are saved, striped, and used to create a URL
    #this URL holds the API request for the next 50 notes
    elif "more_notes_link" in page_source:
        notes_load_button = str(soup.find_all("a",{"class":"more_notes_link"}))
        uniqueID = str(re.findall("tumblrReq\.open\('GET','(.*?)\?", notes_load_button))
        IDparts = uniqueID.split("/")
        post = IDparts[2]
        key_location = IDparts[3]
        key = key_location.strip("']")
        if "?from_c=" not in url:
            if "notes" in url:
                main = str(re.findall("(.*?)/notes", url)).strip("['']")
                print "This is main from notes without C: " + main
                notes_url = str(main + "/notes/" + post + "/" + key)
            if "post" in url:
                main = str(re.findall("(.*?)/post", url)).strip("['']")
                print "This is main from posts without C: " + main
                notes_url = str(main + "/notes/" + post + "/" + key)
                #and save notes
        elif "?from_c=" in url:
            main = str(re.findall("(.*?)\?", url)).strip("['']")
            print "This is main from notes with C: " + main
            next_set_ID_raw = str(re.findall("\?from_c=(.*?)\'", notes_load_button))
            next_set_ID = next_set_ID_raw.strip("['']")
            notes_url = str(main + "?from_c=" + next_set_ID)
            print "notes_url is " + notes_url

        notespage_url = notes_url.strip("['']")
        print "Notespages_url is " + notespage_url
        time.sleep(2)
        #once the URL for the request is created
        #it is opened, read in, and closed

        c = 0
        while True:
            print "Attempting Connection 2..."
            try:
                conn = urllib2.urlopen(notespage_url)
                notes_page_source = conn.read()
                conn.close()
                print 'Successfully loaded URL2!'
                break
            except socket_error as sock_tempt:
                print sock_tempt
                print "Waiting..."
                time.sleep(2)
                c += 1
                if c == 35:
                    print "Did not manage to load the URL - Error!"
                    break

        #this pagesource is converted into a BeautifulSoup object as well
        notesoup = BeautifulSoup(notes_page_source)
        #the notes page is parsed for reblogs and these are written to a new text file
        if "more_notes_link" in notes_page_source:
            reblogs = notesoup.find_all("li",{"class": "reblog"})
            original = notesoup.find_all ("li",{"class":"original_post"})
            print "Continuing"
            if os.path.isfile(folderNew+filename+".txt"):
                outputFile = open(folderNew+filename+".txt", "a")
                for i in reblogs:
                    outputFile.write("\n"+str(i)+"\n")
                if "original_post" in notes_page_source:
                    outputFile.write("Original post: \n")
                    outputFile.write(str(original))

            else:
                last_notes_section = str(soup.find_all("ol",{"class":"notes"}))
                last_notes_soup = BeautifulSoup(last_notes_section)
                last_reblog = last_notes_soup.find_all("li",{"class":"reblog"})

                if os.path.isfile(folderNew+filename+".txt"):
                    outputFile = open(folderNew+filename+".txt", "a")
                    for i in last_reblog:
                        outputFile.write("\n"+str(i)+"\n")
                else:
                    outputFile = open(folderNew+filename+".txt", "w")
                    for i in last_reblog:
                        outputFile.write("\n"+str(i)+"\n")
                print "Finished!"

            #then the key that will request the next 50 notes is found and saved
            notes_page_load_button = str(notesoup.find_all("a",{"class":"more_notes_link"}))
            next_set_ID_raw = str(re.findall("\?from_c=(.*?)\'", notes_page_load_button))
            next_set_ID = next_set_ID_raw.strip("['']")
            print next_set_ID

            #and this key is used to create the URL for the next set of notes
            if "?from_c=" not in url:
                newnotespage = notespage_url + "?from_c=" + next_set_ID
                print "Newnotespage is " + newnotespage
            if "?from_c=" in url:
                newnotespage_base = str(re.findall("(.*?)\?", url))
                print "Newnotespage_base is " + newnotespage_base
                newnotespage_raw = newnotespage_base.strip("['']")
                print "Newnotespage_raw is " + newnotespage_raw
                newnotespage = newnotespage_raw + "?from_c=" + next_set_ID
                print "Newnotespage is " + newnotespage
            #which is then fed back into the original function
            time.sleep(2)
            print "End Pass"
            #the function is then recursively called and the loop runs until there are no additional notes to load
            getnotes(newnotespage)

#The script requests the URL inside of the terminal for ease of use
getnotes(raw_input("Please type the full URL for the post you'd like to investigate: "))
#Note: when you call the function, you must feed it a full permalink URL from Tumblr
