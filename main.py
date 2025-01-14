import requests
import pandas as pd
import matplotlib.pyplot as plt

from utils import TOKEN, API_URL
from clustering import preprocess_data, perform_kmeans, get_cluster_members, plot_clusters


def get_data_p2p(token=TOKEN, api_url=API_URL):

    headers = {
        'Authorization': f'Bearer {token}',  
        'Accept': 'application/json'  
    }
    
    try:
        response = requests.get(api_url, headers=headers)
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
        return None

    print(f"Transacciones de Market Makers para {coin}: {coin_data.shape[0]}")

    coin_data = coin_data.copy()
    coin_data['Created At'] = pd.to_datetime(coin_data['Created At'], errors='coerce')

    coin_data = coin_data.dropna(subset=['Created At', 'Coin Price'])

    coin_data['Coin Price'] = coin_data['Coin Price'].astype(str)
    coin_data['Coin Price'] = coin_data['Coin Price'].str.replace(r'[^0-9.]', '', regex=True)
    coin_data['Coin Price'] = pd.to_numeric(coin_data['Coin Price'], errors='coerce')

    coin_data = coin_data.dropna(subset=['Coin Price'])

    coin_data['Type'] = coin_data['Type'].str.strip().str.lower()

    market_maker_ids = coin_data['User UUID'].unique()

    fig, ax = plt.subplots(figsize=(12, 8))

    for market_maker in market_maker_ids:
        mm_data = coin_data[coin_data['User UUID'] == market_maker]

        username = mm_data['Username'].iloc[0] if not mm_data['Username'].empty else f"UUID {market_maker}"

        daily_sell = mm_data[mm_data['Type'] == 'sell'].groupby(mm_data['Created At'].dt.date)['Coin Price'].mean()
        daily_buy = mm_data[mm_data['Type'] == 'buy'].groupby(mm_data['Created At'].dt.date)['Coin Price'].mean()

        all_dates = pd.date_range(start=coin_data['Created At'].min(), end=coin_data['Created At'].max())
        daily_sell = daily_sell.reindex(all_dates, fill_value=0)
        daily_buy = daily_buy.reindex(all_dates, fill_value=0)

        daily_spread = daily_sell - daily_buy

        if not daily_spread.empty:
            ax.plot(
                daily_spread.index, 
                daily_spread.values, 
                marker='o', 
                label=f'Market Maker: {username}'
            )

    ax.set_xlabel('Fecha')
    ax.set_ylabel('Spread Promedio')
    ax.set_title(f'Promedio Diario del Spread por Market Maker para {coin}')
    ax.legend(title="Market Makers", loc='best', bbox_to_anchor=(1, 1))
    ax.grid()

    return fig


def analyze_volume(df, coin):
    coin_data = df[df['Coin'] == coin]

    if coin_data.empty:
        print(f"No se encontraron transacciones para la moneda {coin}.")
        return None

    # Asegurarse de que la columna 'Amount' sea numérica
    coin_data['Amount'] = pd.to_numeric(coin_data['Amount'], errors='coerce')

    coin_data['Created At'] = pd.to_datetime(coin_data['Created At'])

    daily_offer = coin_data[coin_data['Type'] == 'sell'].groupby(coin_data['Created At'].dt.date)['Amount'].sum()
    daily_demand = coin_data[coin_data['Type'] == 'buy'].groupby(coin_data['Created At'].dt.date)['Amount'].sum()

    # Crear el DataFrame asegurándose de que los valores sean numéricos
    volume_comparison = pd.DataFrame({
        'Oferta': daily_offer,
        'Demanda': daily_demand
    }).fillna(0)

    # Convertir las columnas a numéricas si no lo están
    volume_comparison['Oferta'] = pd.to_numeric(volume_comparison['Oferta'], errors='coerce')
    volume_comparison['Demanda'] = pd.to_numeric(volume_comparison['Demanda'], errors='coerce')

    # Crear figura y ejes
    fig, ax = plt.subplots(figsize=(12, 6))
    volume_comparison.plot(kind='bar', ax=ax)
    ax.set_title(f'Volumen Diario de Oferta y Demanda para {coin}')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Volumen')

    return fig


def data_clustization(df, n_clusters=4, plot=True):
    scaled_df, result_df = preprocess_data(df)

    results = perform_kmeans(scaled_df, n_clusters=n_clusters)

    result_df['cluster_label'] = results['labels']


    if plot:
        plot_clusters(result_df, 'Total_Transactions', 'Total_Volume', 'cluster_label')

    return result_df

def identify_market_makers(df, result_df, cluster_label=-1):
    if cluster_label == -1:
        # Heurística: Seleccionar el cluster con el mayor centroide en Total_Transactions y Total_Volume
        cluster_centers = result_df.groupby('cluster_label')[['Total_Transactions', 'Total_Volume']].mean()
        cluster_label = cluster_centers.sum(axis=1).idxmax()
        print("entree")

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
