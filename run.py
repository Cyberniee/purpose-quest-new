import uvicorn
import asyncio
import sys


### DEV ###
### IMportant: when publishing the app, this can give implementation error ###

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

loop = asyncio.get_event_loop()
print(f"🚦 Asyncio event loop policy in use: {type(loop)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True, port=8000)
