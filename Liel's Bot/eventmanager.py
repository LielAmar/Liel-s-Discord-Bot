# ========== Variables ==========
last_event_time = 0
event_phase = 0
event_type = 0
event_math_answer = 0
event_scramble_answer = ""

# ========== METHODS ==========
async def check_answer(message):
    if message.content == str(event_math_answer):
        return True
    return False
