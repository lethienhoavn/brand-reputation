import asyncio

async def test():
    python_exe = r"D:\H\TCB\brand-reputation\.venv\Scripts\python.exe"
    base_cwd = r"D:\H\TCB\brand-reputation\scrape"

    youtube_proc = await asyncio.create_subprocess_exec(
        python_exe,
        "scripts/youtube_scrape.py",
        cwd=base_cwd
    )

    tiktok_proc = await asyncio.create_subprocess_exec(
        python_exe,
        "scripts/tiktok_scrape.py",
        cwd=base_cwd
    )

    fb_proc = await asyncio.create_subprocess_exec(
        python_exe,
        "scripts/fb_scrape.py",
        cwd=base_cwd
    )

    await asyncio.gather(
        youtube_proc.wait(),
        tiktok_proc.wait(),
        fb_proc.wait()
    )

asyncio.run(test())
