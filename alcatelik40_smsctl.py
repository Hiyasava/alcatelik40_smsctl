"""
<Program Name>
    alcatelik40_smsctl.py
<Author>
    Richard Appleby (модифицировано для получения SMS)
<Purpose>
    Provides a command line interface to an Alcatel Linkkey IK40V/IK41VE1 4G mobile broadband dongle,
    allowing sending and receiving of SMS messages without needing to navigate its web interface.
<Usage>
    Для отправки: alcatelik40_smsctl.py send <mobileNumber> <SMS message text>
    Для получения: alcatelik40_smsctl.py receive [--all|--unread|--file|--json|--contact <number>]
    Для очистки: alcatelik40_smsctl.py clear
"""

import requests
import datetime
import time
import sys
import json
import os
import re

URL = "http://192.168.1.1/jrd/webapi"

JSON_CHECKREQUEST = { 
    "jsonrpc": "2.0",
    "method": "GetSendSMSResult",
    "params": {},
    "id": "6.7"
}

JSON_GET_SMS_LIST = {
    "jsonrpc": "2.0",
    "method": "GetSMSContactList",
    "params": {"Page": 0},
    "id": "6.2"
}

JSON_GET_SMS_LIST_UNREAD = {
    "jsonrpc": "2.0",
    "method": "GetSMSContactList",
    "params": {"Page": 0,"TagType": 1},
    "id": "6.2"
}

JSON_GET_SMS_CONTENT = {
    "jsonrpc": "2.0",
    "method": "GetSMSContentList",
    "params": {"Page": 0,"ContactId": 0},
    "id": "6.3"
}

JSON_DELETE_SMS = {
    "jsonrpc": "2.0",
    "method": "DeleteSMS",
    "params": {"SMSId": []},
    "id": "6.5"
}

HEADERS = {
    "Host": "192.168.1.1",
    "Origin": "http://192.168.1.1",
    "Referer": "http://192.168.1.1/index.html",
    "Content-Type": "application/json"
}

SMS_DIRECTORY = "sms_messages"

def send_request(json_data):
    try:
        r = requests.post(URL, json=json_data, headers=HEADERS, timeout=10)
        return r.json()
    except Exception as e:
        print(f"Request error: {e}")
        return None

def send_sms(phone_number, message):
    dateTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    JSON_SENDREQUEST = {
        "jsonrpc": "2.0",
        "method": "SendSMS",
        "params": {"SMSId": -1,"SMSContent": message,"PhoneNumber": [phone_number],"SMSTime": dateTime},
        "id": "6.6"
    }
    result = send_request(JSON_SENDREQUEST)
    if not result or "error" in result:
        print("Failed to send SMS")
        return False
    time.sleep(1)
    while True:
        status_result = send_request(JSON_CHECKREQUEST)
        if not status_result or "error" in status_result:
            print("Failed to check SMS status")
            return False
        send_status = status_result.get("result", {}).get("SendStatus")
        if send_status == 2:
            print("SMS successfully sent")
            return True
        elif send_status > 2:
            print("SMS failed to send")
            return False
        time.sleep(0.5)

def get_sms_list(unread_only=False, received_only=True):
    result = send_request(JSON_GET_SMS_LIST_UNREAD if unread_only else JSON_GET_SMS_LIST)
    if not result or "error" in result:
        print("Failed to get SMS list")
        return None
    messages_data = result.get("result", {})
    if received_only:
        messages = extract_messages(messages_data)
        received_messages = [msg for msg in messages if msg.get('SMSType') == 0]
        return {"MessageList": received_messages}
    return messages_data

def get_sms_by_contact(contact_id, received_only=True):
    JSON_GET_SMS_CONTENT["params"]["ContactId"] = contact_id
    result = send_request(JSON_GET_SMS_CONTENT)
    if not result or "error" in result:
        print(f"Failed to get SMS for contact ID {contact_id}")
        return None
    messages_data = result.get("result", {})
    if received_only:
        messages = extract_messages(messages_data)
        received_messages = [msg for msg in messages if msg.get('SMSType') == 0]
        return {"ContentList": received_messages}
    return messages_data

def find_contact_id(phone_number):
    messages_data = get_sms_list(False)
    if not messages_data:
        return None
    messages = extract_messages(messages_data)
    normalized_target = normalize_phone(phone_number)
    for msg in messages:
        msg_numbers = msg.get('PhoneNumber', [])
        if not isinstance(msg_numbers, list):
            msg_numbers = [msg_numbers]
        for msg_number in msg_numbers:
            if normalize_phone(msg_number) == normalized_target:
                return msg.get('ContactId')
    return None

def normalize_phone(phone_number):
    if not phone_number:
        return ""
    if not isinstance(phone_number, str):
        phone_number = str(phone_number)
    normalized = re.sub(r'[^\d+]', '', phone_number)
    if len(normalized) == 11 and normalized.startswith('8'):
        normalized = '7' + normalized[1:]
    if normalized.startswith('+'):
        normalized = normalized[1:]
    if not normalized.isdigit():
        return phone_number.lower().strip()
    return normalized

def extract_messages(messages_data):
    if not messages_data:
        return []
    if "MessageList" in messages_data:
        return messages_data["MessageList"]
    if "SMSList" in messages_data:
        return messages_data["SMSList"]
    if "ContentList" in messages_data:
        return messages_data["ContentList"]
    for key, value in messages_data.items():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return value
    return []

def save_sms_to_file(messages_data, filename=None, source_info=""):
    messages = extract_messages(messages_data)
    if not messages:
        print("No messages to save")
        return False
    if not os.path.exists(SMS_DIRECTORY):
        os.makedirs(SMS_DIRECTORY)
    if not filename:
        filename = f"sms_messages_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(SMS_DIRECTORY, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"SMS Messages - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if source_info:
                f.write(f"{source_info}\n")
            f.write("=" * 60 + "\n\n")
            for i, msg in enumerate(messages, 1):
                f.write(f"Message #{i}:\n")
                f.write(f"From: {msg.get('PhoneNumber', msg.get('Number', 'Unknown'))}\n")
                f.write(f"Time: {msg.get('SMSTime', msg.get('Time', 'Unknown'))}\n")
                f.write(f"Type: {get_message_type(msg.get('SMSType', 0))}\n")
                f.write(f"Status: {get_message_status(msg.get('TagType', msg.get('Status', 0)))}\n")
                f.write(f"Content:\n{msg.get('SMSContent', msg.get('Content', 'No content'))}\n")
                f.write("-" * 40 + "\n\n")
        print(f"Saved {len(messages)} messages to: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False

def save_sms_json(messages_data, filename=None, source_info=""):
    messages = extract_messages(messages_data)
    if not messages:
        print("No messages to save")
        return False
    if not os.path.exists(SMS_DIRECTORY):
        os.makedirs(SMS_DIRECTORY)
    if not filename:
        filename = f"sms_messages_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(SMS_DIRECTORY, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "export_date": datetime.datetime.now().isoformat(),
                "source": source_info,
                "message_count": len(messages),
                "messages": messages
            }, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(messages)} messages to JSON: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def get_message_status(tag_type):
    return {0:"Unknown",1:"Unread",2:"Read",3:"Sent",4:"Draft",5:"Failed"}.get(tag_type,f"Unknown ({tag_type})")

def delete_all_sms():
    messages_data = get_sms_list(False, received_only=False)
    if not messages_data:
        print("No messages to delete")
        return False
    messages = extract_messages(messages_data)
    deleted_count = 0
    for msg in messages:
        contact_id = msg.get('ContactId')
        sms_id = msg.get('SMSId', msg.get('Id'))
        if contact_id and sms_id:
            if delete_single_message(contact_id, sms_id):
                deleted_count += 1
            time.sleep(0.1)
    print(f"Deleted {deleted_count} messages")
    return deleted_count > 0

def delete_single_message(contact_id, sms_id):
    JSON_DELETE_SINGLE = {
        "jsonrpc": "2.0",
        "method": "DeleteSMS",
        "params": {"DelFlag": 2,"ContactId": contact_id,"SMSId": sms_id},
        "id": "6.5"
    }
    result = send_request(JSON_DELETE_SINGLE)
    return bool(result and "error" not in result)

def delete_contact_messages(contact_id):
    JSON_DELETE_CONTACT = {
        "jsonrpc": "2.0",
        "method": "DeleteSMS",
        "params": {"DelFlag": 1,"ContactId": contact_id,"SMSId": 0},
        "id": "6.5"
    }
    result = send_request(JSON_DELETE_CONTACT)
    return bool(result and "error" not in result)

def clear_command():
    if len(sys.argv) > 2 and sys.argv[2].lower() == "--contact":
        if len(sys.argv) < 4:
            print("Usage: python alcatelik40_smsctl.py clear --contact <phoneNumber>")
            quit(1)
        phone_number = sys.argv[3]
        contact_id = find_contact_id(phone_number)
        if contact_id:
            confirm = input(f"Delete ALL messages from {phone_number}? (y/N): ")
            if confirm.lower() == 'y':
                delete_contact_messages(contact_id)
            else:
                print("Cancelled")
        else:
            print(f"No messages for {phone_number}")
    else:
        confirm = input("Delete ALL messages? (y/N): ")
        if confirm.lower() == 'y':
            delete_all_sms()
        else:
            print("Cancelled")

def get_message_type(sms_type):
    return {0:"Received",1:"Draft",2:"Sent",3:"Outbox"}.get(sms_type,f"Unknown ({sms_type})")

def print_sms_messages(messages_data, source_info=""):
    messages = extract_messages(messages_data)
    if source_info:
        print(f"{source_info}:")
    print(f"Found {len(messages)} messages")
    print("-" * 80)
    for i, msg in enumerate(messages, 1):
        print(f"Message #{i}:")
        print(f"ID: {msg.get('SMSId', msg.get('Id', 'N/A'))}")
        print(f"Contact ID: {msg.get('ContactId', 'N/A')}")
        print(f"From: {msg.get('PhoneNumber', msg.get('Number', 'Unknown'))}")
        print(f"Time: {msg.get('SMSTime', msg.get('Time', 'Unknown'))}")
        print(f"Type: {get_message_type(msg.get('SMSType', 0))}")
        print(f"Status: {get_message_status(msg.get('TagType', msg.get('Status', 0)))}")
        print(f"Content: {msg.get('SMSContent', msg.get('Content', 'No content'))}")
        print("-" * 80)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Send SMS:    python alcatelik40_smsctl.py send <mobileNumber> <message>")
        print("  Receive SMS: python alcatelik40_smsctl.py receive [--all|--unread|--file|--json|--contact <number>|--sent]")
        print("  Clear SMS:   python alcatelik40_smsctl.py clear [--contact <number>]")
        quit(1)
    command = sys.argv[1].lower()
    if command == "send":
        if len(sys.argv) < 4:
            print("Usage: python alcatelik40_smsctl.py send <mobileNumber> <message>")
            quit(1)
        send_sms(sys.argv[2], ' '.join(sys.argv[3:]))
    elif command == "receive":
        unread_only = False
        save_to_file = False
        save_json = False
        contact_number = None
        received_only = True
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i].lower()
            if arg == "--contact":
                if i + 1 >= len(sys.argv):
                    print("Usage: python alcatelik40_smsctl.py receive --contact <phoneNumber>")
                    quit(1)
                contact_number = sys.argv[i+1]
                i += 2
            elif arg == "--unread":
                unread_only = True; i += 1
            elif arg == "--all":
                unread_only = False; i += 1
            elif arg == "--file":
                save_to_file = True; i += 1
            elif arg == "--json":
                save_json = True; i += 1
            elif arg == "--sent":
                received_only = False; i += 1
            else:
                print(f"Unknown argument: {arg}"); quit(1)
        if contact_number:
            contact_id = find_contact_id(contact_number)
            if contact_id:
                messages = get_sms_by_contact(contact_id, received_only)
                source_info = f"Messages for {contact_number}"
            else:
                print(f"No messages for number: {contact_number}")
                messages = None
        else:
            messages = get_sms_list(unread_only, received_only)
            source_info = "Unread messages" if unread_only else "All messages"
        if messages:
            if save_to_file:
                save_sms_to_file(messages, source_info=source_info)
            elif save_json:
                save_sms_json(messages, source_info=source_info)
            else:
                print_sms_messages(messages, source_info=source_info)
    elif command == "clear":
        clear_command()
    else:
        print(f"Unknown command: {command}")
        quit(1)

if __name__ == "__main__":
    main()
