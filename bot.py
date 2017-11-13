# -*- coding: utf-8 -*-
from tgclient import *
import json
import redis
import re
import urllib.request as ur
from requests import get
import os
import asyncio
from datetime import datetime, timedelta
from PIL import Image
from multiprocessing import Process, freeze_support
import feedparser
import random
import subprocess
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import eyed3

def img(music, image):
    audio = MP3(music, ID3=ID3)
    # add ID3 tag if it doesn't exist
    try:
        audio.add_tags()
    except error:
        pass

    audio.tags.add(
        APIC(
            encoding=3,  # 3 is for utf-8
            mime='image/png',  # image/jpeg or image/png
            type=3,  # 3 is for the cover image
            desc=u'Cover',
            data=open(image, 'rb').read()
        )
    )
    audio.save()


def resize(file, x):
    path = file
    img = Image.open(path)
    img = img.resize((x, x), Image.ANTIALIAS)
    img.save(file)


r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
token = "token"
bot = TelegramBot(token)
sudo = [66488544, 180191663, 000000000]
soltan = [66488544, 180191663, 000000000]


def download(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = get(url)
        # write to file
        file.write(response.content)


def admin(chat_id, user_id):
    try:
        admin = bot.getChatMember(chat_id['chat']['id'], user_id['from']['id'])
        if admin:
            if admin['status'] == 'creator' or admin['status'] == 'administrator':
                return True
            elif user_id['from']['id'] in sudo:
                return True
    except Exception as e:
        print(e)



@bot.command(r'^[/#!][Aa]rshiv on$')
def arshiv(message):
    if message['from']['id'] in sudo:
        r.hset('arshiv', message['chat']['id'], 'ok')
        bot.sendMessage(message['chat']['id'], 'پیام های این گروه همگی به کانال ارشیو ارسال خواهند شد')


@bot.command(r'^[/#!][Aa]rshiv off$')
def arshivrem(message):
    if message['from']['id'] in sudo:
        r.hdel('arshiv', message['chat']['id'])
        bot.sendMessage(message['chat']['id'], 'این گروه از لیست گپ های پر کننده ارشیو حذف شد')


@bot.command(r'[/#!][Aa]mar$')
def stats(message):
    try:
        if message['from']['id'] in sudo:
            groups = r.scard("bot:gp")
            users = r.scard("bot:pv")
            gp = r.smembers("bot:gp")
            text = 'آمار:\n'
            for x in gp:
                expire = r.hget('expire', x)
                expire_start = r.hget('expire_start', x)
                ex_li = r.hget('ex_li', x)
                text += ''' ایدی گروه : {}
        تاریخ انقضا : {}
        این گروه به مدت {} روز در تاریخ {} شارژ شده است.
        ➖
        '''.format(x, ex_li, expire, expire_start)
                with open('gplist.txt', 'a') as out:
                    out.write(text + '\n')
        bot.sendDocument(message['chat']['id'], document=open('gplist.txt', 'rb'))
        os.remove('gplist.txt')
    except:
        pass


@bot.command(r'^[/#!][Tt]ime$')
def fatime(message):
    if admin(message, message):
        try:
            url = 'https://irapi.ir/time'
            req = ur.urlopen(url).read().decode('utf-8')
            jdat = json.loads(req)
            Fatime = jdat['FAtime']
            Fadate = jdat['FAdate']
            Endate = jdat['ENdate']
            Entime = jdat['ENtime']
            timephoto = 'http://smaznet.com/api/t2/?t=mmmd&time={}'.format(Entime)
            download(timephoto, 'time.jpg')
            text = '{}'.format(Fadate)
            bot.sendSticker(message['chat']['id'], sticker=open('time.jpg', 'rb'), reply_markup={
                'inline_keyboard': [
                    [
                        InlineKeyboard(text=text, url='https://t.me/tgMember')
                    ]
                ]
            })
        except:
            print('time error')
    freeze_support()
    Process(target=fatime)

@bot.command(r'^[/#!][Tt]ime@tgK[Ii][Nn][Gg][Bb]ot$')
def fatime(message):
    if admin(message, message):
        try:
            url = 'https://irapi.ir/time'
            req = ur.urlopen(url).read().decode('utf-8')
            jdat = json.loads(req)
            Fatime = jdat['FAtime']
            Fadate = jdat['FAdate']
            Endate = jdat['ENdate']
            Entime = jdat['ENtime']
            timephoto = 'http://smaznet.com/api/t2/?t=mmmd&time={}'.format(Entime)
            download(timephoto, 'time.jpg')
            text = '{}'.format(Fadate)
            bot.sendSticker(message['chat']['id'], sticker=open('time.jpg', 'rb'), reply_markup={
                'inline_keyboard': [
                    [
                        InlineKeyboard(text=text, url='https://t.me/tgMember')
                    ]
                ]
            })
        except:
            print('time error')
    freeze_support()
    Process(target=fatime)
    
    
@bot.command(r'^[/#!]([Ss]et[Aa]dd) (.*)')
def setadd(message, matches):
    if admin(message, message):
        if str(matches[0]).isnumeric():
            r.hset('setadd', message['chat']['id'], matches[0])
            bot.sendMessage(message['chat']['id'],
                            '''⚠️ #توجه 

📝 دستور محدودیت افزودن 
عضو به گروه فعال است.

از این لحظه تمام پیام های کاربران 
توسط ربات هوشمند حذف خواهد شد

هر کاربری که تمایل به چت کردن (درخواست دادن) در گروه را دارد 

موظف است که تعداد {} نفر از مخاطبین خود را اد کند تا چت کردن (درخواست دادن) در گروه برایش آزاد گردد'''.format(
                                matches[0]))


@bot.command(r'^[/#!][Aa]dd [Oo]n$')
def setadd(message):
    if admin(message, message):
        r.set('setaddon:{}'.format(message['chat']['id']), True)
        bot.sendMessage(message['chat']['id'], '''📝 دستور محدودیت افزودن 


عضو به گروه فعال شد.

✅ ON''')


@bot.command(r'^[/#!][Aa]dd [Oo]ff$')
def setadd(message):
    if admin(message, message):
        r.delete('setaddon:{}'.format(message['chat']['id']))
        bot.sendMessage(message['chat']['id'], 'محدودیت افزودن عضو خاموش شد')


@bot.command(r'^[/#!]([Gg]if) (.*) (.*)$')
def gif(message, matches):
    if admin(message, message):
        try:
            mm = {
                '1': 'Blinking+Text',
                '2': 'Dazzle+Text',
                '3': 'No+Button',
                '4': 'Walk+of+Fame+Animated',
                '5': 'Wag+Finger',
                '6': 'Glitter+Text',
                '7': 'Bliss',
                '8': 'Flasher',
                '9': 'Roman+Temple+Animated',
                '10': 'Paper+Airplane',
                '11': 'Princess+Heart+Animated',
                '12': 'Studio+Neon+Animated',
                '13': 'Wave+Animated',
                '14': 'Pink+Heart',
                '15': 'Inner+Heart+Animated',
                '16': 'Growing+Flowers',

            }
            if matches[1] and matches[1] in mm:
                sett = mm[matches[1]]
            text = ur.quote(matches[2], encoding='utf-8')
            colors = (
                '00FF00', '6699FF', 'CC99CC', 'CC66FF', '0066FF', '000000', 'CC0066', 'FF33CC', 'FF0000', 'FFCCCC',
                'FF66CC', '33FF00', 'FFFFFF', '00FF00')
            colorss = (
                '00FF00', '6699FF', 'CC99CC', 'CC66FF', '0066FF', '000000', 'CC0066', 'FF33CC', 'FF0000', 'FFCCCC',
                'FF66CC', '33FF00', 'FFFFFF', '00FF00')
            bc = random.choice(colors)
            tc = random.choice(colorss)
            url2 = 'http://www.imagechef.com/ic/maker.jsp?filter=&jitter=0&tid={}&color0={}&color1={}&color2=000000&customimg=&0={}'.format(
                sett, bc, tc, text)
            data = ur.urlopen(url2).read().decode('utf-8')
            jdat = json.loads(data)
            url = jdat['resImage']
            ur.urlretrieve(url, "gif.gif")
            bot.sendChatAction(message['chat']['id'], 'upload_document')
            bot.sendDocument(message['chat']['id'], document=open('gif.gif', 'rb'))
        except:
            bot.sendMessage(message['chat']['id'], 'نشد که')

    freeze_support()
    Process(target=gif)


@bot.command('^^[/#!][Ii]nfo$')
def info(message):
    if admin(message, message):
        text = r.get('texti:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        sticker = r.get('stickeri:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        photo = r.get('photoi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        doc = r.get('doci:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        gif = r.get('gifi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        voice = r.get('voicei:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        audio = r.get('audioi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        video = r.get('videoi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        contact = r.get('contacti:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        addmember = r.get('addmemberi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        matn = '''👤اطلاعات ارسالی شما :

            📑تعداد متن های ارسالی : {}
            📂تعداد فایل یا گیف ارسالی : {}
            🎭تعداد استیکر : {}
            🏞تعداد عکس : {}
            🗣تعداد ویس : {}
            🎼تعداد موزیک : {}
            🎬تعداد فیلم : {}
            🔢تعداد شماره تلفن : {}
            👥تعداد افرادی که به گروه افزودید : {}'''.format(text, doc, sticker, photo, voice, audio, video, contact,
                                                             addmember)
        bot.sendMessage(message['chat']['id'], matn)

@bot.command('^^[/#!][Ii]nfo@tgKINGbot$')
def info(message):
    if admin(message, message):
        text = r.get('texti:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        sticker = r.get('stickeri:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        photo = r.get('photoi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        doc = r.get('doci:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        gif = r.get('gifi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        voice = r.get('voicei:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        audio = r.get('audioi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        video = r.get('videoi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        contact = r.get('contacti:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        addmember = r.get('addmemberi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        matn = '''👤اطلاعات ارسالی شما :

            📑تعداد متن های ارسالی : {}
            📂تعداد فایل یا گیف ارسالی : {}
            🎭تعداد استیکر : {}
            🏞تعداد عکس : {}
            🗣تعداد ویس : {}
            🎼تعداد موزیک : {}
            🎬تعداد فیلم : {}
            🔢تعداد شماره تلفن : {}
            👥تعداد افرادی که به گروه افزودید : {}'''.format(text, doc, sticker, photo, voice, audio, video, contact,
                                                             addmember)
        bot.sendMessage(message['chat']['id'], matn)

        
@bot.command(r'^(قفل گروه)$')
def lockall(message):
    if admin(message, message):
        r.hset('lockall', message['chat']['id'], 'فعال ✔️')
        bot.sendMessage(message['chat']['id'], "گروه قفل شد")
        bot.sendDocument(message['chat']['id'], document=open('mute.gif', 'rb'), caption='''
    #گروه_تعطیل_است
    #چیزی_ارسال_نکنید_چون
    #توسط_ربات_حذف_خواهد_شد
''')

@bot.command(r'^[/#!][Ll]ock [Aa]ll$')
def lockall1(message):
    if admin(message, message):
        r.hset('lockall', message['chat']['id'], 'فعال ✔️')
        bot.sendMessage(message['chat']['id'], "گروه قفل شد")
        bot.sendDocument(message['chat']['id'], document=open('mute.gif', 'rb'), caption='''
    #گروه_تعطیل_است
    #چیزی_ارسال_نکنید_چون
    #توسط_ربات_حذف_خواهد_شد
''')


@bot.command(r'^(بازکردن گروه)$')
def unlockall(message):
    if admin(message, message):
        r.hset('lockall', message['chat']['id'], 'غیر فعال ❌')
        bot.sendMessage(message['chat']['id'], "گروه باز شد")

@bot.command(r'^[/#!][Uu]n[Ll]ock [Aa]ll$')
def unlockall1(message):
    if admin(message, message):
        r.hset('lockall', message['chat']['id'], 'غیر فعال ❌')
        bot.sendMessage(message['chat']['id'], "گروه باز شد")

# start
@bot.command('^[/#!]start$')
def text(message):
    if message['chat']['type'] == 'private':
        r.sadd('bot:pv', message['chat']['id'])
        text = 'سلام ✋🏻 ' + message['from']['first_name'] + ' \n\nبه ربات تلگرام کینگ خوش اومدی\nلطفا زبون مورد نظر خودتو انتخاب کن\n\nHi ✋🏻 ' + message['from']['first_name'] + ' \n\nWelcome to TeleGram KING Robot\nPlease select your language'
        bot.sendMessage(message['chat']['id'], text,
                                        reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='پارسی', callback_data='fa'),
                ],
                [
                    InlineKeyboard(text='English', callback_data='en'),
                ],
            ],
        })
        
@bot.callback_query()
def callback(message):
  
  
        fa = ['fa']

        linkfa = {
            'fa': 'https://telegram.me/tgMember',
        }
        if message['data'] in fa:
            link = linkfa[message['data']]
            text = '''\n❗️ لازمه کارکرد صحیح و استفاده از تمامی قابلیت های ربات \n🔳 مدیریت کاربر و ربات باهم در یک گروه میباشد ❌\n راهنما         \help  \n
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                [
                    InlineKeyboard(text='افزودن به گروه', url='https://telegram.me/tgkingbot?startgroup=start')
                ],
                [

                    InlineKeyboard(text='مدیرت کانال', url='https://t.me/tgGuardbot'),
                    InlineKeyboard(text='دکمه شیشه ای', url='https://t.me/tgAttachbot'),
                ],
                [
                    InlineKeyboard(text='ویرایش عکس', url='https://t.me/tgMarkbot'),
                    InlineKeyboard(text='آنتی اسپم', url='https://t.me/tgGuardRobot'),
                ],
                [
                    InlineKeyboard(text='کانال ما', url='https://t.me/tgMember'),
                    InlineKeyboard(text='سازنده و ثبت سفارشات', url='https://t.me/sajjad_021'),
                ],
                [
                    InlineKeyboard(text='درباره ما', url='https://telegram.me/tgMemberPlus')
                ],
                                    ]
                                }, parse_mode='Markdown')

        en = ['en']

        linken = {
            'en': 'https://telegram.me/tgMember',
        }
        if message['data'] in en:
            link = linken[message['data']]
            text = '''\n\n\n❗️ For run correct robot \n🔳 you must admin robot to your group or other group that you are administrator ❌\n help menu         \help  \n
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                [
                    InlineKeyboard(text='Add to group', url='https://telegram.me/tgkingbot?startgroup=start')
                ],
                [

                    InlineKeyboard(text='Channel moderator', url='https://t.me/tgGuardbot'),
                    InlineKeyboard(text='Inline keyboard', url='https://t.me/tgAttachbot'),
                ],
                [
                    InlineKeyboard(text='Watermark', url='https://t.me/tgMarkbot'),
                    InlineKeyboard(text='Antispam', url='https://t.me/tgGuardRobot'),
                ],
                [
                    InlineKeyboard(text='Channel', url='https://t.me/tgMember'),
                    InlineKeyboard(text='Develop and order advertising', url='https://t.me/sajjad_021'),
                ],
                [
                    InlineKeyboard(text='about me', url='https://telegram.me/tgMemberPlus')
                ],
                                    ]
                                }, parse_mode='Markdown')

                 
@bot.command('^[/#!]([Ss]hort) (.*)$')
def short(message, matches):
    if admin(message, message):
        try:
            link = ur.quote(matches[0], encoding='utf-8')
            bitly = 'https://api-ssl.bitly.com/v3/shorten?access_token=f2d0b4eabb524aaaf22fbc51ca620ae0fa16753d&longUrl={}'.format(
                link)
            bitn = ur.urlopen(bitly).read().decode('utf-8')
            jdat = json.loads(bitn)
            text = '''📍لینک اصلی : {}
            🌐لینک کوتاه شده : {}
            برای کپی کردن لینک میتوانید بر روی متن لینک زیر کلیک کرده. و برای اشتراک گزاری از دکمه اشتراک گذاری استفاده کنید
            `{}`'''.format(jdat['data']['long_url'], jdat['data']['url'], jdat['data']['url'])
            bot.sendMessage(message['chat']['id'], text, parse_mode='Markdown', disable_web_page_preview=True,
                            reply_markup={
                                'inline_keyboard': [
                                    [
                                        InlineKeyboard(text='اشتراک گذاری',
                                                       url='https://t.me/share/url?url={}'.format(jdat['data']['url']))
                                    ]
                                ]
                            })
        except:
            print('error')


@bot.command('^[/#!]([Aa]parat) (.*)$')
def aparat(message, matches):
    if admin(message, message):
        try:
            text = ur.quote(matches[0], encoding='utf-8')
            url = 'http://www.aparat.com/etc/api/videoBySearch/text/{}'.format(text)
            req = ur.urlopen(url).read().decode('utf-8')
            jdat = json.loads(req)
            data = jdat['videobysearch']
            app = str()
            for x in data:
                title = x['title']
                visit = x['visit_cnt']
                link = 'http://aparat.com/v/{}'.format(x['uid'])
                app += '📽' + title + "\n👀تعداد بازدید : {}".format(
                    visit) + "\n[🌐مشاهده ویدیو در آپارات]({})\n\n".format(
                    link)
            bot.sendMessage(message['chat']['id'], app, parse_mode='Markdown', disable_web_page_preview=True)
        except:
            print('error aparat')


@bot.command('^[/#!][Nn]ews$')
def news(message):
    if admin(message, message):
        try:
            urlxml = 'http://www.yjc.ir/fa/rss/allnews'
            feed = feedparser.parse(urlxml)
            text0 = feed['entries'][0]['title']
            text1 = feed['entries'][1]['title']
            text2 = feed['entries'][2]['title']
            text3 = feed['entries'][3]['title']
            text4 = feed['entries'][4]['title']
            links0 = feed['entries'][0]['links'][0]['href']
            links1 = feed['entries'][1]['links'][0]['href']
            links2 = feed['entries'][2]['links'][0]['href']
            links3 = feed['entries'][3]['links'][0]['href']
            links4 = feed['entries'][4]['links'][0]['href']

            text = '''📑پنج عنوان خبر اخیر سایت باشگاه خبر نگاران جوان :

            1️⃣[{}]({})

            2️⃣[{}]({})

            3️⃣[{}]({})

            4️⃣[{}]({})

            5️⃣[{}]({})

            برای مشاهده خبر بر روی عنوان خبر کلیک کنید'''.format(text0, links0, text1, links1, text2, links2, text3,
                                                                 links3,
                                                                 text4, links4)
            bot.sendMessage(message['chat']['id'], text, parse_mode='Markdown', disable_web_page_preview=True,
                            reply_markup={
                                'inline_keyboard': [
                                    [
                                        InlineKeyboard(text='🔊 @tgMember', url='https://t.me/tgMember')
                                    ]
                                ]
                            })
        except:
            print('error yjc')

@bot.command('^[/#!][Nn]ews@tgKINGbot$')
def news(message):
    if admin(message, message):
        try:
            urlxml = 'http://www.yjc.ir/fa/rss/allnews'
            feed = feedparser.parse(urlxml)
            text0 = feed['entries'][0]['title']
            text1 = feed['entries'][1]['title']
            text2 = feed['entries'][2]['title']
            text3 = feed['entries'][3]['title']
            text4 = feed['entries'][4]['title']
            links0 = feed['entries'][0]['links'][0]['href']
            links1 = feed['entries'][1]['links'][0]['href']
            links2 = feed['entries'][2]['links'][0]['href']
            links3 = feed['entries'][3]['links'][0]['href']
            links4 = feed['entries'][4]['links'][0]['href']

            text = '''📑پنج عنوان خبر اخیر سایت باشگاه خبر نگاران جوان :

            1️⃣[{}]({})

            2️⃣[{}]({})

            3️⃣[{}]({})

            4️⃣[{}]({})

            5️⃣[{}]({})

            برای مشاهده خبر بر روی عنوان خبر کلیک کنید'''.format(text0, links0, text1, links1, text2, links2, text3,
                                                                 links3,
                                                                 text4, links4)
            bot.sendMessage(message['chat']['id'], text, parse_mode='Markdown', disable_web_page_preview=True,
                            reply_markup={
                                'inline_keyboard': [
                                    [
                                        InlineKeyboard(text='🔊 @tgMember', url='https://t.me/tgMember')
                                    ]
                                ]
                            })
        except:
            print('error yjc')


@bot.command('^[/#!]([Qq]uran) (.*) (.*)$')
def quran(message, matches):
    if admin(message, message):
        try:
            if str(matches[1]).isnumeric() and str(matches[2]).isnumeric():
                url = 'http://api.alquran.cloud/ayah/{}:{}/ar.alafasy'.format(matches[1], matches[2])
                req = ur.urlopen(url).read().decode('utf-8')
                jdat = json.loads(req)
                if jdat['status'] == 'OK':
                    text = jdat['data']['text']
                    sore = jdat['data']['surah']['name']
                    ayeall = jdat['data']['surah']['numberOfAyahs']
                    juz = jdat['data']['juz']
                    page = jdat['data']['page']
                    if jdat['data']['sajda'] == False:
                        sajde = 'ندارد'
                    else:
                        sajde = 'دارد'
                    audio = jdat['data']['audio']
                    mm = '''📋مشخصات :

                        🗒متن آیه :
                        {}

                        📍نام سوره : {}
                        📝تعداد آیات : {}
                        🔖شماره جزء : {}
                        📒صفحه ای که این آیه در آن قرار دارد : {}

                        🕋این آیه سجده {}

                        🔊صوت آیه در زیر 👇🏻 
                        [-]({})'''.format(text, sore, ayeall, juz, page, sajde, audio)
                    bot.sendMessage(message['chat']['id'], mm, parse_mode='Markdown')
        except:
            print('quran error')
    freeze_support()
    Process(target=quran)


@bot.command('^[/#!][Vv]ote$')
def vote(message):
    if admin(message, message):
        vote1 = r.scard('vote1:{}'.format(message['chat']['id']))
        vote2 = r.scard('vote2:{}'.format(message['chat']['id']))
        vote3 = r.scard('vote3:{}'.format(message['chat']['id']))
        voteall = r.scard('voteall:{}'.format(message['chat']['id']))

        text = 'نظر خود را در مورد عملکرد گروه اعلام کنید\n1-عالی ({})\n2-متوسط ({})\n3-ضعیف ({})\nتعداد کل آرا : {}'.format(
            vote1, vote2, vote3, voteall)
        bot.sendMessage(message['chat']['id'], text, reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='عالی', callback_data='vote1')
                ],
                [
                    InlineKeyboard(text='متوسط', callback_data='vote2')
                ],
                [
                    InlineKeyboard(text='ضعیف', callback_data='vote3')
                ]
            ]
        })


@bot.command('^(تنظیم لینک) (.*)$')
def setlink(message, matches):
    if admin(message, message):
        try:
            r.hset('link', message['chat']['id'], matches[0])
            text = 'لینک گروه شما ثبت شد\n[{}]({})'.format(message['chat']['title'], matches[0])
            bot.sendMessage(message['chat']['id'], text, parse_mode='Markdown')
        except:
            print('error')


@bot.command('^لینک$')
def link(message):
    if admin(message, message):
        link = r.hget('link', message['chat']['id'])
        if link:
            text = '[{}]({})'.format(message['chat']['title'], link)
            bot.sendMessage(message['chat']['id'], text, parse_mode='Markdown')
            bot.sendMessage(message['chat']['id'], 'لینک گروه :\n{}'.format(link))
        else:
            bot.sendMessage(message['chat']['id'], 'ابتدا لینک را ست کنید')


# expire
@bot.command('^[/#!]([Cc]harge) (.*)$')
def text(message, matches):
    try:
        if message['from']['id'] in sudo:
            if str(matches[1]).isnumeric():
                day = matches[1] * 24
                sc = Timer.hour_to_sec(day)
                irapi = ur.urlopen(url='http://irapi.ir/time').read().decode('utf-8')
                jdat = json.loads(irapi)
                time = jdat['FAdate']
                TIME = datetime.now() + timedelta(days=int(matches[1]))
                y, m, d = TIME.year, TIME.month, TIME.day
                cnv = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
                yy = 979
                y -= 1600
                if (m > 2):
                    y2 = y + 1
                else:
                    y2 = y
                days = (365 * y) + (int((y2 + 3) / 4)) - (int((y2 + 99) / 100)) + (int((y2 + 399) / 400)) - 80 + d + \
                       cnv[
                           m - 1]
                yy += 33 * (int(days / 12053))
                days %= 12053
                yy += 4 * (int(days / 1461))
                days %= 1461
                if (days > 365):
                    yy += int((days - 1) / 365)
                    days = (days - 1) % 365
                if (days < 186):
                    mm = 1 + int(days / 31)
                    dd = 1 + (days % 31)
                else:
                    mm = 7 + int((days - 186) / 30)
                    dd = 1 + ((days - 186) % 30)
                ex_li = '{}/{}/{}'.format(yy, mm, dd)
                r.hset('expire', message['chat']['id'], matches[1])
                r.hset('expire_start', message['chat']['id'], time)
                r.hset('ex_li', message['chat']['id'], ex_li)
                text = '📅 #تاریخ_انقضا_گروه\n\nبه {} روز دیگر تنظیم شد\nتاریخ شروع : {}\nتاریخ انقضا : {}'.format(
                    matches[1], time, ex_li)
                bot.sendMessage(message['chat']['id'], text)
                text_ch = '{}\nاطلاعات گروه :\nایدی گروه : {}\nنام گروه : {}'.format(text, message['chat']['id'],
                                                                                     message['chat']['title'])
                bot.sendMessage('@member_adder', text_ch)
                
            def left():
                r.hset('gp', message['chat']['id'], False)
                text = 'تاریخ انقاضی گروه به اتمام رسید\nما رفتیم\nبای همگی'
                bot.sendMessage(message['chat']['id'], text)
                bot.leaveChat(message['chat']['id'])

                Timer(sc, left)
    except:
        pass


# add
@bot.command('^[/#!][Aa]dd$')
def text(message):
    try:
      if message['from']['id']:
                r.sadd('bot:gp', message['chat']['id'])
                r.hset('gp', message['chat']['id'], True)
                r.hset('locklink', message['chat']['id'], 'فعال ✔️')
                r.hset('lockfwd', message['chat']['id'], 'فعال ✔️')
                r.hset('lockbot', message['chat']['id'], 'فعال ✔️')
                r.hset('lockusername', message['chat']['id'], 'فعال ✔️')
                r.hset('lockcontact', message['chat']['id'], 'فعال ✔️')
                text = '''گروه به دیتابیس ربات افزوده شد.👌🏻
        📝نام گروه : {}
        📍ایدی گروه : {}
        ⚠️برای استفاده از ربات باید در کانال ربات عضو باشید
        ☑️برای عضویت در کانال بر روی دکمه زیر کلیک کنید'''.format(message['chat']['title'], message['chat']['id'])
                bot.sendMessage(message['chat']['id'], text, parse_mode='Markdown', reply_markup={
                    'inline_keyboard': [
                        [
                            InlineKeyboard(text="🔊 @tgMember", url="t.me/tgMember"),
                        ]
                    ]
                })
    except:
             if message['from']['id']:
                r.sadd('bot:gp', message['chat']['id'])
                r.hset('gp', message['chat']['id'], True)
                text = '''گروه به دیتابیس ربات افزوده شد.👌🏻
        📝نام گروه : {}
        📍ایدی گروه : {}
        ⚠️برای استفاده از ربات باید در کانال ربات عضو باشید
        ☑️برای عضویت در کانال بر روی دکمه زیر کلیک کنید'''.format('-', message['chat']['id'])
                bot.sendMessage(message['chat']['id'], text, parse_mode='Markdown', reply_markup={
                    'inline_keyboard': [
                        [
                            InlineKeyboard(text="🔊 @tgMember", url="t.me/tgMember"),
                        ]
                    ]
                })

@bot.command('^[/#!]([Aa]dd) (.*)$')
def text(message, matches):
    try:
        for x in sudo:
            if x == message['from']['id']:
                r.sadd('bot:gp', matches[0])
                r.hset('gp', matches[0], True)
                text = '''گروه به دیتابیس ربات افزوده شد.👌🏻
                    📝نام گروه : {}
                    📍ایدی گروه : {}
                    ⚠️برای استفاده از ربات باید در کانال ربات عضو باشید
                    ☑️برای عضویت در کانال بر روی دکمه زیر کلیک کنید'''.format(message['chat']['title'],
                                                                              message['chat']['id'])
                bot.sendMessage(message['chat']['id'], text, parse_mode='Markdown', reply_markup={
                    'inline_keyboard': [
                        [
                            InlineKeyboard(text="🔊 @tgMember", url="t.me/tgMember"),
                        ]
                    ]
                })
    except:
        for x in sudo:
            if x == message['from']['id']:
                r.sadd('bot:gp', matches[0])
                r.hset('gp', matches[0], True)
                text = '''گروه به دیتابیس ربات افزوده شد.👌🏻
                    📝نام گروه : {}
                    📍ایدی گروه : {}
                    ⚠️برای استفاده از ربات باید در کانال ربات عضو باشید
                    ☑️برای عضویت در کانال بر روی دکمه زیر کلیک کنید'''.format('-', message['chat']['id'])
                bot.sendMessage(message['chat']['id'], text, parse_mode='Markdown', reply_markup={
                    'inline_keyboard': [
                        [
                            InlineKeyboard(text="🔊 @tgMember", url="t.me/tgMember"),
                        ]
                    ]
                })


# rem
@bot.command('^[/#!][Rr]em$')
def text(message):
    for x in sudo:
        if x == message['from']['id']:
            r.hdel('gp', message['chat']['id'])
            text = 'group has been removed'
            bot.sendMessage(message['chat']['id'], text, parse_mode='Markdown')


@bot.command('^بی صدا$')
def mute(message):
    if admin(message, message):
        if 'reply_to_message' in message:
            if not message['reply_to_message']['from']['id'] in sudo:
                bot.restrictChatMember(message['chat']['id'], message['reply_to_message']['from']['id'], until_date=0,
                                       can_send_messages=False, can_send_media_messages=False,
                                       can_send_other_messages=False)
                bot.sendMessage(message['chat']['id'], '😈')
            else:
                bot.sendMessage(message['chat']['id'], '''با همه آره با ما هم آره؟😜
ای شیطون😝''')


@bot.command('^صدا دار$')
def mute(message):
    if admin(message, message):
        if 'reply_to_message' in message:
            bot.restrictChatMember(message['chat']['id'], message['reply_to_message']['from']['id'], until_date=0,
                                   can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
            bot.sendMessage(message['chat']['id'], '😛')



@bot.command('^[/#!][Ii][Dd]$')
def text(message):
    try:
        photoo = bot.getUserProfilePhotos(message['from']['id'])
        text = '👥ایدی گروه : {}\n👤ایدی شما : {}'.format(message['chat']['id'], message['from']['id'])
        bot.sendPhoto(message['chat']['id'], photo=photoo['photos'][0][1]['file_id'], caption=text, reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text="🔊 @tgMember", url="t.me/tgMember"),
                ],
            ]
        })
    except:
        textt = '👥ایدی گروه : {}\n👤ایدی شما : {}'.format(message['from']['id'], message['chat']['id'])
        bot.sendMessage(message['chat']['id'], textt)

@bot.command('^[/#!][Ii][Dd]@tgKINGbot$')
def text(message):
    try:
        photoo = bot.getUserProfilePhotos(message['from']['id'])
        text = '👥ایدی گروه : {}\n👤ایدی شما : {}'.format(message['chat']['id'], message['from']['id'])
        bot.sendPhoto(message['chat']['id'], photo=photoo['photos'][0][1]['file_id'], caption=text, reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text="🔊 @tgMember", url="t.me/tgMember"),
                ],
            ]
        })
    except:
        textt = '👥ایدی گروه : {}\n👤ایدی شما : {}'.format(message['from']['id'], message['chat']['id'])
        bot.sendMessage(message['chat']['id'], textt)

@bot.command('^[/#!][Cc]alc$')
def text(message):
    print(message)
    r.hset('calc', message['from']['id'], 0)
    text = 'ماشین حساب :\n\n{}'.format(r.hget('calc', message['from']['id']))

    id = bot.sendMessage(message['chat']['id'], text, reply_markup={
        'inline_keyboard': [
            [
                InlineKeyboard(text="پیشرفته", callback_data="pro"),
                InlineKeyboard(text="🆑", callback_data="clean"),
            ],
            [
                InlineKeyboard(text="7", callback_data="7"),
                InlineKeyboard(text="8", callback_data="8"),
                InlineKeyboard(text="9", callback_data="9"),
                InlineKeyboard(text="➗", callback_data="taq"),
            ],
            [
                InlineKeyboard(text="4", callback_data="mod"),
                InlineKeyboard(text="5", callback_data="help"),
                InlineKeyboard(text="6", callback_data="alo"),
                InlineKeyboard(text="✖️", callback_data="zarb"),
            ],
            [
                InlineKeyboard(text="3", callback_data="3"),
                InlineKeyboard(text="2", callback_data="2"),
                InlineKeyboard(text="1", callback_data="1"),
                InlineKeyboard(text="➖", callback_data="menha"),
            ],
            [
                InlineKeyboard(text=".", callback_data="noghte"),
                InlineKeyboard(text="0", callback_data="0"),
                InlineKeyboard(text="=", callback_data="mosavi"),
                InlineKeyboard(text="➕", callback_data="jam"),
            ],
            [
                InlineKeyboard(text="بستن ماشین حساب🔚", callback_data="close_calc")
            ],

        ]
    })
    id_bot = id['message_id']
    r.hset('calc_u', id_bot, message['from']['id'])


@bot.command('^[/#!][Cc]alc@tgKINGbot$')
def text(message):
    print(message)
    r.hset('calc', message['from']['id'], 0)
    text = 'ماشین حساب :\n\n{}'.format(r.hget('calc', message['from']['id']))

    id = bot.sendMessage(message['chat']['id'], text, reply_markup={
        'inline_keyboard': [
            [
                InlineKeyboard(text="پیشرفته", callback_data="pro"),
                InlineKeyboard(text="🆑", callback_data="clean"),
            ],
            [
                InlineKeyboard(text="7", callback_data="7"),
                InlineKeyboard(text="8", callback_data="8"),
                InlineKeyboard(text="9", callback_data="9"),
                InlineKeyboard(text="➗", callback_data="taq"),
            ],
            [
                InlineKeyboard(text="4", callback_data="mod"),
                InlineKeyboard(text="5", callback_data="help"),
                InlineKeyboard(text="6", callback_data="alo"),
                InlineKeyboard(text="✖️", callback_data="zarb"),
            ],
            [
                InlineKeyboard(text="3", callback_data="3"),
                InlineKeyboard(text="2", callback_data="2"),
                InlineKeyboard(text="1", callback_data="1"),
                InlineKeyboard(text="➖", callback_data="menha"),
            ],
            [
                InlineKeyboard(text=".", callback_data="noghte"),
                InlineKeyboard(text="0", callback_data="0"),
                InlineKeyboard(text="=", callback_data="mosavi"),
                InlineKeyboard(text="➕", callback_data="jam"),
            ],
            [
                InlineKeyboard(text="بستن ماشین حساب🔚", callback_data="close_calc")
            ],

        ]
    })
    id_bot = id['message_id']
    r.hset('calc_u', id_bot, message['from']['id'])

@bot.message("new_chat_member")
def mm(message):
    r.incr('addmemberi:{}:{}'.format(message['chat']['id'], message['from']['id']))
    lockbot = r.hget('lockbot', message['chat']['id'])
    locktgservice = r.hget('locktgservice', message['chat']['id'])
    print(message)
    try:
        if locktgservice == 'فعال ✔️':
            bot.deleteMessage(message['chat']['id'], message['message_id'])

        if lockbot == 'فعال ✔️':
            if 'username' in message['new_chat_member']:
                if message['new_chat_member']['username'][-3:] == "bot":
                    if not message['new_chat_member']['username'] == "tgKINGbot":
                        bot.kickChatMember(message['chat']['id'], message['new_chat_member']['id'])
    except:
        print('error')


@bot.command('^(بی صدا) (.*)$')
def muteid(message, matches):
    if admin(message, message):
        if str(matches[0]).isnumeric():
            bot.restrictChatMember(message['chat']['id'], matches[0], until_date=0,
                                   can_send_messages=False, can_send_media_messages=False,
                                   can_send_other_messages=False)
            bot.sendMessage(message['chat']['id'],
                            'کاربر با ایدی {} در لیست ممنوعیت ارسال پیام قرار گرفت.🔇'.format(matches[0]))

@bot.command('^[/#!]([Mm]ute) (.*)$')
def muteid2(message, matches):
    if admin(message, message):
        if str(matches[0]).isnumeric():
            bot.restrictChatMember(message['chat']['id'], matches[0], until_date=0,
                                   can_send_messages=False, can_send_media_messages=False,
                                   can_send_other_messages=False)
            bot.sendMessage(message['chat']['id'],
                            'کاربر با ایدی {} در لیست ممنوعیت ارسال پیام قرار گرفت.🔇'.format(matches[0]))

@bot.command('^[/#!]([Ss]ilent) (.*)$')
def muteid3(message, matches):
    if admin(message, message):
        if str(matches[0]).isnumeric():
            bot.restrictChatMember(message['chat']['id'], matches[0], until_date=0,
                                   can_send_messages=False, can_send_media_messages=False,
                                   can_send_other_messages=False)
            bot.sendMessage(message['chat']['id'],
                            'کاربر با ایدی {} در لیست ممنوعیت ارسال پیام قرار گرفت.🔇'.format(matches[0]))

@bot.command('^(صدا دار) (.*)$')
def unmuteid(message, matches):
    if admin(message, message):
        if str(matches[0]).isnumeric():
            bot.restrictChatMember(message['chat']['id'], matches[0], until_date=0,
                                   can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
            bot.sendMessage(message['chat']['id'], 'کاربر {} آزاد شد'.format(matches[0]))

@bot.command('^[/#!]([Uu]n[Mm]ute) (.*)$')
def unmuteid1(message, matches):
    if admin(message, message):
        if str(matches[0]).isnumeric():
            bot.restrictChatMember(message['chat']['id'], matches[0], until_date=0,
                                   can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
            bot.sendMessage(message['chat']['id'], 'کاربر {} آزاد شد'.format(matches[0]))


@bot.command('^[/#!]([Bb]an[Aa]ll) (.*)$')
def muteall(message, matches):
    if message['from']['id'] in soltan:
        if str(matches[0]).isnumeric():
            groups = r.smembers("bot:gp")
            for i in groups:
                try:
                    bot.restrictChatMember(i, matches[0], until_date=0,
                                           can_send_messages=False, can_send_media_messages=False,
                                           can_send_other_messages=False)
                except:
                    pass
            bot.sendMessage(message['chat']['id'],
                            'کاربر {} در تمام گروه های ربات در حالت سکوت قرار گرفت.🔇'.format(matches[0]))
    freeze_support()
    Process(target=muteall)


@bot.command('^[/#!]([Uu]n[Bb]an[Aa]ll) (.*)$')
def unmuteall(message, matches):
    if message['from']['id'] in soltan:
        if str(matches[0]).isnumeric():
            groups = r.smembers("bot:gp")
            for i in groups:
                try:
                    bot.restrictChatMember(i, matches[0], until_date=0,
                                           can_send_messages=True, can_send_media_messages=True,
                                           can_send_other_messages=True)
                except:
                    pass
            bot.sendMessage(message['chat']['id'],
                            'کاربر {} از حالت سکوت کلی خارج شد و میتواند در تمام گروه های ربات چت کند'.format(
                                matches[0]))
    freeze_support()
    Process(target=unmuteall)


@bot.edited_message()
def edit(message):
    print(message)
    locklink = r.hget('locklink', message['chat']['id'])
    lockusername = r.hget('lockusername', message['chat']['id'])
    lockfa = r.hget('lockfa', message['chat']['id'])
    locken = r.hget('locken', message['chat']['id'])
    lockall = r.hget('lockall', message['chat']['id'])
    try:
        if not admin(message, message):
            if locklink == 'فعال ✔️':
                if re.search(r'[Tt]\.[Mm][Ee]', message['text']):
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
                if re.search(r'[Tt][Ee][Ll][Ee][Gg][Rr][Aa][Mm]\.[Mm][Ee]', message['text']):
                    bot.deleteMessage(message['chat']['id'], message['message_id'])

            if lockusername == 'فعال ✔️':
                if re.search(r'@', message['text']):
                    bot.deleteMessage(message['chat']['id'], message['message_id'])

            if lockall == 'فعال ✔️':
                bot.deleteMessage(message['chat']['id'], message['message_id'])

            if 'caption' in message:
                if locklink == 'فعال ✔️':
                    if re.search(r'[Tt]\.[Mm][Ee]', message["caption"]):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])
                    if re.search(r'[Tt][Ee][Ll][Ee][Gg][Rr][Aa][Mm]\.[Mm][Ee]', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

                if lockusername == 'فعال ✔️':
                    if re.search(r'@', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

                if lockall == 'فعال ✔️':
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
    except:
        print('error edit')
    freeze_support()
    Process(target=edit)

@bot.command('^[/#!][Kk]ick$')
def kick(message):
    if admin(message, message):
        if 'reply_to_message' in message:
            ban = bot.kickChatMember(message['chat']['id'], message['reply_to_message']['from']['id'])
            if ban == True:
                bot.sendMessage(message['chat']['id'], 'اخراج شد😶')
            else:
                bot.sendMessage(message['chat']['id'], 'اخراج نشد که☹️')


@bot.command('^اخراج$')
def ban(message):
    if admin(message, message):
        if 'reply_to_message' in message:
            ban = bot.kickChatMember(message['chat']['id'], message['reply_to_message']['from']['id'])
            if ban == True:
                bot.sendMessage(message['chat']['id'], 'اخراج شد😶')
            else:
                bot.sendMessage(message['chat']['id'], 'اخراج نشد که☹️')


def add():
    ms = r.get('mmd:{}:{}'.format(message['chat']['id']))
    if 'message_id' in message:
        bot.deleteMessage(message['chat']['id'], ms)


@bot.command(r'^(فیلتر) (.*)$')
def filter(message, matches):
    if admin(message, message):
        r.sadd('filter:bot:{}'.format(message['chat']['id']), matches[0])
        text = 'کلمه {} به لیست فیلتر افزوده شد✅'.format(matches[0])
        bot.sendMessage(message['chat']['id'], text)

@bot.command(r'^(حذف) (.*)$')
def filter(message, matches):
    if admin(message, message):
        r.srem('filter:bot:{}'.format(message['chat']['id']), matches[0])
        text = 'کلمه {} از فیلتر خارج شد🗑'.format(matches[0])
        bot.sendMessage(message['chat']['id'], text)

@bot.command(r'^پاک کردن فیلتر$')
def filter(message):
    if admin(message, message):
        r.delete('filter:bot:{}'.format(message['chat']['id']))
        text = 'لیست فیلتر پاک سازی شد🗑'
        bot.sendMessage(message['chat']['id'], text)


@bot.command(r'^لیست فیلتر$')
def filter(message):
    if admin(message, message):
        list = r.smembers('filter:bot:{}'.format(message['chat']['id']))
        text = '📑لیست کلمات فیلتر شده :\n'
        for x in list:
            text += '>{}\n'.format(x)
        bot.sendMessage(message['chat']['id'], text)


@bot.message("message")
def message(message):
    try:
        print(message)
        r.incr('texti:{}:{}'.format(message['chat']['id'], message['from']['id']))
        if not message['from']['id'] in sudo:
            if not r.hget('gp', message['chat']['id']):
                text = 'گروه در دیتابیس ربات موجود نمی باشد.با دستور /add  گروه خود را به دیتا بیس ربات اضافه کنید و ربات را مدیر گروه خود کنید.'
                bot.sendMessage(message['chat']['id'], text)
        locklink = r.hget('locklink', message['chat']['id'])
        lockusername = r.hget('lockusername', message['chat']['id'])
        lockfa = r.hget('lockfa', message['chat']['id'])
        locken = r.hget('locken', message['chat']['id'])
        lockall = r.hget('lockall', message['chat']['id'])
        lockfwd = r.hget('lockfwd', message['chat']['id'])
        lockurl = r.hget('lockurl', message['chat']['id'])
        setaddon = r.get('setaddon:{}'.format(message['chat']['id']))
        setadd = r.hget('setadd', message['chat']['id'])
        addmember = r.get('addmemberi:{}:{}'.format(message['chat']['id'], message['from']['id'])) or '0'
        if not admin(message, message):
            list = r.smembers('filter:bot:{}'.format(message['chat']['id']))
            for x in list:
                pattern = re.compile(x)
                if pattern.search(message["text"]):
                    bot.deleteMessage(message['chat']['id'], message['message_id'])

            if setaddon:
                if setadd > addmember:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])

            if lockfwd == 'فعال ✔️':
                if 'forward_date' in message:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])

            if locklink == 'فعال ✔️':
                if re.search(r'[Tt]\.[Mm][Ee]', message['text']):
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
                if re.search(r'[Tt][Ee][Ll][Ee][Gg][Rr][Aa][Mm]\.[Mm][Ee]', message['text']):
                    bot.deleteMessage(message['chat']['id'], message['message_id'])

            if lockusername == 'فعال ✔️':
                if re.search(r'@', message['text']):
                    bot.deleteMessage(message['chat']['id'], message['message_id'])

            if lockall == 'فعال ✔️':
                bot.deleteMessage(message['chat']['id'], message['message_id'])
    except:
        print('error text message')
    freeze_support()
    Process(target=message)


@bot.message('photo')
def photo(message):
    arshiv = r.hget('arshiv', message['chat']['id'])
    if arshiv == 'ok':
        bot.forwardMessage('@arshivpic', from_chat_id=message['chat']['id'], message_id=message['message_id'])
    r.incr('photoi:{}:{}'.format(message['chat']['id'], message['from']['id']))
    locklink = r.hget('locklink', message['chat']['id'])
    lockusername = r.hget('lockusername', message['chat']['id'])
    lockfa = r.hget('lockfa', message['chat']['id'])
    locken = r.hget('locken', message['chat']['id'])
    lockall = r.hget('lockall', message['chat']['id'])
    lockphoto = r.hget('lockphoto', message['chat']['id'])
    try:
        if 'reply_to_message' in message:
            if 'audio' in message['reply_to_message']:
                file_id = r.hget('audio_tag', message['from']['id'])
                file_info = bot.getFile(file_id)
                download('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info['file_path']),
                         'audio/{}.mp3'.format(message['from']['id']))
                fileid = message['photo'][2]['file_id']
                fileinfo = bot.getFile(fileid)
                download('https://api.telegram.org/file/bot{0}/{1}'.format(token, fileinfo['file_path']),
                         'image/{}.png'.format(message['from']['id']))
                img('audio/{}.mp3'.format(message['from']['id']),
                    'image/{}.png'.format(message['from']['id']))
                bot.sendAudio(message['chat']['id'], audio=open('audio/{}.mp3'.format(message['from']['id']), 'rb'),
                              performer=message['reply_to_message']['audio']['performer'],
                              title=message['reply_to_message']['audio']['title'])
                os.remove('audio/{}.mp3'.format(message['from']['id']))
                os.remove('image/{}.png'.format(message['from']['id']))
        if not admin(message, message):
            lockfwd = r.hget('lockfwd', message['chat']['id'])
            if lockfwd == 'فعال ✔️':
                if 'forward_date' in message:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if lockphoto == 'فعال ✔️':
                if message['photo']:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])

            if 'caption' in message:
                if locklink == 'فعال ✔️':
                    if re.search(r'[Tt]\.[Mm][Ee]', message["caption"]):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])
                    if re.search(r'[Tt][Ee][Ll][Ee][Gg][Rr][Aa][Mm]\.[Mm][Ee]', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

                if lockusername == 'فعال ✔️':
                    if re.search(r'@', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

            if lockall == 'فعال ✔️':
                bot.deleteMessage(message['chat']['id'], message['message_id'])
    except:
        print('error')
    freeze_support()
    Process(target=photo)


@bot.message('audio')
def audio(message):
    r.hset('audio_tag', message['from']['id'], message['audio']['file_id'])
    arshiv = r.hget('arshiv', message['chat']['id'])
    if arshiv == 'ok':
        bot.forwardMessage('@arshivaudio', from_chat_id=message['chat']['id'], message_id=message['message_id'])
    r.incr('audioi:{}:{}'.format(message['chat']['id'], message['from']['id']))
    lockmusic = r.hget('lockmusic', message['chat']['id'])
    locklink = r.hget('locklink', message['chat']['id'])
    lockusername = r.hget('lockusername', message['chat']['id'])
    lockfa = r.hget('lockfa', message['chat']['id'])
    locken = r.hget('locken', message['chat']['id'])
    lockall = r.hget('lockall', message['chat']['id'])
    try:
        if not admin(message, message):
            lockfwd = r.hget('lockfwd', message['chat']['id'])
            if lockfwd == 'فعال ✔️':
                if 'forward_date' in message:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if lockmusic == 'فعال ✔️':
                if message['audio']:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])

            if 'caption' in message:
                if locklink == 'فعال ✔️':
                    if re.search(r'[Tt]\.[Mm][Ee]', message["caption"]):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])
                    if re.search(r'[Tt][Ee][Ll][Ee][Gg][Rr][Aa][Mm]\.[Mm][Ee]', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

                if lockusername == 'فعال ✔️':
                    if re.search(r'@', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

            if lockall == 'فعال ✔️':
                bot.deleteMessage(message['chat']['id'], message['message_id'])
    except:
        print("error")
    freeze_support()
    Process(target=audio)


@bot.message('video')
def vedio(message):
    arshiv = r.hget('arshiv', message['chat']['id'])
    if arshiv == 'ok':
        bot.forwardMessage('@arshivvideo', from_chat_id=message['chat']['id'], message_id=message['message_id'])
    r.incr('videoi:{}:{}'.format(message['chat']['id'], message['from']['id']))
    lockvideo = r.hget('lockvideo', message['chat']['id'])
    locklink = r.hget('locklink', message['chat']['id'])
    lockusername = r.hget('lockusername', message['chat']['id'])
    lockfa = r.hget('lockfa', message['chat']['id'])
    locken = r.hget('locken', message['chat']['id'])

    lockall = r.hget('lockall', message['chat']['id'])
    try:
        if not admin(message, message):
            lockfwd = r.hget('lockfwd', message['chat']['id'])
            if lockfwd == 'فعال ✔️':
                if 'forward_date' in message:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if lockvideo == 'فعال ✔️':
                if message['video']:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if 'caption' in message:
                if locklink == 'فعال ✔️':
                    if re.search(r'[Tt]\.[Mm][Ee]', message["caption"]):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])
                    if re.search(r'[Tt][Ee][Ll][Ee][Gg][Rr][Aa][Mm]\.[Mm][Ee]', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

                if lockusername == 'فعال ✔️':
                    if re.search(r'@', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

            if lockall == 'فعال ✔️':
                bot.deleteMessage(message['chat']['id'], message['message_id'])
    except:
        print('error')
    freeze_support()
    Process(target=vedio)


@bot.message('contact')
def contact(message):
    r.incr('contacti:{}:{}'.format(message['chat']['id'], message['from']['id']))
    lockcontact = r.hget('lockcontact', message['chat']['id'])
    lockall = r.hget('lockall', message['chat']['id'])
    try:
        if not admin(message, message):
            lockfwd = r.hget('lockfwd', message['chat']['id'])
            if lockfwd == 'فعال ✔️':
                if 'forward_date' in message:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if lockcontact == 'فعال ✔️':
                if message['contact']:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if lockall == 'فعال ✔️':
                bot.deleteMessage(message['chat']['id'], message['message_id'])
    except:
        print('error')
    freeze_support()
    Process(target=contact)


@bot.message('document')
def document(message):
    arshiv = r.hget('arshiv', message['chat']['id'])
    if arshiv == 'ok':
        bot.forwardMessage('@otherarshiv', from_chat_id=message['chat']['id'], message_id=message['message_id'])
    r.incr('doci:{}:{}'.format(message['chat']['id'], message['from']['id']))
    lockgif = r.hget('lockgif', message['chat']['id'])
    lockfile = r.hget('lockfile', message['chat']['id'])
    locklink = r.hget('locklink', message['chat']['id'])
    lockusername = r.hget('lockusername', message['chat']['id'])
    lockfa = r.hget('lockfa', message['chat']['id'])
    locken = r.hget('locken', message['chat']['id'])
    lockall = r.hget('lockall', message['chat']['id'])
    try:
        if not admin(message, message):
            lockfwd = r.hget('lockfwd', message['chat']['id'])
            if lockfwd == 'فعال ✔️':
                if 'forward_date' in message:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if lockgif == 'فعال ✔️':
                if message['document']:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if lockfile == 'فعال ✔️':
                if message['document']:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if 'caption' in message:
                if locklink == 'فعال ✔️':
                    if re.search(r'[Tt]\.[Mm][Ee]', message["caption"]):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])
                    if re.search(r'[Tt][Ee][Ll][Ee][Gg][Rr][Aa][Mm]\.[Mm][Ee]', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

                if lockusername == 'فعال ✔️':
                    if re.search(r'@', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

            if lockall == 'فعال ✔️':
                bot.deleteMessage(message['chat']['id'], message['message_id'])
    except:
        print('error')
    freeze_support()
    Process(target=document)


@bot.message('voice')
def voice(message):
    r.incr('voicei:{}:{}'.format(message['chat']['id'], message['from']['id']))
    lockvoice = r.hget('lockvoice', message['chat']['id'])
    locklink = r.hget('locklink', message['chat']['id'])
    lockusername = r.hget('lockusername', message['chat']['id'])
    lockfa = r.hget('lockfa', message['chat']['id'])
    locken = r.hget('locken', message['chat']['id'])
    lockall = r.hget('lockall', message['chat']['id'])
    try:
        if not admin(message, message):
            lockfwd = r.hget('lockfwd', message['chat']['id'])
            if lockfwd == 'فعال ✔️':
                if 'forward_date' in message:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if lockvoice == 'فعال ✔️':
                if message['voice']:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])

            if 'caption' in message:
                if locklink == 'فعال ✔️':
                    if re.search(r'[Tt]\.[Mm][Ee]', message["caption"]):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])
                    if re.search(r'[Tt][Ee][Ll][Ee][Gg][Rr][Aa][Mm]\.[Mm][Ee]', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

                if lockusername == 'فعال ✔️':
                    if re.search(r'@', message['caption']):
                        bot.deleteMessage(message['chat']['id'], message['message_id'])

            if lockall == 'فعال ✔️':
                bot.deleteMessage(message['chat']['id'], message['message_id'])
    except:
        print('error')
    freeze_support()
    Process(target=voice)


@bot.message('sticker')
def sticker(message):
    r.incr('stickeri:{}:{}'.format(message['chat']['id'], message['from']['id']))
    locksticker = r.hget('locksticker', message['chat']['id'])
    lockall = r.hget('lockall', message['chat']['id'])
    try:
        if not admin(message, message):
            lockfwd = r.hget('lockfwd', message['chat']['id'])
            if lockfwd == 'فعال ✔️':
                if 'forward_date' in message:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if locksticker == 'فعال ✔️':
                if message['sticker']:
                    bot.deleteMessage(message['chat']['id'], message['message_id'])
            if lockall == 'فعال ✔️':
                bot.deleteMessage(message['chat']['id'], message['message_id'])
    except:
        print('error')
    freeze_support()
    Process(target=sticker)


@bot.command(r'^(تایمر) (.*) (.*) (.*)$')
def delete_message(message, args=None):
    if admin(message, message):
        if str(args[1]).isnumeric():
            sc = 0
            if args[2] == "ثانیه":
                sc = args[1]

            elif args[2] == "دقیقه":

                sc = Timer.min_to_sec(args[1])

            elif args[2] == "ساعت":

                sc = Timer.hour_to_sec(args[1])

            bot.sendMessage(message['chat']['id'], "متن : {}\nزمان دریافت {}".format(args[3], sc))

            def send():
                bot.sendMessage(message['chat']['id'], args[3])

            Timer(sc, send)
            
@bot.command('^[/#!]([Dd]el) (.*)$')
def rmsg(message, matches):
    if admin(message, message):
        if str(matches[1]).isnumeric():
            m_id = message['message_id']
            ma = matches[1]
            id = int(m_id) - int(ma)
            for i in range(id, m_id):
                bot.deleteMessage(message['chat']['id'], i)
            bot.deleteMessage(message['chat']['id'], m_id)
            bot.sendMessage(message['chat']['id'], 'تعداد {} پیام پاک شد'.format(matches[1]))
    freeze_support()
    Process(target=rmsg)

@bot.command('^[/#!][Rr]eset [Vv]ote$')
def delvote(message):
    if admin(message, message):
        r.delete('vote1:{}'.format(message['chat']['id']))
        r.delete('vote2:{}'.format(message['chat']['id']))
        r.delete('vote3:{}'.format(message['chat']['id']))
        r.delete('voteall:{}'.format(message['chat']['id']))
        bot.sendMessage(message['chat']['id'], 'پاک شد')

@bot.command(r'^[/#!][Tt][Vv]@tgKINGbot$')
def tv1(message):
        text = 'برای مشاهده شبکه مورد نظر روی اسم آن کلیک کنید'
        bot.sendMessage(message['chat']['id'], text, reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='شبکه 1️⃣', callback_data='bkpnl'),
                    InlineKeyboard(text='شبکه 2️⃣', callback_data='tv2'),
                    InlineKeyboard(text='شبکه 3️⃣', callback_data='tv3'),
                ],
                [
                    InlineKeyboard(text='شبکه 4️⃣', callback_data='tv4'),
                    InlineKeyboard(text='شبکه 5️⃣', callback_data='tv5'),
                ],
                [
                    InlineKeyboard(text='شبکه خبر 📑', callback_data='tv6'),
                    InlineKeyboard(text='شبکه آی فیلم🎥', callback_data='tv7'),
                ],
                [
                    InlineKeyboard(text='شبکه نمایش🏞', callback_data='tv8'),
                    InlineKeyboard(text='شبکه ورزش🤾‍♂️', callback_data='tv9'),
                ],
                [
                    InlineKeyboard(text='شبکه نسیم😛', callback_data='tv10'),
                    InlineKeyboard(text='شبکه مستند🙊', callback_data='tv11'),
                ],
                [
                    InlineKeyboard(text='شبکه قرآن🕌', callback_data='tv12'),
                    InlineKeyboard(text='شبکه کودک👶🏻', callback_data='tv13'),
                ],
                [
                    InlineKeyboard(text='شبکه تماشا 👀', callback_data='tv14'),
                    InlineKeyboard(text='شبکه press tv🌐', callback_data='tv15'),
                ],
            ]
        })
@bot.callback_query()
def callback(message):
        listtv = ['tv1', 'tv2', 'tv3', 'tv4',
                  'tv5', 'tv6', 'tv7', 'tv8',
                  'tv9', 'tv10', 'tv11', 'tv12',
                  'tv13', 'tv14', 'tv15']

        linktv = {
            'tv1': 'http://www.aparat.com/live/tv1',
            'tv2': 'http://www.aparat.com/live/tv2',
            'tv3': 'http://www.aparat.com/live/tv3',
            'tv4': 'http://www.aparat.com/live/tv4',
            'tv5': 'http://www.aparat.com/live/tv5',
            'tv6': 'http://www.aparat.com/live/irinn',
            'tv7': 'http://www.aparat.com/live/ifilm',
            'tv8': 'http://www.aparat.com/live/namayesh',
            'tv9': 'http://www.aparat.com/live/varzesh',
            'tv10': 'http://www.aparat.com/live/nasim',
            'tv11': 'http://www.aparat.com/live/mostanad',
            'tv12': 'http://www.aparat.com/live/quran',
            'tv13': 'http://www.aparat.com/live/pouya',
            'tv14': 'http://www.aparat.com/live/hd',
            'tv15': 'http://www.aparat.com/live/press',
        }
        if message['data'] in listtv:
            link = linktv[message['data']]
            text = '''برای مشاهده آنلاین تلویزیون بر روی عکس زیر این متن کلیک کنید.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست شبکه ها 🖥',
                                                           callback_data='backtvlist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')

        if message['data'] == 'backtvlist':
            text = 'برای مشاهده شبکه مورد نظر روی اسم آن کلیک کنید'
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='شبکه 1️⃣', callback_data='tv1'),
                                            InlineKeyboard(text='شبکه 2️⃣', callback_data='tv2'),
                                            InlineKeyboard(text='شبکه 3️⃣', callback_data='tv3'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه 4️⃣', callback_data='tv4'),
                                            InlineKeyboard(text='شبکه 5️⃣', callback_data='tv5'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه خبر 📑', callback_data='tv6'),
                                            InlineKeyboard(text='شبکه آی فیلم🎥', callback_data='tv7'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه نمایش🏞', callback_data='tv8'),
                                            InlineKeyboard(text='شبکه ورزش🤾‍♂️', callback_data='tv9'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه نسیم😛', callback_data='tv10'),
                                            InlineKeyboard(text='شبکه مستند🙊', callback_data='tv11'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه قرآن🕌', callback_data='tv12'),
                                            InlineKeyboard(text='شبکه کودک👶🏻', callback_data='tv13'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه تماشا 👀', callback_data='tv14'),
                                            InlineKeyboard(text='شبکه press tv🌐', callback_data='tv15'),
                                        ],
                                    ]
                                })


@bot.command(r'^[/#!][Tt][Vv]$')
def tv(message):
    try:
        text = 'برای مشاهده شبکه مورد نظر روی اسم آن کلیک کنید'
        bot.sendMessage(message['chat']['id'], text, reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='شبکه 1️⃣', callback_data='bkpnl'),
                    InlineKeyboard(text='شبکه 2️⃣', callback_data='tv2'),
                    InlineKeyboard(text='شبکه 3️⃣', callback_data='tv3'),
                ],
                [
                    InlineKeyboard(text='شبکه 4️⃣', callback_data='tv4'),
                    InlineKeyboard(text='شبکه 5️⃣', callback_data='tv5'),
                ],
                [
                    InlineKeyboard(text='شبکه خبر 📑', callback_data='tv6'),
                    InlineKeyboard(text='شبکه آی فیلم🎥', callback_data='tv7'),
                ],
                [
                    InlineKeyboard(text='شبکه نمایش🏞', callback_data='tv8'),
                    InlineKeyboard(text='شبکه ورزش🤾‍♂️', callback_data='tv9'),
                ],
                [
                    InlineKeyboard(text='شبکه نسیم😛', callback_data='tv10'),
                    InlineKeyboard(text='شبکه مستند🙊', callback_data='tv11'),
                ],
                [
                    InlineKeyboard(text='شبکه قرآن🕌', callback_data='tv12'),
                    InlineKeyboard(text='شبکه کودک👶🏻', callback_data='tv13'),
                ],
                [
                    InlineKeyboard(text='شبکه تماشا 👀', callback_data='tv14'),
                    InlineKeyboard(text='شبکه press tv🌐', callback_data='tv15'),
                ],
            ]
        })
    except Exception as e:
        print(e)

@bot.callback_query()
def callback(message):
    try:
        listtv = ['tv1', 'tv2', 'tv3', 'tv4',
                  'tv5', 'tv6', 'tv7', 'tv8',
                  'tv9', 'tv10', 'tv11', 'tv12',
                  'tv13', 'tv14', 'tv15']

        linktv = {
            'tv1': 'http://www.aparat.com/live/tv1',
            'tv2': 'http://www.aparat.com/live/tv2',
            'tv3': 'http://www.aparat.com/live/tv3',
            'tv4': 'http://www.aparat.com/live/tv4',
            'tv5': 'http://www.aparat.com/live/tv5',
            'tv6': 'http://www.aparat.com/live/irinn',
            'tv7': 'http://www.aparat.com/live/ifilm',
            'tv8': 'http://www.aparat.com/live/namayesh',
            'tv9': 'http://www.aparat.com/live/varzesh',
            'tv10': 'http://www.aparat.com/live/nasim',
            'tv11': 'http://www.aparat.com/live/mostanad',
            'tv12': 'http://www.aparat.com/live/quran',
            'tv13': 'http://www.aparat.com/live/pouya',
            'tv14': 'http://www.aparat.com/live/hd',
            'tv15': 'http://www.aparat.com/live/press',
        }
        if message['data'] in listtv:
            link = linktv[message['data']]
            text = '''برای مشاهده آنلاین تلویزیون بر روی عکس زیر این متن کلیک کنید.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست شبکه ها 🖥',
                                                           callback_data='backtvlist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')

        if message['data'] == 'backtvlist':
            text = 'برای مشاهده شبکه مورد نظر روی اسم آن کلیک کنید'
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='شبکه 1️⃣', callback_data='tv1'),
                                            InlineKeyboard(text='شبکه 2️⃣', callback_data='tv2'),
                                            InlineKeyboard(text='شبکه 3️⃣', callback_data='tv3'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه 4️⃣', callback_data='tv4'),
                                            InlineKeyboard(text='شبکه 5️⃣', callback_data='tv5'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه خبر 📑', callback_data='tv6'),
                                            InlineKeyboard(text='شبکه آی فیلم🎥', callback_data='tv7'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه نمایش🏞', callback_data='tv8'),
                                            InlineKeyboard(text='شبکه ورزش🤾‍♂️', callback_data='tv9'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه نسیم😛', callback_data='tv10'),
                                            InlineKeyboard(text='شبکه مستند🙊', callback_data='tv11'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه قرآن🕌', callback_data='tv12'),
                                            InlineKeyboard(text='شبکه کودک👶🏻', callback_data='tv13'),
                                        ],
                                        [
                                            InlineKeyboard(text='شبکه تماشا 👀', callback_data='tv14'),
                                            InlineKeyboard(text='شبکه press tv🌐', callback_data='tv15'),
                                        ],
                                    ]
                                })

        votes = ['vote1', 'vote2', 'vote3']
        if message['data'] in votes:
            for vote in votes:
                if vote == message['data']:
                    r.sadd('{}:{}'.format(vote, message['message']['chat']['id']), message['from']['id'])
                else:
                    r.srem('{}:{}'.format(vote, message['message']['chat']['id']), message['from']['id'])
            r.sadd('voteall:{}'.format(message['message']['chat']['id']), message['from']['id'])
            bot.editMessageText(
                'نظر خود را در مورد عملکرد گروه اعلام کنید\n1-عالی ({})\n2-متوسط ({})\n3-ضعیف ({})\nتعداد کل آرا : {}'.format
                    (
                    r.scard('vote1:{}'.format(message['message']['chat']['id'])),
                    r.scard('vote2:{}'.format(message['message']['chat']['id'])),
                    r.scard('vote3:{}'.format(message['message']['chat']['id'])),
                    r.scard('voteall:{}'.format(message['message']['chat']['id']))
                ),
                message['message']['chat']['id'],
                message['message']['message_id'],
                reply_markup={
                    'inline_keyboard': [
                        [
                            InlineKeyboard(text='عالی', callback_data='vote1')
                        ],
                        [
                            InlineKeyboard(text='متوسط', callback_data='vote2')
                        ],
                        [
                            InlineKeyboard(text='ضعیف', callback_data='vote3')
                        ]
                    ]
                }
            )

       except:
        print('error callback')

    freeze_support()
    Process(target=callback)


@bot.command('^[/#!]([Ll]ogo) (.*) (.*)$')
def logo(message, matches):
    if admin(message, message):
        try:
            if str(matches[1]).isnumeric() and str(matches[1]) >= str(100) and str(matches[1]):
                url = 'http://logo.irapi.ir/create/{}/{}'.format(matches[1], matches[2])
                req = ur.urlopen(url).read().decode('utf-8')
                jdat = json.loads(req)
                p = jdat['url']
                ur.urlretrieve(p, "logo.jpg")
                bot.sendPhoto(message['chat']['id'], photo=open('logo.jpg', 'rb'), caption='@tgMember',
                              reply_markup={
                                  'inline_keyboard': [
                                      [
                                          InlineKeyboard(text='🔊 @tgMember',
                                                         url='https://t.me/tgMember')
                                      ]
                                  ]
                              })
        except:
            print('error photo')
    freeze_support()
    Process(target=logo)


@bot.command('^[/#!]([Tt]ag) (.*) (.*)$')
def rename(message, matches):
    if admin(message, message):
        try:
            if 'reply_to_message' in message:
                if 'audio' in message['reply_to_message']:
                    if message['chat']['type'] == 'supergroup':
                        if message['reply_to_message']['audio']['file_size'] >= 20971519:
                            bot.sendMessage(message['chat']['id'],
                                            'ببین بیا منطقی باشیم😑\nخدایی این حجمش خیلی زیاده 🙁\nبیشتر 20 مگابایت نمیتونم 😞')
                        else:
                            file_id = message['reply_to_message']['audio']['file_id']
                            file_info = bot.getFile(file_id)
                            file = ur.urlretrieve(
                                'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info['file_path']),
                                'music.mp3')
                            bot.sendChatAction(message['chat']['id'], 'upload_document')
                            bot.sendAudio(message['chat']['id'], audio=open('music.mp3', 'rb'),
                                          duration=message['reply_to_message']['audio']['duration'],
                                          performer=matches[0], title=matches[1])
        except:
            bot.sendMessage(message['chat']['id'], 'تغییر نام ناموفق بود.\nمجدد تلاش کنید')
    freeze_support()
    Process(target=rename)

@bot.command(r'^[/#!]([Ss]et[Tt]ag) (.*)$')
def tagedit(message, matches):
    try:
        if message['from']['id'] in sudo:
            r.hset('tag', message['chat']['id'], matches[0])
            text = 'تگ تغییر نام خودکار موزیک به => {} <= تغییر یافت☑️'.format(matches[0])
            bot.sendMessage(message['chat']['id'], text)
        else:
            bot.sendMessage(message['chat']['id'], 'فقط صاحب ربات میتواند این عملیات را انجام دهد.\n🆔 : @sajjad_021')
    except:
        pass

@bot.command(r'^[/#!][Cc]aption [Oo]n$')
def capt(message):
    try:
        if message['from']['id'] in sudo:
            r.hset('caption', message['chat']['id'], True)
            text = 'فعال شد'
            bot.sendMessage(message['chat']['id'], text)
    except:
        pass    

@bot.command(r'^[/#!][Cc]aption [Oo]ff$')
def capf(message):
    try:
        if message['from']['id'] in sudo:
            r.hdel('caption', message['chat']['id'])
            text = 'غیر فعال شد'
            bot.sendMessage(message['chat']['id'], text)
    except:
        pass                
@bot.command('^[/#!][Tt]ag$')
def rename(message, matches):
    tag = r.hget('tag', message['chat']['id'])
    tagup = r.hget('tagup', message['chat']['id'])
    caption = r.hget('caption', message['chat']['id'])
    if admin(message, message):
        try:
            if 'reply_to_message' in message:
                if 'audio' in message['reply_to_message']:
                    if tag:
                        if tagup:
                            if message['chat']['type'] == 'supergroup':
                                if message['reply_to_message']['audio']['file_size'] >= 20971519:
                                    bot.sendMessage(message['chat']['id'],
                                                    'ببین بیا منطقی باشیم😑\nخدایی این حجمش خیلی زیاده 🙁\nبیشتر 20 مگابایت نمیتونم 😞')
                                else:
                                    file_id = message['reply_to_message']['audio']['file_id']
                                    file_info = bot.getFile(file_id)
                                    file = ur.urlretrieve(
                                        'https://api.telegram.org/file/bot{0}/{1}'.format(token,
                                                                                          file_info['file_path']),
                                        'audio/music-{}.mp3'.format(message['from']['id']))
                                    bot.sendChatAction(message['chat']['id'], 'upload_document')
                                    if caption:
                                      file_id = message['reply_to_message']['audio']['file_id']
                                      file_info = bot.getFile(file_id)
                                      file = ur.urlretrieve(
                                        'https://api.telegram.org/file/bot{0}/{1}'.format(token,
                                                                                          file_info['file_path']),
                                        'audio/music-{}.mp3'.format(message['from']['id']))
                                      res = message['reply_to_message']['audio']['file_size'] / 1024 / 1024
                                      time = message['reply_to_message']['audio']['duration'] / 60
                                      bot.sendAudio(message['chat']['id'], audio=open('audio/music-{}.mp3'.format(message['from']['id']), 'rb'),
                                                  duration=message['reply_to_message']['audio']['duration'],
                                                  performer=message['reply_to_message']['audio']['performer'],
                                                  caption='''🎶عنوان : {}
🕘زمان : {} دقیقه
🖱حجم : {} مگابایت
'''.format(message['reply_to_message']['audio']['performer'],
            str(time).split(".")[0],
            str(res).split(".")[0] + '.' + str(res).split(".")[1][:1]),
                                                  title=tag)
                                    else:
                                      file_id = message['reply_to_message']['audio']['file_id']
                                      file_info = bot.getFile(file_id)
                                      file = ur.urlretrieve(
                                        'https://api.telegram.org/file/bot{0}/{1}'.format(token,
                                                                                          file_info['file_path']),
                                        'audio/music-{}.mp3'.format(message['from']['id']))
                                      bot.sendAudio(message['chat']['id'], audio=open('audio/music-{}.mp3'.format(message['from']['id']), 'rb'),
                                                  duration=message['reply_to_message']['audio']['duration'],
                                                  performer=message['reply_to_message']['audio']['performer'],
                                                  title=tag)
                        else:
                            if message['chat']['type'] == 'supergroup':
                                if message['reply_to_message']['audio']['file_size'] >= 20971519:
                                    bot.sendMessage(message['chat']['id'],
                                                    'ببین بیا منطقی باشیم😑\nخدایی این حجمش خیلی زیاده 🙁\nبیشتر 20 مگابایت نمیتونم 😞')
                                else:
                                  if caption:
                                    file_id = message['reply_to_message']['audio']['file_id']
                                    file_info = bot.getFile(file_id)
                                    file = ur.urlretrieve(
                                        'https://api.telegram.org/file/bot{0}/{1}'.format(token,
                                                                                          file_info['file_path']),
                                        'audio/music-{}.mp3'.format(message['from']['id']))
                                    res = message['reply_to_message']['audio']['file_size'] / 1024 / 1024
                                    time = message['reply_to_message']['audio']['duration'] / 60
                                    bot.sendAudio(message['chat']['id'], audio=open('audio/music-{}.mp3'.format(message['from']['id']), 'rb'),
                                                  duration=message['reply_to_message']['audio']['duration'],
                                                  performer=tag,
                                                  caption='''🎶عنوان : {}
🕘زمان : {} دقیقه
🖱حجم : {} مگابایت
'''.format(message['reply_to_message']['audio']['title'],
            str(time).split(".")[0],
            str(res).split(".")[0] + '.' + str(res).split(".")[1][:1]),
                                                  title=message['reply_to_message']['audio']['title'])
                                  else:
                                    file_id = message['reply_to_message']['audio']['file_id']
                                    file_info = bot.getFile(file_id)
                                    file = ur.urlretrieve(
                                        'https://api.telegram.org/file/bot{0}/{1}'.format(token,
                                                                                          file_info['file_path']),
                                        'audio/music-{}.mp3'.format(message['from']['id']))
                                    bot.sendAudio(message['chat']['id'], audio=open('audio/music-{}.mp3'.format(message['from']['id']), 'rb'),
                                                  duration=message['reply_to_message']['audio']['duration'],
                                                  performer=tag,
                                                  title=message['reply_to_message']['audio']['title'])
                    else:
                        bot.sendMessage(message['chat']['id'],
                                        'تگ خودکار موزیک ست نشده است❌\nبه صاحب ربات مراجعه کنید',
                                        reply_markup={
                                            'inline_keyboard': [
                                                [
                                                    InlineKeyboard(text='Creator', url='t.me/sajjad_021')
                                                ]
                                            ]
                                        })
        except Exception as e:
            print(e)
    freeze_support()
    Process(target=rename)

@bot.command('^[/#!][Pp]ing$')
def robot(message):
    print(message)
    if message['from']['id'] in sudo:
        bot.sendMessage(message['chat']['id'], 'آنلاینم مدیر ارشد ربات😌', reply_to_message_id=message['message_id'])
    elif admin(message, message):
        bot.sendMessage(message['chat']['id'], 'بله ادمین جونم🤓', reply_to_message_id=message['message_id'])
    else:
        bot.sendMessage(message['chat']['id'], 'جانم ؟ 🤓', reply_to_message_id=message['message_id'])

@bot.command('^[/#!][Pp]ing@tgKINGbot$')
def robot(message):
    print(message)
    if message['from']['id'] in sudo:
        bot.sendMessage(message['chat']['id'], 'آنلاینم مدیر ارشد ربات😌', reply_to_message_id=message['message_id'])
    elif admin(message, message):
        bot.sendMessage(message['chat']['id'], 'بله ادمین جونم🤓', reply_to_message_id=message['message_id'])
    else:
        bot.sendMessage(message['chat']['id'], 'جانم ؟ 🤓', reply_to_message_id=message['message_id'])


@bot.command('^[/#!][Ss]ticker$')
def sticker(message):
    if admin(message, message):
        try:
            if 'reply_to_message' in message:
                if 'photo' in message['reply_to_message']:
                    if message['chat']['type'] == 'supergroup':
                        file_id = message['reply_to_message']['photo'][2]['file_id']
                        file_info = bot.getFile(file_id)
                        file = ur.urlretrieve(
                            'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info['file_path']),
                            'photo.png')
                        img = resize('photo.png', 512)
                        bot.sendDocument(message['chat']['id'], document=open('photo.png', 'rb'),
                                         caption='🔊 @tgMember\nبرای ساخت پک استیکر میتوانید از این عکس استفاده کنید(سایز 512x512)')
                        bot.sendSticker(message['chat']['id'], sticker=open('photo.png', 'rb'), reply_markup={
                            'inline_keyboard': [
                                [
                                    InlineKeyboard(text='🔊 @tgMember', url='t.me/tgMember')
                                ]
                            ]
                        })
        except:
            print('error sticker')


@bot.command('^[/#!][Dd]emo$')
def demo(message):
    try:
        if 'reply_to_message' in message:
            if 'audio' in message['reply_to_message']:
                if message['chat']['type'] == 'supergroup':
                    file_id = message['reply_to_message']['audio']['file_id']
                    file_info = bot.getFile(file_id)
                    download('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info['file_path']),
                             'music.mp3')
                    os.system('cutmp3 -i music.mp3 -O musicdemo.mp3 -a 0:15.0 -b 0:45.0')
                    bot.sendChatAction(message['chat']['id'], 'upload_document')
                    bot.sendVoice(message['chat']['id'], voice=open('musicdemo.mp3', 'rb'))
    except:
        pass


@bot.command('^[/#!][Ff]ile$')
def demo(message):
    try:
        if 'reply_to_message' in message:
            if 'voice' in message['reply_to_message']:
                if message['chat']['type'] == 'supergroup':
                    file_id = message['reply_to_message']['voice']['file_id']
                    file_info = bot.getFile(file_id)
                    download('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info['file_path']),
                             'voice.mp3')
                    bot.sendChatAction(message['chat']['id'], 'upload_document')
                    bot.sendAudio(message['chat']['id'], audio=open('voice.mp3', 'rb'),
                                  performer='@tgMember', title='❣️ tgMember ❣️')

            if 'video' in message['reply_to_message']:
                if message['chat']['type'] == 'supergroup':
                    file_id = message['reply_to_message']['video']['file_id']
                    file_info = bot.getFile(file_id)
                    download('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info['file_path']),
                             'video.mp3')
                    bot.sendChatAction(message['chat']['id'], 'upload_document')
                    bot.sendAudio(message['chat']['id'], audio=open('video.mp3', 'rb'),
                                  performer='@tgMember', title='🔊 @tgMember')

    except:
        pass

@bot.command(r'^[/#!][Hh]elp$')
def text(message):
       text = 'برای مشاهده دستور مورد نظر روی آن کلیک کنید'
       bot.sendMessage(message['chat']['id'], text,
                                        reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='نکته بسیار مهم', callback_data='help1'),
                ],
                [
                    InlineKeyboard(text='دستورات تک قسمتی', callback_data='help4'),
                ],
                [
                    InlineKeyboard(text='دستورات چند قسمتی', callback_data='help6'),
                ],
                [
                    InlineKeyboard(text='راهنمای گروه', callback_data='help9'),
                ],
                [
                    InlineKeyboard(text='دستورات فارسی گروه', callback_data='help11'),
                ],
                [
                    InlineKeyboard(text='راهنمای تصویری', callback_data='help13'),
                ],
            ]
        })
        
@bot.callback_query()
def callback(message):
  
  
        help1 = ['help1']

        linkhelp1 = {
            'help4': 'https://t.me/tgMember',
        }
   
        if message['data'] in help1:
            link = message['data']
            text = '''برای استفاده از تمامی قابلیت های ربات ابتدا ربات را به داخل یک گروه اضافه کنید و سپس با دستور \n/add\nگروه خودتون رو به دیتابیس ربات اضافه کنید و با دستور\n/charge\nگروه خودتون رو شارژ کنید.\nبه عنوان مثال :\n/charge 365\nبه مدت 365 روز شارژ میشود.\nسپس ربات رو به لیست مدیران گروه اضافه کنید تا تمامی قابلیت ها برای شما و بقیه مدیران فعال شود.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')

        help4 = ['help4']

        linkhelp4 = {
            'help4': 'https://t.me/tgMember',
        }
        if message['data'] in help4:
            link = linkhelp4[message['data']]
            text = '''\nدستورات تک قسمتی\n\n/start\nشروع ربات\n\n/ping\nتست آنلاین بودن و سِمَت شما در ربات\n\n/tv\nمشاهده تلویزیون ایران\n\n/id\nمشاهده یوزرآیدے خودتان و گروه\n\n/time\nمشاهده تاریخ و ساعت\n\n/info\nمشاهده جزئیات اطلاعات خودتان\n\n/news\nمشاهده تیتر اخبار روز و خواندن خبر مورد نظر\n\n/calc\nماشین حساب.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')
        help6 = ['help6']

        linkhelp6 = {
            'help6': 'https://t.me/tgMember',
        }
        if message['data'] in help6:
            link = linkhelp6[message['data']]
            text = '''دستورات چند قسمتی\n\n/short\nڪوتاه ڪردن لینڪ\nمثال \n/short https://www.تلگرام.cf\n\n/tag\nتغییر تگ موزیڪ\nمثال\n/tag artist name\nبا ریپلای روی موزیک مورد نظر میتوانید، اسم و تگ موزیک را تغییر دهید\n\n/videomsg\nتبدیل فیلم بہ ویدئو مسیج\nبا ریپلای بر روی یک فیلم بصورت ویدئو مسیج فرستاده میشود.\nتوجه کنید باتوجه به محدودیت تلگرام، فیلم انتخابی باید کمتر از یک دقیقه باشد.\n\n/cap\nڪپشن زدن روے موزیڪ\nبا ریپلای بر روی موزیک مورد نظر اطلاعات موزیک از قبیل زمان، تگ، ... بصورت توضیحات زیر موزیک درج میشود.\n\n/face\nتغییر چهره\nبا ریپلای بر روی یک تصویر صورت، و انتخاب این دستور، میتوانید تصویر مورد نظر را به ٦ حالت مختلف تغییر دهید.\n\n/aparat\nجستجو فیلم در آپارات\nمثال\n/aparat tgMember\n\n/gif\nساخت ۱٦ مدل گیف\nمثال\n/gif 1 tgMember\n/gif 16 tgMember\nمیتوانید اعداد ۱~۱٦ را قرار دهید و بعد از آن کلمه مورد نظر را بنویسید\n\n/logo\nساخت ٤٦ مدل لوگو\nمثال\n/logo 110 tgMember\nمیتوانید اعداد ۱۰۰~۱٤٥ و بعد از آن کلمه مورد نظر را بنویسید\n\n/quran\nدریافت آیہ بصورت متن و صوت\nمثال \n/quran  شماره آیه شماره سوره\n/quran 114 2\n\n/sticker\nتبدیل عڪس بہ استیڪر\nبا ریپلای روی عکس مورد نظر ارسال این دستور، عکس مورد نظر به استیکر تبدیل میشود.\n\n/demo\nبرش قسمت ڪوتاهے از آهنگ\nبا ریپلای بر روی یک آهنگ میتوانید یک دقیقه از آن را به عنوان دمو برش بزنید و با حجم بسیار کمتر دریافت کنید.\n\n/file\nتبدیل فیلم بہ صدا\nبا ریپلای روی فیلم، تبدیل به فایل صوتی میشود.\n\n/app\n apk تغییر نام فایل\nمثال\n/app newname\nبا ریپلای بر روی برنامه های اندروید اسم برنامه را عوض کنید.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')
        help9 = ['help9']

        linkhelp9 = {
            'help9': 'https://t.me/tgMember',
        }
        if message['data'] in help9:
            link = linkhelp9[message['data']]
            text = '''دستورات مدیریتے گروه\n\n/add\nاضافه ڪردن ربات به گروه\n\n/charge\nشارژ ڪردن گروه نسبت به روز\nمثال\n/charge 365\n\n/panel\nپنل مدیریت تنظیمات گروه\nربات باید مدیر باشد و تنها مدیران گروه دسترسے دارند.\n\n/del\nپاڪ سازے پیام ها گروه\nمثال\n/del 50\nپاک سازے ۵۰ پیام\n\n/vote\nساخت نظرسنجے براے گروه\n\n/reset vote\nصفر ڪردن آمار نظرسنجی\n\n/add on\nروشن ڪردن اد اجباری\n\n/add off\nخاموش ڪردن اد اجباری\n\n/setadd\nمشخص ڪردن تعداد اد\nمثال\n/setadd 2\nهر نفر باید ۲ نفر ادد ڪند تا بتواند چت ڪند.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')
            
        help11 = ['help11']

        linkhelp11 = {
            'help11': 'https://t.me/tgMember',
        }
        if message['data'] in help11:
            link = linkhelp11[message['data']]
            text = '''دستورات مدیریتے گروهقفل گروه\nقفل ڪلے گروه\n\nتنظیم لینک\nتنظیم لینڪ گروه\nمثال\nتنظیم لینک https://telegram.me/joinchat/..\n\nلینک\nدریافت لینک گروه\n\nبی صدا\nبا ریپلاے بر روے پیام یک شخص آن را ممنوع الپیام ڪنید\n\nصدا دار\nبا ریپلاے بر روے فرد ممنوع شده، آن را آزاد ڪنید\n\nبی صدا 00000\nبا یوزر آیدے یک شخص را از پیام دادن ممنوع ڪنید\n\nصدا دار 00000\nبا یوزر آیدے شخص منع شده را آزاد ڪنید\n\nاخراج\nبا ریپلاے بر روے پیام یک شخص، او را ازگروه حذف ڪنید\n\nفیلتر xxxx\nیک ڪلمه خاص را فیلتر ڪنید\n\nحذف xxxx\nڪلمه خاص را از فیلتر پاک ڪنید\n\nپاک کردن فیلتر\nپاک ڪردن تمام ڪلمات فیلتر شده\n\nلیست فیلتر\nمشاهده لیست فیلتر.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')
        help13 = ['help13']

        linkhelp13 = {
            'help13': 'https://t.me/tgMember',
        }
        if message['data'] in help13:
            link = linkhelp13[message['data']]
            text = '''دستورات مدیریتے گروهقفل گروه\nقفل ڪلے گروه\n\nتنظیم لینک\nتنظیم لینڪ گروه\nمثال\nتنظیم لینک https://telegram.me/joinchat/..\n\nلینک\nدریافت لینک گروه\n\nبی صدا\nبا ریپلاے بر روے پیام یک شخص آن را ممنوع الپیام ڪنید\n\nصدا دار\nبا ریپلاے بر روے فرد ممنوع شده، آن را آزاد ڪنید\n\nبی صدا 00000\nبا یوزر آیدے یک شخص را از پیام دادن ممنوع ڪنید\n\nصدا دار 00000\nبا یوزر آیدے شخص منع شده را آزاد ڪنید\n\nاخراج\nبا ریپلاے بر روے پیام یک شخص، او را ازگروه حذف ڪنید\n\nفیلتر xxxx\nیک ڪلمه خاص را فیلتر ڪنید\n\nحذف xxxx\nڪلمه خاص را از فیلتر پاک ڪنید\n\nپاک کردن فیلتر\nپاک ڪردن تمام ڪلمات فیلتر شده\n\nلیست فیلتر\nمشاهده لیست فیلتر.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')

        if message['data'] == 'backhelplist':
            text = 'برای مشاهده ستور مورد نظر روی آن کلیک کنید'
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='نکته بسیار مهم', callback_data='help1'),
                ],
                [
                    InlineKeyboard(text='دستورات تک قسمتی', callback_data='help4'),
                ],
                [
                    InlineKeyboard(text='دستورات چند قسمتی', callback_data='help6'),
                ],
                [
                    InlineKeyboard(text='راهنمای گروه', callback_data='help9'),
                ],
                [
                    InlineKeyboard(text='دستورات فارسی گروه', callback_data='help11'),
                ],
                [
                    InlineKeyboard(text='راهنمای تصویری', callback_data='help13'),
                ],
            ]
        })

@bot.command('^[/#!][Hh]elp@tgKINGbot$')
def text(message):
       text = 'برای مشاهده دستور مورد نظر روی آن کلیک کنید'
       bot.sendMessage(message['chat']['id'], text,
                                        reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='نکته بسیار مهم', callback_data='help1'),
                ],
                [
                    InlineKeyboard(text='دستورات تک قسمتی', callback_data='help4'),
                ],
                [
                    InlineKeyboard(text='دستورات چند قسمتی', callback_data='help6'),
                ],
                [
                    InlineKeyboard(text='راهنمای گروه', callback_data='help9'),
                ],
                [
                    InlineKeyboard(text='دستورات فارسی گروه', callback_data='help11'),
                ],
                [
                    InlineKeyboard(text='راهنمای تصویری', callback_data='help13'),
                ],
            ]
        })
        
@bot.callback_query()
def callback(message):
  
  
        help1 = ['help1']

        linkhelp1 = {
            'help4': 'https://t.me/tgMember',
        }
   
        if message['data'] in help1:
            link = message['data']
            text = '''برای استفاده از تمامی قابلیت های ربات ابتدا ربات را به داخل یک گروه اضافه کنید و سپس با دستور \n/add\nگروه خودتون رو به دیتابیس ربات اضافه کنید و با دستور\n/charge\nگروه خودتون رو شارژ کنید.\nبه عنوان مثال :\n/charge 365\nبه مدت 365 روز شارژ میشود.\nسپس ربات رو به لیست مدیران گروه اضافه کنید تا تمامی قابلیت ها برای شما و بقیه مدیران فعال شود.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')

        help4 = ['help4']

        linkhelp4 = {
            'help4': 'https://t.me/tgMember',
        }
        if message['data'] in help4:
            link = linkhelp4[message['data']]
            text = '''\nدستورات تک قسمتی\n\n/start\nشروع ربات\n\n/ping\nتست آنلاین بودن و سِمَت شما در ربات\n\n/tv\nمشاهده تلویزیون ایران\n\n/id\nمشاهده یوزرآیدے خودتان و گروه\n\n/time\nمشاهده تاریخ و ساعت\n\n/info\nمشاهده جزئیات اطلاعات خودتان\n\n/news\nمشاهده تیتر اخبار روز و خواندن خبر مورد نظر\n\n/calc\nماشین حساب.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')
        help6 = ['help6']

        linkhelp6 = {
            'help6': 'https://t.me/tgMember',
        }
        if message['data'] in help6:
            link = linkhelp6[message['data']]
            text = '''دستورات چند قسمتی\n\n/short\nڪوتاه ڪردن لینڪ\nمثال \n/short https://www.تلگرام.cf\n\n/tag\nتغییر تگ موزیڪ\nمثال\n/tag artist name\nبا ریپلای روی موزیک مورد نظر میتوانید، اسم و تگ موزیک را تغییر دهید\n\n/videomsg\nتبدیل فیلم بہ ویدئو مسیج\nبا ریپلای بر روی یک فیلم بصورت ویدئو مسیج فرستاده میشود.\nتوجه کنید باتوجه به محدودیت تلگرام، فیلم انتخابی باید کمتر از یک دقیقه باشد.\n\n/cap\nڪپشن زدن روے موزیڪ\nبا ریپلای بر روی موزیک مورد نظر اطلاعات موزیک از قبیل زمان، تگ، ... بصورت توضیحات زیر موزیک درج میشود.\n\n/face\nتغییر چهره\nبا ریپلای بر روی یک تصویر صورت، و انتخاب این دستور، میتوانید تصویر مورد نظر را به ٦ حالت مختلف تغییر دهید.\n\n/aparat\nجستجو فیلم در آپارات\nمثال\n/aparat tgMember\n\n/gif\nساخت ۱٦ مدل گیف\nمثال\n/gif 1 tgMember\n/gif 16 tgMember\nمیتوانید اعداد ۱~۱٦ را قرار دهید و بعد از آن کلمه مورد نظر را بنویسید\n\n/logo\nساخت ٤٦ مدل لوگو\nمثال\n/logo 110 tgMember\nمیتوانید اعداد ۱۰۰~۱٤٥ و بعد از آن کلمه مورد نظر را بنویسید\n\n/quran\nدریافت آیہ بصورت متن و صوت\nمثال \n/quran  شماره آیه شماره سوره\n/quran 114 2\n\n/sticker\nتبدیل عڪس بہ استیڪر\nبا ریپلای روی عکس مورد نظر ارسال این دستور، عکس مورد نظر به استیکر تبدیل میشود.\n\n/demo\nبرش قسمت ڪوتاهے از آهنگ\nبا ریپلای بر روی یک آهنگ میتوانید یک دقیقه از آن را به عنوان دمو برش بزنید و با حجم بسیار کمتر دریافت کنید.\n\n/file\nتبدیل فیلم بہ صدا\nبا ریپلای روی فیلم، تبدیل به فایل صوتی میشود.\n\n/app\n apk تغییر نام فایل\nمثال\n/app newname\nبا ریپلای بر روی برنامه های اندروید اسم برنامه را عوض کنید.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')
        help9 = ['help9']

        linkhelp9 = {
            'help9': 'https://t.me/tgMember',
        }
        if message['data'] in help9:
            link = linkhelp9[message['data']]
            text = '''دستورات مدیریتے گروه\n\n/add\nاضافه ڪردن ربات به گروه\n\n/charge\nشارژ ڪردن گروه نسبت به روز\nمثال\n/charge 365\n\n/panel\nپنل مدیریت تنظیمات گروه\nربات باید مدیر باشد و تنها مدیران گروه دسترسے دارند.\n\n/del\nپاڪ سازے پیام ها گروه\nمثال\n/del 50\nپاک سازے ۵۰ پیام\n\n/vote\nساخت نظرسنجے براے گروه\n\n/reset vote\nصفر ڪردن آمار نظرسنجی\n\n/add on\nروشن ڪردن اد اجباری\n\n/add off\nخاموش ڪردن اد اجباری\n\n/setadd\nمشخص ڪردن تعداد اد\nمثال\n/setadd 2\nهر نفر باید ۲ نفر ادد ڪند تا بتواند چت ڪند.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')
            
        help11 = ['help11']

        linkhelp11 = {
            'help11': 'https://t.me/tgMember',
        }
        if message['data'] in help11:
            link = linkhelp11[message['data']]
            text = '''دستورات مدیریتے گروهقفل گروه\nقفل ڪلے گروه\n\nتنظیم لینک\nتنظیم لینڪ گروه\nمثال\nتنظیم لینک https://telegram.me/joinchat/..\n\nلینک\nدریافت لینک گروه\n\nبی صدا\nبا ریپلاے بر روے پیام یک شخص آن را ممنوع الپیام ڪنید\n\nصدا دار\nبا ریپلاے بر روے فرد ممنوع شده، آن را آزاد ڪنید\n\nبی صدا 00000\nبا یوزر آیدے یک شخص را از پیام دادن ممنوع ڪنید\n\nصدا دار 00000\nبا یوزر آیدے شخص منع شده را آزاد ڪنید\n\nاخراج\nبا ریپلاے بر روے پیام یک شخص، او را ازگروه حذف ڪنید\n\nفیلتر xxxx\nیک ڪلمه خاص را فیلتر ڪنید\n\nحذف xxxx\nڪلمه خاص را از فیلتر پاک ڪنید\n\nپاک کردن فیلتر\nپاک ڪردن تمام ڪلمات فیلتر شده\n\nلیست فیلتر\nمشاهده لیست فیلتر.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')
        help13 = ['help13']

        linkhelp13 = {
            'help13': 'https://t.me/tgMember',
        }
        if message['data'] in help13:
            link = linkhelp13[message['data']]
            text = '''دستورات مدیریتے گروهقفل گروه\nقفل ڪلے گروه\n\nتنظیم لینک\nتنظیم لینڪ گروه\nمثال\nتنظیم لینک https://telegram.me/joinchat/..\n\nلینک\nدریافت لینک گروه\n\nبی صدا\nبا ریپلاے بر روے پیام یک شخص آن را ممنوع الپیام ڪنید\n\nصدا دار\nبا ریپلاے بر روے فرد ممنوع شده، آن را آزاد ڪنید\n\nبی صدا 00000\nبا یوزر آیدے یک شخص را از پیام دادن ممنوع ڪنید\n\nصدا دار 00000\nبا یوزر آیدے شخص منع شده را آزاد ڪنید\n\nاخراج\nبا ریپلاے بر روے پیام یک شخص، او را ازگروه حذف ڪنید\n\nفیلتر xxxx\nیک ڪلمه خاص را فیلتر ڪنید\n\nحذف xxxx\nڪلمه خاص را از فیلتر پاک ڪنید\n\nپاک کردن فیلتر\nپاک ڪردن تمام ڪلمات فیلتر شده\n\nلیست فیلتر\nمشاهده لیست فیلتر.
        [-]({})'''.format(link)
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
                                    'inline_keyboard': [
                                        [
                                            InlineKeyboard(text='بازگشت به لیست راهنما 🖥',
                                                           callback_data='backhelplist')
                                        ]
                                    ]
                                }, parse_mode='Markdown')

        if message['data'] == 'backhelplist':
            text = 'برای مشاهده ستور مورد نظر روی آن کلیک کنید'
            bot.editMessageText(text, message['message']['chat']['id'], message['message']['message_id'],
                                reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='نکته بسیار مهم', callback_data='help1'),
                ],
                [
                    InlineKeyboard(text='دستورات تک قسمتی', callback_data='help4'),
                ],
                [
                    InlineKeyboard(text='دستورات چند قسمتی', callback_data='help6'),
                ],
                [
                    InlineKeyboard(text='راهنمای گروه', callback_data='help9'),
                ],
                [
                    InlineKeyboard(text='دستورات فارسی گروه', callback_data='help11'),
                ],
                [
                    InlineKeyboard(text='راهنمای تصویری', callback_data='help13'),
                ],
            ]
        })


@bot.command(r'^[/#!][Ff]ace$')
def faceapp(message):
    if admin(message, message):
        try:
            if 'reply_to_message' in message:
                if 'photo' in message['reply_to_message']:
                    file_id = message['reply_to_message']['photo'][2]['file_id']
                    file_info = bot.getFile(file_id)
                    file = ur.urlretrieve(
                        'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info['file_path']),
                        'pics/pic:{}.jpg'.format(message['from']['id']))
                    bot.sendPhoto(message['chat']['id'],
                                  photo=open('pics/pic:{}.jpg'.format(message['from']['id']), 'rb'),
                                  caption='برای تغییر چهره یکی از حالت های زیر را انتخاب کنید',
                                  reply_markup={
                                      'inline_keyboard': [
                                          [
                                              InlineKeyboard(text='جذاب 🤓', callback_data='hot'),
                                              InlineKeyboard(text='خندان 😁', callback_data='smile_2')
                                          ],
                                          [
                                              InlineKeyboard(text='مرد 👱🏻', callback_data='male'),
                                              InlineKeyboard(text='زن 👱🏻‍♀️', callback_data='female')
                                          ],
                                          [
                                              InlineKeyboard(text='کودک 👶🏻', callback_data='young'),
                                              InlineKeyboard(text='پیر 👴🏻', callback_data='old')
                                          ],
                                      ]
                                  })
        except:
            print('error')

@bot.command('^[/#!][Cc]ap$')
def tagg(message, matches):
  tag = r.hget('tag', message['chat']['id'])
  tagup = r.hget('tagup', message['chat']['id'])
  if admin(message, message):
    try:
      if 'reply_to_message' in message:
        if 'audio' in message['reply_to_message']:
          if message['chat']['type'] == 'supergroup':
            if tagup:
              file_id = message['reply_to_message']['audio']['file_id']
              file_info = bot.getFile(file_id)
              file = ur.urlretrieve(
                                        'https://api.telegram.org/file/bot{0}/{1}'.format(token,
                                                                                          file_info['file_path']),
                                        'music.mp3')
              bot.sendChatAction(message['chat']['id'], 'upload_document')
              res = message['reply_to_message']['audio']['file_size'] / 1024 / 1024
              time = message['reply_to_message']['audio']['duration'] / 60
              ti = '{} . {}'.format(message['reply_to_message']['audio']['title'],
                                                            message['reply_to_message']['audio']['performer'])
              bot.sendAudio(message['chat']['id'], audio=open('music.mp3', 'rb'),
                                  duration=message['reply_to_message']['audio']['duration'],
                                  performer='{} . {}'.format(message['reply_to_message']['audio']['title'],
                                                            message['reply_to_message']['audio']['performer']),
                                  title=tag,
                         caption='''🎶عنوان : {}
🕘زمان : {} دقیقه
🖱حجم : {} مگابایت
'''.format(ti, str(time).split(".")[0], str(res).split(".")[0] + '.' + str(res).split(".")[1][:1]))
            else:
              file_id = message['reply_to_message']['audio']['file_id']
              file_info = bot.getFile(file_id)
              file = ur.urlretrieve(
                                        'https://api.telegram.org/file/bot{0}/{1}'.format(token,
                                                                                          file_info['file_path']),
                                        'music.mp3')
              bot.sendChatAction(message['chat']['id'], 'upload_document')
              res = message['reply_to_message']['audio']['file_size'] / 1024 / 1024
              time = message['reply_to_message']['audio']['duration'] / 60
              ti = '{} . {}'.format(message['reply_to_message']['audio']['title'],
                                                            message['reply_to_message']['audio']['performer'])
              bot.sendAudio(message['chat']['id'], audio=open('music.mp3', 'rb'),
                                  duration=message['reply_to_message']['audio']['duration'],
                                  performer=tag,
                                  title='{} . {}'.format(message['reply_to_message']['audio']['title'],
                                                            message['reply_to_message']['audio']['performer']),
                         caption='''🎶عنوان : {}
🕘زمان : {} دقیقه
🖱حجم : {} مگابایت
'''.format(ti, str(time).split(".")[0], str(res).split(".")[0] + '.' + str(res).split(".")[1][:1]))
    except:
      pass
      
bot.run(report_http_errors=False)
