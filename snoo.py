#Import required modules.
from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging
from prawcore import NotFound
import praw
import json

#Initiate API objects.
text = file.open("config.json")
config = json.loads(text)
reddit = praw.Reddit(client_id = config.reddit_client_id, client_secret = config.reddit_client_secret, username = config.reddit_username, password = config.reddit_password, user_agent =config.reddit_user_agent)
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
updater = Updater(token = config.telegram_bot_token)
dispatcher = updater.dispatcher

#Set variables.
sub = 'news'
lmt = 10

def sub_exists(subr): #Function to check for valid subreddit name.

    exists = True

    try:
        reddit.subreddits.search_by_name(subr, exact=True)
    except NotFound:
        exists = False

    return exists

def setSubreddit(bot, update, args): #Funtion to set subreddit. Input taken from user.

    global sub

    if len(args) == 1:
        sub = args[0]

        if sub_exists(sub):
            print(f"Subreddit set to {sub}.")

        else:
            bot.send_message(chat_id = update.message.chat_id, text = "Invalid subreddit name. Try again.")
            print("Invalid subreddit name.")

    else:
        bot.send_message(chat_id = update.message.chat_id, text = "Invalid subreddit name. Try again.")
        print("Invalid subreddit name.")

def setLimit(bot, update, args): #Funtion to set limit of articles pulled. Input taken from user.

    global lmt

    if len(args) == 1 and not args[0].isalpha():
        lmt = int(args[0])
        print(f"Limit set to {lmt}.")

    else:
        bot.send_message(chat_id = update.message.chat_id, text = "Invalid limit value. Try again.")
        print("Invalid limit value.")

def show(bot, update, args): #Function to pull and show desired number of articles from desired subreddit.

    subreddit = reddit.subreddit(sub)

    if len(args) == 1:

        if args[0] == 'hot':
            submissions = subreddit.hot(limit = lmt)
            print(f"Displayed -> {sub} : {lmt} : hot")

        elif args[0] == 'new':
            submissions = subreddit.new(limit = lmt)
            print(f"Displayed -> {sub} : {lmt} : new")

        elif args[0] == 'top':
            submissions = subreddit.new(time_filters = 'all', limit = lmt)
            print(f"Displayed -> {sub} : {lmt} : top all")

        else:
            bot.send_message(chat_id = update.message.chat_id, text = "Choose between hot/new/top.")
            print("Invalid show parameter.")
            return 1

    elif len(args) == 2 and args[0] == 'top':

        if args[1] == 'hour' or args[1] == 'day' or args[1] == 'week' or args[1] == 'month' or args[1] == 'year' or args[1] == 'all':
            submissions = subreddit.top(time_filter = args[1], limit = lmt)
            print(f"Displayed -> {sub} : {lmt} : top {args[1]}")

        else:
            bot.send_message(chat_id = update.message.chat_id, text = "Choose between hour/day/week/month/year/all.")
            print("Invalid show parameter.")
            return 1

    else:
            bot.send_message(chat_id = update.message.chat_id, text = "Choose between hot/new/top.")
            print("Invalid show parameter.")
            return 1

    count = 1
    submission_form = "{}) {} : {} <{}>"
    for submission in submissions:
        bot.send_message(chat_id = update.message.chat_id, text = submission_form.format(count,submission.ups, submission.title, submission.url))
        count += 1

def help(bot, update): #Function to send help message to user.
    print("Help message sent.")
    bot.send_message(chat_id = update.message.chat_id, text = "Use /setsub to set subreddit.\nSyntax: /setsub (subreddit name)")
    bot.send_message(chat_id = update.message.chat_id, text = "Use /setlmt to set article pull limit.\nSyntax: /setlmt (limit number)")
    bot.send_message(chat_id = update.message.chat_id, text = "Use /show to display articles.\nSyntax: /show (hot/new/top) (if top(all/year/month/week/day/hour))")

#Create handlers for functions.
show_handler = CommandHandler('show', show, pass_args = True)
sub_handler = CommandHandler('setsub', setSubreddit, pass_args = True)
lmt_handler = CommandHandler('setlmt', setLimit, pass_args = True)
help_handler = CommandHandler('help', help)

#Add handlers to dispatcher.
dispatcher.add_handler(show_handler)
dispatcher.add_handler(sub_handler)
dispatcher.add_handler(lmt_handler)
dispatcher.add_handler(help_handler)

#Start polling updater.
updater.start_polling()
print("Bot Online.")
