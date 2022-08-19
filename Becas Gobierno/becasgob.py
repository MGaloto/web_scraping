from bs4 import BeautifulSoup as BS
import requests
from time import sleep
from lxml import etree, html
import json
import pandas as pd




class Gobern():
    
    def __init__(self):
            self.main()

    def main(self):
        self.url_contenido = 'https://campusglobal.educacion.gob.ar/becas/enextranjero?BecasSearch%5Bareas%5D=&BecasSearch%5Bareas%5D%5B%5D=6&BecasSearch%5Bareas%5D%5B%5D=2&BecasSearch%5Bareas%5D%5B%5D=12&BecasSearch%5Bareas%5D%5B%5D=5&BecasSearch%5Bareas%5D%5B%5D=4&BecasSearch%5Bareas%5D%5B%5D=10&BecasSearch%5Bareas%5D%5B%5D=8&BecasSearch%5Bpaises%5D=&BecasSearch%5BtiposDeBecas%5D=&BecasSearch%5Bduraciones%5D='
        self.url = 'https://campusglobal.educacion.gob.ar/becas'
        links = self.getLinks(self.url_contenido, self.url)
        urls = []
        diccionario = []
        count = 0
        
        for link in links:
            count += 1
            soup     = self.getSoup(link)
            tree     = self.getTree(link)
            print(link)
            if soup.find('a', {'class': 'btn btn-primary btn-search-becas showLoading'}) != None:
                urls.append(link)
                continue
            else:
                sleep(0.25)
                country = self.getCountry(soup)
                nombre = soup.find('h1').text
                tipo = tree.xpath('//*[@id="page-loader"]/section/article/div/div[7]/div[2]/p/text()')[0].replace('\n','').replace('\t','')
                duracion = tree.xpath('//*[@id="page-loader"]/section/article/div/div[19]/div[2]/p/text()')[0].replace('\n','').replace('\t','')
                area = tree.xpath('//*[@id="page-loader"]/section/article/div/div[9]/div[2]/p/text()')[0].replace('\n','').replace('\t','')
                beca = tree.xpath('//*[@id="page-loader"]/section/article/div/div[1]/div[1]/h1/text()')[0].replace('\n','').replace('\t','')
                descripcion = self.getDescription('//*[@id="page-loader"]/section/article/div/div[14]/div[2]/p/text()', tree)
                bases = self.getBases(soup)
                pagina = 'https://campusglobal.educacion.gob.ar/becas'
                
                variables = {
                    
                    'Nombre'    : nombre,
                    'Pais'      : country,
                    'Tipo'      : tipo,
                    'Duracion'  : duracion,
                    'Area'      : area,
                    'Descripcion' : descripcion,
                    'Bases'     : bases,
                    'Link'      :link,
                    'Pagina'    : pagina
                    
                    }
                
                diccionario.append(variables)
            
                print('\n')
                print('NOMBRE: ',nombre)
                print('COUNTRY: ',country)
                print('TIPO: ',tipo)
                print('DURACION: ',duracion)
                print('AREA: ',area)
                print('DESCRIPCION: ',descripcion)
                print('BASES: ',bases)
                print('LINK: ',link)
                print('Pagina: ',pagina)
                print('\n')
                print('Restan: ',len(links) - count)
            
        
        '''
        Save Json, Excel and Txt.
        '''
        
        with open('becasgob.json', 'w', encoding='utf-8') as archivo_json:
            json.dump(diccionario, archivo_json, ensure_ascii=False, indent = 2)
        
        with open('becasgob.txt', 'w') as f:
            for line in urls:
                f.write(line)
                f.write('\n')
        
        df = pd.read_json('becasgob.json')
        df.to_excel('becasgob.xlsx')
        
        '''
        End Save
        '''

    
    def getLinks(self, url_contenido, url):
        request = requests.get(url_contenido)
        soup = BS(request.text, 'lxml')
        categorias = soup.find_all('a', attrs = { 'class': 'btn btn-sm btn-primary'})
        links = [url + categorias[i]['href'].replace('/becas','') for i in range(len(categorias))]
        return links
    
    
    def getCountry(self,soup):
        country = [soup.text for soup in soup.find_all('div', attrs = { 'class': 'pull-left'})]
        try:
            if len(country) > 1:
                return country
            else:
                return country[0]
        except:
            return None
        
        
    def getSoup(self,link):
        response = requests.get(link)
        soup =  BS(response.text, 'lxml')
        return soup
    
    
    def getTree(self,link):
        response = requests.get(link)
        tree     = html.fromstring(response.content)
        return tree
    
    
    def getDescription(self,XPATH, tree):
        descripcion_completo = tree.xpath(XPATH)
        descripcion_parcial = [descripcion_completo[i].replace('\n','').replace('\r','') for i in range(len(descripcion_completo))]
        descripcion = ' '.join(descripcion_parcial)
        return descripcion
        
    
    def getBases(self,soup):
        bases = soup.find('div', attrs = { 'class': 'row ver-bases-y-condiciones-container'}).find_all('a')
        if len(bases) <= 1:
            if bases[0]['href'].split(':')[0] == 'https' or bases[0]['href'].split(':')[0] == 'http':
                return bases[0]['href']
            else:
                for soup in bases:
                    bases = self.url.replace('/becas','') + soup['href']
                return bases
        elif len(bases) > 1:
            links = [base['href'] for base in bases]
            nuevos_links = []
            for link in links:
                if 'http' in link:
                    nuevos_links.append(link)
                else:
                    link_clean = self.url.replace('/becas','') + link
                    nuevos_links.append(link_clean)
                    
            return nuevos_links
        else:
            return None
    


if __name__ == "__main__":
    objName = Gobern()
    objName.main() 



 







