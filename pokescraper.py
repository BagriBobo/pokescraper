import scrapy

class PokemonSpider(scrapy.Spider):
    name = 'pokemons'
    start_urls = ['https://pokemondb.net/pokedex/all']
    base_url = 'https://pokemondb.net'

    def parse(self, response):
        tabela_pokedex = "table#pokedex > tbody > tr"
      
        linhas = response.css(tabela_pokedex)

        for linha in linhas:
            coluna_href = linha.css("td:nth-child(2) > a::attr(href)")
            yield response.follow(coluna_href.get(), self.parse_pokemon)

    def parse_pokemon(self, response):
        id_selec = ".vitals-table > tbody > tr:nth-child(1) > td > strong::text"
        nome_selec = "#main > h1::text"
        peso_selec = ".vitals-table > tbody > tr:nth-child(5) > td::text"
        altura_selec = ".vitals-table > tbody > tr:nth-child(4) > td::text"
        tipo1_selec = ".grid-row > div:nth-child(2) > table > tbody > tr:nth-child(2) > td > a:nth-child(1)::text"
        tipo2_selec = ".grid-row > div:nth-child(2) > table > tbody > tr:nth-child(2) > td > a:nth-child(2)::text"
        ability_selector = ".vitals-table > tbody > tr:nth-child(6) > td > span > a::attr(href)"
        evolutions_selector = ".infocard-list-evo > div.infocard"

        id = response.css(id_selec)
        nome = response.css(nome_selec)
        peso = response.css(peso_selec)
        altura = response.css(altura_selec)
        tipo1 = response.css(tipo1_selec)
        tipo2 = response.css(tipo2_selec)
        url = response.request.url

        evolutions = []
        for evolucoes in response.css(evolutions_selector):
            idEvolucao = evolucoes.css("span > small::text").get()
            nomeEvolucao = evolucoes.css("span:nth-child(2) > a::text").get()
            urlEvolucao = evolucoes.css("span:nth-child(2) > a::attr(href)").get()

            evolucao = {
                'IdEvolucao': idEvolucao if idEvolucao else None,
                'NomeEvolucao': nomeEvolucao,
                'UrlEvolucao': f"{self.base_url}{urlEvolucao}" if urlEvolucao else None
            }
            evolutions.append(evolucao)
        linha = {
            'id': int(id.get()),
            'nome': nome.get().strip(),
            'peso': peso.get(),
            'altura': altura.get(),
            'tipo1': tipo1.get(),
            'tipo2': tipo2.get(),
            'url': url,  
            'abilities': [],
            'evolutions': evolutions
        }

        css_result = response.css(ability_selector).getall()

        for href_ability in css_result:
            request = scrapy.Request(f"{self.base_url}{href_ability}", callback=self.parse_ability)
            request.meta['linha'] = linha
            yield request

    def parse_ability(self, response):
        ability_info = response.css("#main > div > div > p::text").getall()
        ability_nome = response.css("#main > h1::text").get().strip()

        linha = response.meta['linha']

        linha['abilities'].append({'nome': ability_nome, 'text': ' '.join(ability_info).strip(), 'url': response.request.url})
        yield linha
