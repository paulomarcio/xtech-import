import functions
import settings
from time import sleep
from datetime import datetime

# Aqui eu listo todos os produtos obtidos na Xtech
page = 73
pages = int(settings.db_products / settings.db_per_page)
now = datetime.now()
tentativas = 1
falhas = []

print("Processo iniciado em %s/%s/%s as %s:%s:%s" % (now.day, now.month, now.year, now.hour, now.minute, now.second))

while page <= pages:
    try:
        print("Atualizando os %s produtos da página %s ..." % (settings.db_per_page, page))
        # Chamada da API da Xtech para listar os produtos da página atual
        url = "/api-v1/products?per_page=%s&page=%s" % (settings.db_per_page, page)
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
                print("Tentativas executadas: %s" % tentativas)
                print("Reniciando de onde parou em 10 segundos...")

                sleep(10)
                has_stopped = True
                tentativas = tentativas + 1

                if tentativas >= 5:
                    falhas.append(produto['sku'])
                    tentativas = 1
                    has_stopped = False

                break

        if has_stopped is False:
            page = page + 1

    except:
        print("Ocorreu um erro ao tentar recuperar a lista de produtos")
        print("Reniciando de onde parou em 10 segundos...")
        sleep(10)

print("Processo finalizado em %s/%s/%s as %s:%s:%s" % (now.day, now.month, now.year, now.hour, now.minute, now.second))
print("Lista de produtos que deram falha no upload de imagens:")
print(falhas)
