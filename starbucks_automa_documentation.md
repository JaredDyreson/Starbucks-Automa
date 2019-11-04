# Starbucks Automa

## What is this program

Quite simply, this was a project created to automate the input of my Starbucks work schedule directly to my Google Calendar.
This project was quite primitive in early development, where everything was handled in one script.
Overtime and constant refactoring, separate modules were created to consolidate functionality and help keep my sanity.
The final rewrite of this program took the preexisting code base and optimized it heavily, leading to fast runtime.

## Stack

Here is a list of the external Python modules needed:

- selenium
- google-api-python-client 
- google-auth-httplib2 
- google-auth-oauthlib
- datetime
- json
- collections 

## How does it work (Logging in and scraping the page)

First, we load a webdriver instance (Firefox in this case) this driver is sent to a class called `driver_utils` wherein control over the driver is handled.
Here we are able to create methods to get through the three stages of a login; username, two factor authentication and password.
These functions have also been stitched together in another function to be used in other scripts.
The engineers at Starbucks decided not to change this login page for the other portal and that method can login from either URL provided.
All of the settings/crucial information for the program is stored in a `credentials.json` file and yes, I am aware of how blatantly stupid this is.
Future revisions will include a SQL database so plain text is not used, but in all honesty, why would anyone want to see my work schedule.
Extracting all the information for login and authentication is handled with a small json parsing class which can be called once at the top of every script.
This allows for me to show you the source code without fear of you logging into my partner portal ;) .
Once logged in, we need to find a certain element on the page that holds all the information we need to scrape.
In all of Starbucks engineering department's infinite wisdom, they decided to embed two webpages but the webdriver is only allowed to access elements on the outer layer.
Think of it like a picture in a frame; you can see the picture but you can't physically touch it.
This problem took way too long for me to crack. I initially just gave up because I couldn't access the information but I tried saving the page by pressing CTRL+S.
I was then able to `grep` for key terms throughout the files and found there was indeed another HTML file embedded in another folder.
This was then addressed by using a combination of `pyautogui` and `beautifulsoup` to accomplish the scraping portion.
The actual algorithm implemented is covered the section below.
Anyways, I allowed the code to be as it was and it worked for a while. I just had this feeling that the code could be better so I decided to take a deeper dive.
It turns out you could find element of the whole box in which the calendar was contained in. 
That subsequently had an attribute of a link, which when loaded, opened a new window with access to the calendar.
The same logic was applied from the old code and the janky solution for scraping the page was thrown out.
Seriously, I had to have file exception handling and using `beautifulsoup` for HTML parsing.
I will say that `selenium` definitely has done it right when it comes to method naming.
I could not stand `beautifulsoup`'s version.


## How does it work (Getting the dates to align algorithm)

The one problem that I had to deal with was scraping this:
![alt text](assets/calendar_view.png)
As you can see, the date and time do not align. Even if I was able to successfully scrape all of the times, the corresponding date would be wrong.
What I ended up doing was something I initially thought wouldn't be a viable solution but turned out to be perfect.
Since I had this key piece of information:

![alt text](assets/week_view.png)

I was able to generate a list of seven `datetime.datetime` objects and treat them as constants.
These would then be stitched with proper `datetime.datetime.time` objects.
While creating this, I found myself more in need of a dictionary rather than a stand alone list as a start and an end time were present but attached to a common date.
Initial iterations, used a primitive class called `time_struct` which was meant to extend the functionality of a regular dictionary where it is a direct key->value system.
Many random functions scattered across multiple modules found their way to be integrated into the `time_struct` class as it allowed for cleaner code.
The biggest weakness of early versions was the lack of consolidation of work, where we needed to import modules constantly for only one use.
Getting back to `time_struct`, we decided to add a flag if we were working or not.
This becomes quite helpful when we are scraping the page for times.
Since every box can contain a certain element varying from a working time, to text saying "Time Off", we can use this a condition.
If the box contains the element (in the case of the picture the green box), we can create a list of `time_struct` objects with either passed in start and end times or predetermined times that can be ignored.


## How does it work (Filtering out bad dates)

Since we now have a consolidated list of `time_struct` objects, we can then thin down by passing this into a `starbucks_week` class.
One of the parameters is this list, where it is then filtered into another list based on the condition if the working flag is present. By default, `time_struct` has this labeled to false.
We can then safely work with valid `time_struct` objects, calculating the total time, possible revenue and adding them to the calendar.


