import asyncio

async def test_ffmpeg():
    proc = await asyncio.create_subprocess_exec(
        'ffmpeg', '-version',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    print(out.decode())

asyncio.run(test_ffmpeg())