import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt

from utils import TOKEN, API_URL
from clustering import preprocess_data, perform_kmeans, get_cluster_members, plot_clusters


def get_data_p2p():

    headers = {
        'Authorization': f'Bearer {TOKEN}',  
        'Accept': 'application/json'  
    }
    
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al conectar con la API: {e}")
    except Exception as e:
        raise Exception(f"Error inesperado: {e}")

def turn_data_into_df(data):
    transactions = []
    for transaction in data['data']:
        transactions.append({
            'Transaction UUID': transaction['uuid'],
            'Type': transaction['type'],
            'Coin': transaction['coin'],
            'Amount': transaction['amount'],
            'Receive': transaction['receive'],
            'Message': transaction['message'],
            'Status': transaction['status'],
            'Created At': transaction['created_at'],
            'Updated At': transaction['updated_at'],
            'Coin Name': transaction['coin_data']['name'],
            'Coin Price': transaction['coin_data']['price'],
            'User UUID': transaction['owner']['uuid'],
            'Username': transaction['owner']['username'],
            'Name': transaction['owner']['name'],
            'Lastname': transaction['owner']['lastname'],
            'KYC': transaction['owner']['kyc'],
            'Average Rating': transaction['owner']['average_rating'],
        })

    df = pd.DataFrame(transactions)

    return df


def plot_daily_spread(market_makers, coin):
    coin_data = market_makers[market_makers['Coin'] == coin]

    if coin_data.empty:
        print(f"No se encontraron transacciones de Market Makers para la moneda {coin}.")
        return

    print(f"Transacciones de Market Makers para {coin}: {coin_data.shape[0]}")

    coin_data = coin_data.copy()  
    coin_data['Created At'] = pd.to_datetime(coin_data['Created At'])

    coin_data['Coin Price'] = pd.to_numeric(coin_data['Coin Price'], errors='coerce')

    coin_data['Spread'] = coin_data['Coin Price'].diff().abs()

    daily_spread = coin_data.groupby(coin_data['Created At'].dt.date)['Spread'].mean()

    if daily_spread.empty:
        print(f"No se pudo calcular el spread diario para la moneda {coin}.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(daily_spread.index, daily_spread.values, marker='o', label=f'Promedio Diario del Spread ({coin})')
    plt.xlabel('Fecha')
    plt.ylabel('Spread Promedio')
    plt.title(f'Promedio Diario del Spread para {coin}')
    plt.legend()
    plt.grid()
    plt.show()

def analyze_volume(df, coin):

    coin_data = df[df['Coin'] == coin]

    if coin_data.empty:
        print(f"No se encontraron transacciones para la moneda {coin}.")
        return

    coin_data['Created At'] = pd.to_datetime(coin_data['Created At'])

    daily_offer = coin_data[coin_data['Type'] == 'sell'].groupby(coin_data['Created At'].dt.date)['Amount'].sum()
    daily_demand = coin_data[coin_data['Type'] == 'buy'].groupby(coin_data['Created At'].dt.date)['Amount'].sum()

    volume_comparison = pd.DataFrame({
        'Oferta': daily_offer,
        'Demanda': daily_demand
    }).fillna(0)

    consistent_demand = (volume_comparison['Demanda'] > volume_comparison['Oferta']).sum()
    consistent_offer = (volume_comparison['Oferta'] > volume_comparison['Demanda']).sum()

    if consistent_demand > consistent_offer:
        print("La demanda supera consistentemente a la oferta.")
    elif consistent_offer > consistent_demand:
        print("La oferta supera consistentemente a la demanda.")
    else:
        print("La oferta y la demanda están equilibradas.")

    volume_comparison.plot(kind='bar', figsize=(12, 6), title=f'Volumen Diario de Oferta y Demanda para {coin}')
    plt.xlabel('Fecha')
    plt.ylabel('Volumen')
    plt.show()

def data_clustization(df, n_clusters=4, plot=True):
    scaled_df, result_df = preprocess_data(df)

    results = perform_kmeans(scaled_df, n_clusters=n_clusters)

    result_df['cluster_label'] = results['labels']


    if plot:
        plot_clusters(result_df, 'Total_Transactions', 'Total_Volume', 'cluster_label')

    return result_df

def identify_market_makers(df, result_df, cluster_label=None):
    if cluster_label is None:
        # Heurística: Seleccionar el cluster con el mayor centroide en Total_Transactions y Total_Volume
        cluster_centers = result_df.groupby('cluster_label')[['Total_Transactions', 'Total_Volume']].mean()
        cluster_label = cluster_centers.sum(axis=1).idxmax() 

    print(f"Cluster seleccionado: {cluster_label}")
    cluster_members = result_df[result_df['cluster_label'] == cluster_label]

    print(cluster_members[['User UUID', 'Username', 'Name', 'Lastname']])

    market_makers = df[df['Username'].isin(cluster_members['Username'])]

    return market_makers

def main():

    data = get_data_p2p()
    print(data)

    df = turn_data_into_df(data)
    
    result_df = data_clustization(df, n_clusters=4, plot=True)

    market_makers = identify_market_makers(df, result_df)

    print(market_makers.head())

    plot_daily_spread(market_makers, 'BANK_MLC')
    
    analyze_volume(df, 'BANK_MLC')

if __name__ == "__main__":
    main()
