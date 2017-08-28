import functions
import settings
import csv
import sys
from time import sleep
from datetime import datetime


class Xtech:

    def __init__(self):
        self.page = 1
        self.pages = int(settings.db_products / settings.db_per_page)
        self.now = datetime.now()
        self.tentativas = 1
        self.falhas = []
        self.produtos = []

    def update_from_api(self):

        # Aqui eu listo todos os produtos obtidos na Xtech
        print("Processo iniciado em %s/%s/%s as %s:%s:%s" % (self.now.day, self.now.month, self.now.year, self.now.hour, self.now.minute, self.now.second))

        while self.page <= self.pages:
            try:
                print("Atualizando os %s produtos da página %s ..." % (settings.db_per_page, self.page))
                # Chamada da API da Xtech para listar os produtos da página atual
                url = "/api-v1/products?per_page=%s&page=%s" % (settings.db_per_page, self.page)
                produtos = functions.api_get(url)
                has_stopped = False

                for produto in produtos:
                    try:
                        item = functions.get_produto(produto['sku'])
                        images = functions.get_imagens_produto(item[0])
                        imagens = []
                        for image in images:
                            imagens.append("%s/assets/images/produtos/%s/detalhe/%s" % (settings.s3_bucket_url, item[0], image[3]))

                        params = {"product": {"name": "%s" % item[13],
                                              "sku": "%s" % produto['sku'],
                                              "description": "%s" % item[15],
                                              "excerpt": "%s" % item[15],
                                              "price": produto['price'],
                                              "saleprice": produto['saleprice'],
                                              "images": imagens}}

                        print("Atualizando as imagens do produto SKU[%s]" % produto['sku'])
                        # Chamada da API para atualizar o produto na Xtech inserindo suas imagens
                        response = functions.api_put("/api-v1/products?id=%s" % produto['id'], params)
                        sleep(2)
                    except:
                        print("Ocorreu um erro ao tentar atualizar o produto SKU[%s]" % produto['sku'])
                        print("Tentativas executadas: %s" % self.tentativas)
                        print("Reniciando de onde parou em 10 segundos...")

                        sleep(10)
                        has_stopped = True
                        self.tentativas = self.tentativas + 1

                        if self.tentativas >= 5:
                            self.falhas.append(produto['sku'])
                            self.tentativas = 1
                            has_stopped = False

                        break

                if has_stopped is False:
                    self.page += 1

            except:
                print("Ocorreu um erro ao tentar recuperar a lista de produtos")
                print("Reniciando de onde parou em 10 segundos...")
                sleep(10)

        print("Processo finalizado em %s/%s/%s as %s:%s:%s" % (self.now.day, self.now.month, self.now.year, self.now.hour, self.now.minute, self.now.second))
        print("Lista de produtos que deram falha no upload de imagens:")
        print(self.falhas)

    def get_products_from_api(self):

        # Aqui eu listo todos os produtos obtidos na Xtech
        print("Processo iniciado em %s/%s/%s as %s:%s:%s" % (
        self.now.day, self.now.month, self.now.year, self.now.hour, self.now.minute, self.now.second))

        while self.page <= self.pages:
            try:
                print("Lendo os %s produtos da página %s ..." % (settings.db_per_page, self.page))
                # Chamada da API da Xtech para listar os produtos da página atual
                url = "/api-v1/products?per_page=%s&page=%s" % (settings.db_per_page, self.page)
                produtos = functions.api_get(url)
                for produto in produtos:
                    try:
                        self.produtos.append(produto)
                    except:
                        print("Ocorreu um erro ao armazenar o produto SKU[%s]" % produto['sku'])
                self.page += 1
            except:
                print("Ocorreu um erro ao obter produtos da API")

    def update_from_csv(self):
        f = open('produtos_sku.csv', 'r')
        try:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                for produto in self.produtos:
                    if produto['sku'] in row:
                        try:
                            item = functions.get_produto(produto['sku'])
                            images = functions.get_imagens_produto(item[0])
                            imagens = []
                            for image in images:
                                imagens.append(
                                    "%s/assets/images/produtos/%s/detalhe/%s" % (settings.s3_bucket_url, item[0], image[3]))

                            params = {"product": {"name": "%s" % produto['name'], "sku": "%s" % produto['sku'],
                                                  "description": "%s" % produto['description'], "price": produto['price'],
                                                  "saleprice": produto['saleprice'], "images": imagens}}

                            print("Atualizando as imagens do produto SKU[%s]" % produto['sku'])
                            # Chamada da API para atualizar o produto na Xtech inserindo suas imagens
                            response = functions.api_put("/api-v1/products?id=%s" % produto['id'], params)
                        except:
                            print("An error ocurred when getting product images")

        except:
            print("An error ocurred: %s" % sys.exc_info()[0])
        finally:
            f.close()

    def update_products_categories(self):
    
        # Aqui eu listo todos os produtos obtidos na Xtech
        print("Processo iniciado em %s/%s/%s as %s:%s:%s" % (self.now.day, self.now.month, self.now.year, self.now.hour,
                                                             self.now.minute, self.now.second))
        
        while self.page <= self.pages:
            try:
                print("Atualizando os %s produtos da página %s ..." % (settings.db_per_page, self.page))
                # Chamada da API da Xtech para listar os produtos da página atual
                url = "/api-v1/products?per_page=%s&page=%s" % (settings.db_per_page, self.page)
                produtos = functions.api_get(url)

                for produto in produtos:
                    try:
                        item = functions.get_produto(produto['sku'])
                        categories = []
                        
                        # De / Para com as Faixas Etárias do site antigo
                        faixas = {
                            17: 521425,
                            3: 521426,
                            2: 521427,
                            10: 521429,
                            23: 521429,
                            13: 523248,
                            9: 523249,
                            22: 523251,
                            20: 523255
                        }

                        # De / Para com os Gêneros do site antigo
                        generos = {
                            11: 523256,
                            10: 523257
                        }

                        # De / Para com as Marcas do site antigo
                        marcas = {
                            768: 523261,
                            797: 523263,
                            802: 523265,
                            294: 523266,
                            295: 523267,
                            809: 523269,
                            810: 523270,
                            556: 523272,
                            571: 523273,
                            318: 523274,
                            846: 523275,
                            345: 523277,
                            445: 523278,
                            720: 523279,
                            467: 523282,
                            753: 523283,
                            245: 523284,
                            228: 523286,
                            270: 523287,
                            261: 523288,
                            286: 523289,
                            229: 523290,
                            236: 523291,
                            238: 523293,
                            351: 523294,
                            271: 523296,
                            314: 523298,
                            275: 523299,
                            307: 523300,
                            300: 523301
                        }

                        # Adicionando as Marcas como Categoria
                        if item[7] in marcas:
                            categories.append(int(marcas[item[7]]))

                        # Adicionando as Faixas Etárias como Categoria
                        if item[6] in faixas:
                            categories.append(int(faixas[item[6]]))

                        # Adicionando os Gêneros como Categoria
                        if item[5] in generos:
                            categories.append(int(faixas[item[5]]))

                        # Se for Unissex adiciono ambos os Gêneros
                        if item[5] == 9:
                            categories.append(523256)
                            categories.append(523257)

                        # Listando as categorias do produto
                        for category in produto['categories']:
                            # Recuperando a categoria pai dessa categoria do produto
                            cat = functions.api_get('/api-v1/categories?id=%s' % category['id'])

                            # Adicionando a categoria pai na lista de categorias do produto
                            if cat['parent_id'] not in categories and int(cat['parent_id']) > 0:
                                categories.append(int(cat['parent_id']))

                            # Adicionando a categoria na listagem para não atualizar errado
                            if category['id'] not in categories:
                                categories.append(int(category['id']))

                        # Atualizando as categorias do produto
                        params = {"product": {"sku": "%s" % produto['sku'], "categories": categories}}

                        print("Atualizando as categorias do produto SKU[%s]" % produto['sku'])

                        # Chamada da API para atualizar o produto na Xtech inserindo suas categorias atualizadas
                        response = functions.api_put("/api-v1/products?id=%s" % produto['id'], params)
                        sleep(2)

                    except:
                        print("Ocorreu um erro ao tentar atualizar produto: %s" % sys.exc_info()[0])
                        break

                self.page += 1

            except:
                print("Ocorreu um erro ao tentar recuperar a lista de produtos: %s" % sys.exc_info()[0])

    def update_products_promocao(self):
    
        # Aqui eu listo todos os produtos obtidos na Xtech
        print("Processo iniciado em %s/%s/%s as %s:%s:%s" % (self.now.day, self.now.month, self.now.year, self.now.hour,
                                                             self.now.minute, self.now.second))
    
        while self.page <= self.pages:
            try:
                print("Atualizando os %s produtos da página %s ..." % (settings.db_per_page, self.page))
                # Chamada da API da Xtech para listar os produtos da página atual
                url = "/api-v1/products?per_page=%s&page=%s" % (settings.db_per_page, self.page)
                produtos = functions.api_get(url)
            
                for produto in produtos:
                    try:
                        categories = []
                    
                        # Listando as categorias do produto
                        for category in produto['categories']:
                        
                            # Adicionando a categoria na listagem para não atualizar errado
                            if category['id'] not in categories:
                                categories.append(int(category['id']))
                    
                        # Atualizando as categorias do produto
                        params = {"product": {"sku": "%s" % produto['sku'], "categories": categories}}
                    
                        print("Atualizando as categorias do produto SKU[%s]" % produto['sku'])
                    
                        # Chamada da API para atualizar o produto na Xtech inserindo suas categorias atualizadas
                        response = functions.api_put("/api-v1/products?id=%s" % produto['id'], params)
                        sleep(2)
                
                    except:
                        print("Ocorreu um erro ao tentar atualizar produto: %s" % sys.exc_info()[0])
                        break
            
                self.page += 1
        
            except:
                print("Ocorreu um erro ao tentar recuperar a lista de produtos: %s" % sys.exc_info()[0])
        
xtech = Xtech()
xtech.update_products_promocao()
#xtech.update_from_api()
#xtech.get_products_from_api()
#xtech.update_from_csv()
