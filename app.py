import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🛍️ Stok Updater - Shopee & Tokopedia")

# Edukasi Pengguna
with st.expander("📚 Panduan Sebelum Menggunakan Aplikasi"):
    st.markdown("""
    Untuk memastikan sistem berjalan dengan baik, harap ikuti langkah-langkah berikut sebelum mengunggah file:
    
    1. **Siapkan file `copybar.csv`** — file ini adalah hasil konversi dari Excel `copybar.xlsx`.
       - Buka file Excel
       - Klik Save As > Pilih format `.csv (Comma delimited)`
    
    2. **Siapkan file `mass_update.xlsx` (Shopee) / `ubah-sekaligus.xlsx` (Tokopedia)**
       - Buka file asli dari Shopee/Tokopedia
       - Klik Save As > Simpan kembali sebagai file Excel (format .xlsx)
    
    3. Pastikan **kolom SKU tidak kosong dan tidak berubah format (mis. jadi angka 0000nan)**.

    Setelah menyiapkan semuanya, silakan pilih tab di bawah ini untuk memulai.
    """)

tab1, tab2 = st.tabs(["🟠 Shopee", "🟢 Tokopedia"])

# ================= Shopee =================
with tab1:
    st.header("Update Stok Shopee")
    copybar_file = st.file_uploader("Upload file copybar.csv", type=["csv"], key="shopee_copybar")
    shopee_file = st.file_uploader("Upload file mass_update Shopee (.xlsx)", type=["xlsx"], key="shopee_excel")

    if copybar_file and shopee_file:
        copybar_df = pd.read_csv(copybar_file, dtype=str)
        sku_map = dict(zip(copybar_df["SKU"], copybar_df["Stok"]))

        update_df = pd.read_excel(shopee_file, skiprows=6, dtype=str)
        update_df.iloc[:, 7] = update_df.iloc[:, 0].map(sku_map).fillna("SKU tidak ditemukan")
        update_df.iloc[:, 0] = update_df.iloc[:, 0].astype(str)  # Jaga agar SKU tidak berubah format

        st.success("✅ Data Shopee berhasil diperbarui!")
        st.dataframe(update_df[[update_df.columns[0], update_df.columns[7]]].head(10))

        # Download
        hasil_shopee = update_df.to_excel("hasil_shopee.xlsx", index=False)
        with open("hasil_shopee.xlsx", "rb") as f:
            st.download_button("📥 Download Hasil Shopee", f, file_name="hasil_shopee.xlsx")

# ================= Tokopedia =================
with tab2:
    st.header("Update Stok Tokopedia")
    copybar_file_tokped = st.file_uploader("Upload file copybar.csv", type=["csv"], key="tokopedia_copybar")
    tokped_file = st.file_uploader("Upload file mass_update Tokopedia (.xlsx)", type=["xlsx"], key="tokopedia_excel")

    if copybar_file_tokped and tokped_file:
        copybar_df = pd.read_csv(copybar_file_tokped, dtype=str)
        sku_map = dict(zip(copybar_df["SKU"], copybar_df["Stok"]))

        update_df = pd.read_excel(tokped_file, skiprows=3, dtype=str)
        update_df.iloc[:, 10] = update_df.iloc[:, 10].astype(str)  # SKU Kolom K (index 10)
        update_df.iloc[:, 8] = update_df.iloc[:, 10].map(sku_map).fillna("SKU tidak ditemukan")

        st.success("✅ Data Tokopedia berhasil diperbarui!")
        st.dataframe(update_df[[update_df.columns[10], update_df.columns[8]]].head(10))

        # Download
        hasil_tokped = update_df.to_excel("hasil_tokopedia.xlsx", index=False)
        with open("hasil_tokopedia.xlsx", "rb") as f:
            st.download_button("📥 Download Hasil Tokopedia", f, file_name="hasil_tokopedia.xlsx")
