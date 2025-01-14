import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import TOKEN, API_URL
from clustering import preprocess_data, perform_kmeans, get_cluster_members, plot_clusters
from main import get_data_p2p, turn_data_into_df, data_clustization, identify_market_makers, plot_daily_spread, analyze_volume

def main():
    st.title("Analyzing Qvapay Data")

    # Sidebar for parameters
    st.sidebar.subheader("Data Source")
    data_source = st.sidebar.radio("Select Data Source", ["API", "JSON"])

    st.sidebar.header("Parameters")
    n_clusters = st.sidebar.slider("Number of Clusters", min_value=2, max_value=10, value=4)
    coin = st.sidebar.text_input("Coin", value="BANK_MLC")
    cluster_label = st.sidebar.number_input(
        "If after cluster analysis you identify any cluster that can be a market maker, insert the cluster label (optional)",
        value=-1,
        format="%d"
    )

    # Initialize session state for data
    if "df" not in st.session_state:
        st.session_state.df = None
    if "result_df" not in st.session_state:
        st.session_state.result_df = None
    if "market_makers" not in st.session_state:
        st.session_state.market_makers = None

    # Fetch or Upload Data
    if data_source == "API":
        if st.button("Fetch Data from API"):
            with st.spinner("Fetching data from Qvapay API..."):
                data = get_data_p2p()
                st.session_state.df = turn_data_into_df(data)
                st.success("Data fetched successfully!")
    elif data_source == "JSON":
        uploaded_file = st.file_uploader("Upload a JSON file", type="json")
        if uploaded_file is not None:
            data = pd.read_json(uploaded_file)
            st.session_state.df = turn_data_into_df(data)
            st.success("Data loaded successfully from JSON file!")

    # Display Data Preview
    if st.session_state.df is not None:
        st.write("Data Preview:")
        st.dataframe(st.session_state.df, use_container_width=True)

    # Clustering
    st.subheader("Clustering")
    if st.session_state.df is None:
        st.warning("Please fetch data from API or upload a JSON file to proceed.")
    elif st.button("Perform Clustering"):
        with st.spinner("Performing clustering..."):
            st.session_state.result_df = data_clustization(st.session_state.df, n_clusters=n_clusters, plot=False)
            st.success("Clustering completed!")
            st.write("Clustering Results:")
            st.dataframe(st.session_state.result_df.head())
            fig = plot_clusters(st.session_state.result_df, 'Total_Transactions', 'Total_Volume', 'cluster_label')
            st.pyplot(fig)

    # Identify Market Makers
    if st.session_state.result_df is not None:
        if st.button("Identify Market Makers"):
            st.subheader("Market Makers Identification")
            with st.spinner("Identifying Market Makers..."):
                st.session_state.market_makers = identify_market_makers(
                    st.session_state.df, st.session_state.result_df, cluster_label=cluster_label
                )
                st.success("Market Makers identified!")
                st.write("Market Makers:")
                st.dataframe(st.session_state.market_makers['Username'].unique())

    # Daily Spread Plot
    if st.session_state.market_makers is not None:
        st.subheader("Daily Spread Analysis")
        with st.spinner("Plotting daily spread..."):
            fig_spread = plot_daily_spread(st.session_state.market_makers, coin)
            if fig_spread:  # Asegurarse de que no sea None
                st.pyplot(fig_spread)
            else:
                st.warning(f"No data available to plot daily spread for {coin}.")

    # Volume Analysis
    if st.session_state.df is not None:
        st.subheader("Volume Analysis")
        with st.spinner("Analyzing volume..."):
            fig_volume = analyze_volume(st.session_state.df, coin)
            if fig_volume:  # Asegurarse de que no sea None
                st.pyplot(fig_volume)
            else:
                st.warning(f"No data available for volume analysis of {coin}.")


if __name__ == "__main__":
    main()
