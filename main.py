import requests
import time
import json
import csv
import datetime
from bs4 import BeautifulSoup
errors = []
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0', 'accept': '*/*'}
def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params,timeout=20)
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
def get_in(html_product,text):
    index_data_begin = html_product.find(text)
    counter_open = 0
    counter_end = 0
    data_product = ''
    for index_str in range(index_data_begin+len(text)-1,len(html_product)):
        data_product = data_product + html_product[index_str]
        if(html_product[index_str]=='{'):
            counter_open+=1
        if(html_product[index_str]=='}'):
            counter_end+=1
        if(counter_open==counter_end and counter_open!=0):
            break
    return data_product
URL = input()
start_time = time.time()
counter = 0
############################################# ВБ
if(URL.find('wildberries')!=-1):
    products = []
    check = 0
    catalog = ''
    filters = ''
    for i in range(0,len(URL)):
        if(check==1):
            filters = filters+URL[i]
        if(URL[i]=='?'):
            check=1
        if(check==0):
            catalog = catalog+URL[i]
    for i in range(1,1000000):
        if(filters!=''):
            page_url = catalog+'?'+filters+'&page='+str(i)
        else:
            page_url = catalog+'?'+'&page='+str(i)
        try:
            soup = BeautifulSoup(get_html(page_url),'html.parser')
        except:
            break
        soup = soup.find('body')
        soup = soup.find('h1',class_='c-h2-v1')
        if(soup!=None):
            if(soup.find('ÐÐ¾ ÐÐ°ÑÐµÐ¼Ñ Ð·Ð°Ð¿ÑÐ¾ÑÑ Ð½Ð¸ÑÐµÐ³Ð¾ Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½Ð¾')!=-1 or soup.find('По Вашему запросу ничего не найдено')!=-1):
                break
        try:
            all_products = BeautifulSoup(get_html(page_url),'html.parser')
        except:
            break
        all_products = all_products.text
        index_begin = all_products.find('nms: [')
        index_end = all_products.find(']', index_begin)
        all_products = eval(all_products[index_begin+5:index_end+1])
        for product in all_products:
            url_product = 'https://www.wildberries.ru/catalog/'+str(product)+'/detail.aspx'
            try:
                html_product = get_html(url_product)
            except:
                break
            try:
                try:
                    json_product_price = get_in(html_product,'"minPriceForDcn":{')
                    json_product_price = json.loads(json_product_price)
                    json_product_card = get_in(html_product,'"productCard":{')
                    json_product_card = json.loads(json_product_card)
                    products.append({
                        'Артикул': product,
                        'Наименование': json_product_card['goodsName'],
                        'Цена без скидки': json_product_price['item2'],
                        'Цена со скидкой': json_product_price['item1'],
                        'Было куплено': json_product_card["nomenclatures"][str(product)]["ordersCount"]
                    })
                except:
                    data_product = get_in(html_product,'data: {')
                    json_product_data = json.loads(data_product)
                    about_product_data = json_product_data['nomenclatures'][str(product)]
                    products.append({
                        'Артикул': product,
                        'Наименование': json_product_data['goodsName'],
                        'Цена без скидки': about_product_data['minPriceForDcn']['item2'],
                        'Цена со скидкой': about_product_data['minPriceForDcn']['item1'],
                        'Было куплено': about_product_data['ordersCount']
                    })
            except:
                errors.append(str(product))
            print('Cпарсилось - '+str(len(products)))
    # CОХРАНЕНИЕ
    catalog = catalog.replace('https://www.wildberries.ru/catalog/','')
    catalog = catalog.replace('/','-')
    now = datetime.datetime.now()
    name = 'WildBerries-'+catalog+'-'+str(now.day)+'-'+str(now.month)+'-'+str(now.year)+'.csv'
    with open("C:/Users/DIMA/"+name, 'w', encoding='utf-8', errors='replace' , newline="") as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['Артикул','Наименование','Цена без скидки','Цена со скидкой','Было куплено'])
        for product in products:
            try:
                writer.writerow([product['Артикул'],product['Наименование'],product['Цена без скидки'],product['Цена со скидкой'],product['Было куплено']])
            except:
                print(product['Артикул'],product['Наименование'],product['Цена без скидки'],product['Цена со скидкой'],product['Было куплено'])
        print('Спарсилось за -',time.time()-start_time)
############################################# АЛИЭКСПРЕСС        
if(URL.find('aliexpress.ru')!=-1):
    products = []
    setik = set()
    filters = ''
    max_price = ''
    min_price = ''
    checker = 0
    for i in range(0,len(URL)):
        if(checker==1):
            filters=filters+URL[i]
        if(URL[i]=='?'):
            checker=1
    for i in range(URL.find('maxPrice=')+9,len(URL)):
        if(URL[i].isdigit() == True):
            max_price = max_price+URL[i]
        else:
            break
    for i in range(URL.find('minPrice=')+9,len(URL)):
        if(URL[i].isdigit() == True):
            min_price = min_price+URL[i]
        else:
            break
    filters = filters.replace(f'&maxPrice={max_price}','')
    filters = filters.replace(f'&minPrice={min_price}','')
    max_price = int(max_price)//74-1
    min_price = int(min_price)//75+1
    max_price = str(max_price)
    min_price = str(min_price)
    filters = filters.replace('&page=1','')
    filters = filters + '&maxPrice=' + max_price + '&minPrice=' + min_price
    URL_first = 'https://aliexpress.ru/glosearch/api/product?'+filters
    html_first  = get_html(URL_first)
    html_first = html_first.replace('&quot;','"')
    json_page = json.loads(html_first)
    catalog = json_page['breadCrumb']['keywords']
    for i in range(1,1000000):
        URL_products = 'https://aliexpress.ru/glosearch/api/product?'+filters+'&page='+str(i)
        try:
            html_product  = get_html(URL_products)
        except:
            break
        html_product = html_product.replace('&quot;','"')
        json_page = json.loads(html_product)
        counter = json_page['resultCount']
        time_now = time.time()
        while(counter==0):
            if(time.time()-time_now>20):
                break
            html  = get_html(URL_products)
            html = html.replace('&quot;','"')
            json_page = json.loads(html)
            counter = json_page['resultCount']
        if(time.time()-time_now>20):
            print('skeaping... page=',i)
            continue
        try:
            items = json_page['items']
            for item in items:
                articul = item['productId']
                name = item['title']
                base_price = item['originalPrice']
                sale_price = item['price']
                try:
                    was_buy = item['tradeDesc']
                except:
                    was_buy = 0
                if((articul in setik)==False):
                    setik.add(articul)
                    products.append({
                        'Артикул': articul,
                        'Наименование': name,
                        'Цена без скидки': base_price,
                        'Цена со скидкой': sale_price,
                        'Было куплено': was_buy 
                    })
        except:
            break
        print('Cпарсилось - '+str(len(products)))
    if(len(products)==0):
        print('Нет товаров или указана неправильная ссылка')
    else:
        now = datetime.datetime.now()
        catalog = catalog.replace(' ','-')
        name = 'AliexpressRussia-'+catalog+'-'+str(now.day)+'-'+str(now.month)+'-'+str(now.year)+'.csv'
        with open("C:/Users/DIMA/"+name, 'w', encoding='utf-8', errors='replace' , newline="") as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['Артикул','Наименование','Цена без скидки','Цена со скидкой','Было куплено'])
            for product in products:
                writer.writerow([product['Артикул'],product['Наименование'],product['Цена без скидки'],product['Цена со скидкой'],product['Было куплено']])
            print('Спарсилось за -',time.time()-start_time)
print('Артикулы ошибочных продуктов - ',errors)
