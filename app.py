from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import streamlit as st

st.set_page_config(page_title='Amazon Webscraper', 
                   page_icon='✂️', 
                   layout="centered")

def aceptar_cookies():
    try:
        cookies = driver.find_element(By.XPATH, '//*[@id="sp-cc-accept"]')
        time.sleep(1)
        cookies.click()
        print("Cookies aceptadas.")
    except NoSuchElementException:
        print("No hay cookies")
def buscadores(busqueda):
    try:
        buscador = driver.find_element(By.XPATH, '//*[@id="twotabsearchtextbox"]')
        buscador.send_keys(busqueda)
        time.sleep(3)
        buscador.send_keys(Keys.ENTER)
    except NoSuchElementException:
        print('No hay buscador numero 1, probando buscador 2:')
        try:
            buscador = driver.find_element(By.XPATH, '//*[@id="nav-bb-search"]')
            buscador.send_keys(busqueda)
            time.sleep(3)
            buscador.send_keys(Keys.ENTER)
            time.sleep(3)
            aceptar_cookies()
        except NoSuchElementException:
            print('No hay buscadores')   

st.title("Web Scraping de Amazon")

st.sidebar.subheader("Filtro de Precio")
precio_min, precio_max = st.sidebar.slider("Selecciona rango de precio", 0, 500, (0, 500))
busqueda = st.text_input("Introduce lo que quieres buscar:", "Ositos de peluche")

if st.button("Buscar"):
    st.write('Obteniendo datos, espere 15 segundos:')
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"} 
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    opts.add_argument(f"user-agent={headers}")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(
    options=opts,
    service=service,)
    url = "https://www.amazon.es/"
    driver.get(url)

    aceptar_cookies()
    buscadores(busqueda)
    time.sleep(3)

    soup1 = bs(driver.page_source,"lxml")
    productos = soup1.select('div.s-result-item')
    print(productos)
    resultados = []

    for producto in productos:
        producto_info = {}

        titulo_element = producto.select_one('span.a-size-base-plus.a-color-base.a-text-normal')
        producto_info['titulo'] = titulo_element.get_text(strip=True) if titulo_element else False
        
        precio_element = producto.select_one('span.a-price span.a-offscreen')
        producto_info['precio'] = precio_element.get_text(strip=True) if precio_element else '0'
        
        fecha_entrega_element = producto.select_one('span.a-color-base.a-text-bold')
        producto_info['fecha_entrega'] = fecha_entrega_element.get_text(strip=True) if fecha_entrega_element else 'No hay fecha de entrega'
        
        es_prime_element = producto.select_one('i.a-icon.a-icon-prime.a-icon-medium')
        producto_info['es_prime'] = "Prime" in es_prime_element['aria-label'] if es_prime_element else False

        imagen_element = producto.select_one('img.s-image')
        producto_info['imagen_url'] = imagen_element['src'] if imagen_element else 'No hay URL de imagen'

        enlace_element = producto.find('a', class_='a-link-normal')
        producto_info['enlace'] = f"https://www.amazon.es{enlace_element['href']}" if enlace_element else 'No hay enlace'

        precio = float(producto_info['precio'].replace('€', '').replace(',', '.'))
        if precio_min <= precio <= precio_max and producto_info['titulo']:
            producto_info['precio'] = producto_info['precio'].replace('\xa0', ' ')
            resultados.append(producto_info)
        print('Resultados obtenidos, total: ',len(resultados))

    driver.quit()

    for i, resultado in enumerate(resultados, start=1):
        col1,col2,col3 = st.columns(3)
        with col2:
            st.image(resultado['imagen_url'])
        st.write(resultado['titulo'])
        st.write("Precio:", resultado['precio'])
        st.write("Fecha de entrega:", resultado['fecha_entrega'])
        st.write("Es Prime:", resultado['es_prime'])
        link = resultado['enlace']
        st.markdown(
            f'<a href="{link}" style="display: inline-block; padding: 12px 20px; background-color: #4CAF50; color: white; text-align: center; text-decoration: none; font-size: 16px; border-radius: 4px;">Comprar</a>',
            unsafe_allow_html=True)
        
