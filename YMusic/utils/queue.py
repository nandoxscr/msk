QUEUE = {}

def add_to_queue(chat_id, title, duration, audio_file, link):
    if chat_id not in QUEUE:
        QUEUE[chat_id] = []
    QUEUE[chat_id].append({"title": title, "duration": duration, "audio_file": audio_file, "link": link})
    return len(QUEUE[chat_id])

def get_queue(chat_id):
    if chat_id in QUEUE:
        chat_queue = QUEUE[chat_id]
        return chat_queue
    else:
        return 0


def pop_an_item(chat_id):
    if chat_id in QUEUE:
        chat_queue = QUEUE[chat_id]
        chat_queue.pop(0)
        return 1
    else:
        return 0


def clear_queue(chat_id):
    if chat_id in QUEUE:
        QUEUE.pop(chat_id)
        return 1
    else:
        return 0
