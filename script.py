import asyncio
import requests
import datetime as dt
from datetime import timezone

from brother import Brother, SnmpError, UnsupportedModel

import config

# Telegram API url
url = f"https://api.telegram.org/bot{config.tg_apikey}/sendMessage"


async def check():
    try:
        brother = await Brother.create(config.printer_ip)
        data = await brother.async_update()
    except (ConnectionError, SnmpError, UnsupportedModel) as error:
        print(f"{error}")
        return
    finally:
        brother.shutdown()

    if data:
        then = data.uptime
        now = dt.datetime.now(timezone.utc).replace(microsecond=0)
        delta = (now-then).total_seconds()

        if delta > 3600:
            pretty_time = "{:0>8}".format(str(dt.timedelta(seconds=delta)))
            requests.post(
                url,
                data={
                    'chat_id': config.tg_chatId, 'parse_mode': 'html', 'text': f"<b>Brother HL-2270W</b> \nThe printer has been on for {pretty_time}"
                }
            )


async def main():
    await asyncio.create_task(check())

asyncio.run(main())
