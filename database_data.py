import sqlite3
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# XPaths fixos para os dados da página
xpath_health_1 = "//*[@id='app']/div[5]/div/div[3]/div[2]/div[3]/div[1]/div[2]/div[1]/div"
xpath_health_2 = "//*[@id='app']/div[5]/div/div[3]/div[2]/div[3]/div[1]/div[2]/div[2]/div"
xpath_health_3 = "//*[@id='app']/div[5]/div/div[3]/div[2]/div[3]/div[1]/div[2]/div[3]/div"

xpath_speed_1 = "//*[@id='app']/div[5]/div/div[3]/div[2]/div[3]/div[2]/div[2]/div[1]/div"
xpath_speed_2 = "//*[@id='app']/div[5]/div/div[3]/div[2]/div[3]/div[2]/div[2]/div[2]/div"
xpath_speed_3 = "//*[@id='app']/div[5]/div/div[3]/div[2]/div[3]/div[2]/div[2]/div[3]/div"

xpath_side = "//*[@id='app']/div[5]/div/div[3]/div[2]/div[1]/div[1]/div[2]/span"
xpath_squad = "//*[@id='app']/div[5]/div/div[3]/div[2]/div[1]/div[2]/div[3]/span"
xpath_specialities = "//*[@id='app']/div[5]/div/div[3]/div[2]/div[2]/div"

xpath_primary_weapon_count = "//*[@id='app']/div[5]/div/div[5]/div[1]/div/div"
xpath_secundary_weapon_count = "//*[@id='app']/div[5]/div/div[5]/div[2]/div/div"
xpath_gadget_count = "//*[@id='app']/div[5]/div/div[5]/div[3]/div/div"

xpath_unique_name = "//*[@id='app']/div[5]/div/div[5]/div[4]/div/div/p[1]"
xpath_unique_image = "//*[@id='app']/div[5]/div/div[5]/div[4]/div/div/div/img"

# Funções de inicialização e espera
def init_driver(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")

    # # Desabilitar imagens, CSS e plugins via preferências
    # prefs = {
    #     "profile.managed_default_content_settings.images": 2,
    #     "profile.managed_default_content_settings.stylesheets": 2,
    #     "profile.managed_default_content_settings.plugins": 2
    # }
    # chrome_options.add_experimental_option("prefs", prefs)

    # Mantém a opção para desativar imagens via blink-settings (opcional)
    # chrome_options.add_argument("--blink-settings=imagesEnabled=false")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(20)  # Ajuste do timeout
    driver.maximize_window()
    return driver

def wait_for_element(driver, xpath, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

def get_text(driver, xpath, timeout=10):
    try:
        return wait_for_element(driver, xpath, timeout).text
    except Exception:
        return ""

# Funções para extrair dados numéricos (health e speed)
def get_health(driver):
    health_paths = [xpath_health_1, xpath_health_2, xpath_health_3]
    health = 0
    for path in health_paths:
        try:
            class_name = driver.find_element(By.XPATH, path).get_attribute("class")
            if "is-active" in class_name:
                health += 1
        except Exception:
            pass
    return health

def get_speed(driver):
    speed_paths = [xpath_speed_1, xpath_speed_2, xpath_speed_3]
    speed = 0
    for path in speed_paths:
        try:
            class_name = driver.find_element(By.XPATH, path).get_attribute("class")
            if "is-active" in class_name:
                speed += 1
        except Exception:
            pass
    return speed

# Funções auxiliares para extrair dados de armas
def parse_weapon(weapon_element):
    ps = weapon_element.find_elements(By.TAG_NAME, "p")
    nome = ps[0].text if len(ps) >= 1 else ""
    tipo = ps[-1].text if len(ps) >= 2 else ""
    try:
        img = weapon_element.find_element(By.TAG_NAME, "img").get_attribute("src")
    except Exception:
        img = ""
    return {"nome": nome, "tipo": tipo, "img": img}

def parse_gadget(gadget_element):
    try:
        nome = gadget_element.find_element(By.TAG_NAME, "p").text
    except Exception:
        nome = ""
    try:
        img = gadget_element.find_element(By.TAG_NAME, "img").get_attribute("src")
    except Exception:
        img = ""
    return {"nome": nome, "img": img}

def parse_unique_ability(driver, xpath = None):
    if xpath == None:
        try:
            nome = driver.find_element(By.XPATH, xpath_unique_name).text
        except Exception:
            nome = ""
        try:
            img = driver.find_element(By.XPATH, xpath_unique_image).get_attribute("src")
        except Exception:
            img = ""
        return [{"nome": nome, "img": img}]
    else:
        try:
            nome = driver.find_element(By.XPATH, '//*[@id="app"]/div[5]/div/div[5]/div[3]/div/div/p[1]').text
        except Exception:
            nome = ""
        try:
            img = driver.find_element(By.XPATH, '//*[@id="app"]/div[5]/div/div[5]/div[3]/div/div/div/img').get_attribute("src")
        except Exception:
            img = ""
        return [{"nome": nome, "img": img}]


# Criação do banco de dados e tabela
def create_db():
    conn = sqlite3.connect('operators.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS operators;")
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS operators (
                name TEXT PRIMARY KEY,
                images_background TEXT,
                images_logo TEXT,
                link TEXT,
                side TEXT,
                squad TEXT,
                specialities TEXT,
                health INTEGER,
                speed INTEGER,
                primary_weapon TEXT,
                secundary_weapon TEXT,
                gadget TEXT,
                unique_ability TEXT
            )
        ''')
    conn.commit()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                password TEXT
            )
        ''')
    conn.commit()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                operator_name TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (operator_name) REFERENCES operators(name)
            )
        ''')
    conn.commit()
    return conn, cursor

def insert_operator(cursor, operator):
    cursor.execute('''
        INSERT INTO operators (
            name, images_background, images_logo, link, side, squad, specialities, 
            health, speed, primary_weapon, secundary_weapon, gadget, unique_ability
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        operator['name'],
        operator['images_background'],
        operator['images_logo'],
        operator['link'],
        operator['side'],
        operator['squad'],
        ', '.join(operator['specialities']),
        operator['health'],
        operator['speed'],
        json.dumps(operator["primary_weapon"]),
        json.dumps(operator["secundary_weapon"]),
        json.dumps(operator["gadget"]),
        json.dumps(operator["unique_ability"])
    ))


def main_database_data(callback=None):
    driver = init_driver(headless=True)
    url = "https://www.ubisoft.com/en-us/game/rainbow-six/siege/game-info/operators"
    driver.get(url)
    wait_for_element(driver, "/html/body/div[1]/div[5]/div[4]/div[4]")

    operator_cards = driver.find_elements(By.CSS_SELECTOR, "a.oplist__card")
    operator_links = [card.get_attribute("href") for card in operator_cards]

    operators_data = []
    for card, link in zip(operator_cards, operator_links):
        name = card.find_element(By.TAG_NAME, "span").text if card.find_elements(By.TAG_NAME, "span") else ""
        images = [img.get_attribute("src") for img in card.find_elements(By.TAG_NAME, "img")]
        operators_data.append({
            "name": name,
            "images_background": images[0],
            "images_logo": images[1],
            "link": link,
        })

    conn, cursor = create_db()

    total = len(operators_data)
    for idx, operator in enumerate(operators_data):
        print(f"A processar: {idx + 1}/{total} ({operator['link']})")
        driver.get(operator["link"])

        # Extração dos demais dados...
        side = get_text(driver, xpath_side)
        squad = get_text(driver, xpath_squad)
        specialities_text = get_text(driver, xpath_specialities)
        specialities_list = [s.strip() for s in specialities_text.replace("SPECIALTIES", "").split(",") if s.strip()]
        health = get_health(driver)
        speed = get_speed(driver)

        # Processamento das armas, gadgets e habilidade única
        primary_elements = driver.find_elements(By.XPATH, xpath_primary_weapon_count)
        primary_weapon = [parse_weapon(el) for el in primary_elements]

        secundary_heading = driver.find_element(By.XPATH, '//*[@id="app"]/div[5]/div/div[5]/div[2]/h2/span').text

        if secundary_heading == "SECONDARY WEAPON":
            secundary_elements = driver.find_elements(By.XPATH, xpath_secundary_weapon_count)
            secundary_weapon = [parse_weapon(el) for el in secundary_elements]
            gadget_elements = driver.find_elements(By.XPATH, xpath_gadget_count)
            gadget = [parse_gadget(el) for el in gadget_elements]
            unique_ability = parse_unique_ability(driver)
        else:
            secundary_weapon = []
            gadget_elements = driver.find_elements(By.XPATH, '//*[@id="app"]/div[5]/div/div[5]/div[2]/div/div')
            gadget = [parse_gadget(el) for el in gadget_elements]
            unique_ability = parse_unique_ability(driver, xpath=True)

        operator.update({
            "side": side,
            "squad": squad,
            "specialities": specialities_list,
            "health": health,
            "speed": speed,
            "primary_weapon": primary_weapon,
            "secundary_weapon": secundary_weapon,
            "gadget": gadget,
            "unique_ability": unique_ability
        })

        insert_operator(cursor, operator)

        # Atualiza o progresso via callback, se fornecido
        if callback:
            callback(idx + 1, total)

    conn.commit()
    driver.quit()
    conn.close()

    print(f"Total de operadores processados e armazenados no banco de dados: {total}")