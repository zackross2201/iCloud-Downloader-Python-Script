INSTALL FIRST:
Type into CMD:
"pip install pyicloud tqdm"
----------------------------
Problems that could/will occur and how to fix:
1. [ERROR] Failed to download IMG_0015.HEIC: Request failed to iCloud
   You may get a lot of these, but its just apples server saying "Slow down!" to the script. Since the script skips files that have already been
   downloaded, all you need to do is run the script after it says that its finished, and keep reapting it until theres none.
----------------------------
2. [CRITICAL ERROR] Failed to log in. Check your Apple ID and password.
   This is likey due to how you type in your details. Here's how:

Enter your Apple ID (email): thisisaexample1978@icloud.com
Enter your Apple ID Password (or App-Specific Password): example12345678 
---
NOTE: (Just type in your normal Apple ID passowrd, Ignore the app specific passoword)
---
--- Two-Factor Authentication Required ---
Enter the 6-digit code that appeared on one of your trusted Apple devices: 123456
----------------------------
The only file here (icloud_photo_downloader.py) is a python file that you can use to download all of your photos and videos from Apple iCloud. You
just download it, save it where you want. (On Windows) Right click on the path at the top where you saved it in File Expoler, click "Copy Address as
text" (or something along the lines of that) Open CMD, type in "cd *Paste the address*" and then "python icloud_photo_downloader.py" It will ask
for your apple id details, then a 2FA code sent to your devices and it should start downloading all the photos in a folder in the same folder
where the script is saved. Thats it!
