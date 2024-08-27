from threading import Lock

QUEUE = {}
MAX_QUEUE_SIZE = 10
queue_lock = Lock()

def add_to_queue(chat_id, title, duration, audio_file, link, requester_name, requester_id, query):
    with queue_lock:
        if chat_id not in QUEUE:
            QUEUE[chat_id] = []
        if len(QUEUE[chat_id]) >= MAX_QUEUE_SIZE:
            return False
        QUEUE[chat_id].append({
            "title": title, 
            "duration": duration, 
            "audio_file": audio_file, 
            "link": link,
            "requester_name": requester_name,
            "requester_id": requester_id,
            "query": query
        })
        return len(QUEUE[chat_id])

def get_queue(chat_id):
    with queue_lock:
        return QUEUE.get(chat_id, []).copy()

def get_queue_length(chat_id):
    with queue_lock:
        return len(QUEUE.get(chat_id, []))

def get_current_song(chat_id):
    with queue_lock:
        if chat_id in QUEUE and QUEUE[chat_id]:
            return QUEUE[chat_id][0].copy()
    return None

def pop_an_item(chat_id):
    with queue_lock:
        if chat_id in QUEUE and QUEUE[chat_id]:
            item = QUEUE[chat_id].pop(0)
            if not QUEUE[chat_id]:
                del QUEUE[chat_id]
            print(f"Popped item from queue for chat {chat_id}: {item['title']}")
            return item
    print(f"No items in queue for chat {chat_id}")
    return None

def clear_queue(chat_id):
    with queue_lock:
        if chat_id in QUEUE:
            del QUEUE[chat_id]
            return True
    return False

def is_queue_empty(chat_id):
    with queue_lock:
        return chat_id not in QUEUE or not QUEUE[chat_id]