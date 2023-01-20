import json


def addSchedule(item):
    # Get the inputs
    id = item.get("id")
    user_id = str(item.get("user_id")),
    user_name = item.get("user_name"),
    src_name =  item.get("src_name"),
    src_address = item.get("src_address"),
    dst_name = item.get("dst_name"),
    dst_address = item.get("dst_address"),
    medium = item.get("medium"),
    days_of_week = item.get("days_of_week")

    response = {}
    ResponseMetadata = {}
    HTTPHeaders = {}

    HTTPHeaders["connection"] = "keep-alive"
    HTTPHeaders["content-length"] = "2"
    HTTPHeaders["concontent-typenection"] = "application/x-amz-json-1.0"
    HTTPHeaders["date"] = "Fri, 20 Jan 2023 20:06:39 GMT"
    HTTPHeaders["server"] = "Server"
    HTTPHeaders["x-amz-crc32"] = "2745614147"
    HTTPHeaders["x-amzn-requestid"] = "MQBQKK0MJRO981KSNES8KOMPAVVV4KQNSO5AEMVJF66Q9ASUAAJG"

    ResponseMetadata["HTTPStatusCode"] = 200
    ResponseMetadata["RequestId"] = "MQBQKK0MJRO981KSNES8KOMPAVVV4KQNSO5AEMVJF66Q9ASUAAJG"
    ResponseMetadata["RetryAttempts"] = 0

    ResponseMetadata["HTTPHeaders"] = HTTPHeaders
    response["ResponseMetadata"] = ResponseMetadata
    response["id"] = 1674245199212

    json_object = json.dumps(response)
    print(json_object)

    """jsonStr = {
    "ResponseMetadata": {
        "HTTPHeaders": {
            "connection": "keep-alive",
            "content-length": "2",
            "content-type": "application/x-amz-json-1.0",
            "date": "Fri, 20 Jan 2023 20:06:39 GMT",
            "server": "Server",
            "x-amz-crc32": "2745614147",
            "x-amzn-requestid": "MQBQKK0MJRO981KSNES8KOMPAVVV4KQNSO5AEMVJF66Q9ASUAAJG"
        },
        "HTTPStatusCode": 200,
        "RequestId": "MQBQKK0MJRO981KSNES8KOMPAVVV4KQNSO5AEMVJF66Q9ASUAAJG",
        "RetryAttempts": 0
    },
    "id":1674245199212 }"""


item = {"user_id": 111, "src_name": "Work", "src_address": ("2798 Arapahoe Ave, Boulder CO 80302",),
        "dst_name": ("Target",), "dst_address": "2800 Pearl St, Boulder, CO 80301", "medium":"DRIVING",
        "days_of_week": {"Sunday": ["23:00:00", "22:30:00"], "Monday": ["2:30:00", "6:30:00"]}}

addSchedule(item)