import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import seaborn as sns
import streamlit as st

sns.set(style='darkgrid')

# HELPER FUNCTION
def create_weather_df(df):
    return df.groupby('weather_label')['cnt'].mean().reset_index().sort_values(by='cnt', ascending=False)

def create_season_df(df):
    return df.groupby('season_label')['cnt'].mean().reset_index().sort_values(by='cnt', ascending=False)

def create_workingday_df(df):
    return df.groupby('day_type')['cnt'].mean().reset_index()

def create_hourly_df(df):
    return df.groupby('hr')['cnt'].mean().reset_index()

def create_monthly_df(df):
    df = df.copy()
    df['month'] = df['dteday'].dt.to_period('M')
    monthly_df = df.groupby('month')['cnt'].sum().reset_index()
    monthly_df['month'] = monthly_df['month'].astype(str)
    return monthly_df

def create_hourly_extreme_df(df):
    hourly = df.groupby('hr')['cnt'].mean().reset_index()
    
    top5 = hourly.sort_values(by='cnt', ascending=False).head(5)
    bottom5 = hourly.sort_values(by='cnt', ascending=True).head(5)
    
    return hourly, top5, bottom5

def create_hourly_category_df(df):
    hourly = df.groupby('hr')['cnt'].mean().reset_index()
    
    hourly['usage_category'] = pd.cut(
        hourly['cnt'],
        bins=3,
        labels=['Low', 'Medium', 'High']
    )
    
    hourly = hourly.sort_values(by='cnt', ascending=False)
    
    return hourly

# LOAD DATA
df = pd.read_csv('dashboard/main_data.csv', parse_dates=['dteday'])
df.sort_values(by='dteday', inplace=True)

# SIDEBAR FILTER
min_date = df['dteday'].min()
max_date = df['dteday'].max()

with st.sidebar:
    st.title("Bike Sharing 🚲")
    st.caption("Dashboard analisis penyewaan sepeda tahun 2011–2012")

    st.image(
        "https://storage.googleapis.com/gweb-uniblog-publish-prod/images/image1_hH9B4gs.width-1600.format-webp.webp",
        use_container_width=True
    )

    st.divider()

    with st.container():
        st.subheader("Filter Data 📊")

        start_date, end_date = st.date_input(
            "Pilih Rentang Waktu",
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )

    st.divider()

# FILTER + COPY
filtered_df = df[
    (df['dteday'] >= pd.to_datetime(start_date)) &
    (df['dteday'] <= pd.to_datetime(end_date))
].copy()

filtered_df['day_type'] = filtered_df['workingday'].map({
    0: 'Hari Libur',
    1: 'Hari Kerja'
})

# DATA PREPARATION
weather_df = create_weather_df(filtered_df)
season_df = create_season_df(filtered_df)
workingday_df = create_workingday_df(filtered_df)
monthly_df = create_monthly_df(filtered_df)

hourly_mean, top5, bottom5 = create_hourly_extreme_df(filtered_df)
hourly_mean_sorted = create_hourly_category_df(filtered_df)

PRIMARY = '#355872'
SECONDARY = '#CFE2F3'

# HEADER
st.title("Bike Sharing Dashboard 🚲")
st.caption("Analisis penyewaan sepeda tahun 2011–2012")

total = filtered_df['cnt'].sum()
total_casual = filtered_df['casual'].sum()
total_registered = filtered_df['registered'].sum()

hourly_avg = filtered_df.groupby('hr')['cnt'].mean()

peak_hour = hourly_avg.idxmax()
lowest_hour = hourly_avg.idxmin()

col1, col2, col3 = st.columns(3)
col1.metric("Total Rentals", int(total))
col2.metric("Total Registered", int(total_registered))
col3.metric("Total Casual", int(total_casual))

#TREN PENYEWAAN SEPEDA PER BULAN
st.subheader("Tren Penyewaan Sepeda per Bulan")
monthly_df = create_monthly_df(filtered_df)

fig, ax = plt.subplots(figsize=(7,4))

ax.plot(monthly_df['month'], monthly_df['cnt'], marker='o')
ax.set_title("Total Penyewaan per Bulan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Penyewaan")

plt.xticks(rotation=45)

st.pyplot(fig)
plt.close(fig)
with st.expander("Insight Penyewaan Sepeda Per Bulan"):
    st.write("""
    - Terlihat adanya pola perubahan jumlah penyewaan dari bulan ke bulan
    - Beberapa periode menunjukkan peningkatan yang signifikan
    - Hal ini mengindikasikan adanya pengaruh musim terhadap penggunaan sepeda
    """)

# CUACA & MUSIM (2 KOLOM)
st.subheader("Pengaruh Cuaca dan Musim terhadap Penyewaan")

weather_df = create_weather_df(filtered_df)
season_df = create_season_df(filtered_df)

col1, col2 = st.columns(2)

# CUACA
with col1:
    st.markdown("**Berdasarkan Cuaca**")

    # cari nilai tertinggi
    max_val = weather_df['cnt'].max()

    # warna
    colors = [
        PRIMARY if val == weather_df['cnt'].max() else SECONDARY for val in weather_df['cnt']
    ]
    fig, ax = plt.subplots(figsize=(5,4))
    sns.barplot(
        data=weather_df,
        x='weather_label',
        y='cnt',
        palette=colors,
        ax=ax
    )
    
    ax.set_xlabel("")
    ax.set_ylabel("Rata-rata Penyewaan")
    
    plt.xticks(rotation=45)

    st.pyplot(fig)
    plt.close(fig)

    # Insight Expander
    best_weather = weather_df.iloc[0]
    worst_weather = weather_df.iloc[-1]

    with st.expander("Insight Cuaca"):
        st.write(f"""
        - Penyewaan tertinggi terjadi saat **{best_weather['weather_label']}**
        - Penyewaan terendah terjadi saat **{worst_weather['weather_label']}**
        - Kondisi cuaca yang lebih buruk cenderung menurunkan jumlah penyewaan
        """)

# MUSIM
with col2:
    st.markdown("**Berdasarkan Musim**")
    
    # cari nilai tertinggi
    max_val = season_df['cnt'].max()

    #warna
    colors = [
        PRIMARY if val == weather_df['cnt'].max() else SECONDARY for val in weather_df['cnt']
    ]

    fig, ax = plt.subplots(figsize=(5,4))

    sns.barplot(
        data=season_df,
        x='season_label',
        y='cnt',
        palette=colors,
        ax=ax
    )
    ax.set_xlabel("")
    ax.set_ylabel("Rata-rata Penyewaan")
    
    st.pyplot(fig)
    plt.close(fig)

    # Insight Expander
    best_season = season_df.iloc[0]
    worst_season = season_df.iloc[-1]

    with st.expander("Insight Musim"):
        st.write(f"""
        - Penyewaan tertinggi terjadi pada musim **{best_season['season_label']}**
        - Penyewaan terendah terjadi pada musim **{worst_season['season_label']}**
        - Faktor musim mempengaruhi pola penggunaan sepeda secara signifikan
        """)

# WORKINGDAY
st.subheader("Rata-Rata Penyewaan : Hari Kerja vs Hari Libur")

workingday_df = create_workingday_df(filtered_df)

fig, ax = plt.subplots(figsize=(5,4))
sns.barplot(
    data=workingday_df,
    x='day_type',
    y='cnt',
    palette=['#355872', '#CFE2F3'],
    legend=False,
    ax=ax
)
plt.xlabel('Jenis Hari', fontsize=12)
plt.ylabel('Rata-rata Penyewaan', fontsize=12)

st.pyplot(fig)
plt.close(fig)

higher_day = workingday_df.sort_values(by='cnt', ascending=False).iloc[0]
with st.expander("Insight Penyewaan Berdasarkan Jenis Hari"):
    st.write(f"""
    Rata-rata penyewaan sepeda lebih tinggi pada **{higher_day['day_type']}**, yang mengindikasikan bahwa 
    sepeda lebih banyak digunakan sebagai moda transportasi penunjang aktivitas harian seperti bekerja atau bersekolah.
    """)

# POLA PER JAM
st.subheader("Pola Jam: Hari Kerja vs Hari Libur")

hourly_working = filtered_df.groupby(['hr', 'day_type'])['cnt'].mean().reset_index()

fig, ax = plt.subplots(figsize=(6,4))
sns.lineplot(
    data=hourly_working,
    x='hr',
    y='cnt',
    hue='day_type',
    marker='o',
    ax=ax
)

ax.set_xticks(range(0,24))

plt.xlabel('Jam', fontsize=12)
plt.ylabel('Rata-rata Penyewaan', fontsize=12)

st.pyplot(fig)
plt.close(fig)

with st.expander("Insight Pola Penyewaan Per Jam"):
    st.write("""
    - Pola penyewaan pada hari kerja menunjukkan dua puncak utama, yaitu pada pagi dan sore hari, yang mencerminkan pola mobilitas komuter.
    - Pada hari libur, pola penyewaan cenderung lebih landai dan terpusat pada siang hari, menunjukkan penggunaan untuk aktivitas rekreasi.
    """)

# TOP & BOTTOM 5 JAM
st.subheader("Jam Tertinggi & Terendah")

hourly_mean = create_hourly_df(filtered_df)

top5 = hourly_mean.sort_values(by='cnt', ascending=False).head(5)
bottom5 = hourly_mean.sort_values(by='cnt', ascending=True).head(5)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Top 5 Jam Tertinggi**")
    
    fig, ax = plt.subplots(figsize=(5,4))
      
    sns.barplot(
    data=top5,
    x='hr',
    y='cnt',
    order=top5['hr'],
    palette=[PRIMARY] + ['#7BA6B5'] * 4,
    ax=ax
    )

    ax.set_title('5 Jam Tertinggi', fontsize=13)
    ax.set_xlabel('Jam')
    ax.set_ylabel('Rata-rata Penyewaan')

    st.pyplot(fig)
    plt.close(fig)
    peak = top5.iloc[0]
    with st.expander("Insight Jam Tertinggi"):
        st.write(f"""
        Rata-rata penyewaan sepeda tertinggi terjadi pada pukul {int(peak['hr'])}:00, yang mengindikasikan peningkatan penggunaan pada waktu pulang kerja (evening rush hour).
        """)

with col2:
    st.markdown("**Top 5 Jam Terendah**")
    
    fig, ax = plt.subplots(figsize=(5,4))
    bottom_colors = ['#8B0000'] + ['#FFA0A0'] * 4
    sns.barplot(
        data=bottom5,
        x='hr',
        y='cnt',
        order=bottom5['hr'],
        palette=bottom_colors,
        ax=ax
    )

    ax.set_title('5 Jam Terendah', fontsize=13)
    ax.set_xlabel('Jam')
    ax.set_ylabel('Rata-rata Penyewaan')

    st.pyplot(fig)
    plt.close(fig)

    low = bottom5.iloc[0]
    with st.expander("Insight Jam Terendah"):
        st.write(f"""
        Rata-rata penyewaan sepeda terendah terjadi pada pukul {int(low['hr'])}:00, yang menunjukkan aktivitas penggunaan sangat rendah pada dini hari.
        """)

hourly_sorted = hourly_mean_sorted

st.subheader("Kategori Penyewaan per Jam (Low–Medium–High)")

colors_map = {
    'Low': '#CFE2F3',
    'Medium': '#7FA7C9',
    'High': '#355872'
}

fig, ax = plt.subplots(figsize=(8,4))

sns.barplot(
    data=hourly_mean_sorted,
    x='hr',
    y='cnt',
    order=hourly_mean_sorted['hr'],
    palette=[colors_map[val] for val in hourly_mean_sorted['usage_category']],
    ax=ax
)
ax.set_xlabel('Jam')
ax.set_ylabel('Rata-rata Penyewaan')

legend_elements = [
    Patch(facecolor='#CFE2F3', label='Low'),
    Patch(facecolor='#7FA7C9', label='Medium'),
    Patch(facecolor='#355872', label='High')
]

ax.legend(handles=legend_elements, title='Usage Category')

st.pyplot(fig)
plt.close(fig)

top_hour = hourly_sorted.iloc[0]
low_hour = hourly_sorted.iloc[-1]

with st.expander("Insight Kategori Penyewaan Per Jam"):
    st.write(f"""
    - Jam dengan kategori **High** menunjukkan periode dengan permintaan tertinggi, terutama pada jam sibuk
    - Penyewaan tertinggi terjadi pada pukul **{int(top_hour['hr'])}:00**
    - Penyewaan terendah terjadi pada pukul **{int(low_hour['hr'])}:00**
    - Mayoritas jam dengan kategori **Low** terjadi pada dini hari
    - Pola ini menunjukkan bahwa penyewaan sepeda sangat dipengaruhi oleh aktivitas harian pengguna
    """)

# FOOTER
st.caption("Bike Sharing Analysis by Vina Widiasari © 2026")