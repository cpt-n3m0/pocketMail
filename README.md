# pocketMail
Get through your reading backlog using your own self-hosted pocket newsletter. 

# Set up
1. [Create a pocket application](https://getpocket.com/developer/apps/new.php?) (and copy the consumer key assigned to it in the `consumer_key` field of config.yml )
2. Create a gmail address from which you want to receive the daily reads (don't recommend using your main gmail address if gmail is your main provider)
3. download ngrok, run `ngrok http 8000`, and replace the bracket text with the url in the `callback_uri` field in the config.yml file to expose your localhost at port 8000 to be used as a callback (required as part of the pocket API's auth procedure
4. Populate the rest of the fields in the config.yml file (lmk if you have any issues with this)
5. Now it's time to get your access token. Assuming you're in the root directory of the project, go to `src/authserver`, start the Django server with `python3 manage.py runserver`, open a browser window to the url `localhost:8000/pocketauth/`, log in if required then authorize your app
6. And voila! now everytime your run `python3 main.py` you'll get sent 5 unread articles, you might want to set up a cron job to make it a daily thing

