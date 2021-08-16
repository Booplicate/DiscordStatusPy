# DiscordStatusPy - async API wrapper around [discordstatus](https://discordstatus.com)

### Requirements:
Tested with the stack below. May or may not work on other versions.
 - `Python 3.9.6`
 - `AIOHTTP 3.7.4`

### Usage:
Example 1:

```python
import asyncio
import DiscordStatusPy

async def main():
    maintenances = await DiscordStatusPy.get_maintenances()
    print(maintenances['scheduled_maintenances'])

asyncio.run(main())
```

While you can access the API via the appropriate functions,
it's better performance-wise if you use the APIClient class,
especially if you're making multiple calls.

Always close connection when you don't need your APIClient instance anymore.
For that call its `close` method:
```python
await my_client.close()
```
Or use an async content manager which will do that for you:
```python
async with APIClient() as client:
    # Do stuff
# Now it's closed
```

Example 2:

```python
import asyncio
from DiscordStatusPy import APIClient

async def main():
    async with APIClient() as client:
        status = await client.get_status()
        incidents = await client.get_incidents()
        print(status['status']['description'])
        print(incidents)

    # Alternatively (less desirable)
    client = APIClient()
    components = await client.get_components()
    print(components)
    await client.close()

asyncio.run(main())
```
