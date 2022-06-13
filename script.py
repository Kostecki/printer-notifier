import asyncio
from calendar import c
from sys import argv
import json
import requests
import datetime as dt
from datetime import timezone

from brother import Brother, SnmpError, UnsupportedModel

import config

# Telegram API url
url = f"https://api.telegram.org/bot{config.tg_apikey}/sendMessage"

async def main():
    brother = Brother(config.printer_ip, kind="laser")

    try:
        data = await brother.async_update()
    except (ConnectionError, SnmpError, UnsupportedModel) as error:
        print(f"{error}")
        return

    brother.shutdown()

    if data:
        then = data.uptime
        now = dt.datetime.now(timezone.utc).replace(microsecond=0)
        delta = (now-then).total_seconds()

        if delta > 3600:
            pretty_time = "{:0>8}".format(str(dt.timedelta(seconds=delta)))
            requests.post(url, data = {'chat_id': config.tg_chatId, 'parse_mode': 'html', 'text': f"<b>Brother HL-2270W</b> \nThe printer has been on for {pretty_time}"})

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()
