#!/usr/bin/python3
from telegram.ext import *
from telegram import *
from SQLHandler import *
from PriceTracker import *
import LinkHandler as lh
import threading
import asyncio
#import ekaroLinkGen as eklg
import time
token = "6006418181:AAG6KR_5-GFdFmYmGqGyANrVDPgULmyXqbI"
#token = "6072951807:AAEO1-qSDieDVwLUY0t4JWqaM3DpVm0Z7_s" #token of main bot (APT)
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "add_product":
        await query.delete_message()
        context.user_data['amzn_id_bot'] = await context.bot.send_message(chat_id=update.effective_chat.id, text="REPLY me any product link from Amazon or Flipkart\n(⚠️ Only in reply to this message)")
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
    if update.message.reply_to_message:
        if update.message.reply_to_message.message_id == context.user_data.get('amzn_id_bot').message_id:
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
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="❗The link you sent doesn't seems to be associated with any particular product. Please Copy and reply me actual product link.")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="There is no product link in your message.\nPlease reply me an amazon or flipkart product link.")
        elif update.message.reply_to_message.message_id == context.user_data.get('act_pincode').message_id:
            if len(update.message.text) == 6 and update.message.text.isnumeric():
                context.user_data['pincode'] = update.message.text

                #await context.bot.send_message(update.effective_chat.id, "Thanks For the info.")
                context.user_data['desired_price_id'] = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Input your desired price at which you want to be notified.\nCurrent Price: {context.user_data.get('price_data1')['prices']['price']}\n(⚠️ ONLY in reply to this message)")
                add_pincode(context.user_data.get('uid'), context.user_data.get('pincode'))
                print(context.user_data.get('pincode'))
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Please input your valid 6 digit pincode.")
        elif update.message.reply_to_message.message_id == context.user_data.get('desired_price_id').message_id:
            context.user_data['desired_price'] = update.message.text
            add_product_sql(context.user_data.get('uid'), context.user_data.get('pid'), context.user_data.get('desired_price'), context.user_data.get('price_data1')['prices']['price'], context.user_data.get('price_data1')["prices"]["highest_price"], context.user_data.get('price_data1')["prices"]["average_price"], context.user_data.get('price_data1')["prices"]["lowest_price"], context.user_data.get('price_data1')['name'], context.user_data.get('website'), context.user_data.get('fkpid'), context.user_data.get('fkslug'))
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
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, \nDrop a message on @B2B_Deals_Support_Bot if you have any type of questions.", reply_markup=reply)

async def show_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print('----------------------1')
    back = [
        [InlineKeyboardButton("Back", callback_data="back")],
    ]
    reply = InlineKeyboardMarkup(back)
    tup = watchlist(context.user_data.get('uid'))
    #for i, row in enumerate(tup):
    #    result_str += f"{i+1}. {row[0]} - {row[1]}\n   Desired Price: {row[2]}\n   Current Price: {row[3]}\n"
    print('----------------------2')
    if tup != None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The Products I am tracking for you are as follows:\n\n" + tup,reply_markup=reply, parse_mode=constants.ParseMode.MARKDOWN, disable_web_page_preview=True, disable_notification=True)
    else:
        back = [
            [InlineKeyboardButton("Back", callback_data="back")],
        ]
        reply = InlineKeyboardMarkup(back)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Current I am tracking no products for you.\nClick Back to add products to your tracklist.", reply_markup=reply)

async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_product_present(context.user_data.get('uid'), context.user_data.get('pid'), context.user_data.get('fkpid')) == False:
        message = await context.bot.send_message(chat_id=update.effective_chat.id, text='10')
        def price_data11():
            print(context.user_data['link'])
            context.user_data['price_data1'] = crawler(context.user_data.get('link'))[0]
        t = threading.Thread(target=price_data11)
        t.start()
        for i in range(9, 0, -1):
            time.sleep(1)
            await context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text=str(i))
        await context.bot.delete_message(chat_id=message.chat_id, message_id=context.user_data['waiting_text'].message_id)
        await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
        print("Price Data------", context.user_data.get('price_data1'))
        if context.user_data.get('price_data1') != None:
            if context.user_data.get('website') == 'Amazon':

                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Name:\n{context.user_data.get('price_data1')['name']}\n\nCurrent Price: *₹{context.user_data.get('price_data1')['prices']['price']}*\n\n[Show on Amazon](https://www.amazon.in/dp/{context.user_data.get('pid')}?tag=b2bdeals-21)", parse_mode=constants.ParseMode.MARKDOWN, disable_web_page_preview=True)
            elif context.user_data.get('website') == 'Flipkart':
                context.user_data['fklink'] = f"https://www.flipkart.com/{context.user_data.get('fkslug')}/p/{context.user_data.get('fkpid')}"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Name:\n{context.user_data.get('price_data1')['name']}\n\nCurrent Price: *₹{context.user_data.get('price_data1')['prices']['price']}*\n\n[Show on Flipkart]({context.user_data.get('fklink')})", parse_mode=constants.ParseMode.MARKDOWN, disable_web_page_preview=True)
            context.user_data['act_pincode'] = await context.bot.send_message(chat_id=update.effective_chat.id, text="Your Pincode? (for product availability check) \n(⚠️ ONLY in reply to this message)")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Hmmm\nI was not able to find any product for the given link. Please recheck the link.")
    else:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['waiting_text'].message_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"I am already tracking your product. I will send you the alert when your product will fall below your Desired price of {is_product_present(context.user_data.get('uid'), context.user_data.get('pid'), context.user_data.get('fkpid'))[0][2]}")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Add A Product (Link)", callback_data="add_product"),
            InlineKeyboardButton("Show My TrackList", callback_data="show_watchlist"),
        ],
        [InlineKeyboardButton("Get Help!", callback_data="help")],
    ]    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Select an option from below.", reply_markup=reply_markup)
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
        await update.message.reply_text(f"Hello {update.message.from_user.first_name}, \n\nWelcome to one of the most accurate and responsive Bot for Price Tracking.\n\nYou can contact us here @B2B_Deals_Support_Bot")
        print(update.effective_chat.id)
        await main_menu(update, context)

async def send_price(idss, prev_data,  curr_price, des_price, link, name) -> None:
    global bot
    print(f"being executed? ---- {idss}")
    bot = Bot(token=token)
    await bot.send_message(chat_id=idss, text=f"🚨 Price Alert 🚨 \n\nThe price of your product has changed!\n\nName: {name}\n\nCurrent Price: ₹{curr_price}\nPrevious Price: ₹{prev_data}\nDesired Price: ₹{des_price}\n\nLink: {link}\n\nJoin [B2BDeals](https://t.me/backtoback_deals) for DealBreaker Deals", parse_mode=constants.ParseMode.MARKDOWN, disable_web_page_preview=True)


def datawatcher():
    watching()
    while True:
        wat = watcher()
        print(f"watcher------------{wat}")
        if wat != None:
            returning, data_row, prev_data = wat
            print(f"tg code ------------------------------ {data_row} -------- {returning}")
            userIDss = get_users_for_product(data_row[0])
            for userIDs in userIDss:
                print(userIDs)
                idss = userIDs[0]
                print(idss)
                old_price = prev_data[2]
                current_price = data_row[2]
                desired_price = userIDs[1]
                #print(f"current_price -=------=-=-=-=-=---{}")
                #print(f"desired_price---=-=-=--=--=-= {}")
                name = data_row[6]
                if data_row[7] == 'Amazon':
                    link = f"[Open Amazon](https://www.amazon.in/dp/{data_row[1]}?tag=b2bdeals-21)"
                elif data_row[7] == 'Flipkart':
                    link = f"[Open Flipkart](https://www.flipkart.com/{data_row[9]}/p/{data_row[8]})"
                asyncio.run(send_price(idss, old_price, current_price, desired_price, link, name))
        else:
            print("Data Not changed")
        time.sleep(1)

if __name__ == '__main__':
    threa = threading.Thread(target=datawatcher)
    threa.daemon = True
    threa.start()
    application = ApplicationBuilder().token(token).build()
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()