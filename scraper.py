import json
from playwright.sync_api import sync_playwright

url = "https://ekantipur.com"
with sync_playwright() as p:
    try:
        # launch browser and tab
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # launch ekantipur site
        page.goto(url)

        #********** task 1************
        # clicking on button with text मनोरञ्जन on navbar
        page.click(".bottom-nav .bottom-nav-inside-wrapper .bottom-nav-wrap a:has-text('मनोरञ्जन')")
        # wait until the page loads (no network activity)
        page.wait_for_load_state("networkidle")

        # triggering lazy load as images were not being fetched, scrolling the page
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)

        # fetching category name from top of the page(navbar)
        category_name = page.query_selector(".category-name p a").inner_text().strip()
        # print(category_name)
        # Fetching the first five articles from the page with the selector for entertainment news with classname "category"
        articles = page.query_selector_all(".category-wrapper .category")[:5]
        top_articles = []
        # using for loop to iterate between the elements in each article to extract the respective data
        for article in articles:
            title_element = article.query_selector("h2")
            author_element = article.query_selector(".author-name")
            img_element = article.query_selector(".category-image a figure img")
            # print(img_element)
            # adding to top_articles
            top_articles.append(
                {
                    "title": title_element.text_content(),
                    "image_url": img_element.get_attribute("src"),
                    "category": category_name,
                    "author": (
                        author_element.text_content().strip() if author_element else None
                    ),
                }
            )

        # **********task 2*************
        # redirect to home
        page.click(".logo a")
        # click cartoon
        page.click("a:has-text('कार्टुन')")
        page.wait_for_load_state("networkidle")
        #due to lazy loading the url was not being fetched in few cases so used timeout to wait 1 sec before proceeding
        page.wait_for_timeout(1000)
        # Selecting the first cartoon element using the appropriate selector
        cartoon_element = page.locator(".cartoon-wrapper").first
        #using locator to select img selector 
        img = cartoon_element.locator(".cartoon-image figure a img")

        # Safe defaults in case selectors don't match.
        cartoon_image = None
        text = ""
        cartoon_title = None
        cartoon_author = None

        # Retrieving image url
        if img.count():
            cartoon_image = img.get_attribute("src")

        # Selecting the description from the cartoon element
        description_element = cartoon_element.locator(".cartoon-description p").first
        # Retrieving the description text
        if description_element.count():
            text = description_element.inner_text().strip()

        # Separating text and author since the description had both author and title merged
        if "-" in text:
            # Split into two parts only (title - author), in case title contains '-'
            parts = text.split("-", 1)
            cartoon_title = parts[0].strip()
            cartoon_author = parts[1].strip()
        else:
            cartoon_title = text if text else None
            cartoon_author = None

        cartoon_of_the_day = {
            "title": cartoon_title,
            "image_url": cartoon_image,
            "author": cartoon_author,
        }

        result = {
            "entertainment_news": top_articles,
            "cartoon_of_the_day": cartoon_of_the_day,
        }
    finally:
        browser.close()

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
