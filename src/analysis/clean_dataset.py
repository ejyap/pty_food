import pandas as pd
import numpy as np

df = pd.read_csv('..\\..\\data\\processed\\city_restaurants_unfiltered.csv', header=None, encoding='utf-8')
df = df.drop(df.columns[0], axis=1)
df.columns = ['Name', 'Type', 'Area', 'Neighborhood', 'Address', 'Lat', 'Long', 'Price', 'Comida_rating',
              'Servicio_rating', 'Ambiente_rating', 'Votes', 'Menu_ejecutivo', 'Acceso_discapacitados',
              'Estacionamientos', 'Kosher', 'Wifi', 'Domicilio', 'Dog_friendly']

df.Type = df.Type.apply(lambda x: [s.strip() for s in str(x).split(',')] if pd.notnull(x) else np.nan)
df.Price = df.Price.apply(lambda x: np.nan if x == 0 else x)
df.Comida_rating = df.Comida_rating.apply(lambda x: np.nan if x == 0 else x)
df.Servicio_rating = df.Servicio_rating.apply(lambda x: np.nan if x == 0 else x)
df.Ambiente_rating = df.Ambiente_rating.apply(lambda x: np.nan if x == 0 else x)

lat = (8.94, 9.05)
long = (-79.6, -79.45)

df = df[(df['Lat'] > lat[0]) & (df['Lat'] < lat[1]) & (df['Long'] > long[0]) & (df['Long'] < long[1])]
df = df[df['Area'] == 'Panamá']
df = df[~df['Price'].isnull()]
df['agg_rating'] = df['Comida_rating'] + df['Servicio_rating'] + df['Ambiente_rating']
df = df[df['Votes'] > 75]

df = df[~df['Neighborhood'].isin(['San Miguelito', 'Cocoli', 'Calidonia', 'Villa Lucre', 'Tocumen', 'Chanis', 'Ancon',
                                 'Parque Lefevre', 'Via España', 'Causeway', 'Pueblo Nuevo'])]
def remove_outliers(column, df):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    df = df.query('(@Q1-1.5*@IQR) <= Price <= (@Q3+1.5*@IQR)').sort_values(column)
    return df
df = remove_outliers('Price', df)

neigh_map = {'Via Brasil': 'Obarrio',
            'Coco del Mar': 'San Francisco',
            'Los Angeles': 'El Dorado/Bethania',
            'Bethania' : 'El Dorado/Bethania',
            'Tumba Muerto': 'El Dorado/Bethania',
             'El Dorado': 'El Dorado/Bethania',
            'El Carmen': 'El Carmen/El Cangrejo',
            'El Cangrejo': 'El Carmen/El Cangrejo',
            'Albrook': 'Albrook/Clayton',
            'Clayton': 'Albrook/Clayton',
            'Ciudad del Saber': 'Albrook/Clayton',
            'La Cresta': 'Bella Vista',
            'Paitilla': 'Paitilla/Punta Pacifica',
            'Punta Pacifica': 'Paitilla/Punta Pacifica',
            'Marbella': 'Marbella/Area Bancaria',
            'Area Bancaria': 'Marbella/Area Bancaria'}

df['Neighborhood'] = df['Neighborhood'].map(lambda x: neigh_map[x] if x in neigh_map else x)

def create_annotation(name, votes, price, rating):
    return '{} ({} Check-ins)<br>Price: ${}.<br>Rating: {}/15.'.format(name, votes, int(price), round(rating, 2))

df['text'] = df.apply(lambda row: create_annotation(row['Name'], row['Votes'], row['Price'], row['agg_rating']), axis=1)

df.to_csv('..\\..\\data\\processed\\city_restaurants_filtered.csv', encoding='utf-8')