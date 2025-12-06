import asyncio
import datetime
import json
import os
import re
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import User, MessageMediaPhoto, MessageMediaPoll, MessageMediaStory, MessageMediaDocument
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from argparse import ArgumentParser

# Customize Lib

from modules.colors import colors,messages,wol,workwol,termux,worktermux


FILES = {
    "accounts": "accounts.json",
    "groups": "groups.json",
    "channels": "channels.json",
    "bots": "bots.json",
    "directs": "directs.json",
    "messages": "messages.json",
    "capture": "capture.json",
    "links": "links.json",
}
GLOBAL_UNIQUE_MESSAGES = set()

def readname(name):
    return __import__("unicodedata").normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    
def load_accounts(name):
    if not os.path.exists(name):
        return []
    with open(name, "r", encoding="utf-8") as f:
        return json.load(f)

def save_accounts(data):
    with open(FILES['accounts'], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def clear():
    os.system("cls || clear")

def OS():
    return os.path.exists("/data/data/com.termux")

def get_message_type(message):
    if message.media:
        match message.media:
            case MessageMediaPhoto():
                return "Photo"
            case MessageMediaPoll():
                return "Poll"
            case MessageMediaStory():
                return "Story"
            case MessageMediaDocument():
                mime = message.media.document.mime_type or ""
                file_name = ""
                if message.media.document.attributes:
                    for attr in message.media.document.attributes:
                        if hasattr(attr, "file_name"):
                            file_name = attr.file_name.lower()
                match mime:
                    case mime if mime.startswith("video"):
                        return "Video"
                    case mime if mime.startswith("audio"):
                        return "Audio"
                    case mime if "ogg" in mime:
                        return "Voice"
                    case "image/gif":
                        return "GIF"
                    case "application/x-tgsticker":
                        return "Sticker"
                    case _ if file_name.endswith(".pdf"):
                        return "PDF"
                    case _ if file_name.endswith(".sql"):
                        return "SQL"
                    case _ if file_name.endswith(".py"):
                        return "Python File"
                    case _ if file_name.endswith(".go"):
                        return "Go File"
                    case _ if file_name.endswith(".php"):
                        return "Php File"
                    case _ if file_name.endswith(".docx"):
                        return "DOCX"
                    case _ if file_name.endswith(".zip"):
                        return "ZIP"
                    case _ if file_name.endswith(".rar"):
                        return "RAR"
                    case _ if file_name.endswith(".apk"):
                        return "APK File"
                    case _ if file_name.endswith(".exe"):
                        return "Executable File"
                    case _ if file_name.endswith(".txt"):
                        return "Text File"
                    case _ if file_name.endswith(".json"):
                        return "JSON File"
                    case _:
                        return "File"
    return "Text"

async def get_chat_id_by_username(client, username):
    try: 
        entity = await client.get_entity(username)
        
        if isinstance(entity, User):  
            return entity.id 
        else:
            print(f"{messages['error']}{username} is not a user.")
            return 3
    except Exception as e:
        print(f"{messages['error']}Error while resolving {username}: {e}")  
        return 3


async def get_user_by_username(client, username):
    try:
        user = await client.get_entity(username)
        return user
    except Exception as e:
        print(f"{messages['error']}Error fetching user by username {username}: {e}")
        return 3
    
def show_accounts():
    accounts = load_accounts(FILES['accounts'])
    if accounts:
        print(f"\n{messages['normal']}")
        for acc in accounts:
            print(f"{messages['suc']}Account Number: {acc['account_number']}")
            print(f"{messages['suc']}Name: {acc['first_name']} {acc['last_name']}")
            print(f"{messages['suc']}Username: @{acc['username']}")
            print(f"{messages['suc']}Phone: {acc['phone']}")
            print(f"{messages['suc']}User ID: {acc['user_id']}")
            print(f"{messages['suc']}Session File: {acc['session_file']}")
            print(f"{messages['suc']}Session Created At: {acc['session_created_at']}")
            print(f"{colors['yellow']}-" * 50)
    else:
        print(f"{messages['error']}No accounts found.") 

async def get_user_by_id(client, user_id):
    try:
        user = await client.get_entity(user_id)
        return user
    except Exception as e:
        print(f"{messages['war']}Error fetching user by ID {user_id}: {e}")
        return 3
    
async def add_account(api_hash, api_id, phone):
    session_name = f"session_{phone.replace('+','')}"
    print(f"{messages['suc']}Creating session: {session_name}.session")

    client = TelegramClient(session_name, api_id=int(api_id), api_hash=api_hash)
    await client.connect()  

    if not await client.is_user_authorized():  
        print(f"{messages['suc']}Code sent to {phone}")
        sent_code = await client.send_code_request(phone) 
        code = input(f"{messages['suc']}Enter the code: ")

        try:
            await client.sign_in(phone, phone_code_hash=sent_code.phone_code_hash, code=code) 
        except SessionPasswordNeededError:
            password = input(f"{messages['war']}Two-step password required: ")
            await client.sign_in(password=password) 

    me = await client.get_me()  

    account_data = {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone,
        "user_id": me.id,
        "username": me.username,
        "first_name": me.first_name,
        "last_name": me.last_name,
        "session_file": f"{session_name}.session",
        "session_created_at": datetime.datetime.now().isoformat(),
        "is_active": True
    }

    accounts = load_accounts(FILES['accounts'])
    account_data["account_number"] = len(accounts) + 1
    accounts.append(account_data)
    save_accounts(accounts)

    print(f"\n{messages['normal']}Account added successfully:")
    print(f"{messages['suc']}Name: {me.first_name} {me.last_name}")
    print(f"{messages['suc']}Username: @{me.username}")
    print(f"{messages['suc']}User ID: {me.id}")
    print(f"{messages['suc']}Session File: {session_name}.session")

    await client.disconnect()  

async def search_messages_for_account(account, search_text=3, sender=3, limit=3, forward_to=3, file_type=3):
    try:
        session_name = account['session_file'].split('.')[0]
        client = TelegramClient(session_name, account['api_id'], account['api_hash'])
        await client.connect()

        print(f"{messages['wait']}Searching messages for account: {account['phone']}")

        messages_found = []
        find_counter = 0

        try:
            async for dialog in client.iter_dialogs():
                if dialog.is_channel or dialog.is_group or dialog.is_user or (isinstance(dialog.entity, User) and dialog.entity.bot):
                    async for message in client.iter_messages(dialog.id):
                        msg_text = message.text or ""
                        if not msg_text:
                            continue

                        if search_text and search_text.lower() not in msg_text.lower():
                            continue

                        if sender and str(message.sender_id) != sender:
                            continue

                        if file_type:
                            message_type = get_message_type(message)
                            if message_type.lower() != file_type.lower():
                                continue

                        cleaned_msg_text = readname(msg_text)
                        message_type = get_message_type(message)

                        sender_obj = await message.get_sender()
                        if isinstance(sender_obj, User):
                            sender_name = sender_obj.first_name or "Unknown"
                        elif dialog.is_channel:
                            sender_name = dialog.entity.title or "Unknown Channel"
                        elif dialog.is_group:
                            sender_name = dialog.entity.title or "Unknown Group"
                        else:
                            sender_name = "Unknown"

                        messages_found.append({
                            "dialog_id": dialog.id,
                            "message_id": message.id,
                            "sender_id": message.sender_id,
                            "sender_name": sender_name,
                            "message_type": message_type,
                            "message": cleaned_msg_text[:150],
                            "date": message.date.isoformat()
                        })

                        find_counter += 1
                        if limit and find_counter >= limit:
                            break

                if limit and find_counter >= limit:
                    break

        except Exception as e:
            print(f"{messages['error']}Error: {e}")

        await client.disconnect()
        return messages_found

    except Exception as e:
        print(f"{messages['war']}{account['phone']}: {e}")
        return []

sent_message_ids = set() 
sent_messages_info = []   

async def forward_messages_for_all_clients(account_messages, forward_user, forward_clients, limit=3):
    f = 0  

    print(f"{messages['suc']}Forwarding messages from {len(forward_clients)} clients.")

    async def forward_from_client(forward_client, messages):
        nonlocal f
        for msg in messages:
            if limit and f >= limit:
                return 
            if msg["message_id"] in sent_message_ids:
                print(f"{messages['war']}Skipping already forwarded message {msg['message_id']}")
                continue  

            try:
               
                original = await forward_client.get_messages(msg["dialog_id"], ids=msg["message_id"])
                await original.forward_to(forward_user.id)
               
                sent_message_ids.add(msg["message_id"]) 
                sent_messages_info.append({
                    "sender_id": msg["sender_id"],
                    "sender_name": msg["sender_name"],
                    "message_type": msg["message_type"],
                    "message": msg["message"], 
                    "date": msg["date"]
                })

                f += 1
                print(f"{messages['suc']}Forwarded message {f} to {forward_user.username if forward_user else forward_user.id}")
                if f >= limit:
                    return  

            except Exception as e:
                print(f"{messages['war']}Error forwarding message from client {forward_client.session.filename}: {e}")

    tasks = []
    for forward_client, account in zip(forward_clients, account_messages.keys()):
        messages = account_messages[account]
        tasks.append(forward_from_client(forward_client, messages))

    await asyncio.gather(*tasks)

    print(f"{messages['suc']}Messages forwarded successfully!")

async def search_messages(account_numbers, search_text=3, sender=3, limit=3, forward_to=3, file_type=3):
    accounts = load_accounts(FILES['accounts'])

    if account_numbers == "all":
        selected_accounts = accounts
    else:
        account_numbers = list(map(int, account_numbers.split(",")))
        selected_accounts = [acc for acc in accounts if acc['account_number'] in account_numbers]

    if not selected_accounts:
        print(f"{messages['war']}No accounts found.")
        return

    account_messages = {}

    tasks = []
    for account in selected_accounts:
        tasks.append(search_messages_for_account(account, search_text, sender, limit, forward_to, file_type))

    results = await asyncio.gather(*tasks)

    for i, result in enumerate(results):
        account_messages[selected_accounts[i]['phone']] = result

    if limit:
        all_messages = []
        for messages in account_messages.values():
            all_messages.extend(messages)

        all_messages = all_messages[:limit]
    else:
        all_messages = []
        for messages in account_messages.values():
            all_messages.extend(messages)

    if forward_to and all_messages:
        print(f"\n{messages['wait']}Forwarding messages...")

        forward_clients = []

        for account in selected_accounts:
            forward_client = TelegramClient(account['session_file'], account['api_id'], account['api_hash'])
            await forward_client.connect()
            forward_clients.append(forward_client)

        forward_user = 3
        if forward_to.startswith('@'):
            forward_user = await get_user_by_username(forward_clients[0], forward_to[1:])
        else:
            try:
                forward_user = await get_user_by_id(forward_clients[0], int(forward_to))
            except ValueError:
                print(f"{messages['error']}Invalid forward_to value: {forward_to}")
                forward_user = 3

        if not forward_user:
            print(f"{messages['war']}Forward target not found.")
        else:

            await forward_messages_for_all_clients(account_messages, forward_user, forward_clients, limit)

        for forward_client in forward_clients:
            await forward_client.disconnect()

    if sent_messages_info:
        headers = ["Sender ID", "Sender Name", "Message Type", "Message Text", "Date"]
        table = [
            [msg["sender_id"], msg["sender_name"], msg["message_type"], msg["message"], msg["date"]]
            for msg in sent_messages_info
        ]
        print(f"{messages['suc']}Results Table:")
        print(tabulate(table, headers, tablefmt="fancy_grid", maxcolwidths=[15, 15, 15, 40, 20]))
    else:
        print(f"{messages['war']}No messages found or forwarded.")


async def fetchDGC(account_numbers, entity_type):
    accounts = load_accounts(FILES['accounts'])

    if account_numbers == "all":
        selected_accounts = accounts
    else:
        account_numbers = list(map(int, account_numbers.split(",")))
        selected_accounts = [acc for acc in accounts if acc['account_number'] in account_numbers]

    if not selected_accounts:
        print(f"{messages['war']} No accounts found.")
        return

    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=5)  

    async def process_account(account):

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)

        session_name = account['session_file'].split('.')[0]
        client = TelegramClient(session_name, account['api_id'], account['api_hash'])
        await client.connect()

        print(f"{messages['wait']} Fetching {entity_type} for account: {account['phone']}")

        entities = []
        
        try:
            async for dialog in client.iter_dialogs():
                if (dialog.is_group and entity_type == "groups") or \
                (dialog.is_channel and entity_type == "channels") or \
                (dialog.is_user and entity_type == "dms") or \
                (isinstance(dialog.entity, User) and dialog.entity.bot and entity_type == "bots"):
                    try:
                        entity = await client.get_entity(dialog.id)
                        name = readname(dialog.name)
                        username = getattr(entity, 'username', 'Private')

                        if entity_type == "bots" and isinstance(dialog.entity, User) and getattr(dialog.entity, 'bot', False):
                            entities.append({
                                "name": name,
                                "id": entity.id,
                                "username": username,
                                "type": "Bot",
                                "created_at": datetime.datetime.now().isoformat(),
                                "account_phone": account['phone']
                            })
                        elif entity_type == "dms" and dialog.is_user:
                            phone = getattr(entity, 'phone', "N/A")
                            entities.append({
                                "name": name,
                                "id": entity.id,
                                "username": username,
                                "phone": phone,
                                "type": "Direct Message",
                                "created_at": datetime.datetime.now().isoformat(),
                                "account_phone": account['phone']
                            })
                        elif entity_type != "bots" and entity_type != "dms":
                            entities.append({
                                "name": name,
                                "id": entity.id,
                                "username": username,
                                "type": entity_type.capitalize(),
                                "created_at": datetime.datetime.now().isoformat(),
                                "account_phone": account['phone']
                            })
                    except Exception as e:
                        print(f"{messages['error']}Error: {e}")

            save_data(FILES.get(entity_type, FILES['groups']), entities)

        except Exception as e:
            print(f"{messages['error']}: {e}")

        await client.disconnect()

        if entities:
            headers = [f"{entity_type.capitalize()} Name", f"{entity_type.capitalize()} ID", "Username"]
            table = [[entity["name"], entity["id"], entity["username"]] for entity in entities]
            print(tabulate(table, headers, tablefmt="fancy_grid"))
        else:
            print(f"{messages['war']}No {entity_type} found.")

    tasks = []
    for account in selected_accounts:

        task = loop.run_in_executor(executor, lambda: asyncio.run(process_account(account)))
        tasks.append(task)
    await asyncio.gather(*tasks)




async def capture_messages(account, target_username, forward_to, limit=3, file_type=3):
    session_name = account['session_file'].split('.')[0]
    client = TelegramClient(session_name, account['api_id'], account['api_hash'])
    await client.connect()

    print(f"{messages['wait']}Searching for messages of user {target_username} in account {account['phone']}")
    target = await get_chat_id_by_username(client, target_username)
    collected = []

    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group:  
                try:
                    async for message in client.iter_messages(dialog.id):
                        if message.sender_id == target:  
                            if file_type:
                                message_type = get_message_type(message)
                                if message_type.lower() != file_type.lower():
                                    continue 

                            
                            if message.id in GLOBAL_UNIQUE_MESSAGES:
                                continue 
                            GLOBAL_UNIQUE_MESSAGES.add(message.id) 

                            cleaned_msg_text = readname(message.text or "")
                            sender_name = dialog.entity.title

                            collected.append({
                                "dialog_id": dialog.id,
                                "message_id": message.id,
                                "sender_id": message.sender_id,
                                "sender_name": sender_name,
                                "message_type": get_message_type(message),
                                "message": cleaned_msg_text[:150],  
                                "date": message.date.isoformat()
                            })

                        if limit and len(collected) >= limit:
                            break
                except Exception as e:
                    print(f"{messages['war']}Error processing messages in group {dialog.id}: {e}")
    except Exception as e:
        print(f"{messages['error']}Error in account {account['phone']}: {e}")

    await client.disconnect()

    save_data(FILES["capture"], collected)

    if collected:
        headers = ["Sender ID", "Sender Name", "Message Type", "Message Text", "Date"]
        table = [
            [msg["sender_id"], msg["sender_name"], msg["message_type"], msg["message"], msg["date"]]
            for msg in collected
        ]
        print(f"\n{messages['suc']}Results Table:")
        print(tabulate(table, headers, tablefmt="fancy_grid", maxcolwidths=[15, 15, 15, 40, 20]))

        if forward_to:
            print(f"\n{messages['wait']}Forwarding messages...")
            forward_client = TelegramClient("forwarder", account['api_id'], account['api_hash'])
            await forward_client.connect()

            forward_user = 3
            if forward_to.startswith('@'):
                forward_user = await client.get_entity(forward_to)
            else:
                try:
                    forward_user = await client.get_entity(int(forward_to))
                except ValueError:
                    print(f"{messages['error']}Invalid forward_to value: {forward_to}")

            if forward_user:
                for msg in collected:
                    original = await forward_client.get_messages(msg["dialog_id"], ids=msg["message_id"])
                    await original.forward_to(forward_user.id)

                print(f"{messages['suc']} Messages forwarded successfully!")
            await forward_client.disconnect()

    else:
        print(f"{messages['war']}No messages found.")

async def capture_messages_for_account(account, target_username, forward_to, limit=3, file_type=3):
    await capture_messages(account, target_username, forward_to, limit, file_type)

async def capture_main(account_numbers, target_username, forward_to, limit=3, file_type=3):
    accounts = load_accounts(FILES['accounts'])

    if account_numbers == "all":
        selected_accounts = accounts
    else:
        account_numbers = list(map(int, account_numbers.split(",")))
        selected_accounts = [acc for acc in accounts if acc['account_number'] in account_numbers]

    tasks = []
    for account in selected_accounts:
        tasks.append(capture_messages_for_account(account, target_username, forward_to, limit, file_type))

    await asyncio.gather(*tasks)

async def fetch_messages_from_channel(client, channel_link, limit="all"):
    try:
        channel = await client.get_entity(channel_link)
        print(f"{messages['wait']}Fetching messages from channel: {channel.title} ({channel.id})")

        messages = []
        async for message in client.iter_messages(channel.id, limit=None if limit == "all" else int(limit)):
            msg_text = message.text or ""
            if not msg_text:
                continue

            messages.append({
                "dialog_id": channel.id,
                "message_id": message.id,
                "sender_id": message.sender_id,
                "message": msg_text[:150], 
                "date": message.date.isoformat()
            })

          
            if limit != "all" and len(messages) >= int(limit):
                break

        return messages
    except Exception as e:
        print(f"{messages['war']}Error fetching messages from channel {channel_link}: {e}")
        return []


async def forward_messages_to_channel(client, messages, forward_to, limit="all"):
    try:
        forward_user = None
        if forward_to.startswith('@'):
            forward_user = await get_user_by_username(client, forward_to[1:])
        else:
            try:
                forward_user = await get_user_by_id(client, int(forward_to))
            except ValueError:
                print(f"{messages['error']}Invalid forward_to value: {forward_to}")
                forward_user = None

        download_messages = False

        if forward_user:
            f = 0  
            for msg in messages:
                if limit != "all" and f >= int(limit):  
                    break

                original = await client.get_messages(msg["dialog_id"], ids=msg["message_id"])

                try:
                    
                    if original.text and not original.media:
                       
                        await client.send_message(forward_user.id, original.text)
                        f += 1
                        print(f"{messages['suc']}Forwarded message (text) to {forward_user.username if forward_user else forward_user.id}")

              
                    elif original.media and not original.text:
                       
                        file_path = await original.download_media(file="downloads/")
                        print(f"{messages['suc']}Downloaded media file to {file_path}")
                        await client.send_file(forward_user.id, file_path)
                        f += 1
                        print(f"{messages['suc']}Forwarded media message to {forward_user.username if forward_user else forward_user.id}")

                   
                    elif original.media and original.text:
                        
                        await original.forward_to(forward_user.id)
                        f += 1
                        print(f"{messages['suc']}Forwarded media with caption to {forward_user.username if forward_user else forward_user.id}")

                except Exception as e:
                    print(f"{messages['war']}Error forwarding message: {e}")
                  
                    if not download_messages: 
                        user_input = input(f"{messages['ques']}Do you want to download and send the post manually? (y/n): ").lower()
                        if user_input == 'y':
                            download_messages = True
                            print(f"{messages['suc']}sending post {msg['message_id']} manually...")
                    
                    if download_messages:
                     
                        if original.media:
                            file_path = await original.download_media(file="downloads/")
                            if file_path:
                                print(f"{messages['suc']}File downloaded to {file_path}")
                                
                              
                                await client.send_file(forward_user.id, file_path, caption=original.text)
                                print(f"{messages['wait']}Manually forwarded message to {forward_user.username if forward_user else forward_user.id} with caption.")
                                f += 1
                        else:
                            print(f"{messages['war']}No media found in message {msg['message_id']}, skipping download.")
        else:
            print(f"{messages['war']}Forward target not found.")
    except Exception as e:
        print(f"{messages['war']}Error forwarding messages: {e}")

async def forward_from_channel(account_numbers, link, forward_to, limit="all", show_table=False):
    accounts = load_accounts(FILES['accounts'])

    if account_numbers == "all":
        selected_accounts = accounts
    else:
        account_numbers = list(map(int, account_numbers.split(",")))
        selected_accounts = [acc for acc in accounts if acc['account_number'] in account_numbers]

    all_forwarded_messages = []

    tasks = []
    for account in selected_accounts:
        session_name = account['session_file'].split('.')[0]
        client = TelegramClient(session_name, account['api_id'], account['api_hash'])
        await client.connect()

        messages = await fetch_messages_from_channel(client, link, limit)

        if messages:

            await forward_messages_to_channel(client, messages, forward_to, limit)

            for msg in messages:
                all_forwarded_messages.append([msg["sender_id"], msg["message"], msg["date"]]) 

        await client.disconnect()

    if show_table and all_forwarded_messages:
        headers = ["Sender ID", "Message", "Date"]
        print(f"\n{messages['suc']}Forwarded Messages:")
        print(tabulate(all_forwarded_messages, headers, tablefmt="fancy_grid", maxcolwidths=[15, 40, 20]))
    else:
        print(f"{messages['suc']}Messages forwarded successfully!")


def save_links(links):
    if not links:
        return

    if os.path.exists(FILES["links"]):
        with open(FILES["links"], "r", encoding="utf-8") as f:
            existing_links = json.load(f)
    else:
        existing_links = {}

    for domain, domain_links in links.items():
        if domain not in existing_links:
            existing_links[domain] = []

        for link in domain_links:
            if link not in existing_links[domain]:
                existing_links[domain].append(link)

    with open(FILES["links"], "w", encoding="utf-8") as f:
        json.dump(existing_links, f, indent=4, ensure_ascii=False)

async def link_finder(account_number):
    accounts = load_accounts(FILES['accounts'])

    account_numbers = list(map(int, account_number.split(","))) if isinstance(account_number, str) else [account_number]

    account = [acc for acc in accounts if acc['account_number'] in account_numbers]

    if not account:
        print(f"{messages['war']}Account not found.")
        return

    account = account[0]  
    session_name = account['session_file'].split('.')[0]
    client = TelegramClient(session_name, account['api_id'], account['api_hash'])
    await client.connect()

    print(f"{messages['wait']}Searching links for account: {account['phone']}")

    links_found = {} 
    existing_links_in_memory = set()  

    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_channel or dialog.is_group or dialog.is_user or isinstance(dialog.entity, User):
                async for message in client.iter_messages(dialog.id):
                    msg_text = message.text or ""
                    if msg_text:
                        links = extract_links(msg_text) 
                        for link in links:
                            if link in existing_links_in_memory:  
                                continue
                            
                         
                            domain = get_domain(link)
                            
                            if domain not in links_found:
                                links_found[domain] = []

                            links_found[domain].append(link)
                            existing_links_in_memory.add(link)
                            save_links(links_found)

                            print(f"{messages['suc']}Found: {colors['yellow']}{link} ({colors['white']}Domain: {colors['red']}{domain}{colors['reset']})")

    except Exception as e:
        print(f"{messages['error']}Error: {e}")

    await client.disconnect()

    if links_found:
        print(f"\n{messages['suc']}Links Found and Saved:")
        for domain, domain_links in links_found.items():
            if domain_links:
                print(f"{colors['cyan']}Domain: {colors['yellow']}{domain}")
                for link in domain_links:
                    print(f"{colors['green']}Link:{colors['yellow']}{link}")
                    print("-" * 50)
    else:
        print(f"{messages['error']}No links found.")


def extract_links(text):
    
    link_regex = r'https?://[^\s]+' 
    return re.findall(link_regex, text)


def get_domain(link):
    parsed_url = urlparse(link)
    domain = parsed_url.netloc  
    
    if domain.startswith("www."): 
        domain = domain[4:]

    return domain


if __name__ == "__main__":
    b = termux if OS() else wol
    w = worktermux if OS() else workwol
    clear()
    print (b)
    parser = ArgumentParser(description=f"{messages['wait']}Telegram Message and Entity Search Tool")

    parser.add_argument("--add", type=str, help="Add account: apihash:apiid:phone")
    parser.add_argument("--show", action="store_true", help="Show all accounts")
    parser.add_argument("--acc", type=str, help="Account numbers for specific actions (e.g. 1,2 or all)")
    parser.add_argument("--groups", action="store_true", help="Show all groups for the specified account")
    parser.add_argument("--channels", action="store_true", help="Show all channels for the specified account")
    parser.add_argument("--bots", action="store_true", help="Show all bots for the specified account")
    parser.add_argument("--dms", action="store_true", help="Show direct messages")

    parser.add_argument("--search-text", type=str, help="Text to search in messages")
    parser.add_argument("--sender", type=str, help="Chat ID of the sender to filter messages")
    parser.add_argument("--limit", type=int, help="Limit the number of messages to search")
    parser.add_argument("--forward", type=str, help="Username or User ID to forward the messages")
    parser.add_argument("--file-type", type=str, help="Filter by file type (e.g. pdf, zip, etc.)")
    parser.add_argument("--capture", action="store_true", help="Capture all messages of a target user")
    parser.add_argument("--target", type=str, help="Username or user_id to capture messages from")
    parser.add_argument("--post-channel", type=str, help="The number of posts to fetch or 'all' to fetch all messages from a channel")
    parser.add_argument("--link", type=str, help="Link or username of the channel to fetch messages from")
    parser.add_argument("--table", action="store_true", help="Show results in a table format")
    parser.add_argument("--linkfinder", action="store_true", help="Find all links in messages and save them")

    args = parser.parse_args()

    if args.add:
        parts = args.add.split(":")
        if len(parts) != 3:
            print(f"{messages['warn']}Format must be: apihash:apiid:phone")
        else:
            api_hash, api_id, phone = parts
            asyncio.run(add_account(api_hash, api_id, phone))
        exit()

    if args.show:
        show_accounts()
        exit()

    if not args.acc:
        print(f"{messages['error']}Invalid arguments. Use --help for usage information.")
        exit()

    dispatch = [
        (args.search_text, lambda: search_messages(args.acc, args.search_text, args.sender, args.limit, args.forward, args.file_type)),
        (args.link and args.forward, lambda: forward_from_channel(args.acc, args.link, args.forward, args.limit, args.table)),
        (args.groups, lambda: fetchDGC(args.acc, "groups")),
        (args.linkfinder, lambda: link_finder(args.acc)),
        (args.capture and args.target, lambda: capture_main(args.acc, args.target, args.forward, args.limit, args.file_type)),
        (args.channels, lambda: fetchDGC(args.acc, "channels")),
        (args.bots, lambda: fetchDGC(args.acc, "bots")),
        (args.dms, lambda: fetchDGC(args.acc, "dms")),
    ]

    for condition, func in dispatch:
        if condition:
            clear()
            print(w)
            asyncio.run(func())
            break
    else:
        print (f"""{colors['yellow']}
 _____    _      _   _             _   
|_   _|__| | ___| | | |_   _ _ __ | |_ 
  | |/ _ \ |/ _ \ |_| | | | | '_ \| __|
  | |  __/ |  __/  _  | |_| | | | | |_ 
  |_|\___|_|\___|_| |_|\__,_|_| |_|\__|
               
    {messages['error']}Invalid arguments. Use --help for usage information.
""")
