import notification_handler as notify


def send_push():
    #token = "ExponentPushToken[QbAEWfKlJQaOKdHxV5R7QJ]"
    token = "ExponentPushToken[aajk2kK3Js04PZoEdXMFh9]"
    msg = "Another alert to Expo!"
    notify.send_push_message(token, msg, None)
    return "Tried to send!"


# Test the function
send_push()
