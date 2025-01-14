import requests
import pandas as pd
import matplotlib.pyplot as plt

from utils import TOKEN, API_URL
from clustering import preprocess_data, perform_kmeans, plot_clusters


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

def main():

    data = get_data_p2p()
    print(data)

    df = turn_data_into_df(data)
    scaled_df, result_df = preprocess_data(df)

    results = perform_kmeans(scaled_df, n_clusters=4)

    result_df['cluster_label'] = results['labels']

    plot_clusters(result_df, 'Total_Transactions', 'Total_Volume', 'cluster_label')
    
    cluster_label = 1
    cluster_members = result_df[result_df['cluster_label'] == cluster_label]

    print(cluster_members[['User UUID', 'Username', 'Name', 'Lastname']])

    market_makers = df[df['Username'].isin(cluster_members['Username'])]

    print(market_makers.head())

    resultado = plot_daily_spread(market_makers, 'BANK_MLC')

    print(resultado.head())


if __name__ == "__main__":
    main()
