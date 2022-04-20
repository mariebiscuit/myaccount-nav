# myaccount-nav

This script automates the navigation of Brown University’s MyAccount website for batch AdminID actions using the Chrome browser.

The user inputs a csv file containing identifying information of the users they would like to access on MyAccount (Login/Email/Banner ID/ Brown ID/Net ID). The program can then perform:
- Reading: Generate a CSV file containing information scraped from the “Overview” page of a user’s MyAccount.
- Creating: Create AdminIDs for a specific app for a batch of users, setting a comment and “Performed By:” field, and also automatically setting “End Date’ attentions for students and affiliates. The script will not create an AdminID if it finds that a user is terminated and not an affiliate. Also generates a CSV file of information as per the Reading function.
- Deleting: Delete AdminIDs for a specific app for a batch of users, setting a comment, “Performed By” and “Expiry Reason” fields. Also generates a CSV file of information as per the Reading function.
- Purging: Purging AdminIDs for a specific app for a batch of users.  Also generates a CSV file of information as per the Reading function
- Commenting: Add a comment to the AdminID for a specific app for a batch of users. Also generates a CSV file of information as per the Reading function.

[Quickstart Guide](https://docs.google.com/document/d/1OxWnFVyNsECtqon6fnsNbsno8AVexNi_AIQ2kAiB4ig/edit#heading=h.6uu6py7jyo9p)
