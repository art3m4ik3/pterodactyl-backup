from datetime import datetime
from dotenv import load_dotenv
import asyncio
import aiohttp
import pycron
import os

load_dotenv()

PANEL_URL: str = os.getenv("PANEL_URL")
DELAY_BETWEEN_REQUESTS: int = int(os.getenv("DELAY_BETWEEN_REQUESTS"))
HEADERS: dict = {
    "Authorization": f"Bearer {os.getenv('API_KEY')}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


async def get_servers(session: aiohttp.ClientSession) -> list[dict]:
    async with session.get(f"{PANEL_URL}/api/client", headers=HEADERS) as response:
        response.raise_for_status()
        data: dict = await response.json()
        return data["data"]


async def get_backups(session: aiohttp.ClientSession, server_id: str) -> list[dict]:
    async with session.get(
        f"{PANEL_URL}/api/client/servers/{server_id}/backups", headers=HEADERS
    ) as response:
        response.raise_for_status()
        data: dict = await response.json()
        return data["data"]


async def delete_backup(
    session: aiohttp.ClientSession, server_id: str, backup_id: str
) -> None:
    url: str = f"{PANEL_URL}/api/client/servers/{server_id}/backups/{backup_id}"
    async with session.delete(url, headers=HEADERS) as response:
        response.raise_for_status()
        print(f"Deleted backup {backup_id} for server {server_id}")


async def create_backup(session: aiohttp.ClientSession, server_id: str) -> None:
    url: str = f"{PANEL_URL}/api/client/servers/{server_id}/backups"
    async with session.post(url, headers=HEADERS) as response:
        response.raise_for_status()
        data: dict = await response.json()
        print(f"Backup created for server {server_id}: {data['attributes']['uuid']}")


async def check_and_create_backup(session: aiohttp.ClientSession, server: dict) -> None:
    server_id: str = server["attributes"]["identifier"]
    backups: list[dict] = await get_backups(session, server_id)

    if not backups:
        await create_backup(session, server_id)
        return
    else:
        oldest_backup: dict = sorted(
            backups, key=lambda x: x["attributes"]["created_at"]
        )[0]
        await delete_backup(session, server_id, oldest_backup["attributes"]["uuid"])
        await create_backup(session, server_id)


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        servers: list[dict] = await get_servers(session)
        if DELAY_BETWEEN_REQUESTS > 0:
            for server in servers:
                await check_and_create_backup(session, server)
                await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
        else:
            tasks: list = [
                check_and_create_backup(session, server) for server in servers
            ]
            await asyncio.gather(*tasks)


@pycron.cron("0 4 * * *")
async def backup_schedule(timestamp: datetime) -> None:
    print(f"Execution at {timestamp}")
    await main()


if __name__ == "__main__":
    asyncio.run(main())
    pycron.start()
