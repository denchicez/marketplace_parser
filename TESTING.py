import requests
import time
import json
import csv
from bs4 import BeautifulSoup
products = [] 
def get_html(url, params=None):
    r = requests.get(url, params=params)
    return r.text
def NameCheck(string,code1,code2): #Можно ли расшифровать stirng с помощью code1 и code2
    letters = ['“','…','”','<','>','«','»',chr(9),chr(13),chr(10),'(',')','|',':',' ',chr(34),'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','а','a','б','в','г','д','е','ё','ж','з','и','й','к','л','м','н','о','п','р','с','т','у','ф','х','ц','ч','ш','щ','ъ','ы','ь','э','ю','я','-','+',',','.','/','[',']','1','2','3','4','5','6','7','8','9','0','#','№','-','—','_','=','}','{','+','!','?','#']
    try:
        string=string.encode(code1).decode(code2) #декодируем если можно
    except:
        return False # выходим
    try:
        string=string.lower() # пытаемся сделать нижний регистр
    except:
        string=string
    for delite_symbole in letters: #удаляем символы
        string=string.replace(delite_symbole,'')
    if(len(string)>2): #Если длина остатков больше 2 выходим
        return False
    else:
        return True #все верно
def decode(string): #декодируем строку 
    all_code = ['UTF-8','cp1251','latin1'] #возможные виды кодировок
    chk=0
    for code_in_all1 in all_code:
        for code_in_all2 in all_code:
            if(NameCheck(string,code_in_all1,code_in_all2)==True):
                code1=code_in_all1
                code2=code_in_all2
                chk=1
                break
        if(chk==1): #если нашлась кодировка 
            string=string.encode(code1).decode(code2) #декодируем
            return string,code1,code2
    return 'У сайта неизвестная кодировка','UTF-8', 'UTF-8'

URL = 'https://www.wildberries.ru/catalog/detyam/shkola/rantsy'
start_time = time.time()
counter = 0
for i in range(1,1000000):
    page_url = URL+'?page='+str(i)
    soup = BeautifulSoup(get_html(page_url),'html.parser')
    soup = soup.find('body')
    soup = soup.find('h1',class_='c-h2-v1')
    if(soup!=None):
        if(soup.find('ÐÐ¾ ÐÐ°ÑÐµÐ¼Ñ Ð·Ð°Ð¿ÑÐ¾ÑÑ Ð½Ð¸ÑÐµÐ³Ð¾ Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½Ð¾')!=-1):
            break
    all_products = BeautifulSoup(get_html(page_url),'html.parser')
    all_products = all_products.text
    index_begin = all_products.find('nms: [')
    index_end = all_products.find(']', index_begin)
    all_products = eval(all_products[index_begin+5:index_end+1])
    for product in all_products:
        counter+=1
        url_product = 'https://www.wildberries.ru/catalog/'+str(product)+'/detail.aspx?targetUrl=GP'
        html_product = get_html(url_product)    
        index_data_begin = html_product.find('data: {')
        counter_open = 0
        counter_end = 0
        data_product = ''
        for index_str in range(index_data_begin+6,len(html_product)):
            data_product = data_product + html_product[index_str]
            if(html_product[index_str]=='{'):
                counter_open+=1
            if(html_product[index_str]=='}'):
                counter_end+=1
            if(counter_open==counter_end and counter_open!=0):
                break
        json_product_data = json.loads(data_product)
        abot_product_data = json_product_data['nomenclatures'][str(product)]
        products.append({
            'Маркетплейс': 'Wildberries',
            'Каталог':  '/detyam/shkola/rantsy',
            'Артикул': product,
            'Наименование': json_product_data['goodsName'],
            'Цена без скидки': abot_product_data['minPriceForDcn']['item2'],
            'Цена со скидкой': abot_product_data['minPriceForDcn']['item1'],
            'Было куплено': abot_product_data['ordersCount']
        })
with open('product.csv', 'w', newline="") as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(['Маркетплейс','Каталог','Артикул','Наименование','Цена без скидки','Цена со скидкой','Было куплено'])
    for product in products:
        writer.writerow([product['Маркетплейс'],product['Каталог'],product['Артикул'],product['Наименование'],product['Цена без скидки'],product['Цена со скидкой'],product['Было куплено']])
print(start_time-time.time())