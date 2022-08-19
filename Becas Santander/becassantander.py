import requests
from time import sleep
import json
import re
import pandas as pd


p = re.compile(r'<.*?>')


class Santander():
    
    def __init__(self):
            self.main()
            

    def main(self):
        self.link = 'https://api-manager.universia.net/becas-programs/api/search?page='
        links_data = self.getData(self.getLinks(self.link))
        count = 0
        diccionario = []
        
        for link in links_data:
            jsonparser = self.getContentJson(link)
            print(link)
            nombre      = jsonparser['data'][0]['name']
            fromcountry = self.timeZone(jsonparser)
            area        = jsonparser['data'][0]['primaryCategory']
            duracion    = jsonparser['data'][0]['duration']
            descripcion = self.cleanDescription(jsonparser)
            tipo        = self.becaTipo(descripcion)
            link = 'https://app.becas-santander.com/es/program/' + jsonparser['data'][0]['slug']
            pagina = 'https://app.becas-santander.com/es/program/search'
            bases = self.getBases(jsonparser)
            count += 1
            sleep(0.25)
            print('\n')
            print('NOMBRE:      ',nombre)
            print('PAIS:        ',fromcountry)
            print('AREA:        ',area)
            print('DURACION:    ',duracion)
            print('TIPO:        ',tipo)
            print('DESCRIPCION: ',descripcion)
            print('BASES:       ',bases)
            print('LINK:        ',link)
            print('Pagina:      ',pagina)
            print('\n')
            print('Restan:      ',len(links_data) - count)
            
            
            variables = {
                
                'Nombre'         : nombre,
                'Pais'           : fromcountry,
                'Tipo'           : tipo,
                'Duracion'       : duracion,
                'Area'           : area,
                'Descripcion'    : descripcion,
                'Bases'          : bases,
                'Link'           : link,
                'Pagina'         : pagina
                
                }
            
            diccionario.append(variables)
        

        '''
        Save Json, Excel.
        '''
        
        
        with open('becassantander.json', 'w', encoding='utf-8') as archivo_json:
            json.dump(diccionario, archivo_json, ensure_ascii=False, indent = 2)
        
        
        df = pd.read_json('becassantander.json')
        df.to_excel('becassantander.xlsx')
        
        '''
        End Save
        '''
    
    
    def getLinks(self, link_principal):
        '''
        Esta funcion nos regresa todos los links para acceder a cada contenido desde la API
        '''
        link_prinicipal = link_principal + str(1)
        link_principal = self.getContentJson(link_prinicipal)
        links_totales = link_principal['data']['totalPages']
        total_links = []
        for i in range(links_totales):
            links = 'https://api-manager.universia.net/becas-programs/api/search?page=' + str(i + 1)
            total_links.append(links)    
        return total_links
        

    def getContentJson(self, link):
            retry_count = 5
            delay = 2
            for retry in range(retry_count):
                res = requests.get(link)
                if res.status_code == 200:
                    data = res.json()
                    break
                else:
                    sleep(delay)
            if res.status_code == 200:
                return data
            else:
                return None
    
    
    
    def getData(self, links):
        urls_slug = []
        for link in links:
            jsonparser = self.getContentJson(link)
            jsonpage   = jsonparser['data']['hits']
            for page in jsonpage:
                url = 'https://api-manager.universia.net/becas-programs/api/programs/find/' + page['slug'] +'?findBy=slug'
                urls_slug.append(url)
        return urls_slug
    
    
    def getBases(self, jsonparser):
        link_general = 'https://api-manager.universia.net/coreplatform-document-management/v2/document-management/public/'
        basesjson = jsonparser['data'][0]['documentationDocuments']
        if len(basesjson) == 0:
            try:
                lista_bases = jsonparser['data'][0]['logo_url']
            except:
                
                lista_bases = None
        else:
            lista_bases = []
            if len(basesjson) > 1:
                for i in range(len(basesjson)):
                    chequeo = list(basesjson[i].keys())
                    if 'idDoc' in chequeo:
                        print(basesjson[i]['idDoc'])
                        code = link_general + basesjson[i]['idDoc']
                        lista_bases.append(code)
            else:
                try:
                    bases = link_general + basesjson[0]['idDoc']
                    lista_bases.append(bases)
                except:
                    lista_bases = None
        return lista_bases 
            
    def becaTipo(self, descripcion):
        '''
        Al no tenes el campo Tipo en la API utilizamos este metodo para completar el campo
        '''
        tipos = ['Master', 'Magister', 'Curso', 'Course', 'Especializacion', 'Specialization' 'Phd', 'Doctorado', 'especializacion', 'courses', 'specialization', 'voluntariado', 'volunteer', 'volunteer',
                 'programme', 'Programme', 'Programa', 'programa', 'work', 'Work', 'doctoral', 'Máster',
                 'living costs', 'cursos', 'prácticas', 'practicas', 'Prácticas', 'Práctica', 'webinar', 'Webinar', 'curso', 'studiengänge',
                 'programie', 'internship', 'doctorado', 'summer schools', 'Summer schools', 'Summer Schools',
                 'intercambio de experiencias', 'postgrado', 'Postgrado', 'máster', 'lehramtsstudierende', 'proyecto', 'Proyecto',
                 'proyectos de investigación', 'Proyectos de investigación', 'proyectos de investigacion']
        tipo_beca = []
        for tipo in tipos:
            if tipo in descripcion:
                tipo_beca.append(tipo)
        try:
            if len(tipo_beca) > 1:
                
                return tipo_beca[0].title()
            else:
                return tipo_beca[0].capitalize()
        except:
            return None
        
    
         
    
    def cleanDescription(self, jsonparser):
        '''
        Aprovechamos al maximo posible los datos de la API para concatenar en descripcion los siguientes 4 campos
        '''
        try:
            summary     = jsonparser['data'][0]['summary']
        except:
            summary     = ''
        try:
            descripcion = jsonparser['data'][0]['description']
        except:
            descripcion = ''
        try:
            aditional   = jsonparser['data'][0]['additionalInfo']
        except:
            aditional   = ''
        try:
            requirements= jsonparser['data'][0]['requirements']
        except:
            requirements = ''
        total       = summary + ' ' + descripcion + ' ' + aditional + ' ' + requirements
        descript    = p.sub('', total)
        descript    = descript.replace('&nbsp;', '').replace('😊', '')
        return descript.capitalize()
    
    
    
    def timeZone(self, jsonparser):
        try:
            time_zone = jsonparser['data'][0]['timeZone']
        except:
            time_zone = None
        return time_zone
        


if __name__ == "__main__":
    objName = Santander()
    objName.main() 


