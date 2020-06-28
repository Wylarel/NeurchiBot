from asyncio import sleep
import stats
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

    await stats.printstats()
    await analyzewall()


async def analyzewall():
    posts = driver.find_elements_by_css_selector("#root div section article")
    for post in posts:
        header = post.find_element_by_css_selector("div header table").text
        if "neurchi" in header.lower():
            await analyzepost(post)
    await renewwall()
    await sleep(2)
    await analyzewall()


async def renewwall():
    try:
        for button in driver.find_elements_by_css_selector("#root div a.z"):
            if "/stories.php?aftercursorr=" in button.get_attribute("href"):
                button.click()
                return
    except NoSuchElementException:
        await stats.printstats()
        print("No more posts on wall, refreshing the page in 30 seconds")
        await sleep(30)
        driver.refresh()


async def analyzepost(post: WebElement):
    stats.seen_posts += 1
    postname = post.find_element_by_css_selector("div header table").text
    commentslink = None
    for element in post.find_elements_by_css_selector("footer div a"):
        if "commentaire" in element.text:
            commentslink = element.get_attribute("href")

    if not commentslink:
        # DEBUG print("Couldn't see any comments on \"" + postname + "\"")
        return

    await switchtab(1)
    driver.get(commentslink)

    # DEBUG print("-- Analyzing post \"" + postname + "\"")
    stats.analyzed_posts += 1
    for comment in driver.find_elements_by_xpath("//div[@id='m_story_permalink_view']/div/div/div/div/div"):
        try:
            commenttext = comment.find_element_by_xpath("div[1]")
            await analyzecomment(comment)
        except NoSuchElementException:
            # DEBUG print("HAHAHA")
            pass

    await switchtab(0)


async def analyzecomment(comment: WebElement):
    stats.analyzed_comments += 1

    # DEBUG print(driver.current_url)
    commenttext = comment.find_element_by_xpath("div[1]")
    # DEBUG print("<<<<!!! " + commenttext.text + "!!!>>>>")
    try:
        tag = commenttext.find_element_by_xpath("a")
    except NoSuchElementException:
        # DEBUG print("---- Accepted comment: \"" + commenttext.text.replace("\n", "") + "\"")
        return

    if "mbasic.facebook.com/" in tag.get_attribute("href") and "/groups/" not in tag.get_attribute("href") and "/hashtag/" not in tag.get_attribute("href") and tag.text not in tag.get_attribute("href"):
        if len(commenttext.text) < len(tag.text) + 20:
            print("---- Potential Tag: \"" + tag.text.replace("\n", "") + "\"\n" + driver.current_url)
            await alertmember(comment, reason="wildtag")
            stats.detected_comments += 1
            await stats.printstats()
    else:
        pass
        # DEBUG print("---- Accepted comment: \"" + commenttext.text.replace("\n", "") + "\"")


async def switchtab(tab=0):
    try:
        driver.switch_to.window(driver.window_handles[tab])
        # print("Switch to tab " + str(tab))
    except IndexError:
        # DOESNT WORK driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
        # THAT NEITHER ActionChains(driver).key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
        driver.execute_script('window.open("");')
        # print("Opening a new tab")
        await switchtab(tab)


async def alertmember(comment, reason="wildtag"):
    pass


