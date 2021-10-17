import discord
from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from discord_components import *
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
        "item_attack"   INT DEFAULT 0,
        "item_deffens"   INT DEFAULT 0,
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
        "inv_attack" INT DEFAULT 0,
        "inv_deffens"   INT DEFAULT 0,
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

    cur.execute(f"UPDATE char SET activity = '0'") #Сбрасываем статусы
    con.commit()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = settings['prefix'], intents = intents) #прогружаем префикс

@bot.remove_command('help') #УДАЛЯЕМ СРАННЫЙ HELP

@bot.command()
async def help(ctx):
    member = ctx.message.author
    print(f"{datetime.now()} {member} вызвал help") #ПРИНТЫ
    embed = discord.Embed(colour=discord.Colour(0x417505))

    embed.set_footer(text="👁️ - адмниские или закрытые команды")
    embed.add_field(name="help", value="Вызывает эту подсказку")
    embed.add_field(name="profile", value="Посмотреть Ваш профиль ")
    embed.add_field(name="inventory", value="Посмотреть Ваш инвентарь")
    embed.add_field(name="gb", value="Вызвает кнопки, для выбора направления боя")
    embed.add_field(name="pingb (раса)", value="Призывает на бой против написанной расы")
    embed.add_field(name="equip (id предмета)", value="Позволяет надеть предмет/одежду")
    embed.add_field(name="job", value="Вы оправитесь на прогулку и получите опыт и немного денег")
    embed.add_field(name="walk", value="Вы оправитесь на поиски подработки и получите денеги и немного опыта")
    embed.add_field(name="👁️ aprofile (id человека)", value="Посмотреть профиль определенного человека")
    embed.add_field(name="👁️ createguild (название гильдии)", value="Создайте вашу гильдию!\nУчтите, что вы можете пригласить только людей вашей расы!")
    embed.add_field(name="👁️ inviteguild (пинг человека; название гильдии)", value="Создайте вашу гильдию!\nУчтите, что вы можете пригласить только людей вашей расы!")
    embed.add_field(name="👁️ say (текст)", value="Отправить текст от имени бота")
    embed.add_field(name="👁️ sayto (канал; текст)", value="Отправить текст от имени бота в определенный канал")
    embed.add_field(name="👁️ sayto (пинг; id item)", value="Выдать предмет определенному человеку")
    await ctx.channel.send(embed=embed)


async def neeewlvl(member_id):
    print(f"{datetime.now()} {member_id} просчет опыта") #ПРИНТЫ
    cur = con.cursor()
    cur.execute(f"SELECT user_id, level, exp FROM char WHERE user_id = (SELECT id FROM users WHERE discord_id = {member_id})") #Получаем user_id, level, exp
    record = cur.fetchall()
    print(f"{datetime.now()} Просчет ЛВЛ | ID: {record[0][0]} LVL: {record[0][1]} EXP: {record[0][2]} Следующий лвл: {record[0][1] + 1}") #ПРИНТЫ
    cur.execute(f"SELECT MAX(exp_lvl), exp_exp FROM exp WHERE exp_exp <= {record[0][2]}") #Просчет опыта и лвл
    record2 = cur.fetchall()
    if record[0][1] != record2[0][0]: #Если максимальный лвл уже равен просчету, то пропускаем
        cur.execute(f"UPDATE char SET attack = attack + 1, deffens = deffens + 1, level = {record2[0][0]} WHERE user_id = {record[0][0]}") #выдаем новый лвл
        con.commit()

@bot.command() #Тестовая команда
async def ml(ctx):
    member_id = ctx.message.author.id
    await neeewlvl(member_id)

@bot.command()
#@has_permissions(administrator = True)
async def equip(ctx, check_item_id: str):
    print(f"{datetime.now()} {ctx.message.author} пытается одеть item_id: {check_item_id}") #ПРИНТЫ
    member_id = ctx.message.author.id
    flag = True
    slot_list = ("slot_first_hand", "slot_second_hand", "slot_head", "slot_foots", "slot_cheast", "slot_accessory")
    search = {
            1: ("Меч", "Булава", "Лук", "Одноручное", "Двуручное"),
            2: ("Щит", "Одноручное оружие"),
            3: ("Каска", "Шапка"),
            4: ("Тапочки", "Обувь"),
            5: ("Футболка"),
            6: ("Артефакт", "Кольцо", "Кулон", "Повязка")}

    cur.execute(f"SELECT inv_id, inv_owner_id, inv_name, inv_type, inv_attack, inv_deffens, inv_luck, inv_hp, inv_lvl from inv WHERE inv_id = '{check_item_id}' AND inv_owner_id = (SELECT id FROM users WHERE discord_id = '{member_id}')")
    record = cur.fetchall()
    if len(record) == 0:
        await ctx.channel.send("У вас нету такого предмета ")
        return
    item_id = record[0][0]
    item_owner_id = record[0][1]
    item_name = record[0][2]
    item_type = record[0][3]
    item_attack = record[0][4]
    item_deffens = record[0][5]
    item_luck = record[0][6]
    item_hp = record[0][7]
    item_lvl = record[0][8]

    cur.execute(f"SELECT level FROM char WHERE user_id = (SELECT id FROM users WHERE discord_id = {member_id})")
    record2 = cur.fetchall()
    if record2[0][0] <= item_lvl:
        await ctx.channel.send("Вы не можете использовать этот предмет, его уровень больше Вашего")
        return
    for x in search:
        if item_type in search[x]:
            select_slot = x
            flag = False
            break
    if flag:
        await ctx.channel.send("Ваш item был поврежден. Обратитесь к администрации")
        return
    cur.execute(f"UPDATE char SET {slot_list[select_slot-1]} = {item_id} WHERE user_id = (SELECT id FROM users WHERE discord_id = '{member_id}')")
    con.commit()
    print(f"{datetime.now()} {ctx.message.author} смог одеть {item_name}") #ПРИНТЫ


@bot.command()
@has_permissions(administrator = True)
async def aprofile(ctx, member_id: str):
    print(f"{datetime.now()} {ctx.message.author} смотрит свой профиль") #ПРИНТЫ
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
            cur.execute(f"SELECT inv_name FROM inv WHERE inv_id = {search_item}")    #если в слоте есть предмет ищем его название
            search_item = cur.fetchall()
            lol[x] = search_item[0][0]
            con.commit()
    

    value1 = f"✨ LVL: {record[0][2]}\n🔮 EXP: {record[0][16]}/{next_exp[0][0]}\n❤️ HP: {record[0][3]}/{record[0][4]} \n💰 Деньги: {record[0][5]}\n🗡️ Атака: {record[0][6]} \n🛡️ Защита: {record[0][7]}\n \n "
    value2 = f"🧢Голова: {lol[0]}\n👕 Тело: {lol[1]}\n🦵 Ноги: {lol[2]}\n📿Аксессуар: {lol[3]} \n🤚 Левая рука: {lol[4]}\n✋ Правая рука: {lol[5]}"
    statusvalue = f"Занятие: {status[0]} | Бой: {status[1]}"
    embed = discord.Embed(colour=discord.Colour(0x8bc85a), description=f"Ник: {record[0][1]} | ID: {record[0][0]}")
    embed.set_author(name="Игровой профиль")
    embed.set_footer(text=statusvalue)
    embed.add_field(name="Инфо:", value=value1)
    embed.add_field(name="\nСлоты:", value=value2)
    await ctx.author.send(embed=embed)

@bot.command()
async def profile(ctx):
    print(f"{datetime.now()} {ctx.message.author} смотрит свой профиль") #ПРИНТЫ
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
            cur.execute(f"SELECT inv_name FROM inv WHERE inv_id = {search_item}")    #если в слоте есть предмет ищем его название
            search_item = cur.fetchall()
            lol[x] = search_item[0][0]
            con.commit()
    

    value1 = f"✨ LVL: {record[0][2]}\n🔮 EXP: {record[0][16]}/{next_exp[0][0]}\n❤️ HP: {record[0][3]}/{record[0][4]} \n💰 Деньги: {record[0][5]}\n🗡️ Атака: {record[0][6]} \n🛡️ Защита: {record[0][7]}\n \n "
    value2 = f"🧢Голова: {lol[0]}\n👕 Тело: {lol[1]}\n🦵 Ноги: {lol[2]}\n📿Аксессуар: {lol[3]} \n🤚 Левая рука: {lol[4]}\n✋ Правая рука: {lol[5]}"
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

@bot.command()
# @has_permissions(administrator = True)
async def gb(ctx): #Битвы
    member = ctx.message.author #получаем автора сообщения
    print(f"{datetime.now()} {member} вызвал меню gobattle") #ПРИНТЫaa

    await ctx.send( #выводим бесконечную кнопку
    "Выберите расу для защиты/атаки!",
        components = [
            Button(label = 'Дриады!', emoji = '🍀'),
            Button(label = 'Зверолюди!', emoji = '🐱'),
            Button(label = 'Драконы!', emoji = '🐉'),
            Button(label = 'Люди!', emoji = '🧙')
        ]
    )

@bot.command()
# @has_permissions(administrator = True)
async def pingb(ctx, race: str): #Битвы
    member = ctx.message.author #получаем автора сообщения
    print(f"{datetime.now()} {member} вызвал меню pin gobattle") #ПРИНТЫaa
    if race == "Зверолюди":
        label = 'Зверолюди!'
        emoji = '🐱'
    elif race == "Дриады":
        label = 'Дриады!'
        emoji = '🍀'
    elif race == "Драконы":
        label = 'Драконы!'
        emoji = '🐉'
    elif race == "Люди":
        label = 'Люди!'
        emoji = '🧙'
    else:
        await ctx.send("Неверно указана раса! Принимается только: Зверолюди, Дриады, Драконы, Люди")
        return

    await ctx.send(
    f"Вас призвали по направлению на {label} Нажмите на кнопку ниже!",
        components = [
            Button(label = label, emoji = emoji)
        ]
    )

async def joborwalk(member, status, message):
    print(f"{datetime.now()} {member} решил {status}") #Серьезно? Это тоже?
    member_id = member.id
    cur.execute(f"SELECT user_id, level, activity FROM char WHERE user_id = (SELECT id FROM users WHERE discord_id = {member_id})") #Получаем user_id, level, exp
    record = cur.fetchall()

    if record[0][2] != '0': #проверка, что чел не занят
        await member.send(f"Вы сейчас заняты. Ваше текущее занятие: {record[0][2]}")
        print(f"{datetime.now()} {member} занимается чем-то другим, {record[0][2]}")
        return
    else:
        await member.send(message)
        cur.execute(f"UPDATE char SET activity = '{status}' WHERE user_id = {record[0][0]}")
        con.commit()

    if record[0][1] <= 14:  #Проверка на лвл
        x = 3
    elif record[0][1] >= 15 and record[0][1] < 26:
        x = 10
    elif record[0][1] >= 26 and record[0][1] < 31:
        x = 20
    elif record[0][1] >= 31 and record[0][1] < 35:
        x = 30
    elif record[0][1] >= 35 and record[0][1] < 40:
        x = 35
    elif record[0][1] >= 40 and record[0][1] < 45:
        x = 40
    elif record[0][1] <= 45:
        x = 50
    else:
        x = 0 #Если лвл какой-то неправильный, даем ноль денег

    if x == 3: #По сути с 0 до 14 лвл будет давать 1 coin
        z = 1 
    elif x == 0:
        z = 0 #Если лвл какой-то неправильный, даем ноль опыта/денег
    else: #если чел больше 14 лвл, рандомно даем опыта/денег
        z = x + random.randint( -5, -3)
        x = x + random.randint( -5, 2)

    async def jobandwalk():
        if status == "работает":
            cur.execute(f"UPDATE char SET exp = exp + {z}, coins = coins + {x}, activity = 0 WHERE user_id = {record[0][0]}")
            con.commit() 
            await member.send(f"За рфаботу, Вам начисленно {z} опыта и {x} монет !",
            components = [
                Button(label = 'Работать еще!', emoji = '⚒️')
                ]
        )
        else:
            cur.execute(f"UPDATE char SET exp = exp + {x}, coins = coins + {z}, activity = 0 WHERE user_id = {record[0][0]}")
            con.commit() 
            await member.send(f"За прогулку, вам начисленно {z} опыта и {x} монет !",
            components = [
                Button(label = 'Гулять еще!', emoji = '🚶‍♂️')
                ]
        )
            
        await neeewlvl(member_id)
        scheduler.shutdown()

    scheduler = AsyncIOScheduler()
    date_now = datetime.now()
    five_minut = date_now + timedelta(seconds=60*5)
    scheduler.add_job(jobandwalk, trigger='cron', minute=five_minut.minute)
    scheduler.start()

@bot.command()
async def job(ctx):
    status = "работает"
    job_list = [
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
    message = random.choice(job_list)
    await joborwalk(ctx.message.author, status, message)

@bot.command()
# @has_permissions(administrator = True)
async def walk(ctx):
    status = "гуляет"
    walk_list = [
        "Вы решили немного прогуляться",
        "Вы устали работать и решили немного погулять",
        "Вам надоел этот прекрасный мир, который богиня благословляет\nИ вы решили погулять",
        "Пойдем гулять...",
    ]

    message = random.choice(walk_list)
    await joborwalk(ctx.message.author, status, message)

@bot.command()
@has_permissions(administrator = True)
async def giveitem(ctx, opponent:discord.Member, item_id: str):
    print(f"{datetime.now()} {ctx.message.author} выдает предмет {item_id} {opponent}") #ПРИНТЫ
    opponent = opponent.id
    cur.execute(f"SELECT item_name, item_type, item_price, item_attack, item_deffens, item_luck, item_hp, item_lvl FROM item WHERE item_id = '{item_id}'") #получаем инфу о предмете
    record = cur.fetchall()
    cur.execute(f"SELECT * FROM users WHERE discord_id = {opponent}") #пробиваем оппенента 
    record2 = cur.fetchall()
    if len(record) == 0 or len(record2) == 0:    #проверяем наши запросы и выдаем ошибку
        await ctx.send(f"{'Участник' if len(record2) == 0 else 'Item'} не найден")
        return
    print(record[0][1:])
    cur.execute(f"INSERT INTO inv (inv_owner_id, inv_name, inv_type, inv_price, inv_attack, inv_deffens, inv_luck, inv_hp, inv_lvl) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",[record2[0][0], *record[0][0:]]) #записываем в базу всю инфу
    con.commit()
    await ctx.send(f"Предмет выдан")
    print("Предмет выдан")

@bot.command()
async def inventory(ctx):
    print(f"{datetime.now()} {ctx.message.author} смотрит свой инвентарь") #ПРИНТЫ
    opponent = ctx.message.author.id
    member = ctx.message.author
    cur.execute(f"SELECT * from inv WHERE inv_owner_id = (SELECT user_id FROM char WHERE user_id = (SELECT id FROM users WHERE discord_id = '{opponent}'))")
    record = cur.fetchall()
    if len(record) == 0:
        await ctx.send(f"Инвентарь пуст")
        return

    embed = discord.Embed(title = f"Инвентарь {member}", colour=discord.Colour(0x417505))
    for i in record: #Если записи есть - сохраняем
        inv_id = i[0]
        inv_name = i[3]
        inv_type = i[4]
        embed.add_field(name=f"{inv_name} ", value=f"ID: {inv_id} | Тип: {inv_type}", inline=False)

    embed.set_footer(text="👁️ - адмниские или закрытые команды")
    await ctx.channel.send(embed=embed)

@bot.command()
@has_permissions(administrator = True)
async def createguild(ctx, groupname: str):
    groupname = re.sub('[^A-Za-z0-9]+', '', groupname) #уберает все лишнее говно ! - ~/''
    date_registration = datetime.now().date() #Ну тут я беру дану, именно дату без числа
    owner = ctx.message.author.id #получаю id отправителя сообщени
    print(f"{datetime.now()} {ctx.message.author} начал регистрацию своей гильдии с названием {groupname}") #Серьезно? Это тоже?
    #Дальше идет код дата базы, я не думаю, что тут что-то нужно пояснять
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
            new_group: discord.PermissionOverwrite(read_messages=True, send_messages = True)
        }

        #Создаем канал в специально категории
        category_channel = bot.get_channel(891362588221403206)
        await category_channel.create_text_channel(name=groupname, overwrites=overwrites)
        channel = discord.utils.get(ctx.guild.channels, name =groupname.lower())
        print(f"Был создан канал {channel}")
        channel = channel.id

        #Добавляем записи в группы
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
    cur.execute(f"SELECT * FROM groups WHERE owner_id = {member}") #пробиваем гильдию
    record = cur.fetchall()
    if len(record) == 0:    #Если нету записей, соси бобру
        await ctx.send(f"Вы не глава гильдии")
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
    print(ctx)
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
            race = ["Дриады", "Люди", "Драконы", "Зверолюди"]
            kira = guild.get_member(276766244093296640)
            id_role = [890283323224625212, 890287397978402857, 890282890007568425, 890282541850968115, 890294463849726054]
            date_registr = datetime.now().date()
            command_prefix = str(settings['prefix'])
            #закончили

            #проверяем, что чел новенький и его запаха не осталось на футболке нашей дата базы
            cur.execute(f"SELECT * FROM users discord_id WHERE discord_id = {searchuser}") 
            record = cur.fetchall()
            if len(record) != 0:
                print(f"{au_user} попытался зарегистрироваться")
                if get(member.roles, name="Игрок"):
                    await au_user.send(f'Вы уже зарегистрированы\nВы можете получить список команд, прописав {command_prefix}help')
                else:
                    print(f"{datetime.now()} {au_user} начал reregistation")
                    cur.execute(f"SELECT name, race, groups FROM users WHERE discord_id = {searchuser}") 
                    rereguser = cur.fetchall()
                    cur.execute(f"SELECT group_name FROM groups WHERE group_id = {rereguser[0][2]}")
                    group = cur.fetchall()
                    role = discord.utils.get(guild.roles, name = f"{rereguser[0][1]}") #находим роль на сервере
                    await member.add_roles(role) # выдаем роль
                    role_gamer = discord.utils.get(guild.roles, id = 890294463849726054) #находим роль на сервере
                    await member.add_roles(role_gamer) # выдаем роль
                    groups = f"{rereguser[0][2]}"
                    emoji_post = emoji[race.index(str(role))]
                    if len(group) != 0:
                        rolegroup = discord.utils.get(guild.roles, name = f"{group[0][0]}") #находим роль на сервере
                        await member.add_roles(rolegroup) # выдаем роль
                        print(f"{au_user} была выдана роль гильдии {rolegroup}")
                    if member != kira: #Изменяем ник + проверка от Киры
                        newnick = (f"{str(emoji_post)}{rereguser[0][0]}")
                        await member.edit(nick=newnick)
                        print(f"Никнейм был заменен с {au_user} на {newnick}")
                        print(f"{datetime.now()} reregistation {au_user} завершена")
                    else:
                        print(f"{datetime.now()} {kira} пытался зарегаться, но он слишком крутой, что бы я поменял ему ник :(")
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
            await message.channel.send('Бот в разработке')

    await bot.process_commands(message)

@bot.command()
async def top(ctx):
    print(f"{datetime.now()} {ctx.message.author} смотрит топ") #ПРИНТЫ
    member_id = ctx.message.author.id
    raceemoji = ["🐱","🐉","🍀","🧙"]
    racelist = ("Зверолюди", "Драконы", "Дриады", "Люди")
    info_kubki = cur.execute(f"SELECT * FROM battle")
    top_user = ("1", "2", "3", "4", "5")
    top_user = list(top_user)
    b = 0
    top = {"Дриады": 0, "Драконы": 0, "Зверолюди": 0, "Люди": 0}
    a = ["Дриады", "Драконы", "Зверолюди", "Люди"]
    for i in info_kubki:
        top[a[b]] = i[6]
        b += 1
    sorted_battle_top = sorted(top.items(), key=operator.itemgetter(1))
    top_fraction = f"1. {sorted_battle_top[3][0]} - {sorted_battle_top[3][1]}🏆\n2. {sorted_battle_top[2][0]} - {sorted_battle_top[2][1]}🏆\n3. {sorted_battle_top[1][0]} - {sorted_battle_top[1][1]}🏆\n4. {sorted_battle_top[0][0]} - {sorted_battle_top[0][1]}🏆"
    embed1 = discord.Embed(
        title = "🏆 Топ рас 🏆:",
        description = f"{top_fraction}",
        colour = discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    )
    await ctx.send(embed=embed1)

    cur.execute('SELECT * FROM (SELECT ROW_NUMBER() OVER (ORDER BY exp DESC) RowNum, user_id, exp, level FROM char) t WHERE RowNum <= 5')
    record = cur.fetchall()
    for y in range(6):
        if y == 5:
            cur.execute(f'SELECT * FROM (SELECT ROW_NUMBER() OVER ( ORDER BY exp DESC) RowNum, user_id, level, exp FROM char) WHERE user_id = (SELECT id FROM users WHERE discord_id = {member_id})')
            position = cur.fetchall()
            cur.execute(f'SELECT name, race FROM users WHERE id = {position[0][1]}')
            users = cur.fetchall()
            raceindex = racelist.index(users[0][1])
            position = (f"{position[0][0]}. {raceemoji[raceindex]} {users[0][0]} 🔮 {position[0][3]} ✨ {position[0][2]}")
        else:
            cur.execute(f'SELECT name, race FROM users WHERE id = {record[y][1]}')
            users = cur.fetchall()
            raceindex = racelist.index(users[0][1])
            top_user[y] = (f"{y+1}. {raceemoji[raceindex]} {users[0][0]} 🔮 {record[y][2]} ✨{record[y][3]}")
    msg = (f"{top_user[0]}\n{top_user[1]}\n{top_user[2]}\n{top_user[3]}\n{top_user[4]}\n\n**Ваше место:**\n{position}")
    embed2 = discord.Embed(
        title = "🏆 Топ по уровню:",
        description = f"{msg}",
        colour = discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    )
    await ctx.send(embed=embed2)

async def mibattle(select_race, member): #просчет кнопки, которая ниже
    #Кнопка битвы расс
    race = ["Зверолюди", "Драконы", "Дриады", "Люди"] #для индекса
    racestatus = ["Атакует зверолюдей", "Атакует драконов", "Атакует дриад", "Атакует людей", "Защищает свою фракцию"] #для индекса
    raceattak = ["neko_atack", "dragons_atack", "driadas_atack", "people_atack"] #для индекса
    member_id = member.id #получаем id
    cur.execute(f"SELECT id, race, figh, hp, max_hp, level, attack, deffens FROM char, users WHERE user_id = (SELECT id FROM users WHERE discord_id = {member_id}) AND discord_id = {member_id}") #Получаем user_id, level, exp
    record = cur.fetchall()
    for i in record: #получаем данные из рекорда
        member_race = i[1]
        attack = i[6]
        deffens = i[7]
        max_hp = i[4]
        hp = i[3]
        figh = i[2]
    try: #проверка, что чел не в битве
        if int(figh) == 0:
            print(f"{datetime.now()} {member} прошел try")
    except ValueError:
        await member.send("Вы уже участвуйте в битве")
        return

    if record[0][3] == 0: #проверка на HP
        member.send("Вы не можете сражаться с нулевым здоровьем")
        return
    if select_race == record[0][1]: #если защита расы, то записываем
        power = (attack*deffens/2)/2/max_hp*hp
        cur.execute(f"UPDATE battle SET deffens = deffens + {power} WHERE race = '{record[0][1]}'")
        cur.execute(f"UPDATE char SET figh = '{racestatus[4]}' WHERE user_id = {record[0][0]}")
        con.commit()
        print(f"{datetime.now()} {member} {racestatus[4]} {record[0][1]}") #ПРИНТЫ
        await member.send(f"Вы встали на защиту вашей расы")
        return
    power = (deffens*attack/2)/2/max_hp*hp #если человек идет против другой расы - считаем это ниже
    member_race_number = race.index(member_race)
    status_attack = race.index(select_race)
    cur.execute(f"UPDATE battle SET {raceattak[member_race_number]} = {raceattak[member_race_number]} + {power} WHERE race = '{select_race}'")
    cur.execute(f"UPDATE char SET figh = '{racestatus[status_attack]}' WHERE user_id = {record[0][0]}")
    con.commit()
    print(f"{datetime.now()} {member} {racestatus[status_attack]}") #принты
    await member.send(f"Вы записались на битву. Статус: {racestatus[status_attack]}")

@bot.event
async def on_ready():
    print(f"{datetime.now()} Bot сonnected to Discord")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(battle, trigger='cron', hour='12', minute='00')
    scheduler.add_job(battle, trigger='cron', hour='16', minute='00')
    scheduler.add_job(battle, trigger='cron', hour='20', minute='00')
    scheduler.start()

    DiscordComponents(bot)

    while True: 
        interaction = await bot.wait_for("button_click")
        if interaction.component.label == 'Дриады!':
            await mibattle("Дриады", interaction.author)
            await interaction.edit_origin()
        elif interaction.component.label == 'Люди!':
            await mibattle("Люди", interaction.author)
            await interaction.edit_origin()
        elif interaction.component.label == 'Зверолюди!':
            await mibattle("Зверолюди", interaction.author)
            await interaction.edit_origin()
        elif interaction.component.label == 'Драконы!':
            await mibattle("Драконы", interaction.author)
            await interaction.edit_origin()
        elif interaction.component.label == 'Работать еще!':
            await joborwalk(interaction.author, "работает", "Хорошо, давай поработаем еще")
            await interaction.edit_origin()
        elif interaction.component.label == 'Гулять еще!':
            await joborwalk(interaction.author, "гуляет", "Хорошо, давай еще немного погуляем")
            await interaction.edit_origin()
        else:
            await interaction.respond(content="Произошла ошибка, обратитесь к администрации!")

print (f"{datetime.now()} BOT START")
bot.run(settings['token']) #берем токен из конфига и стартуем