#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import requests
import time
import json
import os
from datetime import datetime

# =======================
# Настройки
# =======================
MODEM_IP = "192.168.1.1"  # IP модема
OUTPUT_DIR = "sms_messages"  # директория для сохранения сообщений
MONITOR_FILE = os.path.join(OUTPUT_DIR, "monitor_log.txt")
POLL_INTERVAL = 10  # интервал проверки новых сообщений в секундах

# =======================
# Утилиты
# =======================
def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def format_message(msg):
    return f"[{msg['time']}] From: {msg['from']} - {msg['text']}"

def save_to_file(msgs, file_type="txt"):
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if file_type == "json":
        filename = os.path.join(OUTPUT_DIR, f"sms_{timestamp}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(msgs, f, ensure_ascii=False, indent=2)
    else:
        filename = os.path.join(OUTPUT_DIR, f"sms_{timestamp}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            for msg in msgs:
                f.write(format_message(msg) + "\n")
    print(f"Saved messages to {filename}")

# =======================
# Работа с модемом
# =======================
def send_sms(number, text):
    url = f"http://{MODEM_IP}/api/sms/send"
    payload = {"number": number, "text": text}
    try:
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            print("SMS sent successfully")
        else:
            print(f"Failed to send SMS. Status: {r.status_code}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

def receive_sms(all_msgs=False, unread=False, contact=None):
    url = f"http://{MODEM_IP}/api/sms/list"
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print(f"Failed to fetch SMS. Status: {r.status_code}")
            return []

        messages = r.json()  # предполагается, что модем возвращает JSON
        filtered = []
        for msg in messages:
            if unread and msg.get("read", True):
                continue
            if contact and msg.get("from") != contact:
                continue
            filtered.append(msg)
        return filtered
    except Exception as e:
        print(f"Error receiving SMS: {e}")
        return []

def clear_sms(contact=None):
    url = f"http://{MODEM_IP}/api/sms/clear"
    payload = {}
    if contact:
        payload["contact"] = contact
    try:
        r = requests.post(url, json=payload)
        if r.status_code == 200:
            print("Messages deleted successfully")
        else:
            print(f"Failed to delete messages. Status: {r.status_code}")
    except Exception as e:
        print(f"Error clearing SMS: {e}")

# =======================
# Мониторинг новых сообщений
# =======================
def monitor_sms(interval=POLL_INTERVAL):
    print(f"Starting SMS monitor every {interval} seconds. Press Ctrl+C to stop.")
    ensure_output_dir()
    seen_ids = set()
    while True:
        try:
            msgs = receive_sms(all_msgs=True)
            new_msgs = [m for m in msgs if m["id"] not in seen_ids]
            if new_msgs:
                with open(MONITOR_FILE, "a", encoding="utf-8") as f:
                    for msg in new_msgs:
                        f.write(format_message(msg) + "\n")
                        seen_ids.add(msg["id"])
                        print(format_message(msg))
            time.sleep(interval)
        except KeyboardInterrupt:
            print("Monitor stopped by user")
            break
        except Exception as e:
            print(f"Error in monitor: {e}")
            time.sleep(interval)

# =======================
# Парсер команд
# =======================
def main():
    parser = argparse.ArgumentParser(description="Alcatel LINKKEY IK40/IK41 SMS Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # send
    send_parser = subparsers.add_parser("send", help="Send SMS")
    send_parser.add_argument("number", help="Phone number")
    send_parser.add_argument("text", help="Message text")

    # receive
    receive_parser = subparsers.add_parser("receive", help="Receive SMS")
    receive_parser.add_argument("--all", action="store_true", help="All messages")
    receive_parser.add_argument("--unread", action="store_true", help="Unread messages only")
    receive_parser.add_argument("--contact", help="Filter by number")
    receive_parser.add_argument("--file", action="store_true", help="Save to text file")
    receive_parser.add_argument("--json", action="store_true", help="Save to JSON file")

    # clear
    clear_parser = subparsers.add_parser("clear", help="Delete SMS")
    clear_parser.add_argument("--contact", help="Delete messages from specific number")

    # monitor
    monitor_parser = subparsers.add_parser("monitor", help="Monitor incoming SMS in real-time")
    monitor_parser.add_argument("--interval", type=int, default=POLL_INTERVAL, help="Polling interval in seconds")

    # debug/help
    subparsers.add_parser("debug", help="Debug info")
    subparsers.add_parser("help", help="Show help")

    args = parser.parse_args()

    if args.command == "send":
        send_sms(args.number, args.text)
    elif args.command == "receive":
        msgs = receive_sms(all_msgs=args.all, unread=args.unread, contact=args.contact)
        for m in msgs:
            print(format_message(m))
        if args.file:
            save_to_file(msgs, "txt")
        if args.json:
            save_to_file(msgs, "json")
    elif args.command == "clear":
        clear_sms(contact=args.contact)
    elif args.command == "monitor":
        monitor_sms(interval=args.interval)
    elif args.command == "debug":
        print(f"Mode: DEBUG\nModem IP: {MODEM_IP}\nOutput directory: {OUTPUT_DIR}")
    elif args.command == "help":
        parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
