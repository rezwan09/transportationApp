import notification_handler as notify


def send_push():
    #token = "ExponentPushToken[QbAEWfKlJQaOKdHxV5R7QJ]"
    token = "ExponentPushToken[aajk2kK3Js04PZoEdXMFh9]"
    msg = "Another alert to Expo!"
    notify.send_push_message(token, msg, None)
    return "Tried to send!"


def get_text(item):
    text = "Hi..." + item['user_name'] + ",\nThese are some information that might help you about your trip\n:compass:" \
           + item['src_name'] \
           + " to " + item['dst_name'] \
           + "\n" + ":alarm_clock: in 10 minutes\n\n" \
           + ":world_map:Map Marks:world_map:\n" \
           + "====================\n" \
           + ":large_yellow_circle:Road Constructions \n" \
           + ":red_circle:Road Incident\n" \
           + ":large_purple_circle:Air Quality along the road\n\n" \
           + ":sunny:Weather Conditions:cloud:\n" \
           + "====================\n"
    return text


# Test the function
print(get_text({"user_name":"name", "src_name":"src-name", "dst_name":"dst_name"}))
#send_push()
