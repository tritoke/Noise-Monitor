# Noise Monitor Project

### Background Info
I completed this project during a 1 week work experience at Embecosm. This was a real-world project offered to me prior to my arrival which I decided to attempt

### About The Project
My project consists of a Python 3 file, which then creates a PNG file and a CSV file, and it sends emails. The first section of code imports all the packages you will need throughout the code. The 'fs' variable is the sample rate of your recording and the 2 empty list are where your recorded data goes. Datestring and Timestring save the current date and time as separate variables.
The point function allows the program to obtain a piece of data every 10 seconds, the way I have set it up means that the recorded piece of data, is the loudest point during a 10 second time period. The sys.argv parts work alongside a cron tab so that the code runs between 8am and 6pm on weekdays, and between midday and midnight on weekends. The while loop makes sure the code automatically ends once the current time reaches 6pm or midnight (depending on the day), it also prints the time of each 10 second recording (as a decimal) and the max point (noisiest). The next section of code involves the matplotlib function as plt. This creates our graph using the 2 data sets: time and sound; and saves it as a PNG file. The next section takes our 2 data sets, and saves them as a CSV file. After the 'wait.sleep(5)', is when the email is formulated and sent. The first part is taking Google's SMTP server address, so you can send emails using Python through Gmail. The next part is the username and password to the email you are using to send the data across from, which is followed by where you are sending the email to, and what the email will contain, which are the 'msg' and 'files'. The section after that allows the email to send the additional files as attachments, before finally sending the email. That is the end of the code.

### Installation Requirements
matplotlib, sounddevice, numpy
