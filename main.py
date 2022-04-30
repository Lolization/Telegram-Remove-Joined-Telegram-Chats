import asyncio
import json
from typing import List

from telethon import TelegramClient
from telethon.tl.types import User, MessageActionContactSignUp
from tqdm.asyncio import tqdm

from Consts import CLIENT_PHONE, CLIENT_PASSWORD, API_ID, API_HASH


async def fetch_all_chats(client: TelegramClient) -> List[User]:
	all_chats = []
	
	print("Loading conversations\n")
	
	async for dialog in client.iter_dialogs():
		# Get all user conversations
		entity = dialog.entity
		if isinstance(entity, User):
			if entity.first_name and not entity.last_name:
				print(f"{entity.first_name} {entity.last_name}")
			else:
				print(f"{entity.id} {entity.username}")
			all_chats.append(entity)
	
	return all_chats


async def get_empty_chats(client, chats):
	empty_chats = []
	
	for chat in tqdm(chats):
		# Must check for at least more than 1 message,
		# so you don't accidentally delete chats that have more than 1 message.
		msgs = []
		async for msg in client.iter_messages(chat):
			msgs.append(msg)
			if len(msgs) > 3:
				break
		
		if len(msgs) == 1 and isinstance(msgs[0].action, MessageActionContactSignUp):
			empty_chats.append(chat.id)
	
	return empty_chats


async def remove_empty_chats(client, empty_chats):
	# Remove all empty chats
	for chat_id in empty_chats:
		chat = await client.get_entity(chat_id)
		print(f"Removing {chat.first_name} {chat.last_name}")
		await client.delete_dialog(chat_id)


async def main():
	# region Connect
	client = TelegramClient('session_name', API_ID, API_HASH)
	# noinspection PyTypeChecker
	await client.start(phone=CLIENT_PHONE, password=CLIENT_PASSWORD)
	# endregion
	
	async with client:
		# Fetch all conversations
		chats = await fetch_all_chats(client)
		
		empty_chats = await get_empty_chats(client, chats)
		
		print(json.dumps(empty_chats, indent=4))
		await remove_empty_chats(client, empty_chats)


if __name__ == "__main__":
	asyncio.run(main())
