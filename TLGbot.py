from telegram import Update , ChatPermissions , Message
import time , asyncio
from collections import defaultdict
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes , MessageHandler , filters , Application , BaseHandler
from telegram.constants import ChatMemberStatus , ParseMode
from datetime import datetime, timedelta
import json , pytz
import asyncio
import json
import psutil
import platform , re
from datetime import timedelta
from datetime import datetime
from pytz import timezone, all_timezones
from telegram import Update
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler,
    ContextTypes, JobQueue , 
)
start_time = time.time()
known_users = {}
link_protection = {}
anti_badword_status = {}
safe_domains = [             #safe links
    "youtube.com", "youtu.be",
    "t.me", "telegram.me",
    "instagram.com", "www.instagram.com",
    "facebook.com", "fb.com", "www.facebook.com",
    "twitter.com", "x.com",
    "tiktok.com", "www.tiktok.com",
    "reddit.com", "www.reddit.com",
    "discord.com", "discord.gg",
    "github.com", "gitlab.com",
    "medium.com", "stackoverflow.com"
]

#  ())()()()()()()
#  IMPORTANT >>>>> fix your username in line ( 571  , 563  , 512 , 522 , 536 , 196 )
#  ()()()()()()()()
#
bad_words = ["add some bad words here"]
timezone = pytz.timezone("Asia/Tehran")   # your timezone here
cur_time = datetime.now(timezone)
active = set()
custom_admins = set()
custom_admins.add("owner telegram username like telegram or mahdi") # do not place '@'
custom_admins.add("admin 2 ") #admin for your bot, remove this line if you dont need
blacklist = {}
STICKER_FILE_ID = 'desk.webp'   # place a custom or empty sticker
LIMIT = 5
WINDOW = 60
token = '  your bot token'
userid = ' your user id ' 
user_id_list = []

GROUPS_FILE = "groups.json"  # put a groups.json empty file next to this python file


#async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
#    chat_id = update.effective_chat.id
#    user_id = update.effective_user.id
#    member = await context.bot.get_chat_member(chat_id, user_id)
#    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]

async def adminconf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    admins = await context.bot.get_chat_administrators(chat_id)

def load_groups():
    try:
        with open(GROUPS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_groups(groups):
    with open(GROUPS_FILE, "w") as f:
        json.dump(groups, f)

user_request_times = defaultdict(list)
def is_rate_limited(user_id: int) -> bool:
    now = time.time()
    timestamps = user_request_times[user_id]
    # Remove old timestamps
    user_request_times[user_id] = [ts for ts in timestamps if now - ts < WINDOW]
    return len(user_request_times[user_id]) >= LIMIT\

async def turnon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        chat_id = update.effective_chat.id
        active.add(chat_id)
        await update.message.reply_text("Group lock is Turn on")
    else:
        await update.message.reply_text("sorry, you are not admin.")
async def turnoff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        chat_id = update.effective_chat.id
        active.discard(chat_id)
        await update.message.reply_text("Group lock is Turn off")
    else:
        await update.message.reply_text("sorry, you are not admin.")
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        if context.args:
            try:
                user_id = int(context.args[0])
                if user_id not in user_id_list:
                    user_id_list.append(user_id)
                    await update.message.reply_text(f"User ID added to list!")
                else:
                    await update.message.reply_text(f"User ID is already in the list.")
            except ValueError:
                await update.message.reply_text("Please provide a valid numeric user ID.")
        else:
            await update.message.reply_text("Usage: /add user_id")
    else:
        await update.message.reply_text("sorry you are not admin.")

async def mainapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if chat_id in active:
        try:
            await update.message.delete()
        except Exception as e:
            print("error group lock")


    message: Message = update.message
    chat_id = message.chat_id
    user_id = message.from_user.id
    if chat_id in blacklist and user_id in blacklist[chat_id]:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        except Exception as e:
            print(f"Failed to delete message from blacklisted user")


    if not anti_badword_status.get(chat_id, False):
        return


    msg_text = message.text.lower() if message.text else ""
    if any(bad_word in msg_text for bad_word in bad_words):
        try:
            await message.delete()
            warning = await context.bot.send_message(chat_id=chat_id, text="فحش ندهید باتشکر")
            await asyncio.sleep(2)  # wait 2 seconds
            await context.bot.delete_message(chat_id=chat_id, message_id=warning.message_id)
        except Exception as e:
            print(f"Error deleting message: {e}")
    
    message1 = update.message
    chat_id1 = message.chat.id
    text1 = message.text or ""

    #  Link Protection
    if link_protection.get(chat_id1, False):
        urls = re.findall(r"https?://[^\s]+", text1)
        for url in urls:
            if not any(domain in url for domain in safe_domains):
                try:
                    await message1.delete()
                    warn = await context.bot.send_message(chat_id1, "link is not safe, message has been Deleted.")
                    await asyncio.sleep(2)
                    await warn.delete()
                except Exception as e:
                    print(f"Error deleting message or warning: {e}")
                return  
        if urls: 
            await message1.reply_text(" Link is safe , you can use it.")

    else:
            if update.message.chat.type == 'supergroup':
                if update.effective_user.id == '':
                    if is_rate_limited(user_id):
                        msg = await update.message.reply_text("Rate limit exceeded. 1 minute.")
                        await asyncio.sleep(3)
                        try:
                            await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
                        except Exception as e:
                            print(f"Failed to delete message")
                        return
                    else:
                        await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=STICKER_FILE_ID)
                else:
                    return
            else:
                return
            #end
        #end


async def Commanded(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username == 'owner':
        print("app is closed")
        await update.message.reply_text("oflline")
        await asyncio.sleep(9999999999)
        
    else:
        await update.message.reply_text("access denied, you are not owner")
        return
    

async def analize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        chat = update.effective_chat
        if update.message.chat.type not in ['group', 'supergroup']:
            await update.message.reply_text("This command only works in groups.")
            return
        else:
            admins = await context.bot.get_chat_administrators(chat.id)
            mssg = " Group Admin Info:\n\n"
            for admin in admins:
                user = admin.user
                mssg += f" Name: {user.first_name} {user.last_name or ''}\n"
                mssg += f" ID: {user.id}\n"
                mssg += f" Username: @{user.username}\n" if user.username else ""
                mssg += f" Status: {admin.status}\n"
                mssg += "-" * 20 + "\n"
            mssg = await update.message.reply_text(mssg)
            mssgf = await update.message.reply_text("The message will be deleted in 5 seconds.")
            time.sleep(5)
            chat_id = update.effective_chat.id
            try:
                await context.bot.delete_message(chat_id=mssg.chat_id, message_id=mssg.message_id)
                await context.bot.delete_message(chat_id=mssgf.chat_id, message_id=mssgf.message_id)
                print("object Deleted")
            except:
                print("cant delete msg ")
    else:
        await update.message.reply_text("sorry, you are not admin.")

async def res(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        user_id_list.clear()
        custom_admins.clear()
        active.clear()
        await update.message.reply_text("User ID list has been cleared.")
    else:
        await update.message.reply_text("Sorry you are not admin")

async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:

        if user_id_list:
            ids_text = "\n".join(str(uid) for uid in user_id_list)
            await update.message.reply_text(f"User ID list:\n{ids_text}")
        else:
            await update.message.reply_text("The user ID list is currently empty.")
    else:
        await update.message.reply_text("sorry, you are not admin.")
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:

        if update.message.reply_to_message:
            user_to_ban = update.message.reply_to_message.from_user
            chat_id = update.effective_chat.id

            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
                await update.message.reply_text("I need to be an admin to ban users.")
                return

            try:
                await context.bot.ban_chat_member(chat_id, user_to_ban.id)
                await update.message.reply_text(f"Banned {user_to_ban.full_name}")
            except Exception as e:
                await update.message.reply_text(f"Failed to ban: {e}")
        else:
            await update.message.reply_text("Reply to a user's message to ban them.")
    else:
        await update.message.reply_text("sorry, you are not admin.")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        if update.message.reply_to_message:
            user_to_mute = update.message.reply_to_message.from_user
            chat_id = update.effective_chat.id

            try:
                duration_minutes = int(context.args[0])
            except (IndexError, ValueError):
                await update.message.reply_text("Usage: /mute [reply] [minutes]")
                return

            until_date = datetime.utcnow() + timedelta(minutes=duration_minutes)

            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
                await update.message.reply_text("I need to be admin to mute users.")
                return

            try:
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_to_mute.id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=until_date
                )
                await update.message.reply_text(f"Muted {user_to_mute.full_name} for {duration_minutes} minutes.")
            except Exception as e:
                await update.message.reply_text(f"Failed to mute: {e}")
        else:
            await update.message.reply_text("Reply to a user's message to mute them.")
    else:
        await update.message.reply_text("sorry, you are not admin.")
        
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        chat = update.effective_chat
        bot = context.bot

        try:
            count = int(context.args[0])
            if count < 1 or count > 10000:
                await update.message.reply_text("Please enter a number between 1 and 10000.")
                return
        except (IndexError, ValueError):
            await update.message.reply_text("Usage: /clear 1 - 10000")
            return

        # Check if bot is admin
        bot_member = await bot.get_chat_member(chat.id, bot.id)
        if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
            await update.message.reply_text("I need to be admin to delete messages.")
            return

        try:
            messages = []
            async for msg in bot.get_chat_history(chat.id, limit=count):
                messages.append(msg)

            for msg in messages:
                try:
                    await bot.delete_message(chat.id, msg.message_id)
                except:
                    pass 

            msg = await update.message.reply_text(f"Attempted to delete {len(messages)} messages.")
            await asyncio.sleep(3)
            await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
    else:
        await update.message.reply_text("sorry, you are not admin.")



async def tag_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        chat_id = update.effective_chat.id
        users = known_users.get(chat_id, {})

        if not users:
            await update.message.reply_text("No users to tag yet.")
            return

        mentions = list(users.values())
        text = " Tagging everyone:\n" + "\n".join(mentions)

        try:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        except Exception as e:
            print(f"Failed to tag users: {e}")
            await update.message.reply_text("Too many users to tag at once.")
    else:
        await update.message.reply_text("sorry you are not admin")

async def set_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        chat_id = update.effective_chat.id
        groups = load_groups()
        if chat_id not in groups:
            groups.append(chat_id)
            save_groups(groups)
            await update.message.reply_text(" This group will now receive daily messages.")
        else:
            await update.message.reply_text(" This group is already registered.")
    else:
        await update.message.reply_text("sorry, you are not admin.")

async def remove_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        chat_id = update.effective_chat.id
        groups = load_groups()
        if chat_id in groups:
            groups.remove(chat_id)
            save_groups(groups)
            await update.message.reply_text(" This group will no longer receive daily messages.")
        else:
            await update.message.reply_text(" This group is not registered.")
    else:
        await update.message.reply_text("sorry, you are not admin.")

async def daily_messages(app: Application):
    while True:
        now = datetime.now().strftime("%H:%M")

        if now == "13:00":
            for group_id in load_groups():
                try:
                    await app.bot.send_message(group_id, "Good night!")
                except:
                    pass 
        elif now == "24:00":
            for group_id in load_groups():
                try:
                    await app.bot.send_message(group_id, "Good morning!")
                except:
                    pass

        await asyncio.sleep(60) 


async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        if not update.message.reply_to_message:
            await update.message.reply_text("Please reply to the muted user's message with /unmute.")
            return

        user_id = update.message.reply_to_message.from_user.id
        chat_id = update.effective_chat.id
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                            can_send_polls=True, can_send_other_messages=True,
                                            can_add_web_page_previews=True, can_change_info=False,
                                            can_invite_users=True, can_pin_messages=False)
            )
            await update.message.reply_text(" User has been unmuted.")
        except Exception as e:
            await update.message.reply_text(f" Failed to unmute: {e}")
    else:
        await update.message.reply_text("sorry, you are not admin.")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        await update.message.reply_text("You are admin")
    else:
        await update.message.reply_text("You are NOT admin")

async def del_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        if update.message.reply_to_message:
            try:
                await context.bot.delete_message(
                    chat_id=update.message.chat_id,
                    message_id=update.message.reply_to_message.message_id
                )
                await context.bot.delete_message(
                    chat_id=update.message.chat_id,
                    message_id=update.message.message_id
                )
            except Exception as e:
                await update.message.reply_text(f"Failed to delete message: {e}")
        else:
            await update.message.reply_text("Please reply to a message with /del to delete it.")



async def blacklist_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        if update.message.reply_to_message:
            chat_id = update.message.chat_id
            user_id = update.message.reply_to_message.from_user.id

            if chat_id not in blacklist:
                blacklist[chat_id] = set()
            blacklist[chat_id].add(user_id)

            await update.message.reply_text("User has been blacklisted.")
        else:
            await update.message.reply_text("Reply to a user's message to blacklist them.")
    else:
        await update.message.reply_text("sorry, you are not admin.")

async def unblacklist_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        if update.message.reply_to_message:
            chat_id = update.message.chat_id
            user_id = update.message.reply_to_message.from_user.id

            if chat_id in blacklist and user_id in blacklist[chat_id]:
                blacklist[chat_id].remove(user_id)
                await update.message.reply_text("User has been removed from the blacklist.")
            else:
                await update.message.reply_text("User is not in the blacklist.")
        else:
            await update.message.reply_text("Reply to a user's message to unblacklist them.")
    else:
        await update.message.reply_text("sorry, you are not admin.")

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username == 'owner':
        if context.args:
            username = context.args[0].lstrip('@')  
            custom_admins.add(username)
            await update.message.reply_text(f"@{username} added to custom admin list.")
        else:
            await update.message.reply_text("Usage: /admin @username")
    else:
        await update.message.reply_text("sorry, you are not owner.")
async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username == 'owner':
        if context.args:
            username = context.args[0].lstrip('@')
            if username in custom_admins:
                custom_admins.remove(username)
                await update.message.reply_text(f"@{username} removed from admin list.")
            else:
                await update.message.reply_text(f"@{username} is not in the admin list.")
        else:
            await update.message.reply_text("Usage: /rem @username")
    else:
        await update.message.reply_text("sorry, you are not owner.")

async def remall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username == 'owner':
        custom_admins.clear()
        await update.message.reply_text("Succesful.")
    else:
        await update.message.reply_text("Sorry, you are not owner.")

async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        if update.message.reply_to_message:
            try:
                await context.bot.pin_chat_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.reply_to_message.message_id
                )

                msd = await update.message.reply_text("Message pinned.")
                await asyncio.sleep(2)
                await context.bot.delete_message(chat_id=msd.chat_id, message_id=msd.message_id)
            except Exception as e:
                await update.message.reply_text(f"Failed to pin: {e}")
        else:
            await update.message.reply_text(" Use /pin as a reply to the message you want to pin.")
    else:
        await update.message.reply_text("sorry, you are not admin")

async def spyon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username == 'owner':
        mspp = await update.message.reply_text("spy-mode is now Turn on")
        await asyncio.sleep(2)
        await context.bot.delete_message(chat_id=mspp.chat_id, message_id=mspp.message_id)       
    else:
        await update.message.reply_text("access denied")

async def spyoff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username == 'owner':
        word = '''spy-mode Turned off. 
        Sending data to apt.json ...'''
        msp = await update.message.reply_text(word)
        await asyncio.sleep(3)
        await msp.edit_text("Successful")
        await asyncio.sleep(2)
        await context.bot.delete_message(chat_id=msp.chat_id, message_id=msp.message_id)
    else:
        await update.message.reply_text("access denied")


async def dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username
    timezone = pytz.timezone("Asia/Tehran")
    cur_time = datetime.now(timezone)
    curtimeword = f'''
|
|{cur_time.strftime(">>        %D")}
|
|{cur_time.strftime(">>        %H : %M : %S - Tehran")}
|'''
    await update.message.reply_text(curtimeword)

async def say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        message = ' '.join(context.args)
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("You need to say something. Usage: /say (your message)")

async def on_anti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        chat_id = update.effective_chat.id
        anti_badword_status[chat_id] = True
        await update.message.reply_text("Anti-badword filter is now ON.")
    else:
        await update.message.reply_text("sorry, you are not admin")
# Command to disable anti-badword

async def off_anti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        chat_id = update.effective_chat.id
        anti_badword_status[chat_id] = False
        await update.message.reply_text("anti-badword filter is now OFF.")
    else:
        await update.message.reply_text("sorry, you are not admin")
async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if username in custom_admins:
        chat = update.effective_chat
        bot = context.bot
        user = update.effective_user

        chat_member = await bot.get_chat_member(chat.id, bot.id)
        if not chat_member.can_delete_messages:
            await update.message.reply_text(" I need 'Delete messages' permission to clear chat.")
            return

        # Inform user
        notice = await update.message.reply_text(" Clearing last 100 messages...")

        try:
            # Get recent messages to delete
            async for msg in bot.get_chat_history(chat_id=chat.id, limit=100):
                try:
                    await bot.delete_message(chat_id=chat.id, message_id=msg.message_id)
                except:
                    pass  # Can't delete some messages (too  or not allowed)

            await notice.edit_text(" Cleared up to 100 recent meoldssages.")
        except Exception as e:
            await notice.edit_text(f" Failed to clear messages: {e}")
    else:
        await update.message.reply_text("sorry, you are not admin")


async def bot_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Uptime
    uptime_seconds = int(time.time() - start_time)
    uptime_str = str(timedelta(seconds=uptime_seconds))

    # RAM usage
    process = psutil.Process()
    memory_usage = process.memory_info().rss / 1024 / 1024  # MB

    # Bot info
    bot = context.bot
    me = await bot.get_me()

    info_message = (
        f" <b>{me.first_name}</b> Info\n\n"
        f" ID: <code>{me.id}</code>\n"
        f" Username: @{me.username}\n"
        f" Uptime: <code>{uptime_str}</code>\n"
        f" RAM Usage: <code>{memory_usage:.2f} MB</code>\n"
        f" PSP.vms: <code>{platform.python_version()}</code>\n"
        f" PTB Version: <code>{context.application.__version__}</code>"
        f" Active admin's: {custom_admins}"
    )

    await update.message.reply_text(info_message, parse_mode="HTML")

async def enable_link_protection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    link_protection[chat_id] = True
    await update.message.reply_text("Link protection is now ON.")

async def disable_link_protection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    link_protection[chat_id] = False
    await update.message.reply_text("Link protection is now OFF.")

async def adminList(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    username = update.effective_user.username
    if username in custom_admins:
        chat = update.effective_chat
        bot = context.bot
        user = update.effective_user
        admshow = f'''admins: 
                    {custom_admins}'''
        await update.message.reply_text(admshow)
        print("request admin list success")
        print("")
        print(admshow)
    else:
        await update.message.reply_text("sorry, you are not admin")

if __name__ == '__main__':
    from telegram.ext import ApplicationBuilder
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, mainapp))    #commands are here
    app.add_handler(CommandHandler("cmd", Commanded))
    app.add_handler(CommandHandler("add", add_user))
    app.add_handler(CommandHandler("res", res))
    app.add_handler(CommandHandler("lock", turnon))
    app.add_handler(CommandHandler("unlock", turnoff))
    app.add_handler(CommandHandler("show", show_list))
    app.add_handler(CommandHandler("analize", analize))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute_command))
    app.add_handler(CommandHandler("clear", clear_chat))  #debug need 
    app.add_handler(CommandHandler("tag", tag_all))  #debug need
    app.add_handler(CommandHandler("set", set_group))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("remove", remove_group))
    app.add_handler(CommandHandler("del", del_message))
    app.add_handler(CommandHandler("blackList", blacklist_user))
    app.add_handler(CommandHandler("unblackList", unblacklist_user))
    app.add_handler(CommandHandler("admin", add_admin))
    app.add_handler(CommandHandler("rem", remove_admin))
    app.add_handler(CommandHandler("remall", remall))
    app.add_handler(CommandHandler("pin", pin_message))
    app.add_handler(CommandHandler("spy", spyon))
    app.add_handler(CommandHandler("unspy", spyoff))
    app.add_handler(CommandHandler("date", dates))
    app.add_handler(CommandHandler("say", say))
    app.add_handler(CommandHandler("antion", on_anti))
    app.add_handler(CommandHandler("antioff", off_anti))
    app.add_handler(CommandHandler("info", bot_info))
    app.add_handler(CommandHandler("link_on", enable_link_protection))
    app.add_handler(CommandHandler("link_off", disable_link_protection))
    app.add_handler(CommandHandler("admin_list", adminList))
    app.job_queue.run_repeating(daily_messages, interval=60, first=0, data={})
    print("bot is active")
    app.run_polling()