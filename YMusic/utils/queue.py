QUEUE = {}

def add_to_queue(chat_id, title, duration, audio_file, link):
    if chat_id not in QUEUE:
        QUEUE[chat_id] = []
    QUEUE[chat_id].append({"title": title, "duration": duration, "audio_file": audio_file, "link": link})
    return len(QUEUE[chat_id])

def get_queue(chat_id):
    return QUEUE.get(chat_id, [])

def pop_an_item(chat_id):
    if chat_id in QUEUE and QUEUE[chat_id]:
        item = QUEUE[chat_id].pop(0)
        if not QUEUE[chat_id]:
            del QUEUE[chat_id]
        print(f"Popped item from queue for chat {chat_id}: {item['title']}")
        return item
    print(f"No items in queue for chat {chat_id}")
    return None

def clear_queue(chat_id):
    if chat_id in QUEUE:
        del QUEUE[chat_id]
        return True
    return False

def is_queue_empty(chat_id):
    return chat_id not in QUEUE or not QUEUE[chat_id]

def get_queue_length(chat_id):
    return len(QUEUE.get(chat_id, []))