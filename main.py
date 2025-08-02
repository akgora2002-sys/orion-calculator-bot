from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def extract_marks_from_html(html_url):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(html_url)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        correct = wrong = 0
        questions = soup.find_all("table", class_="menu-tbl")

        for q in questions:
            selected = q.find("td", class_="bordertbl selectedOption")
            correct_ans = q.find("td", class_="rightAnsOption")

            if selected and correct_ans:
                if selected.text.strip() == correct_ans.text.strip():
                    correct += 1
                else:
                    wrong += 1

        attempted = correct + wrong
        unattempted = 100 - attempted
        score = correct * 2 - wrong * 0.5
        accuracy = round((correct / attempted) * 100, 2) if attempted > 0 else 0

        return {
            "correct": correct,
            "wrong": wrong,
            "unattempted": unattempted,
            "score": score,
            "accuracy": accuracy
        }

    except Exception as e:
        return {"error": str(e)}
