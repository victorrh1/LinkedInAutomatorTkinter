from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from time import sleep
import logging
import random

logging.basicConfig(filename='erros.log', filemode='a', level=logging.ERROR)

LINKEDIN_EMAIL = "Digite o usuário"
LINKEDIN_SENHA = "Digite a senha"

def conectar_com_pessoas_na_pagina_atual(driver, wait, window, conexoes_enviadas=0):
    limite_diario = 20
    try:
        window.write_output('Buscando por botões de conectar na página atual\n')
        sleep(random.randint(2, 5))
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        
        botoes_conectar = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//button[contains(@aria-label, 'Convidar')]") ))
        window.write_output('Botões de conectar encontrados\n')
        
        for botao_conectar in botoes_conectar:
            if conexoes_enviadas < limite_diario:
                sleep(random.randint(2, 5))
                driver.execute_script("arguments[0].click()", botao_conectar)
                window.write_output('Clicado no botão conectar\n')
                sleep(random.randint(2, 5))
                
                elemento_com_nome_do_contato = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='flex-1']/strong")))
                nome = elemento_com_nome_do_contato.text
                
                botao_enviar_sem_nota = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Enviar sem nota']")))
                window.write_output(f'Enviando convite sem nota para {nome}\n')
                sleep(random.randint(2, 5))
                botao_enviar_sem_nota.click()
                window.write_output(f'{nome} acaba de ser convidado!\n')
                conexoes_enviadas += 1
                window.write_output(f'Enviado {conexoes_enviadas} de {limite_diario} conexões diárias\n')
                sleep(random.randint(2, 5))
            else:
                window.write_output('Limite diário atingido. Aguardando 24h...\n')
                sleep(86400)
                return conexoes_enviadas
    except Exception as error:
        window.write_output('Erro ao tentar conectar com pessoas\n')
        logging.error(error)
    
    return conexoes_enviadas

def passar_para_proxima_pagina(driver, wait, window):
    try:
        sleep(2)
        botao_proxima_pagina = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Avançar')]")))
        driver.execute_script("arguments[0].click()", botao_proxima_pagina)
        window.write_output('Indo para a próxima página...\n')
        sleep(5)
        return True
    except Exception:
        window.write_output('Nenhuma próxima página encontrada ou erro ao avançar.\n')
        return False

def fazer_login(driver, wait):
    driver.get("https://www.linkedin.com/login")
    sleep(3)
    
    campo_email = wait.until(EC.presence_of_element_located((By.ID, "username")))
    campo_email.send_keys(LINKEDIN_EMAIL)
    
    campo_senha = wait.until(EC.presence_of_element_located((By.ID, "password")))
    campo_senha.send_keys(LINKEDIN_SENHA)
    
    botao_login = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    botao_login.click()
    sleep(5)

def iniciar_driver():
    chrome_options = Options()
    arguments = ['--lang=pt-BR', '--window-size=1920,1080']
    for argument in arguments:
        chrome_options.add_argument(argument)
    
    brave_path = "/usr/bin/brave-browser"
    chrome_options.binary_location = brave_path
    driver = webdriver.Chrome(options=chrome_options)
    
    wait = WebDriverWait(driver, 10, poll_frequency=1, ignored_exceptions=[
        NoSuchElementException,
        ElementNotVisibleException,
        ElementNotSelectableException
    ])
    
    return driver, wait

def iniciar_automacao(palavra_chave, window):
    driver, wait = iniciar_driver()
    fazer_login(driver, wait)
    link_pesquisa_por_palavra_chave = f'https://www.linkedin.com/search/results/people/?keywords={palavra_chave}&origin=SWITCH_SEARCH_VERTICAL&sid=oJd'
    driver.get(link_pesquisa_por_palavra_chave)
    sleep(5)
    
    conexoes_enviadas = 0
    while conexoes_enviadas < 20:
        conexoes_enviadas = conectar_com_pessoas_na_pagina_atual(driver, wait, window, conexoes_enviadas)
        if not passar_para_proxima_pagina(driver, wait, window):
            break
    
    window.write_output('Automação concluída!')
