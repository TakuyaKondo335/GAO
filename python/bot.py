# This example requires the 'message_content' intent.

import discord 
import serial
import os
import config
import random
import openai
from discord.ext import commands
from datetime import datetime, timedelta

# OpenAI APIの初期化
openai.api_key = config.OPENAI_API_KEY
model_engine = "davinci"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)



# ユーザーごとの投稿回数を格納する辞書
post_count = {}
not_good_post_count= {}

# 投稿回数を全てカウントする
def count_posts(author_name):
    if author_name in post_count:
        post_count[author_name] += 1
    else:
        post_count[author_name] = 1

    print(f"{author_name}: 投稿{post_count[author_name]}回目")


# よろしくない投稿回数をカウントして返す
def count_not_good_posts(author_name):
    if author_name in not_good_post_count:
        not_good_post_count[author_name] += 1
    else:
        not_good_post_count[author_name] = 1

    return not_good_post_count[author_name]


# よろしくない発言が多い人へ警告メッセージ
def caution_message(author_name):
    print(f"{author_name}:よろしくない発言を投稿しました。 不適切投稿{not_good_post_count[author_name]}回/全投稿{post_count[author_name]}回。")

    # 0~2の範囲でランダムな整数を生成
    num = random.randint(0, 2)
    if num == 0:
        return "仏の顔も3度までギャオ"
    elif num == 1:
        return "ちょっと発言に注意ギャオ"
    else:
        return "怒ったギャオ"


# レポートを生成する関数
async def generate_report(channel_id):
    # 過去半日のメッセージを取得する
    channel = client.get_channel(channel_id)
    messages = []
    async for message in channel.history(limit=50):
        messages.append(message)

    # メッセージを結合する
    message_text = "\n".join([message.content for message in messages])

    # OpenAI APIで文章を生成する
    prompt = f"Summarize the events of the past half day in this Discord channel: {message_text}"
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # 生成された文章をDiscordに投稿する
    response_text = response.choices[0].text.strip()
    if len(response_text) <= 2000:
        await channel.send(response_text)
    else:
        await channel.send("生成された文章が2000文字を超えています。分割して送信してください。")






# 過去の出来事をOpenAI APIを使用して取得する関数
def get_events(start_date, end_date):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    query = f"events that happened between {start_date_str} and {end_date_str}"
    response = openai.Completion.create(
        engine="davinci",

        prompt=f"Get events happened in past 12 hours. {query}.",
        # prompt=f"Get {query}.",
        temperature=0.5,
        max_tokens=1024,
        n=1,
        stop=None,
        timeout=10,
    )
    events = response.choices[0].text.strip().split("\n")
    events = [{"text": event.strip()} for event in events]
    return events


#When on_ready
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


#When message recieved
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    author_name = message.author.name
    count_posts(author_name) # 投稿回数をカウント

    if '要求仕様' in message.content:
        m = author_name + "さん、それDAOっぽくないギャオ！"
        await message.channel.send(m)

        # よろしくない発言をカウントして、多いと警告メッセージ
        count = count_not_good_posts(author_name)
        if (count == 2):
            m2 = "ウォーターフォールの匂いがするギャオ！"
            await message.channel.send(m2)
        if (count == 3):
            m2 = "よーし！DAOの文化を一緒に勉強しようギャオ！"
            await message.channel.send(m2)

    # if '予算' in message.content:
    #     m = author_name + "さん、それDAOっぽくないギャオ！"
    #     await message.channel.send(m)

    #     # よろしくない発言をカウントして、多いと警告メッセージ
    #     count = count_not_good_posts(author_name)
    #     if (count == 2):
    #         m2 = "予算の決定はOOギャオ！"
    #         await message.channel.send(m2)
    #     if (count == 3):
    #         m2 = "予算の決定はOOギャオ！ちゃんと文章を考えるギャオ！"
    #         await message.channel.send(m2)

    if '予算' in message.content:
        m = "予算を使うには、予算チャンネルを見るんだギャオ。"
        await message.channel.send(m)
        m = "予算をどうしたいんギャオか?"
        await message.channel.send(m)
        
    if '残高' in message.content:
        m = "今の残高は、100万ギャオコインだギャオ!"
        await message.channel.send(m)

    if '寄付' in message.content:
        m = "どこに寄付するんだギャオ？予算チャンネルを見るんだギャオ"
        await message.channel.send(m)
    
    if '購入' in message.content:
        m = "了解詳しい手続きは予算チャンネルを見てほしいギャオ"
        await message.channel.send(m)




    if message.content.startswith('トヨタファースト'):
        m = author_name + "さん、それDAOっぽくないギャオ！"
        await message.channel.send(m)
        
        # よろしくない発言をカウントして、多いと警告メッセージ
        count = count_not_good_posts(author_name)
        if (count > 3):
            m2 = caution_message(author_name)
            await message.channel.send(m2)

        ser =  serial.Serial(config.ROBOT_ID,115200,timeout=1)
        print(ser.name)
        print("send data")
        ser.write(bytes('4','utf-8'))#send robot move command
        ser.close()

    if message.content.startswith('トヨタウェイ'):
        m = author_name + "さん、これが我々の思いだギャオ！"
        path = os.getcwd() #get current path
        filepath = path + '/img/toyotaway.jpeg'
        await message.channel.send(file=discord.File(filepath))
        await message.channel.send(m)
        ser =  serial.Serial('config.ROBOT_ID',115200,timeout=1)
        print(ser.name)
        print("send data")
        ser.write(bytes('1','utf-8'))#send robot move command
        ser.close()
    if message.content.startswith('ミッション'):
        m = author_name + "さん、これを思い出すんだギャオ！"
        path = os.getcwd()
        filepath = path + '/img/toyotamission.jpeg'
        await message.channel.send(file=discord.File(filepath))
        await message.channel.send(m)
    if message.content.startswith('ヴィジョン'):
        m = author_name + "さん、これを思い出すんだギャオ！"
        path = os.getcwd()
        filepath = path + '/img/toyotavision.jpeg'
        await message.channel.send(file=discord.File(filepath))
        await message.channel.send(m)
    if message.content.startswith('toyotaway'):
        m = author_name + " san,check it out ...grrrr!"
        path = os.getcwd()
        filepath = path + '/img/toyotaway_e.jpeg'
        await message.channel.send(file=discord.File(filepath))
        await message.channel.send(m)
        ser =  serial.Serial('config.ROBOT_ID',115200,timeout=1)
        print(ser.name)
        print("send data")
        ser.write(bytes('1','utf-8'))#send robot move command
        ser.close()
    if message.content.startswith('mission'):
        m = author_name + " san,check it out ...grrrr!"
        path = os.getcwd()
        filepath = path + '/img/toyotamission_e.jpeg'
        await message.channel.send(file=discord.File(filepath))
        await message.channel.send(m)
    if message.content.startswith('vision'):
        m = author_name + " san,check it out ...grrrr!"
        path = os.getcwd()
        filepath = path + '/img/toyotavision_e.jpeg'
        await message.channel.send(file=discord.File(filepath))
        await message.channel.send(m)
    if '悩' in message.content:
        m = author_name + "さん、悩んだ時にはこれを思い出すんだギャオ！"
        path = os.getcwd()
        filepath = path + '/img/toyotamission.jpeg'
        await message.channel.send(file=discord.File(filepath))
        await message.channel.send(m)

    # メッセージを残して、URL部分を炎に変える
    if "http://" in message.content: # メッセージに"http"が含まれている場合
        await message.delete()#メッセージの削除
        m =  author_name + "さんの貼ってくれたURL怪しいのでごめんけど、消したギャオ！"
        await message.channel.send(m)  
        unicodeEmoji = "\N{fire}"
        await message.channel.send("メッセージは燃やされてしまった。http:" + str(unicodeEmoji) + str(unicodeEmoji) + str(unicodeEmoji) + str(unicodeEmoji))

# 褒めてくれるGAOくんも実装する。後ほど。





# メッセージ受信時の処理
# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

    if message.content == "レポート作成":
        await generate_report(message.channel.id)


client.run(config.DISCORD_TOKEN)
