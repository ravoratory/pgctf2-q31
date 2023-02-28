import asyncio
from pyppeteer import launch
import sys

async def angel(stat_id):
    browser = await launch(
        headless=True,
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False,
        args=[]
    )
    page = await browser.newPage()
    await page.setViewport({"width": 800, "height": 1000})
    """
        set cookie for answer (secret!)
    """
    await page.goto(f"https://pgctf.tkm.dev/Q31/report/{stat_id}")
    await browser.close()

if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        asyncio.new_event_loop().run_until_complete(angel(args[1]))