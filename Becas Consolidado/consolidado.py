import json
import pandas as pd

gobierno = json.load(open('becasgob.json', encoding='utf-8'))
santander = json.load(open('becassantander.json', encoding='utf-8'))
consolidado = gobierno + santander


with open('becasconsolidado.json', 'w', encoding='utf-8') as archivo_json_consolidado:
    json.dump(consolidado, archivo_json_consolidado, ensure_ascii=False, indent = 2)
    
    
df = pd.read_json('becasconsolidado.json')
df.to_excel('becasconsolidado.xlsx')