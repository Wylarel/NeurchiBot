import asyncio
import json
import background


async def savestats():
    stats = {"seen_posts": background.seen_posts,
             "analyzed_posts": background.analyzed_posts,
             "analyzed_comments": background.analyzed_comments,
             "detected_comments": background.detected_comments}

    with open('stats.json', 'w') as outfile:
        json.dump(stats, outfile)

    print("Saved stats:\n" + str(stats))
    pass


asyncio.run(background.connect())
