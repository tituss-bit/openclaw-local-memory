#!/usr/bin/env python3
"""
Export Telegram chat history using Telethon (user account API).

Usage:
    python tg_export.py --api-id 12345 --api-hash abc123 --chat BotUsername

Get API credentials at https://my.telegram.org/apps
You'll need to enter your phone number and a verification code on first run.
"""
import argparse, json, sys

def main():
    parser = argparse.ArgumentParser(description='Export Telegram chat history')
    parser.add_argument('--api-id', type=int, required=True)
    parser.add_argument('--api-hash', required=True)
    parser.add_argument('--chat', required=True, help='Username or chat ID')
    parser.add_argument('--output', default='result.json', help='Output file')
    parser.add_argument('--session', default='tg_session', help='Session file name')
    args = parser.parse_args()

    try:
        from telethon.sync import TelegramClient
    except ImportError:
        print("Install telethon: pip install telethon")
        sys.exit(1)

    with TelegramClient(args.session, args.api_id, args.api_hash) as client:
        messages = []
        count = 0
        for msg in client.iter_messages(args.chat, limit=None):
            if msg.text:
                messages.append({
                    'id': msg.id,
                    'type': 'message',
                    'date': str(msg.date),
                    'from': 'me' if msg.out else 'bot',
                    'text': msg.text
                })
                count += 1
                if count % 1000 == 0:
                    print(f"  {count} messages...")

        messages.reverse()

        with open(args.output, 'w') as f:
            json.dump({'messages': messages}, f, ensure_ascii=False, indent=2)

        print(f"Exported {count} messages to {args.output}")

if __name__ == '__main__':
    main()
