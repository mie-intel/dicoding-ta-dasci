# Ini adalah dashboard streamlit

# Import library
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


def create_and_show_df(file_name, title):
    # Baca data
    df = pd.read_csv(file_name)

    # Ubah data
    df['season'] = df['season'].replace(season_val)
    df['yr'] = df['yr'].replace(year_val)
    df['weathersit'] = df['weathersit'].replace(wheatersit_val)
    df['weekday'] = df['weekday'].replace(day_val)

    # Ubah format data dteday
    df["dteday"] = pd.to_datetime(df["dteday"])
    st.subheader(title)
    st.write(df.head())
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


# Membaca data
day_df = create_and_show_df("day.csv", "Data Harian*")
hour_df = create_and_show_df("hour.csv", "Data Tiap Jam*")
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
z = np.polyfit(month_df['dtemonth'].map(
    dt.datetime.toordinal), month_df['cnt'], 2)
p = np.poly1d(z)
ax.plot(month_df['dtemonth'], p(
    month_df['dtemonth'].map(dt.datetime.toordinal)), "r")

ax.set_title("Performa penjualan sepeda dari 2011 ke 2012",
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

st.markdown("""
### 🌟 **Insight**

* Grafik ini menunjukkan bahwa terjadi **peningkatan** penjualan sepeda dari tahun 2011 menuju 2012.
* penggunaan sepeda cenderung mengalami peningkatan di bulan Juni hingga Oktober dan cenderung turun di bulan Desember hingga Februari
""")

# Perbandingkan berdasarkan musim
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

st.markdown("""
# 🌟 **Insight**

* Terlihat bahwa dalam setiap tahun, penjualan paling **tinggi** terjadi pada **musim gugur** dan **terendah** pada **musim semi**
* Pada tahun 2012, penjualan mengalami **kenaikan** dibandingkan tahun 2011
""")


# Menunjukkan performa penjualan sepeda berdasarkan cuaca
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

st.markdown("""
# 🌟 **Insight**

* Terlihat bahwa dalam setiap tahun, penjualan paling **tinggi** terjadi pada **cuaca cerah** dan **terendah** pada **cuaca berawan**
* Pada tahun 2012, penjualan mengalami **kenaikan** dibandingkan tahun 2011
""")

# Menunjukkan performa penjualan sepeda berdasarkan jam
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

st.markdown("""
# 🌟 **Insight**

* Terlihat bahwa rata - rata penggunaan sepeda paling tinggi ada di pukul 17.00 dan paling rendah di pukul 04.00
* Pada pagi hari(00.00 hingga 04.00) penggunaan sepeda cenderung **rendah**
* Sementara pada sore hari(16.00 - 19.00) penggunaan sepeda cenderung **tinggi**
""")

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

st.markdown("""
# 🌟 **Insight**

* Terlihat tidak ada perbedaan signifikan di antara setiap hari
* Namun, hari dengan rata - rata penggunaan tertinggi ada pada hari Jumat dan terendah pada hari Minggu.
""")


st.markdown("""
# 🖊️**Kesimpulan**

- Penggunaan sepeda pada tahun 2012 cenderung mengalami peningkatan dibandingkan tahun 2011
- Pada musim gugur, penggunaan sepeda mengalami pelonjakan. Sementara pada musim semi, penggunaan sepeda mengalami penurunan
- Pada cuaca cerah, penggunaan sepeda cenderung tinggi. Sementara pada cuaca berkabut, penggunaan sepeda cenderung rendah
- Jam dengan rata - rata penggunaan sepeda tertinggi adalah pukul 17.00 dan terendah pada pukul 04.00
- Hari dengan rata - rata penggunaan sepeda tertinggi adalah hari Jumat dan terendah adalah hari Minggu
""")
