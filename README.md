# Description

A simple script for periodically emailing yourself a random selection of notes from your Evernote. My personal use case is that I have a bunch of information organized in various Evernote notebooks from interview prep/general learning and wanted a semi-structured way to motivate myself to review bits of information periodically. Took inspiration from [Readwise's](https://readwise.io/) daily email. 

Couldn't find this functionality anywhere online so decided to create it in case other people are looking to do the same thing.

# Setup

Setting this up in terms of authenticating with Evernote (required) and Gmail (optional if you don't want it in the form of an email) is a bit non-trivial.

**Evernote** - Because the script needs access to your Evernote, you need to get a production developer token [here](https://dev.evernote.com/doc/articles/dev_tokens.php). Anyone can get a sandbox token but you'll have to open a ticket with Evernote and request a developer token to get the Production Service Token link to work.

Once you have the token, update the **PROD_DEVELOPER_TOKEN** variable in send_evernote_email.py

**Gmail** - I followed a great tutorial [here](https://blog.macuyiko.com/post/2016/how-to-send-html-mails-with-oauth2-and-gmail-in-python.html) for setting up OAuth2 with Gmail and the gmail.py file is taken from there. This is optional if you don't want an automated email or you want to use a different email integration.

Along with updating GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and  GOOGLE_REFRESH_TOKEN per the tutorial, you'll just need to specify directly below those variables the sending and receiving emails. 

# Usage

In send_evernote_email.py, you can change the tag that you want to use to select notes (default is "Daily-Email"), the number of notes per email, and the email to use for sending and receiving.

I set up this code on a free-tier GCP instance and set up a cron job to run the script every morning. Followed this cron tutorial [here](https://towardsdatascience.com/how-to-schedule-python-scripts-with-cron-the-only-guide-youll-ever-need-deea2df63b4e).

# Evernote SDK

[Quick-Start](https://dev.evernote.com/doc/#start)

[API-Reference](https://dev.evernote.com/doc/reference/)

# Contact

If you have any questions or need help feel free to email me at alhuang10 @ gmail.com. 