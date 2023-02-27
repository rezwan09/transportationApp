import notification_handler as notify
from datetime import datetime


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


def getTimeString():
    arrival_time_str = "2023-02-17 22:50:00"
    arrival_time = datetime.strptime(arrival_time_str, "%Y-%m-%d %H:%M:%S")
    arrival_time_str = arrival_time.strftime("%I:%M %p")
    print(arrival_time_str)


# Test the function
getTimeString()
#print(get_text({"user_name":"name", "src_name":"src-name", "dst_name":"dst_name"}))
#send_push()
