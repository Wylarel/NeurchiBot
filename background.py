from asyncio import sleep
from datetime import date, datetime

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
    commentid = str(comment.find_element_by_xpath('..').get_attribute("id"))
    commentauthorid: str = comment.find_element_by_xpath("h3/a").get_attribute("href").replace("https://mbasic.facebook.com/", "")
    if "profile.php" in commentauthorid:
        commentauthorid = commentauthorid.replace("profile.php?id=", "").split("?")[0]
    else:
        commentauthorid = commentauthorid.split("?")[0]
    try:
        tag = commenttext.find_element_by_xpath("a")
    except NoSuchElementException:
        return

    if "mbasic.facebook.com/" in tag.get_attribute("href") and "/groups/" not in tag.get_attribute("href") and "/hashtag/" not in tag.get_attribute("href") and tag.text not in tag.get_attribute("href"):
        if len(commenttext.text) < len(tag.text) + 10:
            temphistory = await files.readhistory()
            try:
                if commentid in temphistory[commentauthorid]["warnings"]:
                    print("---- Already Seen Tag: \"" + tag.text.replace("\n", "") + "\"\n" + driver.current_url)
                    return
            except KeyError:
                pass
            print("---- Potential Tag: \"" + tag.text.replace("\n", "") + "\"\n" + driver.current_url)
            warning_content = {
                commentid:
                    {"date": str(date.today()),
                     "comment": commenttext.text,
                     "publication": driver.current_url
                     }
            }
            await files.addtohistory("warnings", commentauthorid, warning_content)
    else:
        pass


async def switchtab(tab=0):
    try:
        driver.switch_to.window(driver.window_handles[tab])
    except IndexError:
        driver.execute_script('window.open("");')
        await switchtab(tab)



