import time, random, asyncio
from format import generate_text
from disnake import TextChannel
from disnake.ext import commands
from aiosonic import HTTPClient, HttpResponse

async def update_headers(cookie: str) -> dict:
    headers: dict = {
        "Content-Type": "application/json",
        "Cookie": f"GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
    }

    client = HTTPClient()
    response = await client.post("https://catalog.roblox.com", headers=headers)

    if response.headers.get("x-csrf-token"):
        headers["X-CSRF-TOKEN"] = response.headers["x-csrf-token"]

    return headers

async def claim(group_id: int, headers: dict) -> tuple[HttpResponse, HttpResponse, float]:
    client = HTTPClient()
    start: float = time.time()

    join: HttpResponse = await client.post(f"https://groups.roblox.com/v1/groups/{group_id}/users", headers=headers)
    claim: HttpResponse = await client.post(f"https://groups.roblox.com/v1/groups/{group_id}/claim-ownership", headers=headers)

    end: float = time.time()

    return join, claim, round(end - start, 3)

async def leave(group_id: int, user_id: int, headers: dict) -> None:
    client = HTTPClient()
    await client.delete(f"https://groups.roblox.com/v1/groups/{group_id}/users/{user_id}", headers=headers)

async def shout(group_id: int, message: str, headers: dict) -> None:
    client = HTTPClient()
    await client.patch(f"https://groups.roblox.com/v1/groups/{group_id}/status", json={"message": message}, headers=headers)

async def account_switch(bot: commands.InteractionBot) -> tuple[str, int, dict]:
    client = HTTPClient()

    generate_text("Trying to get new account...", 2)

    with open("cookies.txt", "r") as file:
        cookies = file.read().splitlines()
        cookie: str = random.choice(cookies)

    headers: dict = await update_headers(cookie)
    response: HttpResponse = await client.get("https://users.roblox.com/v1/users/authenticated", headers=headers)
    json: dict = await response.json()

    if response.status_code == 200:
        generate_text("Valid account, checking for ratelimit..", 2)

        join_req, claim_req, time = await claim(1, headers)
        await leave(1, json["id"], headers)

        if join_req.status_code == 200:
            if claim_req.status_code == 403:
                generate_text("Account is working; Returning data!", 2)
                return json["name"], json["id"], cookie, headers
            else:
                if claim_req.status_code == 429:
                    generate_text("Ratelimited!", 2)
                else:
                    generate_text(f"Starnge status code on claim... {claim_req.status_code}", 2)
        else:
            if join_req.status_code == 409:
                generate_text("Account is fulled!", 2)
            elif join_req.status_code == 429:
                generate_text("Ratelimited!", 2)
            elif join_req.status_code == 403:
                generate_text("Account caught captcha!", 2)
            else:
                generate_text(f"Strange status code on join... {join_req.status_code}", 2)
    else:
        if response.status_code == 401:
            generate_text("Invalid cookie!", 2)

            cookies.remove(cookie)
        elif response.status_code == 429:
            generate_text("RATELIMITED!! RATELIMITED!! Sleep for 5 seconds.", 2)
            await asyncio.sleep(4)
    
    if not cookie in cookies:
        with open("cookies.txt", "w") as file:
            file.truncate(0)

            for cookie in cookies:
                file.write(cookie + "\n")
    
        file.close()
    
    await asyncio.sleep(1)
    return await account_switch(bot)