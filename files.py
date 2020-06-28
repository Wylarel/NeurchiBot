import json

with open('stats.json') as stats_json:
    currentstats = json.load(stats_json)
    seen_posts = currentstats["seen_posts"]
    analyzed_posts = currentstats["analyzed_posts"]
    analyzed_comments = currentstats["analyzed_comments"]


async def printstats():
    print("Seen Posts: " + str(seen_posts) + "\nAnalyzed Posts: " + str(analyzed_posts) + "\nAnalyzed Comments: " + str(analyzed_comments))


async def savestats():
    new_stats = {"seen_posts": seen_posts,
                 "analyzed_posts": analyzed_posts,
                 "analyzed_comments": analyzed_comments}

    with open('stats.json', 'w') as outfile:
        json.dump(new_stats, outfile)

    print(str(new_stats))
    pass


async def readhistory():
    with open('history.json') as history_json:
        history = json.load(history_json)
    return history


async def addtohistory(category, key, value: dict):
    currenthistory = await readhistory()
    currenthistory[category][key] = value
    with open('history.json', 'w') as outfile:
        json.dump(currenthistory, outfile)
