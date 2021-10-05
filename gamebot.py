import discord
from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from config import settings
from discord.utils import get
from asyncio import sleep
import sqlite3 as sq
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
#import datetime
from datetime import timedelta
from datetime import datetime
import re
import operator
import random

with sq.connect('DataBase.db') as con:
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        discord_id INT NOT NULL,
        date_registrator TEXT NOT NULL,
        name TEXT NOT NULL,
        groups INT DEFAULT 0,
        race TEXT NOT NULL,
        validate BOOL DEFAULT TRUE,
        ad BOOL DEFAULT FALSE
        )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS groups (
        group_id INTEGER PRIMARY KEY,
        owner_id INT NOT NULL,
        group_date_registrator TEXT NOT NULL,
        group_name TEXT NOT NULL,
        group_race TEXT NOT NULL,
        group_chat_id INT
        )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS item (
        "item_id"   INTEGER DEFAULT 0 PRIMARY KEY,
        "item_name" TEXT DEFAULT null,
        "item_type" TEXT DEFAULT null,
        "item_price"    INT DEFAULT 0,
        "iteam_attak"   INT DEFAULT 0,
        "item_luck" INT DEFAULT 0,
        "item_hp"   INT DEFAULT 0,
        "item_lvl"  INT DEFAULT 0
        )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS inv (
        "inv_id"    INTEGER DEFAULT 0 PRIMARY KEY,
        "inv_sharp" INT DEFAULT 0,
        "inv_owner_id" INT,
        "inv_name"  TEXT DEFAULT null,
        "inv_type"  TEXT DEFAULT null,
        "inv_price" INT DEFAULT 0,
        "inv_attak" INT DEFAULT 0,
        "inv_luck"  INT DEFAULT 0,
        "inv_hp"    INT DEFAULT 0,
        "inv_lvl"   INT DEFAULT 0
        )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS char (
        user_id INT NOT NULL,
        attack INT DEFAULT 1,
        deffens INT DEFAULT 1,
        exp INT DEFAULT 10,
        level INT DEFAULT 1,
        hp INT DEFAULT 10,
        max_hp INT DEFAULT 10,
        coins INT DEFAULT 0,
        slot_first_hand INT DEFAULT 0,
        slot_second_hand INT DEFAULT 0,
        slot_head INT DEFAULT 0,
        slot_foots INT DEFAULT 0,
        slot_chest INT DEFAULT 0,
        slot_accessory INT DEFAULT 0,
        "activity"  TEXT DEFAULT 0,
        "figh"  TEXT DEFAULT 0
        )""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS battle (

        race TEXT NOT NULL,
        deffens INT DEFAULT 0,
        driadas_atack INT DEFAULT 0,
        dragons_atack INT DEFAULT 0,
        neko_atack INT DEFAULT 0,
        people_atack INT DEFAULT 0,
        kubky INT DEFAULT 0     

        )""")

    cur.execute(f"UPDATE char SET activity = '0', figh = '0'") #Сбрасываем статусы
    con.commit()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = settings['prefix'], intents = intents) #прогружаем префикс
#@commands.has_permissions( administrator = True )

@bot.remove_command('help') #УДАЛЯЕМ СРАННЫЙ HELP

@bot.command()
async def help(ctx):
    await ctx.channel.send("Команда в разработке")


def neeewlvl(member_id):
    print(member_id)
    cur = con.cursor()
    cur.execute(f"SELECT user_id, level, exp FROM char WHERE user_id = (SELECT id FROM users WHERE discord_id = {member_id})") #Получаем user_id, level, exp
    record = cur.fetchall()
    print(f"{datetime.now()} Просчет ЛВЛ | ID: {record[0][0]} LVL: {record[0][1]} EXP: {record[0][2]} Следующий лвл: {record[0][1] + 1}") #ПРИНТЫ
    cur.execute(f"SELECT MAX(exp_lvl), exp_exp FROM exp WHERE exp_exp <= {record[0][2]}") #Просчет опыта и лвл
    record2 = cur.fetchall()
    if record[0][1] != record2[0][0]: #Если максимальный лвл уже равен просчету, то пропускаем
        cur.execute(f"UPDATE char SET level = {record2[0][0]} WHERE user_id = {record[0][0]}") #выдаем новый лвл
        con.commit()


@bot.command() #Тестовая команда
async def ml(ctx):
    member_id = ctx.message.author.id
    neeewlvl(member_id)



@bot.command()
async def profile(ctx):
    member_id = ctx.message.author.id
    cur.execute(f"SELECT id, name, level, hp, max_hp, coins, attack, deffens, slot_head, slot_chest, slot_foots, slot_accessory, slot_first_hand, slot_second_hand, activity, figh, exp FROM char, users WHERE user_id = (SELECT id FROM users WHERE discord_id = {member_id}) AND discord_id = {member_id}") #Получаем кучу дерьма
    record = cur.fetchall()
    cur.execute(f"SELECT exp_exp FROM exp WHERE exp_lvl = {record[0][2]} + 1")
    next_exp = cur.fetchall()
    con.commit()

    status = (record[0][14], record[0][15])
    status = list(status)
    if status[0] == '0':
        status[0] = "свободен"
    if status[1] == '0':
        status[1] = "отдыхает"

    lol = list(record[0][8:])
    for x in range(6):      #разгребаем дерьмо инвентаря
        if lol[x] == 0:
            lol[x] = "пусто"    #если слот пустой, так и пишем
        else: 
            search_item = lol[x]
            cur.execute(f"SELECT item_name FROM item WHERE item_id = {search_item}")    #если в слоте есть предмет ищем его название
            search_item = cur.fetchall()
            lol[x] = search_item[0][0]
            con.commit()
        

    value1 = f"✨ LVL: {record[0][2]}\n🔮 EXP: {record[0][16]}/{next_exp[0][0]}\n❤️ HP: {record[0][3]}/{record[0][4]} \n💰 Деньги: {record[0][5]}\n🗡️ Атака: {record[0][6]} \n🛡️ Защита: {record[0][7]}\n \n "
    value2 = f"🧢Голова: {lol[0]}\n👕 Тело: {lol[1]}\n🦵 Ноги: {lol[0]}\n📿Аксессуар: {lol[2]} \n🤚 Левая рука: {lol[3]}\n✋ Правая рука: {lol[4]}"
    statusvalue = f"Занятие: {status[0]} | Бой: {status[1]}"
    embed = discord.Embed(colour=discord.Colour(0x8bc85a), description=f"Ник: {record[0][1]} | ID: {record[0][0]}")
    embed.set_thumbnail(url=ctx.message.author.avatar_url)
    embed.set_author(name="Игровой профиль")
    embed.set_footer(text=statusvalue)
    embed.add_field(name="Инфо:", value=value1)
    embed.add_field(name="\nСлоты:", value=value2)
    await ctx.channel.send(embed=embed)






async def battle():
    with sq.connect('DataBase.db') as con:
        cur = con.cursor()
        bebra = cur.execute(f"SELECT * FROM battle")
        Direction = {"Дриады": [0, 0, "", 0, " "], "Драконы": [0, 0, "", 0, " "], "Зверолюди": [0, 0, "", 0, ""], "Люди": [0, 0, "", 0, ""]} #Задаю словарь, для облегчения вывода репорта.
        for hl in bebra: #Обсчет результатов битвы за направление
            high = max(hl[1], hl[2], hl[3], hl[4])
            win = hl.index(high)
            if win == 1: #Если деферы победили
                Direction[str(hl[0])][0] += 1
                Direction[str(hl[0])][1] += high*2
                Direction[str(hl[0])][2] = "🛡️Деф"
                Direction[str(hl[0])][3] = high*2
            else: #Если победила атака
                if win == 2: #Проверка кому отдать раунд
                    Direction["Дриады"][0] += 1
                    Direction[str(hl[0])][2] = "🍀Дриады"
                elif win == 3:
                    Direction["Драконы"][0] += 1
                    Direction[str(hl[0])][2] = "🐉Драконы"
                elif win == 4:
                    Direction["Зверолюди"][0] += 1
                    Direction[str(hl[0])][2] = "🐱Зверолюди"
                elif win == 5:
                    Direction["Люди"][0] += 1
                    Direction[str(hl[0])][2] = "🧙Люди"
                else: 
                    print(f"NaN\n -----------------------------------------------------------")
                Direction[str(hl[0])][3] = high*2
                n = 2
                for i in Direction: #Просчет предвадительных (чистых) очков, без бонуса.
                    Direction[i][1] += hl[n]*2
                    n += 1
        b = 0
        smile = ["🍀", "🐉", "🐱", "🧙"] #Доп список, для вывода смайлов в репорте
        for hl in Direction: #Помощь в выводе результатов битвы(для репорта)
            if Direction[hl][2] == "🛡️Деф":
                a = Direction[hl]
                Direction[hl][4] = f"🛡️Защита {smile[b]}{hl} прошла успешно. Защита отразила натиск атаки."
            else:
                a = Direction[hl]
                Direction[hl][4] = f"⚔️Битва за {smile[b]}{hl} прошла успешно для нападающих - защита проиграла под натиском атаки."
            b += 1
        battle_top = {"Зверолюди": [0, ''], "Люди": [0, ''], "Драконы": [0, ''], "Дриады": [0, ''],}
        for i in Direction: #обсчет кубков за битву(с бонусами), добавление кубков фракциям
            if Direction[i][0] == 2:
                kubki = round(Direction[i][1] * 1.2)
                battle_top[i][1] = " (х1.2)"
            elif Direction[i][0] == 3:
                kubki = round(Direction[i][1] * 1.5)
                battle_top[i][1] = " (х1.5)" 
            elif Direction[i][0] == 4:
                kubki = round(Direction[i][1] * 2)
                battle_top[i][1] = " (х2)" 
            else:
                kubki = round(Direction[i][1] * 1)
            battle_top[i][0] = kubki
            cur.execute(f"UPDATE battle SET kubky = kubky + {kubki} WHERE race = '{i}'") 
        sorted_battle_top = sorted(battle_top.items(), key=operator.itemgetter(1)) #Сортировка списка(определение топа)
        top_fraction = f"1. {sorted_battle_top[3][0]} - {sorted_battle_top[3][1][0]}🏆{sorted_battle_top[3][1][1]}\n2. {sorted_battle_top[2][0]} - {sorted_battle_top[2][1][0]}🏆{sorted_battle_top[2][1][1]}\n3. {sorted_battle_top[1][0]} - {sorted_battle_top[1][1][0]}🏆{sorted_battle_top[1][1][1]}\n4. {sorted_battle_top[0][0]} - {sorted_battle_top[0][1][0]}🏆{sorted_battle_top[0][1][1]}"             
        record = cur.fetchall() #Эмбед-репорт о битве
        reports = bot.get_channel(890294191027011625) #канал отправки эмбеда
        embed = discord.Embed(
            title = f'БИТВА на {datetime.now().hour} часов\n\n',
            description = f'{Direction["Дриады"][4]}\nРаунд за: {Direction["Дриады"][2]}\nПобедители набрали: {Direction["Дриады"][3]}🏆\n\n{Direction["Драконы"][4]}\nРаунд за: {Direction["Драконы"][2]}\nПобедители набрали: {Direction["Драконы"][3]}🏆\n\n{Direction["Зверолюди"][4]}\nРаунд за: {Direction["Зверолюди"][2]}\nПобедители набрали: {Direction["Зверолюди"][3]}🏆\n\n{Direction["Люди"][4]}\nРаунд за: {Direction["Люди"][2]}\nПобедители набрали: {Direction["Люди"][3]}🏆\n\nТОП ФРАКЦИЙ:\n{top_fraction}\n',
            colour = discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        )
        await reports.send(embed=embed)
        cur.execute(f"UPDATE battle SET deffens = 0,driadas_atack = 0, neko_atack = 0, people_atack = 0, dragons_atack = 0") 
        cur.execute(f"UPDATE char SET figh = '0'") #обнуляем у всех статусы битв
        con.commit() #Окончание работы с бд






@bot.event
async def on_ready():
    print(f"{datetime.now()} Bot сonnected to Discord")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(battle, trigger='cron', hour='12', minute='00')
    scheduler.add_job(battle, trigger='cron', hour='16', minute='00')
    scheduler.add_job(battle, trigger='cron', hour='20', minute='00')
    scheduler.start()







@bot.command()
# @has_permissions(administrator = True)
async def gb(ctx, Direction: str ): #Битвы
    member_id = ctx.message.author.id
    member = ctx.message.author
    print(f"{datetime.now()} {member} пытается зарегаться на битву против {Direction}") #ПРИНТЫ
    cur.execute(f"SELECT id, race, figh, hp, max_hp, level, attack, deffens FROM char, users WHERE user_id = (SELECT id FROM users WHERE discord_id = {member_id}) AND discord_id = {member_id}") #Получаем user_id, level, exp
    record = cur.fetchall()
    #raceemoji = ["🐱","🐉","🍀","🧙"] наработка на будущее
    race = ["Зверолюди", "Драконы", "Дриады", "Люди"]
    racestatus = ["Атакует зверолюдей", "Атакует драконов", "Атакует дриад", "Атакует людей", "Защищает свою фракцию"] 
    raceattak = ["neko_atack", "dragons_atack", "driadas_atack", "people_atack"]

    for i in record:
        member_race = i[1]
        attack = i[6]
        deffens = i[7]
        max_hp = i[4]
        hp = i[3]
        figh = i[2]
    try:
        if int(figh) == 0:
            print(f"{datetime.now()} {member} прошел try")
    except ValueError:
        await member.send("Вы уже участвуйте в битве")
        return

    if record[0][3] == 0:
        await member.send("Вы не можете сражаться с нулевым здоровьем")
        return

    if Direction == record[0][1]:
        power = (attack*deffens/2)/2/max_hp*hp
        print(power)
        cur.execute(f"UPDATE battle SET deffens = deffens + {power} WHERE race = '{record[0][1]}'")
        cur.execute(f"UPDATE char SET figh = '{racestatus[4]}' WHERE user_id = {record[0][0]}")
        con.commit()
        print(f"{datetime.now()} {member} {racestatus[4]}") #ПРИНТЫ
        return

    if Direction not in race:
        await member.send("Принимается только: Зверолюди; Драконы; Дриады; Люди; Дефф")
        return

    power = (deffens*attack/2)/2/max_hp*hp
    member_race_number = race.index(member_race)
    status_attack = race.index(Direction)
    cur.execute(f"UPDATE battle SET {raceattak[member_race_number]} = {raceattak[member_race_number]} + {power} WHERE race = '{Direction}'")
    cur.execute(f"UPDATE char SET figh = '{racestatus[status_attack]}' WHERE user_id = {record[0][0]}")
    con.commit()
    print(f"{datetime.now()} {member} {racestatus[status_attack]}")

    await member.send(f"Вы записались на битву. Стаутус: {racestatus[status_attack]}")





    






@bot.command()
# @has_permissions(administrator = True)
async def job(ctx):
    print(f"{datetime.now()} {ctx.message.author} решил поработать") #Серьезно? Это тоже?
    member_id = ctx.message.author.id
    member = ctx.message.author
    cur.execute(f"SELECT user_id, level, activity FROM char WHERE user_id = (SELECT id FROM users WHERE discord_id = {member_id})") #Получаем user_id, level, exp
    record = cur.fetchall()

    if record[0][2] != '0': #проверка, что чел не занят
        await member.send(f"Вы сейчас не можете гулять. Ваше текущее занятие: {record[0][2]}")
        print(f"{datetime.now()} {ctx.message.author} не может сейчас работать, он: {record[0][2]}")
        return
    else:
        cur.execute(f"UPDATE char SET activity = 'работает' WHERE user_id = {record[0][0]}")
        con.commit()

    if record[0][1] <= 14:  #Проверка на лвл
        max_coin = 3
    elif record[0][1] >= 15 and record[0][1] < 26:
        max_coin = 10
    elif record[0][1] >= 26 and record[0][1] < 31:
        max_coin = 20
    elif record[0][1] >= 31 and record[0][1] < 35:
        max_coin = 30
    elif record[0][1] >= 35 and record[0][1] < 40:
        max_coin = 35
    elif record[0][1] >= 40 and record[0][1] < 45:
        max_coin = 40
    elif record[0][1] <= 45:
        max_coin = 50
    else:
        max_coin = 0 #Если лвл какой-то неправильный, даем ноль денег

    if max_coin == 3: #По сути с 0 до 14 лвл будет давать 1 coin
        xp = 1 
    elif max_coin == 0:
        xp = 0 #Если лвл какой-то неправильный, даем ноль опыта
    else: #если чел больше 14 лвл, рандомно даем опыта
        max_coin = max_xp + random.randint( -5, 2)
        xp = max_xp + random.randint( -5, -3)

    walk_list = [
        "Надо немного поработать",
        "Я каменщик, работаю три дня и еще ХОЧУ!",
        'Как же иногда хочется стать безработным и реинкарнировать и написать свою историю "о приключениях в другом мире"\nНо сегодня - надо работать',
        "Я уникальный человек! Они меня заставляют заниматься черным трудом, да еще и в подземелье..",
        "В подземелье я пойду и кристалы я найду!"
        "Взял кредит - заставили пахать на горнодобывающую компанию вместе с каким то ящером.",
        "Сегодня пришёл на работу с нарисованными усами... Женщины, с нарисованными бровями сказали, что я дурак.",
        "ДА ВЫ ЧТО???\nМошенничество?!\nМахинации?!?!\nДа вы подходите нашему банку!",
        "Ты пришёл в строительную компанию и спросил, нужна ли с чем то помощь. Тебе заплатят через 5 минут, что бы ты ушёл.",
        "Какой же трудный рабочий день... Работодатели вообще вкурсе что мы работаем ради денег, а не ради работы?",
        "Давай поработаем...",
        "Опять работа?",
    ]

    scheduler = AsyncIOScheduler()

    async def job_time():
        print("НУЖНЫЙ ПРИНТ")
        cur.execute(f"UPDATE char SET exp = exp + {xp}, coins = coins + {max_coin}, activity = 0 WHERE user_id = {record[0][0]}")
        con.commit() 
        await member.send(f"За работу, Вам начисленно {xp} опыта и {max_coin} монет !")
        neeewlvl(member_id)
        scheduler.shutdown()


    date_now = datetime.now()
    five_minut = date_now + timedelta(seconds=60*5)
    scheduler.add_job(job_time, trigger='cron', minute=five_minut.minute)
    scheduler.start()
    await member.send(random.choice(walk_list))







@bot.command()
# @has_permissions(administrator = True)
async def walk(ctx):
    print(f"{datetime.now()} {ctx.message.author} решил пойти погулять") #Серьезно? Это тоже?
    member_id = ctx.message.author.id
    member = ctx.message.author
    cur.execute(f"SELECT user_id, level, activity FROM char WHERE user_id = (SELECT id FROM users WHERE discord_id = {member_id})") #Получаем user_id, level, exp
    record = cur.fetchall()

    if record[0][2] != '0': #проверка, что чел не занят
        await member.send(f"Вы сейчас не можете гулять. Ваше текущее занятие: {record[0][2]}")
        print(f"{datetime.now()} {ctx.message.author} не может сейчас гулять, он: {record[0][2]}")
        return
    else:
        cur.execute(f"UPDATE char SET activity = 'гуляет' WHERE user_id = {record[0][0]}")
        con.commit()

    if record[0][1] <= 14:  #Проверка на лвл
        max_xp = 3
    elif record[0][1] >= 15 and record[0][1] < 26:
        max_xp = 10
    elif record[0][1] >= 26 and record[0][1] < 31:
        max_xp = 20
    elif record[0][1] >= 31 and record[0][1] < 35:
        max_xp = 30
    elif record[0][1] >= 35 and record[0][1] < 40:
        max_xp = 35
    elif record[0][1] >= 40 and record[0][1] < 45:
        max_xp = 40
    elif record[0][1] <= 45:
        max_xp = 50
    else:
        max_xp = 0 #Если лвл какой-то неправильный, даем ноль опыта

    if max_xp == 3: #По сути с 0 до 14 лвл будет давать 1 coin
        coin = 1 
    elif max_xp == 0:
        coin = 0 #Если лвл какой-то неправильный, даем ноль денег
    else: #если чел больше 14 лвл, рандомно даем денег
        max_xp = max_xp + random.randint( -5, 2)
        coin = max_xp + random.randint( -5, -3)

    walk_list = [
        "Вы решили немного прогуляться",
        "Вы устали работать и решили немного погулять",
        "Вам надоел этот прекрасный мир, который богиня благословляет\nИ вы решили погулять",
        "Пойдем гулять...",
    ]

    scheduler = AsyncIOScheduler()

    async def walk_time():
        print("НУЖНЫЙ ПРИНТ")
        cur.execute(f"UPDATE char SET exp = exp + {max_xp}, coins = coins + {coin}, activity = 0 WHERE user_id = {record[0][0]}")
        con.commit() 
        await member.send(f"За прогулку, вам начисленно {max_xp} опыта и {coin} монет !")
        neeewlvl(member_id)
        scheduler.shutdown()


    date_now = datetime.now()
    five_minut = date_now + timedelta(seconds=60*5)
    scheduler.add_job(walk_time, trigger='cron', minute=five_minut.minute)
    scheduler.start()
    await member.send(random.choice(walk_list))







@bot.command()
@has_permissions(administrator = True)
async def giveitem(ctx, opponent:discord.Member, item_id: str):
    opponent = opponent.id
    with sq.connect('DataBase.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM item WHERE item_id = '{item_id}'") #получаем инфу о предмете
        record = cur.fetchall()
        cur.execute(f"SELECT * FROM users WHERE discord_id = {opponent}") #пробиваем оппенента 
        record2 = cur.fetchall()
        if len(record) == 0 or len(record2) == 0:    #проверяем наши запросы и выдаем ошибку
            await ctx.send(f"{'Участник' if len(record2) == 0 else 'Item'} не найден")
            con.commit()
            return
        cur.execute(f"INSERT INTO inv (inv_owner_id, inv_name, inv_type, inv_price, inv_attak, inv_luck, inv_hp, inv_lvl) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",[record2[0][0], *record[0][1:]]) #записываем в базу всю инфу
        con.commit()
    await ctx.send(f"Предмет выдан")
    print("Предмет выдан")






@bot.command()
@has_permissions(administrator = True)
async def inv(ctx):
    opponent = ctx.message.author.id
    with sq.connect('DataBase.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM users WHERE discord_id = {opponent}")
        record = cur.fetchall()
        if len(record) == 0:
            await ctx.send(f"Инвентарь пуст")
            con.commit()
            return
        for i in record: #Если записи есть - сохраняем
            owner_id = i[0]
        cur.execute(f"SELECT * FROM inv WHERE inv_owner_id = '{owner_id}'")
        record = cur.fetchall()
        for i in record: #Если записи есть - сохраняем
            inv_name = i[3]
            inv_type = i[4]
            text = (f"{inv_name} | {inv_type} |  | ")
            await ctx.send(f"{text}")
        con.commit()





@bot.command()
@has_permissions(administrator = True)
async def createguild(ctx, groupname: str):
    groupname = re.sub('[^A-Za-z0-9]+', '', groupname) #уберает все лишнее говно ! - ~/''
    date_registration = datetime.now().date() #Ну тут я беру дану, именно дату без числа
    owner = ctx.message.author.id #получаю id отправителя сообщени
    print(f"{datetime.now()} {ctx.message.author} начал регистрацию своей гильдии с названием {groupname}") #Серьезно? Это тоже?
    #Дальше идет код дата базы, я не думаю, что тут что-то нужно пояснять
    with sq.connect('DataBase.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM users discord_id WHERE discord_id = {owner} AND groups = 0")
        record = cur.fetchall()
        for i in record:
            race = i[5]
        con.commit()
        if len(record) == 0:
            await ctx.send("Вы уже имеете или состоите в группе")
            print(f"{datetime.now()} {ctx.message.author} не смог зарегать свой отряд. Т-к уже состоит в другом.")
        else:
            guild = ctx.guild 
            await guild.create_role(name=groupname) #Создаем роль
            new_group = get(ctx.guild.roles, name=groupname) #получаем объект роли
            await ctx.message.author.add_roles(new_group) #добавялем чела в роль

            #пермишионы для нового чата
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                new_group: discord.PermissionOverwrite(read_messages=True)
            }

            #Создаем канал в специально категории
            category_channel = bot.get_channel(891362588221403206)
            await category_channel.create_text_channel(name=groupname, overwrites=overwrites)
            channel = discord.utils.get(ctx.guild.channels, name =groupname.lower())
            print(f"Был создан канал {channel}")
            channel = channel.id

            #Добавляем записи в группы
            with sq.connect('DataBase.db') as con:
                cur = con.cursor()
                cur.execute(f"INSERT INTO groups (owner_id, group_date_registrator, group_name, group_race, group_chat_id) VALUES({owner}, '{date_registration}', '{groupname}', '{race}', {channel})")
                cur.execute(f"SELECT * FROM groups WHERE group_name = '{groupname}'")
                record = cur.fetchall()
                for i in record:
                    id_group = i[0]
                cur.execute(f"UPDATE users SET groups = {id_group} WHERE discord_id = {owner}")
                record = cur.fetchall()                    
                con.commit()

            #ИЗИ БЛЯТЬ, ГОТОВО
            await ctx.send("Успешно")
            print(f"{datetime.now()} {ctx.message.author} зарегистрировал отряд {groupname}")






@bot.command()
@has_permissions(administrator = True)
async def inviteguild(ctx, opponent: discord.Member):
    member = ctx.message.author.id #получаю id отправителя сообщени
    print(f"{datetime.now()} {member} пытается пригласить {opponent} в гильдию")
    opponent = opponent.id #получаем id оппонента
    with sq.connect('DataBase.db') as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM groups WHERE owner_id = {member}") #пробиваем гильдию
        record = cur.fetchall()
        if len(record) == 0:    #Если нету записей, соси бобру
            await ctx.send(f"Вы не глава гильдии")
            con.commit()
            return
        for i in record: #Если записи есть - сохраняем
            id_group = i[0]
            owner_id = i[1]
            group_name = i[3]
            group_race = i[4]

        cur.execute(f"SELECT * FROM users WHERE discord_id = {opponent}") #пробиваем оппенента 
        record = cur.fetchall()
        if len(record) == 0:    #если чела нету на серерве - пусть сосет бобру
            await ctx.send(f"Участник не найден")
            con.commit()
            return
        for i in record: #а если есть, то - сохраняем
            name = i[3]
            race = i[5]
            groups = i[4]     

        if group_race != race: #проверка, что челы одной расы
            await ctx.send(f"Выбранный участник  - другой расы, {race}.")
            return
        if groups == id_group: #проверка, что чел уже не состоит в этой гильдии
            await ctx.send(f"Выбранный участник  - уже состоит в вашей гильдии.")
            return    
        elif groups != 0: #проверка, что чел не состоит в гильдии
            await ctx.send(f"Выбранный участник  - уже состоит в другой гильдии.")
            return

        cur.execute(f"UPDATE users SET groups = {id_group} WHERE discord_id = {opponent}") #меняем id группы в дата базе
        guildrole = get(ctx.guild.roles, name=group_name) #получаем роль на сервере - через название
        member = ctx.guild.get_member(opponent) #получаем объект оппонента через id
        await member.add_roles(guildrole) #добавялем чела в роль
        await ctx.send(f"Выбранный участник  - был добалвен в гильдию")
        print(f"{datetime.now()} {member} был добавлен в гильдию {guildrole}")
        con.commit() #закрываем базу





@bot.command()
@has_permissions(administrator = True)
async def say(ctx, *, text):
    message = ctx.message
    await message.delete()
    await ctx.send(text)





@bot.command() # отправляет в какой либо чат - сообщение.
@has_permissions(administrator = True)
async def sayto(ctx, channel:discord.TextChannel, *, text):
    print(f"{datetime.now()} {ctx.message.author}, sayto")
    message = ctx.message
    await message.delete()
    await channel.send(text)





@bot.event
async def on_message(message):
    msg = message.content.lower()
    try:
        message.guild.id == None #проверяем, что сообщение не на сервере
    except AttributeError:
        if msg == "start":

            #Тут все необходимые переменные
            au_user = message.author
            searchuser = au_user.id
            guild = bot.get_guild(890003889858957382)
            member = guild.get_member(au_user.id)
            emoji = ["🍀","🧙","🐉","🐱"]
            kira = guild.get_member(276766244093296640)
            id_role = [890283323224625212, 890287397978402857, 890282890007568425, 890282541850968115, 890294463849726054]
            date_registr = datetime.now().date()
            command_prefix = str(settings['prefix'])
            #закончили

            #проверяем, что чел новенький и его запаха не осталось на футболке нашей дата базы
            with sq.connect('DataBase.db') as con:  
                cur = con.cursor()
                cur.execute(f"SELECT * FROM users discord_id WHERE discord_id = {searchuser}") 
                record = cur.fetchall()
                con.commit()
            if len(record) != 0:
                print(f"{au_user} попытался зарегистрироваться")
                await au_user.send(f'Вы уже зарегистрированы\nВы можете получить список команд, прописав {command_prefix}help')
                return

            #ПРИНТ И ОТПРАВКА, ПРИКИНЬ
            print(f"{datetime.now()} Начало регистрации {au_user}")
            await au_user.send("Старт регистрации")

            #Багованная хуйня, которая делает твой ник пустым
            await au_user.send("Напишите ваш никнейм, без специальных символов. (нельзя сменить позже)")
            def check(msg):
                return msg.author == au_user
            message = await bot.wait_for("message", check=check)
            nick = message.content #уберает все лишнее говно ! - ~/''
            print(f"{datetime.now()} Указан ник: {nick}")


            #Выбераем расу
            await au_user.send(f"Хорошо, {nick}\nВыберите расу. (нельзя сменить позже)")
            rolemessage = await au_user.send("🍀 Дриады\n:mage: Люди\n:dragon: Драконы\n🐱 Зверолюди")
            #накидываем эмоджи, по красоте
            for i in emoji:
                await rolemessage.add_reaction(i)

            #Ждем пока чел нажмет на эмоджи
            def check1(reaction, user):
                return reaction.emoji in emoji and user.id == au_user.id
            reaction, user_reaction = await bot.wait_for('reaction_add', check=check1)
            emoji_post = emoji.index(str(reaction))
            id_role = id_role[emoji_post] # сопоставляем эмоджи и id роли
            role = discord.utils.get(guild.roles, id = id_role) #находим роль на сервере
            await member.add_roles(role) # выдаем роль
            role_gamer = discord.utils.get(guild.roles, id = 890294463849726054) 
            await member.add_roles(role_gamer)

            #ПРИНТЫ!
            print(f"{datetime.now()} Выбрана расу: {role}")
            await au_user.send(f"Вы выбрали расу: {role}")

            if member != kira: #Изменяем ник + проверка от Киры
                newnick = (f"{str(reaction)}{nick}")
                await member.edit(nick=newnick)
                print(f"{datetime.now()} Никнейм был заменен с {au_user} на {newnick}")
                
            else:
                print(f"{datetime.now()} {kira} пытался зарегаться, но он слишком крутой, что бы я поменял ему ник :(")

            #Разрешение
            await au_user.send(f'{nick}, Вы должны дать разрешение боту - отправлять сообщения.\n напишите в ответ: "Да')
            def check(msg):
                return msg.author == au_user 
            while True:
                с_msg = await bot.wait_for("message", check=check)  #Ждем пока куколд даст разрешение на отправку сообщения
                с_msg = с_msg.content
                if с_msg == "Да" or с_msg == "да":
                    print(f"{datetime.now()} {au_user} Дал разрешение на оправку сообщения")
                    break
                else:
                    await au_user.send('Введите "Да".\nИначе вы не сможете играть "')
                    pass

            #Усе, чел дал всю хуйню, теперь можно и в базу записать
            with sq.connect('DataBase.db') as con:
                cur = con.cursor()
                cur.execute(f"INSERT INTO users (discord_id, date_registrator, name, race) VALUES({au_user.id}, '{date_registr}', '{nick}', '{role}')")
                cur.execute(f"INSERT INTO char(user_id) SELECT id FROM users WHERE discord_id = {searchuser}")
                con.commit()

            #Принты!
            await au_user.send(f"Регистрация успешно закончена\nВы можете получить список команд, прописав {command_prefix}help")
            print(f"{datetime.now()} Регистрация {nick} успешно закончена")
            #закончили работу

    if message.author == bot.user:
        return
    else:
        if bot.user in message.mentions:
            await message.channel.send('kira seed started')

    await bot.process_commands(message)




@bot.command()
async def top(ctx):
    info_kubki = cur.execute(f"SELECT * FROM battle")
    top = {"Дриады": 0, "Драконы": 0, "Зверолюди": 0, "Люди": 0}
    a = ["Дриады", "Драконы", "Зверолюди", "Люди"]
    b = 0
    for i in info_kubki:
        top[a[b]] = i[6]
        b += 1
    sorted_battle_top = sorted(top.items(), key=operator.itemgetter(1))
    top_fraction = f"1. {sorted_battle_top[3][0]} - {sorted_battle_top[3][1]}🏆\n2. {sorted_battle_top[2][0]} - {sorted_battle_top[2][1]}🏆\n3. {sorted_battle_top[1][0]} - {sorted_battle_top[1][1]}🏆\n4. {sorted_battle_top[0][0]} - {sorted_battle_top[0][1]}🏆"
    embed = discord.Embed(
        title = "🏆Топ рас🏆:",
        description = f"{top_fraction}",
        colour = discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    )
    await ctx.send(embed=embed)




@bot.command()#топ по опыту
async def topexp(ctx):
    with sq.connect('DataBase.db') as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM char WHERE user_id>0 ORDER BY exp DESC')
        record = cur.fetchall()
        cur.execute('SELECT * FROM users WHERE id>0 ORDER BY id')
        record2 = cur.fetchall()
        member_id = ctx.message.author.id
        top = []
        mesto = []
        fraction = {"Дриады": "🍀", "Драконы": "🐉", "Зверолюди": "🐱", "Люди": "🧙"}
        for i in record:
            top.append(record.index(i) + 1)
            top.append(fraction[record2[record.index(i)][5]])
            top.append(record2[record.index(i)][3])
            top.append(record[record.index(i)][3])
            top.append(record[record.index(i)][4])
            if record2[record.index(i)][1] == member_id:
                mesto.append((round((len(top))/5)) + 1)
                mesto.append(fraction[record2[record.index(i)][5]])
                mesto.append(record2[record.index(i)][3])
                mesto.append(record[record.index(i)][3])
                mesto.append(record[record.index(i)][4])
            else:
                pass
        topmsg = f"{top[0]}. {top[1]}{top[2]} 🔮{top[3]} ✨{top[4]}\n{top[5]}. {top[6]}{top[7]} 🔮{top[8]} ✨{top[9]}\n{top[10]}. {top[11]}{top[12]} 🔮{top[13]} ✨{top[14]}\n{top[15]}. {top[16]}{top[17]} 🔮{top[18]} ✨{top[19]}\n{top[20]}. {top[21]}{top[22]} 🔮{top[23]} ✨{top[24]}\n\nВаше место:\n {mesto[0]}. {mesto[1]}{mesto[2]} 🔮{mesto[3]} ✨{mesto[4]}"
        embed = discord.Embed(
            title = "🏆Топ по уровню:",
            description = f"{topmsg}",
            colour = discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        )
        await ctx.send(embed=embed)
        con.commit()

print (f"{datetime.now()} BOT START")
bot.run(settings['token']) #берем токен из конфига и стартуем