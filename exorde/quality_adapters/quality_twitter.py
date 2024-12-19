async def extract_text(page):
    # Extract text from the tweetText div if available
    selector = 'div[data-testid="tweetText"]'
    await page.locator(selector).wait_for(state="visible")
    tweet_text = await page.locator(selector).text_content()
    return tweet_text

async def processing_interface(app, args: dict) -> dict:
    page, free = await app["pfetch"](args['url'])
    content = await extract_text(page)
    await free()
    return {
        "adapter": content
    }
