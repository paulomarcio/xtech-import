import functions
import settings
from time import sleep


# Aqui eu listo todos os produtos obtidos na Xtech
for i in range(1, (settings.db_pages + 1), 1):
    print("Atualizando os %s produtos da página %s ..." % (settings.db_per_page, i))
    # Chamada da API da Xtech para listar os produtos da página atual
    url = "/api-v1/products?per_page=%s&page=%s" % (settings.db_per_page, i)
    produtos = functions.api_get(url)

    for produto in produtos:
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
        print("Aguardando 2 min para o próximo produto...")
        sleep(120)
    sleep(300)
    print("Aguardando 5 min para a próxima página...")
