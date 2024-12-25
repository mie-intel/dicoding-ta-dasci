# Ini adalah dashboard streamlit

# Import library
import math
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

st.title("Bike Sharing Dashboard")
st.text("""
    Oleh  : Polikarpus Arya Pradhanika
""")

st.write("**Sekilas tentang Bike Sharing Dataset**")
st.write("""
    Bike Sharing Dataset adalah dataset yang berisi data tentang penggunaan sepeda dari tahun 2011 hingga 2012.
Dataset ini mampu menggambarkan dengan cukup baik perilaku penggunaan sepeda di kota Washington DC, Amerika Serikat.
         """)

# persiapkan parsing data
season_val = {1: 'Semi', 2: 'Panas', 3: 'Gugur', 4: 'Dingin'}
year_val = {0: 2011, 1: 2012}
wheatersit_val = {1: 'Cerah', 2: 'Berawan', 3: 'Kabut', 4: 'Hujan'}
day_val = {0: 'Minggu', 1: 'Senin', 2: 'Selasa',
           3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'}


def create_df(file_name):
    # Baca data
    df = pd.read_csv(file_name)

    # Ubah data
    df['season'] = df['season'].replace(season_val)
    df['yr'] = df['yr'].replace(year_val)
    df['weathersit'] = df['weathersit'].replace(wheatersit_val)
    df['weekday'] = df['weekday'].replace(day_val)

    # Ubah format data dteday
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df


def create_month_df(day_df):
    # Kelompokkan data per bulan
    month_df = day_df.groupby(day_df['dteday'].dt.strftime(
        '%Y-%B'))['cnt'].mean().reset_index()
    month_df.rename(columns={"dteday": "dtemonth"}, inplace=True)
    month_df['dtemonth'] = pd.to_datetime(month_df['dtemonth'], format='%Y-%B')
    month_df.sort_values(by='dtemonth', ascending=True, inplace=True)
    month_df = month_df.assign(
        year_month=month_df['dtemonth'].dt.strftime('%B %Y'))
    return month_df


def create_season_df(day_df):
    # Mengelompokkan data berdasarkan musim
    season_order = {'Semi': 0, 'Panas': 1, 'Gugur': 2, 'Dingin': 3}
    season_df = day_df.groupby(['season', 'yr']).agg({
        'cnt': 'mean'
    }).reset_index()

    season_df['season_order'] = season_df['season'].map(season_order)
    season_df.sort_values(
        by=['yr', 'season_order'],
        ascending=True,
        inplace=True
    )
    season_df.drop(columns='season_order', inplace=True)
    return season_df


def create_weather_df(day_df):
    # Mengelompokkan data berdasarkan cuaca
    # Dapatkan rata - rata penggunaan sepeda tiap hari cuaca
    weather_df = day_df.groupby(['weathersit', 'yr']).agg({
        'cnt': 'mean'
    }).reset_index()

    # urutkan nilainya
    weather_df.sort_values(
        by=['yr', 'weathersit'],
        ascending=True,
        inplace=True
    )

    # reset index
    weather_df.reset_index(drop=True, inplace=True)

    return weather_df


def create_hour_cat_df(hour_df):
    # Kelompokkan data berdasarkan jamnya
    # Dapatkan rata - rata penggunaan sepeda setiap jam
    hour_cat_df = hour_df.groupby(['hr']).agg({
        'cnt': 'mean'
    }).reset_index()
    return hour_cat_df


def create_day_cat_df(day_df):
    # Dapatkan tabel sederhana berisi rata - rata penggunaan sepeda
    day_cat_df = day_df.groupby("weekday").agg({
        'cnt': 'mean'
    }).reset_index()

    # Urutkan data berdasarkan hari
    day_back = {"Minggu": 0, "Senin": 1, "Selasa": 2,
                "Rabu": 3, "Kamis": 4, "Jumat": 5, "Sabtu": 6}
    day_cat_df = day_cat_df.assign(
        weekday_order=day_cat_df['weekday'].map(day_back))
    day_cat_df.sort_values(by='weekday_order', inplace=True)

    # Drop kolom pembantu
    day_cat_df.drop(columns='weekday_order', inplace=True)
    return day_cat_df


def show_df(df, title):
    st.subheader(title)
    st.write(df.head())


# Membaca data
raw_day_df = create_df("day.csv")
raw_hour_df = create_df("hour.csv")

min_date = raw_day_df['dteday'].min()
max_date = raw_day_df['dteday'].max()
cur_min_date = min_date
cur_max_date = max_date


def filter_data(df, start_date, end_date):
    return df[(df['dteday'] >= str(start_date)) & (df['dteday'] <= str(end_date))]


with st.sidebar:
    st.write("Filter Data")
    try:
        start_date, end_date = st.date_input(
            label="Rentang tanggal",
            min_value=min_date,
            max_value=max_date,
            value=[cur_min_date, cur_max_date]
        )
        cur_min_date = start_date
        cur_max_date = end_date

    except ValueError:
        st.write("Masukkan end date!")

    if (st.button("Reset Filter")):
        cur_min_date = min_date
        cur_max_date = max_date


day_df = filter_data(raw_day_df, cur_min_date, cur_max_date)
hour_df = filter_data(raw_hour_df, cur_min_date, cur_max_date)


show_df(day_df, "Data Harian*")
show_df(hour_df, "Data Tiap Jam*")
st.caption("*Hanya menampilkan 5 data teratas")

st.markdown("""
# **Analisis Data Pengunaan Sepeda**
""")

# Dapatkan semua data yang diperlukan
month_df = create_month_df(day_df)
season_df = create_season_df(day_df)
weather_df = create_weather_df(day_df)
hour_cat_df = create_hour_cat_df(hour_df)
day_cat_df = create_day_cat_df(day_df)

# Menunjukkan performa penjualan sepeda
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(month_df['dtemonth'],
        month_df['cnt'], marker='o', color='darkblue')

# Menambahkan trendline menggunakan polynomial
if (month_df.shape[0] > 1):
    z = np.polyfit(month_df['dtemonth'].map(
        dt.datetime.toordinal), month_df['cnt'], 2)
    p = np.poly1d(z)
    ax.plot(month_df['dtemonth'], p(
        month_df['dtemonth'].map(dt.datetime.toordinal)), "r")

min_year = month_df['dtemonth'].dt.year.min()
max_year = month_df['dtemonth'].dt.year.max()
ax.set_title(f"Performa penjualan sepeda dari {min_year} ke {max_year}",
             loc="center", fontsize=20, pad=20)

# Set untuk sumbu x
ax.set_xlabel("Bulan", fontsize=15)  # set label
ax.set_xticks(ticks=month_df['dtemonth'][::3])  # set interval sumbu x
ax.set_xticklabels(month_df['dtemonth']
                   # Set interval sumbu x
                   [::3].dt.strftime('%B\n%Y'), fontsize=13, rotation=45)

# Set untuk sumbu y
ax.set_ylabel("Jumlah sepeda (unit)", fontsize=15)  # set label
ax.tick_params(axis='y', labelsize=12)  # Set ukuran label sumbu y
ax.set_yticks(np.arange(0, 8000, 1000))  # Set interval sumbu y

# Menambahkan legend
ax.legend(["Penjualan sepeda", "Trendline"], fontsize=12)
st.pyplot(fig)

# Menunjukkan peringkat bulan terbaik
month_list = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
              'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
month_rank = day_df.groupby(by="mnth").agg({
    'cnt': 'mean'
}).reset_index()
month_rank = month_rank.sort_values(by="cnt", ascending=False)
best_month = month_list[math.floor(month_rank.iloc[0]['mnth']) - 1]
worst_month = month_list[math.floor(month_rank.iloc[-1]['mnth']) - 1]
best_month_rate = month_rank.iloc[0]['cnt']
worst_month_rate = month_rank.iloc[-1]['cnt']

# Membandingkan penjualan dari tahun 2011 dan 2022
y2011_df = month_df[month_df['dtemonth'].dt.strftime("%Y") == '2011']
y2012_df = month_df[month_df['dtemonth'].dt.strftime("%Y") == '2012']
fig, ax = plt.subplots(figsize=(12, 6))

ax.bar(y2012_df['dtemonth'].dt.strftime("%B"),
       y2012_df['cnt'], color='orange', label='2012')
ax.bar(y2011_df['dtemonth'].dt.strftime("%B"),
       y2011_df['cnt'], color='lightblue', label='2011')
ax.set_title("Perbandingan penggunaan sepeda tahun 2011 dan 2012",
             loc="center", fontsize=20, pad=20)

ax.set_xlabel("Bulan", fontsize=17)
ax.set_ylabel("Jumlah sepeda (unit)", fontsize=15)
ax.tick_params(axis='x', rotation=45, labelsize=13)
ax.tick_params(axis='y', labelsize=13)

ax.legend(loc='upper left', fontsize=13)
st.pyplot(fig)

st.markdown(f"""
### 🌟 **Insight**

* Grafik ini menunjukkan bahwa terjadi **peningkatan** penjualan sepeda dari tahun {min_year} menuju {max_year}.
* Penggunaan sepeda cenderung mengalami peningkatan di bulan {best_month} dengan rerata {best_month_rate:.2f} dan cenderung turun di bulan {worst_month} dengan rerata {worst_month_rate:.2f}
""")

# Perbandingkan berdasarkan musim

# Mencari musim terbaik
season_rank = season_df.groupby(by="season").agg({
    'cnt': 'mean'
}).reset_index()
best_season = season_rank[season_rank['cnt'] ==
                          season_rank['cnt'].max()]['season'].values[0]
worst_season = season_rank[season_rank['cnt'] ==
                           season_rank['cnt'].min()]['season'].values[0]
best_season_rate = season_rank['cnt'].max()
worst_season_rate = season_rank['cnt'].min()

# Pisahkan data
y2011_season_df = season_df[season_df['yr'] == 2011]
y2012_season_df = season_df[season_df['yr'] == 2012]
# Buat plot
fig, ax = plt.subplots(figsize=(12, 6))

ax.bar((y2011_season_df['season'] + " " + y2011_season_df["yr"].astype(str)),
       y2011_season_df['cnt'], color='lightblue', label='2011')
ax.bar((y2012_season_df['season'] + " " + y2012_season_df["yr"].astype(str)),
       y2012_season_df['cnt'], color='orange', label='2012')

# Menambahkan trendline
# Menambahkan trendline menggunakan linear
if (season_df.shape[0] > 1):
    z = np.polyfit(np.arange(len(season_df)), season_df['cnt'], 1)
    p = np.poly1d(z)
    ax.plot((season_df['season'] + " " + season_df["yr"].astype(str)),
            p(np.arange(len(season_df))), "black", label='Trend', linewidth=2)

ax.set_title("Perbandingan penggunaan sepeda berdasarkan musim",
             loc="center", fontsize=20, pad=20)
ax.set_xlabel("Musim", fontsize=15)
ax.set_ylabel("Jumlah sepeda (unit)", fontsize=15)

ax.legend(loc='upper left')
ax.tick_params(axis='x', rotation=45, labelsize=13)
ax.tick_params(axis='y', labelsize=13)
st.pyplot(fig)

st.markdown(f"""
# 🌟 **Insight**

* Terlihat bahwa dalam setiap tahun, penjualan paling **tinggi** terjadi pada **musim {best_season}** dengan rerata {best_season_rate:.2f} dan **terendah** pada **musim {worst_season}** dengan rerata {worst_season_rate:.2f}
""")


# Menunjukkan performa penjualan sepeda berdasarkan cuaca
# Cari yang terbaik

# Mencari cuaca terbaik
weather_rank = weather_df.groupby(by="weathersit").agg({
    'cnt': 'mean'
}).reset_index()
best_weather = weather_rank[weather_rank['cnt'] ==
                            weather_rank['cnt'].max()]['weathersit'].values[0]
worst_weather = weather_rank[weather_rank['cnt'] ==
                             weather_rank['cnt'].min()]['weathersit'].values[0]
best_weather_rate = weather_rank['cnt'].max()
worst_weather_rate = weather_rank['cnt'].min()

# Pisahkan data
y2011_weather_df = weather_df[weather_df['yr'] == 2011]
y2012_weather_df = weather_df[weather_df['yr'] == 2012]

# Buat plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar((y2011_weather_df['weathersit'] + " " + y2011_weather_df["yr"].astype(str)),
       y2011_weather_df['cnt'], color='lightblue', label='2011')
ax.bar((y2012_weather_df['weathersit'] + " " + y2012_weather_df["yr"].astype(str)),
       y2012_weather_df['cnt'], color='orange', label='2012')
# Menambahkan trendline
# Menambahkan trendline menggunakan linear
ax.set_title("Perbandingan penggunaan sepeda berdasarkan cuaca",
             loc="center", fontsize=20, pad=20)

if (weather_df.shape[0] > 1):
    z = np.polyfit(np.arange(len(weather_df)), weather_df['cnt'], 1)
    p = np.poly1d(z)
    ax.plot((weather_df['weathersit'] + " " + weather_df["yr"].astype(str)),
            p(np.arange(len(weather_df))), "black", label='Trend', linewidth=2)

ax.set_xlabel("Cuaca", fontsize=15)
ax.set_ylabel("Jumlah sepeda (unit)", fontsize=15)
ax.tick_params(axis='x', rotation=45, labelsize=13)
ax.tick_params(axis='y', labelsize=13)
ax.legend(loc='upper left')
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

st.markdown(f"""
# 🌟 **Insight**

* Terlihat bahwa dalam setiap tahun, penjualan paling **tinggi** terjadi pada **cuaca {best_weather}** dengan rerata {best_weather_rate:.2f} dan **terendah** pada **cuaca {worst_weather}** dengan rerata {worst_weather_rate:.2f}
""")

# Menunjukkan performa penjualan sepeda berdasarkan jam

# Mencari jam terbaik
hour_rank = hour_cat_df.groupby(by="hr").agg({
    'cnt': 'mean'
}).reset_index()
best_hour = hour_rank[hour_rank['cnt'] ==
                      hour_rank['cnt'].max()]['hr'].values[0]
worst_hour = hour_rank[hour_rank['cnt'] ==
                       hour_rank['cnt'].min()]['hr'].values[0]
best_hour = str(best_hour).zfill(2) + '.00'
worst_hour = str(worst_hour).zfill(2) + '.00'

best_hour_rate = hour_rank['cnt'].max()
worst_hour_rate = hour_rank['cnt'].min()

# Persiapkan data
hour_cat_df = hour_cat_df.copy()
hour_cat_df['hr_str'] = hour_cat_df['hr'].astype(
    str).str.zfill(2) + '.00'

# Buat plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(hour_cat_df['hr_str'], hour_cat_df['cnt'], color='lightblue')
ax.set_xticks(ticks=hour_cat_df['hr_str'][::3],
              labels=hour_cat_df['hr_str'][::3])

ax.tick_params(axis='x', labelsize=13)
ax.tick_params(axis='y', labelsize=13)
ax.set_xlabel("Jam", fontsize=12)
ax.set_ylabel("Jumlah sepeda (unit)", fontsize=15)
ax.set_title("Rata - rata penggunaan sepeda per jam", fontsize=20, pad=20)
st.pyplot(fig)

st.markdown(f"""
# 🌟 **Insight**

* Terlihat bahwa rata - rata penggunaan sepeda paling tinggi ada di pukul {best_hour} dengan rerata {best_hour_rate:.2f} dan paling rendah di pukul {worst_hour} dengan rerata {worst_hour_rate:.2f}
""")

# Mencari hari terbaik
day_rank = day_cat_df.groupby(by="weekday").agg({
    'cnt': 'mean'
}).reset_index()
best_day = day_rank[day_rank['cnt'] ==
                    day_rank['cnt'].max()]['weekday'].values[0]
worst_day = day_rank[day_rank['cnt'] ==
                     day_rank['cnt'].min()]['weekday'].values[0]
best_day_rate = day_rank['cnt'].max()
worst_day_rate = day_rank['cnt'].min()

# Menunjukkan performa penjualan sepeda berdasarkan hari
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(day_cat_df['weekday'], day_cat_df['cnt'], color='lightblue')
ax.set_xticks(ticks=day_cat_df['weekday'])
ax.set_xticklabels(day_cat_df['weekday'], fontsize=12)
ax.tick_params(axis='y', labelsize=13)
ax.tick_params(axis='x', labelsize=13)
ax.set_xlabel("Hari", fontsize=15)
ax.set_ylabel("Jumlah sepeda (unit)", fontsize=15)
ax.set_title("Rata - rata penggunaan sepeda per hari", fontsize=20, pad=20)
st.pyplot(fig)

st.markdown(f"""
# 🌟 **Insight**

* Terlihat bahwa rata - rata penggunaan sepeda paling tinggi ada di hari {best_day} dengan rerata {best_day_rate:.2f} dan paling rendah di hari {worst_day} dengan rerata {worst_day_rate:.2f}
""")


st.markdown(f"""
# 🖊️**Kesimpulan**

{max_year != min_year and "- Penggunaan sepeda pada tahun 2012 cenderung mengalami peningkatan dibandingkan tahun 2011"}
- Pada musim {best_season}, penggunaan sepeda mengalami pelonjakan dengan rerata {best_season_rate:.2f}. Sementara pada musim {worst_season}, penggunaan sepeda mengalami penurunan dengan rerata {worst_season_rate:.2f}
- Pada cuaca {best_weather}, penggunaan sepeda cenderung tinggi dengan rerata {best_weather_rate:.2f}. Sementara pada cuaca {worst_weather}, penggunaan sepeda cenderung rendah dengan rerata {worst_weather_rate:.2f}
- Jam dengan rata - rata penggunaan sepeda tertinggi adalah pukul {best_hour} dan terendah pada pukul {worst_hour}
- Hari dengan rata - rata penggunaan sepeda tertinggi adalah hari {best_day} dengan rerata {best_day_rate:.2f} dan terendah adalah hari {worst_day} dengan reata {worst_day_rate:.2f}
""")
