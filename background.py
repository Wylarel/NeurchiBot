import json
from asyncio import sleep
from datetime import date, datetime
import random

import files
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

driver: WebDriver
commentdriver: WebDriver


async def connect(email="neurchibotv2@gmail.com", password=open("PASSWORD.txt", "r").read()):
    print("Connecting . . .")

    global driver

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(options=options)
    driver.get("https://mbasic.facebook.com/")

    driver.find_element_by_name('email').send_keys(email)
    driver.find_element_by_name('pass').send_keys(password)
    driver.find_element_by_name('login').click()
    try:
        driver.find_element_by_name('xc_message')
        print("NeurchiBot connected")
    except NoSuchElementException:
        print("NeurchiBot couldn't connect to Facebook")
        await sleep(20)
        driver.quit()
        return

    await files.printstats()
    await analyzewall()


async def analyzewall():
    while True:
        posts = driver.find_elements_by_css_selector("#root div section article")
        for post in posts:
            header = post.find_element_by_css_selector("div header table").text
            if "neurchi" in header.lower():
                await analyzepost(post)
        await renewwall()
        await sleep(2)


async def renewwall():
    try:
        for button in driver.find_elements_by_css_selector("#root div a.z"):
            if "/stories.php?aftercursorr=" in button.get_attribute("href"):
                button.click()
                return
    except NoSuchElementException:
        await files.printstats()
        print("No more posts on wall, refreshing the page in 30 seconds")
        await sleep(30)
        driver.refresh()


async def analyzepost(post: WebElement):
    files.seen_posts += 1
    await files.savestats()
    commentslink = None
    for element in post.find_elements_by_css_selector("footer div a"):
        if "commentaire" in element.text:
            commentslink = element.get_attribute("href")

    if not commentslink:
        return

    await switchtab(1)
    driver.get(commentslink)

    files.analyzed_posts += 1
    for comment in driver.find_elements_by_xpath("//div[@id='m_story_permalink_view']/div/div/div/div/div"):
        try:
            commenttext = comment.find_element_by_xpath("div[1]")
            await analyzecomment(comment)
        except NoSuchElementException:
            pass

    await switchtab(0)


async def analyzecomment(comment: WebElement):
    files.analyzed_comments += 1

    commenttext = comment.find_element_by_xpath("div[1]")
    commenttexttext = str(commenttext.text)
    commentid = str(comment.find_element_by_xpath('..').get_attribute("id"))
    commentauthorid: str = comment.find_element_by_xpath("h3/a").get_attribute("href").replace("https://mbasic.facebook.com/", "")
    if "profile.php" in commentauthorid:
        commentauthorid = commentauthorid.replace("profile.php?id=", "").split("&")[0]
    else:
        commentauthorid = commentauthorid.split("?")[0]
    try:
        tag = commenttext.find_element_by_xpath("a")
    except NoSuchElementException:
        return

    href = tag.get_attribute("href")
    tagtext = tag.text
    if "mbasic.facebook.com/" in href and "/groups/" not in href and "/hashtag/" not in href and tagtext not in href:
        if len(commenttexttext) < len(tagtext) + 10:
            temphistory = await files.readhistory()
            try:
                if commentid in temphistory[commentauthorid]["warnings"]:
                    print("---- Already Seen Tag: \"" + tagtext.replace("\n", "") + "\"\n" + driver.current_url)
                    return
            except KeyError:
                pass
            answerlink = ""
            for element in comment.find_elements_by_xpath("div[last()]/a"):
                if "Répondre" in element.text:
                    answerlink = element.get_attribute("href")

            await switchtab(2)
            driver.get(href)
            if "profile picture" not in driver.find_element_by_css_selector("div#root").find_element_by_xpath("div/div/div[2]/div/div/div/a/img").get_attribute("alt"):
                print("---- Page Tag: \"" + tagtext.replace("\n", "") + "\"\n" + driver.current_url)
                await switchtab(1)
                return

            if answerlink != "":
                driver.get(answerlink)
                with open('messages.json', encoding="utf-8") as messages_json:
                    messages = json.load(messages_json, encoding="utf-8")
                    driver.find_element_by_css_selector("#composerInput").send_keys((messages["prefix"] + messages["wildtag"][random.randint(0, len(messages["wildtag"])-1)] + messages["suffix"]).replace("{}", commentid))
                    driver.find_element_by_xpath("//input[@type='submit'][@value='Répondre']").click()

            else:
                await switchtab(1)
                print("---- NO ANSWER BUTTON " + driver.current_url)
                return

            print("---- Potential Tag: \"" + tagtext.replace("\n", "") + "\"\n" + driver.current_url)
            warning_content = {
                commentid:
                    {"date": str(date.today()),
                     "comment": commenttexttext,
                     "publication": driver.current_url
                     }
            }

            await files.addtohistory("warnings", commentauthorid, warning_content)
            await switchtab(1)

    else:
        pass


async def switchtab(tab=0):
    try:
        driver.switch_to.window(driver.window_handles[tab])
    except IndexError:
        driver.execute_script('window.open("");')
        await switchtab(tab)



