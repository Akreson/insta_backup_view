import os
import sys
import json

JSON_EXT = ".json"
PATH_SPLIT = None

html_header = """
<!DOCTYPE html>
<html lang="en">

<head>

	<meta charset="utf-8">

	<title>Title</title>
	<meta name="description" content="">

	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">

	<meta property="og:image" content="path/to/image.jpg">
	<meta name="theme-color" content="#000">
	<meta name="msapplication-navbutton-color" content="#000">
	<meta name="apple-mobile-web-app-status-bar-style" content="#000">

    <style>
        .main_column
        {
            width: 30%;
            margin: auto;
            border-style: solid;
            border-width: 2px;
            border-color: black;
            display: flex;
            flex-direction: column;
        }

        .name
        {
            padding-left: 2%;
            padding-right: 2%;
            padding-top: 5px;
            padding-bottom: 5px;
            background-color: #cccccc;
        }

        .msg-body
        {
            padding-left: 5%;
            padding-right: 5%;
            padding-top: 5px;
            padding-bottom: 5px;
            font-size: 20px;
        }

        .send .msg-body
        {
            width: 55%;
            float: right;
            text-align: right;
        }

        .send .name
        {
            text-align: right;
        }

        img
        {
            width: 50%;
            display: block;
        }

        .send img
        {
            margin-left: auto;
        }

        .recv .msg-body
        {
            width: 56%;
            float: left;
        }

        .recv .name
        {
            text-align: left;
        }

        .recv img
        {
            margin-right: auto;
        }

        .message-wrapper
        {
            width: 100%;
        }
    </style>
</head>

"""
html_body_start = "<body><div class='main_column'>"
html_body_end = "</div></body>"

msg_pattert_start = """
<div class="message-wrapper">
    <div class="{0}">
        <div class="name">{1}</div>
"""

msg_content = "<div class='msg-body'>{0}</div>"
msg_image = "<img src='{0}'>"

msg_pattert_end = """
    </div>
</div>
"""

def error(str):
    print(str)
    sys.exit()

def get_utf8_str(str):
    return str.encode('latin1').decode('utf8')

class MsgType:
    Generic = 1
    Share = 2
    Call = 3

class ChatRoom:
    def __init__(self, folder: str):
        self.owner = None
        self.chat_page = str()
        self.path = folder
        self.chat_folder = folder.split(os.path.sep)[-1]

        self.chat_page += html_header
        self.chat_page += html_body_start

    def get_msg_type(self, msg):
        result = None
        type_str = msg["type"]

        if type_str == "Generic":
            result = MsgType.Generic
        elif type_str == "Share":
            result = MsgType.Share
        elif type_str == "Call":
            result = MsgType.Call
        
        return result

    def get_local_path(self, path):
        result_path = None
        split_path = path.split('/')
        split_sym = os.path.sep

        for i, name in enumerate(split_path):
            if name == self.chat_folder:
                result_path = split_sym.join(split_path[(i + 1)::])

        return result_path
    
    def parse_data(self, data):
        messages = data["messages"]

        for msg in reversed(messages):
            sender = get_utf8_str(msg["sender_name"])
            msg_type = self.get_msg_type(msg)

            msg_class = None
            if sender == self.owner:
                msg_class = "send"
            else:
                msg_class = "recv"

            if msg_type == MsgType.Generic or msg_type == MsgType.Call:
                add_text = str()
                add_text += msg_pattert_start.format(msg_class, sender)

                if "content" in msg:
                    msg_body = get_utf8_str(msg["content"])
                    add_text += msg_content.format(msg_body)
                elif "photos" in msg:
                    photos = msg["photos"]
                    for photo in photos:
                        photo_uri = photo["uri"]
                        local_path = self.get_local_path(photo_uri)
                        add_text += msg_image.format(local_path)

                add_text += msg_pattert_end
                self.chat_page += add_text

    def check_owner(self, msg_list):
        for msg in msg_list:
            owner_name = get_utf8_str(msg["participants"][1]["name"])

            if self.owner is None:
                self.owner = owner_name
            elif self.owner != owner_name:
                return False
        
        return True

    def sort_by_time(self, msg_list):
        result_list = []
        time_list = []

        for i, msg in enumerate(msg_list):
            time = msg["messages"][0]["timestamp_ms"]
            time_list.append((i, time))
        
        time_list = sorted(time_list, key=lambda tup: tup[1])

        for item in time_list:
            result_list.append(msg_list[item[0]])

        return result_list

    def build_html(self, data):
        message_list = []
        for file in files:
            with open(file, encoding='utf-8') as f:
                try:
                   msg = json.load(f)
                   message_list.append(msg)
                except:
                    error("ERROR: Invalid json file")

        if not self.check_owner(message_list):
            error("ERROR: Owner in json file not match")

        sorted_msg_list = self.sort_by_time(message_list)

        print("Sorting done")
        for msg_list in sorted_msg_list:
            self.parse_data(msg_list)

        self.chat_page += html_body_end
        
        result_html = open("this_chat.html", "wb")
        result_html.write(self.chat_page.encode())
        result_html.close()

        
def get_json_files():
    result = []

    for file in os.listdir():        
        if os.path.isfile(file):
            extension = os.path.splitext(file)[1]
            if extension == JSON_EXT:
                result.append(file)
    
    return result

def main():
    # NOTE: Full path to chat folder
    messages_dir = sys.argv[1]

    if os.path.isdir(messages_dir):
        Chat = ChatRoom(messages_dir)
        os.chdir(messages_dir)

        files = get_json_files()    
        Chat.build_html(files)
    else:
        print("ERROR: Invalid path")

if __name__ ==  "__main__":
    main() 