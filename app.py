from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

driver: WebDriver
commentdriver: WebDriver

seen_posts = 0
analyzed_posts = 0
analyzed_comments = 0
detected_comments = 0


def connectaccount(email, password):
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
        sleep(20)
        driver.quit()
        return

    printstats()
    analyzewall()


def analyzewall():
    posts = driver.find_elements_by_css_selector("#root div section article")
    for post in posts:
        header = post.find_element_by_css_selector("div header table").text
        if "neurchi" in header.lower():
            analyzepost(post)
    renewwall()
    sleep(10)
    analyzewall()


def renewwall():
    try:
        for button in driver.find_elements_by_css_selector("#root div a.z"):
            if "/stories.php?aftercursorr=" in button.get_attribute("href"):
                button.click()
                return
    except NoSuchElementException:
        printstats()
        print("No more posts on wall, refreshing the page in 30 seconds")
        sleep(30)
        driver.refresh()


def analyzepost(post: WebElement):
    global seen_posts
    seen_posts += 1
    postname = post.find_element_by_css_selector("div header table").text
    commentslink = None
    for element in post.find_elements_by_css_selector("footer div a"):
        if "commentaire" in element.text:
            commentslink = element.get_attribute("href")

    if not commentslink:
        # DEBUG print("Couldn't see any comments on \"" + postname + "\"")
        return

    switchtab(1)
    driver.get(commentslink)

    # DEBUG print("-- Analyzing post \"" + postname + "\"")
    global analyzed_posts
    analyzed_posts += 1
    for comment in driver.find_elements_by_xpath("//div[@id='m_story_permalink_view']/div/div/div/div/div"):
        try:
            commenttext = comment.find_element_by_xpath("div[1]")
            analyzecomment(comment)
        except NoSuchElementException:
            # DEBUG print("HAHAHA")
            pass

    switchtab(0)


def analyzecomment(comment: WebElement):
    global analyzed_comments
    analyzed_comments += 1

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
            global detected_comments
            detected_comments += 1
            printstats()
    else:
        pass
        # DEBUG print("---- Accepted comment: \"" + commenttext.text.replace("\n", "") + "\"")


def switchtab(tab=0):
    try:
        driver.switch_to.window(driver.window_handles[tab])
        # print("Switch to tab " + str(tab))
    except IndexError:
        # DOESNT WORK driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
        # THAT NEITHER ActionChains(driver).key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
        driver.execute_script('window.open("");')
        # print("Opening a new tab")
        switchtab(tab)


def printstats():
    print("Seen Posts: " + str(seen_posts) + "\nAnalyzed Posts: " + str(analyzed_posts) + "\nAnalyzed Comments: " + str(analyzed_comments) + "\nDetected Comments: " + str(detected_comments))


connectaccount("neurchibotv2@gmail.com", open("PASSWORD.txt", "r").read())
