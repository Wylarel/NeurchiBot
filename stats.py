import json
with open('stats.json') as json_file:
    data = json.load(json_file)
    seen_posts = data["seen_posts"]
    analyzed_posts = data["analyzed_posts"]
    analyzed_comments = data["analyzed_comments"]
    detected_comments = data["detected_comments"]


async def printstats():
    print("Seen Posts: " + str(seen_posts) + "\nAnalyzed Posts: " + str(analyzed_posts) + "\nAnalyzed Comments: " + str(analyzed_comments) + "\nDetected Comments: " + str(detected_comments))


async def savestats():
    stats = {"seen_posts": seen_posts,
             "analyzed_posts": analyzed_posts,
             "analyzed_comments": analyzed_comments,
             "detected_comments": detected_comments}

    with open('stats.json', 'w') as outfile:
        json.dump(stats, outfile)

    print("Saved stats:\n" + str(stats))
    pass
