import asyncio
import requests
import datetime as dt
from datetime import timezone

from brother import Brother, SnmpError, UnsupportedModel

import config


async def check():
    try:
        brother = await Brother.create(config.printer_address)
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

        if delta > config.uptime_threshold:
            pretty_time = "{:0>8}".format(str(dt.timedelta(seconds=delta)))
            response = requests.post(
                config.ntfy_url,
                headers={
                    "Authorization": f"Basic {config.ntfy_auth}"
                },
                json={
                    "topic": "Tower",
                    "tags": ["printer"],
                    "title": "Brother HL-2270W",
                    "message": f"The printer has been on for {pretty_time}"
                }
            )

            print(response.text)


async def main():
    await asyncio.create_task(check())

asyncio.run(main())
