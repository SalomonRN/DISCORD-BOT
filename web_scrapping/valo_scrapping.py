from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver import EdgeOptions
from selenium.webdriver.edge.service import Service
from selenium.webdriver import Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
# from asyncio import run

async def search(url):
    print(url)
    if requests.get(url).status_code != 200:
        return "Algo salió mal en la peticion :/"
    
    service = Service(EdgeChromiumDriverManager().install())
    options = EdgeOptions()

    # options.add_argument("window-size=1920,1080") 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    options.add_argument("--headless")
    options.add_argument("--headless=new")  # Usa el nuevo modo headless (más estable)
    options.add_argument("--window-size=1920,1080")  # Define un tamaño de ventana
    options.add_argument("--disable-gpu")  # Evita problemas en algunos sistemas
    options.add_argument("--disable-gpu")

    options.add_argument("--no-sandbox")  # Útil en algunos entornos
    options.add_argument("--disable-dev-shm-usage")  # Evita problemas en contenedores


    driver = Edge(service=service, options=options)
    wait = WebDriverWait(driver, 20)
    driver.get(url)
    
    PUBLIC = "/html/body/div[1]/div[3]/div[2]/div[2]/h1"
    elementos = driver.find_elements(By.XPATH, PUBLIC)
    if elementos:
        reason = elementos[0].text
        driver.quit()
        return reason
    
    USER_NAME = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "player-name"))).text

    UPDATE = "/html/body/div[1]/div[3]/div[1]/div[2]/header/div[1]/div/div[2]/div[3]/button"
    button = wait.until(EC.presence_of_element_located((By.XPATH, UPDATE)))
    button.click()

    while button.text != "Actualizado":
        button.click()
        time.sleep(1)

    # what = wait.until(lambda driver: driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[5]/div/main/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[2]/span"))
    # print(what)
    # print(what.text)

    RANGE_PATH = "/html/body/div[1]/div[3]/div[5]/div/aside/div[1]/div[2]/div/div[2]/strong"
    range = wait.until(EC.presence_of_element_located((By.XPATH, RANGE_PATH))).text

    KDA_PATH = "/html/body/div[1]/div[3]/div[5]/div/aside/div[2]/div[2]/div[1]/ul/li[3]/strong/span"
    kda = wait.until(EC.presence_of_element_located((By.XPATH, KDA_PATH))).text

    HEAD_SHOT_PATH = "/html/body/div[1]/div[3]/div[5]/div/aside/div[2]/div[2]/div[2]/ul/li[1]/div/strong"
    head_shot = wait.until(EC.presence_of_element_located((By.XPATH, HEAD_SHOT_PATH))).text

    BODY_SHOT_PATH = "/html/body/div[1]/div[3]/div[5]/div/aside/div[2]/div[2]/div[2]/ul/li[3]/div/strong"
    body_shot = wait.until(EC.presence_of_element_located((By.XPATH, BODY_SHOT_PATH))).text

    LEGS_SHOT_PATH = "/html/body/div[1]/div[3]/div[5]/div/aside/div[2]/div[2]/div[2]/ul/li[5]/div/strong"
    legs_shot = wait.until(EC.presence_of_element_located((By.XPATH, LEGS_SHOT_PATH))).text

    DAMAGE_PER_ROUND_PATH = "/html/body/div[1]/div[3]/div[5]/div/aside/div[2]/div[2]/div[1]/ul/li[1]/strong"
    damage_round = wait.until(EC.presence_of_element_located((By.XPATH, DAMAGE_PER_ROUND_PATH))).text

    WIN_RATE_PATH = "/html/body/div[1]/div[3]/div[5]/div/main/div/div[1]/div[2]/div/div[1]/div[2]/div[1]/div[2]/span"
    win_rate = wait.until(EC.presence_of_element_located((By.XPATH, WIN_RATE_PATH))).text

    user_data = {
        "user_name": " ".join(USER_NAME.splitlines()),
        "range": range,
        "kda": kda,
        "head_shot": head_shot,
        "body_shot": body_shot,
        "legs_shot": legs_shot,
        "damage_round": damage_round,
        "win_rate": win_rate
    }

    TABLE = "/html/body/div[1]/div[3]/div[5]/div/aside/div[3]/table/tbody"
    roles = wait.until(EC.presence_of_element_located((By.XPATH, TABLE)))
    TAGS = roles.find_elements(By.TAG_NAME, "tr")
    roles = []
    for tag in TAGS:
        
        element = tag.find_elements(By.TAG_NAME, "td")
        rol_name = element[1].find_element(By.CLASS_NAME, "role-name").text
        pick_rate = element[1].find_elements(By.TAG_NAME, "span")[1].text   
        kda_ = tag.find_elements(By.TAG_NAME, "strong")[0].text
        winrate = element[3].find_elements(By.TAG_NAME, "span")[0].text 

        rol = {
            "rol_name": rol_name,
            "pick_rate": pick_rate,
            "kda": kda_,
            "winrate": winrate
        }
        roles.append(rol)
        

    driver.quit()
    return [user_data, roles]

if __name__ == "__main__":
    # user_data = search("https://valorant.op.gg/profile/PortiSeriaBatman-beibi")
    user_data = search("https://valorant.op.gg/profile/%E7%A5%9E%20Willy-1111?statQueueId=competitive")
    print(user_data)

# print("---------------------------------------------------------------------------")
# print(" ".join(USER_NAME.splitlines()))
# print(f"Range: {range}")
# print(f"KDA: {kda}")
# print(f"Head Shot: {head_shot}")
# print(f"Body Shot: {body_shot}")
# print(f"Legs Shot: {legs_shot}")
# print(f"Damage per round: {damage_round}")
# print(f"WinRate {win_rate}")
# print("--------------------------------ROLES--------------------------------------")
# for rol in roles:
#     print(f"Rol: {rol['rol_name']}")
#     print(f"Pick Rate: {rol['pick_rate']}")
#     print(f"KDA: {rol['kda']}")
#     print(f"WinRate: {rol['winrate']}")
#     print(" ")
# print("---------------------------------------------------------------------------")

# /html/body/div[1]/div[3]/div[2]/div[2]/h1
# /html/body/div[1]/div[3]/div[2]/div[2]/h1 -> NO EXISTE

