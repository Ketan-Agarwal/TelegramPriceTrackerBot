#!/usr/bin/python3
from telegram.ext import *
from telegram import *
from SQLHandler import *
from PriceTracker import *
from telegram.ext import ConversationHandler
import LinkHandler as lh
import threading
#import ekaroLinkGen as eklg
import time
token = "6006418181:AAG6KR_5-GFdFmYmGqGyANrVDPgULmyXqbI"
amzn_id_bot = ''
pincode = ''
desired_price = ''
price_data1 = ''
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global amzn_id_bot
    query = update.callback_query
    await query.answer()
    if query.data == "add_product":
        await query.delete_message()
        amzn_id_bot = await context.bot.send_message(chat_id=update.effective_chat.id, text="Please Send me any product link from Amazon | Flipkart (in reply to this message)")
    elif query.data == "show_watchlist":
        await query.delete_message()
        await show_watchlist(update, context)
    elif query.data == "help":
        await query.delete_message()
        await help1(update, context)
    elif query.data == "back":
        await query.delete_message()
        await main_menu(update, context)
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global amzn_id_bot, pincode, desired_price
    if update.message.reply_to_message:
        if update.message.reply_to_message.message_id == amzn_id_bot.message_id:
            link = lh.message_link_extractor(update.message.text)
            if link != None:
                context.user_data['waiting_text'] = await context.bot.send_message(update.effective_chat.id, "Please wait while I get product details for you.")
                context.user_data['link'] = link
                direct = lh.LinkDirector(link)
                print(direct)
                if type(direct) == tuple:
                    context.user_data['website'] = 'Flipkart'
                    context.user_data['pid'] = None
                    context.user_data['fkpid'] = direct[0]
                    context.user_data['fkslug'] = direct[1]
                    await add_product(update, context)
                elif type(direct) == str:
                    context.user_data['website'] = 'Amazon'
                    context.user_data['pid'] = direct
                    await add_product(update, context)
                elif direct == None:
                    context.user_data['pid'] = None
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="The link you sent doesn't seems to be associated with any particular product. Please Copy and paste actual product link.")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="There is no product link in your message.\nPlease send me a amazon or flipkart product link.")
        elif update.message.reply_to_message.message_id == pincode.message_id:
            if len(update.message.text) == 6 and update.message.text.isnumeric():
                context.user_data['pincode'] = update.message.text

                await context.bot.send_message(update.effective_chat.id, "Thanks For the info.")
                desired_price = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Please input your desired price at which you want to be notified.\nCurrent Price: {price_data1['prices']['price']}\n(in reply to this message)")
                add_pincode(context.user_data.get('uid'), context.user_data.get('pincode'))
                print(context.user_data.get('pincode'))
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Please input your valid 6 digit pincode.")
        elif update.message.reply_to_message.message_id == desired_price.message_id:
            context.user_data['desired_price'] = update.message.text
            add_product_sql(context.user_data.get('uid'), context.user_data.get('pid'), context.user_data.get('desired_price'), price_data1['prices']['price'], price_data1["prices"]["highest_price"], price_data1["prices"]["average_price"], price_data1["prices"]["lowest_price"], price_data1['name'], context.user_data.get('website'), context.user_data.get('fkpid'), context.user_data.get('fkslug'))
            await context.bot.send_message(chat_id=update.effective_chat.id,text=f"We will send you notification when your product price will fall below your Desired price.")
            await main_menu(update, context)

        else:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please type in reply to query message.")

    else:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please type in reply to the query message. You can also start over by clicking /start")
    
    
async def help1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    back = [
        [InlineKeyboardButton("Back", callback_data="back")],
    ]
    reply = InlineKeyboardMarkup(back)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, \nCurrently you can only add products, will will be including more features in upcoming days.", reply_markup=reply)

async def show_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    back = [
        [InlineKeyboardButton("Back", callback_data="back")],
    ]
    reply = InlineKeyboardMarkup(back)
    #tup = watchlist(context.user_data.get('uid'))
    #for i, row in enumerate(tup):
    #    result_str += f"{i+1}. {row[0]} - {row[1]}\n   Desired Price: {row[2]}\n   Current Price: {row[3]}\n"
    if watchlist(context.user_data.get('uid')) != None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The Products I am tracking for you are as follows:\n\n" + watchlist(context.user_data.get('uid')),reply_markup=reply, parse_mode=constants.ParseMode.MARKDOWN, disable_web_page_preview=True, disable_notification=True)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Current I am tracking no products for you.\nClick /start to add products to your tracklist.")

async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global pincode, desired_price, price_data1
    message = await context.bot.send_message(chat_id=update.effective_chat.id, text='10')
    def price_data11():
        global price_data1
        print(context.user_data['link'])
        price_data1 = crawler(context.user_data.get('link'))[0]
    t = threading.Thread(target=price_data11)
    t.start()
    for i in range(9, 0, -1):
        time.sleep(1)
        await context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text=str(i))
    await context.bot.delete_message(chat_id=message.chat_id, message_id=context.user_data['waiting_text'].message_id)
    await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
    if is_product_present(context.user_data.get('uid'), context.user_data.get('pid'), context.user_data.get('fkpid')) == False:
    
        print("Price Data------", price_data1)
        if price_data1 != None:
            if context.user_data.get('website') == 'Amazon':

                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Name:\n{price_data1['name']}\n\nCurrent Price: *₹{price_data1['prices']['price']}*\n\n[Show on Amazon](https://www.amazon.in/dp/{context.user_data.get('pid')})", parse_mode=constants.ParseMode.MARKDOWN, disable_web_page_preview=True)
            elif context.user_data.get('website') == 'Flipkart':
                context.user_data['fklink'] = f"https://www.flipkart.com/{context.user_data.get('fkslug')}/p/{context.user_data.get('fkpid')}"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Name:\n{price_data1['name']}\n\nCurrent Price: *₹{price_data1['prices']['price']}*\n\n[Show on Flipkart]({context.user_data.get('fklink')})", parse_mode=constants.ParseMode.MARKDOWN, disable_web_page_preview=True)
            pincode = await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Pincode? (for product availability check) (in reply to this message)")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Hmmm\nI was not able to find any product for the given link. Please recheck the link.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"We are already tracking your product. We will send you the alert when your product will fall below your Desired price of {is_product_present(context.user_data.get('uid'), context.user_data.get('pid'), context.user_data.get('fkpid'))[0][2]}")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Add A Product", callback_data="add_product"),
            InlineKeyboardButton("Show TrackList", callback_data="show_watchlist"),
        ],
        [InlineKeyboardButton("Status", callback_data="help")],
    ]    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Main Menu", reply_markup=reply_markup)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['uid'] = update.message.from_user.id
    context.user_data['website'] = None
    context.user_data['pid'] = None
    context.user_data['fkpid'] = None
    context.user_data['fkslug'] = None
    context.user_data['link'] = None
    context.user_data[''] = None
    print(update.message.from_user.username)
    print(update.message.from_user.is_premium)
    print(context.user_data)
    if isPresent(context.user_data.get('uid')):
        await update.message.reply_text(f"Welcome Back, {update.message.from_user.first_name}")
        print(update.effective_chat.id)
        print (context.user_data)
        await main_menu(update, context)
        return
    else:
        add_user(context.user_data.get('uid'), update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.is_premium)
        await update.message.reply_text(f"Hello {update.message.from_user.first_name}, \nWelcome to one of the most accurate and responsive Bot for Price Tracking.")
        print(update.effective_chat.id)
        await main_menu(update, context)

if __name__ == '__main__':
    
    application = ApplicationBuilder().token(token).build()
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()