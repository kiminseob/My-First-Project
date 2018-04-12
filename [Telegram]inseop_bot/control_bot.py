from telegram import InlineKeyboardButton, InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import telegram
import logging
import test_bot
import re
import time
token = '텔레그램 봇 토큰'
#텔레그렘 봇의 API 키 가져옴
bot = telegram.Bot(token)


sadfasdfasdf!!!!!!!!!!!!!!!!!!



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

chat_id=""
message_id=""

announcement=""
homework=""
resource=""
major=""
name=""

keyboard2 = [[KeyboardButton("로그아웃", callback_data='1')]]
keyboard = [[KeyboardButton("로그인", callback_data='1')]]

def start(bot, update):
    global keyboard,keyboard2
    reply_markup = ReplyKeyboardMarkup(keyboard)
    if test_bot.my_name =="":
        update.message.reply_text('★충남대학교 사이버캠퍼스 인섭봇★', reply_markup=reply_markup)

# message reply function
def get_message(bot, update) :
    global announcement,homework,resource,chat_id, message_id,keyboard2,keyboard

    chat_id= update.message.chat_id
    message_id=update.message.message_id
    ID=""
    PW=""
    p = re.compile('\d{9}')
    if update.message.text=="공지 모아보기":
        if announcement is not "":
            update.message.reply_text(text="＊＊＊최근 1주일 공지 사항 UP＊＊＊\n오늘 : "+time.strftime("%m")+"월"+time.strftime("%d")+"일"+"\n"+announcement)
        else:
            update.message.reply_text(text="로그인 해주세요.")
    elif update.message.text=="과제 모아보기":
        if homework is not "":
            update.message.reply_text(text="＊＊＊진행중인 과제＊＊＊\n오늘 : "+time.strftime("%m")+"월"+time.strftime("%d")+"일"+"\n"+homework)
        else:
            update.message.reply_text(text="로그인 해주세요.")
    elif update.message.text=="자료실 모아보기":
        if resource is not "":
            update.message.reply_text(text="＊＊＊최근 1주일 자료실 UP＊＊＊\n오늘 : "+time.strftime("%m")+"월"+time.strftime("%d")+"일"+"\n" + resource)
        else:
            update.message.reply_text(text="로그인 해주세요.")
    elif update.message.text == "도움말":
        update.message.reply_text(text="안녕하세요. CNU E-Learing 공지 도우미 인섭봇입니다.\n"
                                   "[명령어]\n"
                                   "1. /help : 현재창\n"
                                   "2. /start : 버튼창")
    elif update.message.text == "로그인":
        update.message.reply_text(text="학번/비번 형식으로 입력해주세요.\n")
    elif update.message.text == "로그아웃":
        if test_bot.login_state:
            test_bot.login_state=False
            update.message.reply_text("로그아웃 되었습니다.")
            reply_markup = ReplyKeyboardMarkup(keyboard)
            update.message.reply_text(
                '★충남대학교 사이버캠퍼스 인섭봇★',
                reply_markup=reply_markup)
        else:
            reply_markup = ReplyKeyboardMarkup(keyboard)
            update.message.reply_text(
                '★충남대학교 사이버캠퍼스 인섭봇★',
                reply_markup=reply_markup)
    else:
        try:
            ID_PW = update.message.text
            ID_PW_List = list(ID_PW)
            if 9<ID_PW_List.__len__():
                if ID_PW_List.pop(9) is "/":
                    ID_PW_Length = ID_PW_List.__len__()

                    for i in range(ID_PW_Length):
                        if i <9:
                            ID = ID + ID_PW_List.pop(0)
                        else:
                            PW = PW + ID_PW_List.pop(0)
                    if p.match(ID) is None:
                        update.message.reply_text("학번/비번 형식으로 입력해주세요.\n")
                    else :
                        test_bot.ID = ID
                        test_bot.PW = PW
                        announcement=""
                        homework=""

                        update.message.reply_text("로그인 중...")
                        try:
                            test_bot.creat_session()
                            if test_bot.login_state:
                                update.message.reply_text("로그인 되었습니다.")
                                reply_markup = ReplyKeyboardMarkup(keyboard2)
                                update.message.reply_text(
                                    '★충남대학교 사이버캠퍼스 인섭봇★' + '\n' + major + "\b" + name + '\b환영합니다',
                                    reply_markup=reply_markup)
                                update.message.reply_text(
                                    text="＊＊＊최근 1주일 공지 사항 UP＊＊＊\n오늘 : " + time.strftime("%m") + "월" + time.strftime(
                                        "%d") + "일" + "\n" + announcement)
                                update.message.reply_text(
                                    text="＊＊＊진행중인 과제＊＊＊\n오늘 : " + time.strftime("%m") + "월" + time.strftime(
                                        "%d") + "일" + "\n" + homework)
                                update.message.reply_text(
                                    text="＊＊＊최근 1주일 자료실 UP＊＊＊\n오늘 : " + time.strftime("%m") + "월" + time.strftime(
                                        "%d") + "일" + "\n" + resource)
                        except error as e:
                            update.message.reply_text("로그인 실패. 학번/비번 형식으로 입력해주세요.\n")
                            print(e)
                else:
                    update.message.reply_text("학번/비번 형식으로 입력해주세요.\n")
            else:
                update.message.reply_text("학번/비번 형식으로 입력해주세요.\n")
        except error as e:
            update.message.reply_text("학번/비번 형식으로 입력해주세요.\n")
            print(e)


def help(bot, update):
    update.message.reply_text(text="안녕하세요. CNU E-Learing 공지 도우미 인섭봇입니다.\n"
                                   "[사용법]\n"
                                   "1. '/start' 명령어를 입력or터치한다.\n"
                                   "2. '로그인'버튼을 눌러 아이디와 비밀번호를 입력한다.\n"
                                   "3. 기능을 활용한다.\n"
                                   "[명령어]\n"
                                   "1. /help : 현재창\n"
                                   "2. /start : 선택창")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def contol_main():
    # Create the Updater and pass it your bot's token.
    global token
    updater = Updater(token)
    dp = updater.dispatcher
    message_handler = MessageHandler(Filters.text, get_message)
    dp.add_handler(message_handler)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler('help', help))
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

