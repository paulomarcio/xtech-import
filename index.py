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

                        params = {"product": {"name": "%s" % produto['name'], "sku": "%s" % produto['sku'],
                                  "description": "%s" % produto['description'], "price": produto['price'],
                                              "saleprice": produto['saleprice'], "images": imagens}}

                        print("Atualizando as imagens do produto SKU[%s]" % produto['sku'])
                        # Chamada da API para atualizar o produto na Xtech inserindo suas imagens
                        response = functions.api_put("/api-v1/products?id=%s" % produto['id'], params)
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


xtech = Xtech()
xtech.get_products_from_api()
xtech.update_from_csv()
