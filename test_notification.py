import notification_handler as notify


def send_push():
    #token = "ExponentPushToken[QbAEWfKlJQaOKdHxV5R7QJ]"
    token = "ExponentPushToken[aajk2kK3Js04PZoEdXMFh9]"
    msg = "Another alert to Expo!"
    notify.send_push_message(token, msg, None)
    return "Tried to send!"


def get_text(item):
    text = "Hi..." + item['user_name'] + ",\nThese are some information that might help you about your trip\n:compass:"\
           +item['src_address']\
           +" to " + item['dst_address']\
           +"\n" + ":alarm_clock: in 10 minutes\n"\
           +"=============================\n:boom:Road Accidents:car:\n=============================\n"\
           +"None reported\n"\
           +"=============================\n:male-construction-worker:Construction Events :female-construction-worker:\n=============================\n"\
           +"None reported\n"\
           +"=============================\n:motorway:Road Conditions:motorway:\n=============================\n"\
           +"None reported\n"\
           +"=============================\n:sunny:Weather:cloud:\n=============================\n"\
           +"None reported\n"
    return text


# Test the function
print(get_text({"user_name":"name", "src_address":"src-addr", "dst_address":"dst_addr"}))
#send_push()
