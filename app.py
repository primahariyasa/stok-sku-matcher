import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Stok Updater Shopee & Tokopedia", layout="centered")

st.title("📦 Sistem Pembaruan Stok Shopee & Tokopedia")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📘 Panduan", "🛍️ Shopee", "🟢 Tokopedia"])

# --- Tab 1: Panduan ---
with tab1:
    st.header("📘 Panduan Penggunaan Sistem")
    st.markdown("""
    Selamat datang di sistem update stok otomatis oleh Prima Hariyasa!

    ### 📌 1. Siapkan File Referensi `copybar.xlsx` to `.csv`
    - File berasal dari sistem SIP atau copybar internal yakni dari tab `Modul` lalu klik `Export Stok Barang`.
    - Kolom A: SKU (kode barang)
    - Kolom C: Stok
    - **Simpan ulang sebagai `.csv`** agar bisa digunakan di sistem ini.

    ### 📌 2. Siapkan File Mass Update
    - **Shopee:** Gunakan file export mass update, SKU di kolom F, Stok di kolom H
        - **Cara download** : Masuk pada menu `Produk Saya` lalu pada kanan atas layar klik `Pengaturan Massal` > `Update Update`
        - Pilih bullets `Informasi Penjualan` klik `Buat` lalu `Download`
    - **Tokopedia:** Gunakan file export mass update, SKU di kolom K, Stok di kolom I
        - **Cara download** : Masuk pada menu `Daftar Produk` lalu pada kanan atas layar klik `Atur Sekaligus` > `Ubah Sekaligus`
        - Pilih bullets `Informasi Penjualan` dan `Semua Barang` lalu `Buat Template` dan Download
    - **Simpan ulang (Save As) sebagai `.xlsx`** untuk memastikan format valid dengan nama yang baru (misal : mass_update_clean.xlsx).

    ### 📌 3. Upload dan Proses
    - Buka tab **Shopee** atau **Tokopedia**
    - Upload file `copybar.csv` dan file mass update
    - Sistem akan memperbarui stok berdasarkan pencocokan SKU

    💡 *Jika SKU tidak ditemukan, stok akan diisi dengan pesan “SKU tidak ditemukan”*
    """)

# --- Fungsi Umum ---
def read_reference(file):
    try:
        try:
            df_raw = pd.read_csv(file, header=None, dtype=str)
        except pd.errors.ParserError:
            file.seek(0)
            df_raw = pd.read_csv(file, header=None, delimiter=';', dtype=str)

        df = df_raw.iloc[1:, [0, 2]]
        df.columns = ["SKU", "Stok"]
        df["SKU"] = df["SKU"].astype(str).str.zfill(7).str.strip()
        df["Stok"] = df["Stok"].astype(str).str.strip()
        df.dropna(subset=["SKU", "Stok"], inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Gagal membaca file referensi: {e}")
        return None

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# --- Tab 2: Shopee ---
with tab2:
    st.subheader("🛍️ Mass Update Shopee")
    st.caption("📌 Kolom SKU: F (index 5), Kolom Stok: H (index 7)")

    ref_file = st.file_uploader("📋 Upload File Referensi (CSV Copybar)", type=["csv"], key="shopee_ref")
    shopee_file = st.file_uploader("🗂️ Upload File Mass Update Shopee (.xlsx)", type=["xlsx"], key="shopee_mass")

    if ref_file and shopee_file:
        with st.spinner("🔄 Memproses file Shopee..."):
            ref_df = read_reference(ref_file)
            try:
                df = pd.read_excel(shopee_file, header=None, dtype=str)
                df = df.iloc[6:, :].reset_index(drop=True)  # mulai dari baris ke-7

                df['SKU'] = df.iloc[:, 5].astype(str).str.split('.').str[0].str.zfill(7).str.strip()
                stok_dict = dict(zip(ref_df["SKU"], ref_df["Stok"]))
                df['Stok Baru'] = df['SKU'].apply(lambda sku: stok_dict.get(sku, "SKU tidak ditemukan"))

                df.iloc[:, 7] = df['Stok Baru']  # kolom stok = kolom H

                result_df = df[['SKU', df.columns[7]]]
                st.success("✅ Data Shopee berhasil diperbarui!")
                st.dataframe(result_df)

                output = convert_df_to_excel(result_df)
                st.download_button(
                    label="⬇️ Download Hasil Shopee",
                    data=output.getvalue(),
                    file_name="stok-update-shopee.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"❌ Gagal membaca file Shopee: {e}")

# --- Tab 3: Tokopedia ---
with tab3:
    st.subheader("🟢 Mass Update Tokopedia")
    st.caption("📌 Kolom SKU: K (index 10), Kolom Stok: I (index 8)")

    ref_file_tokped = st.file_uploader("📋 Upload File Referensi (CSV Copybar)", type=["csv"], key="tokped_ref")
    tokped_file = st.file_uploader("🗂️ Upload File Mass Update Tokopedia (.xlsx)", type=["xlsx"], key="tokped_mass")

    if ref_file_tokped and tokped_file:
        with st.spinner("🔄 Memproses file Tokopedia..."):
            ref_df = read_reference(ref_file_tokped)
            try:
                df = pd.read_excel(tokped_file, header=None, dtype=str)
                df = df.iloc[2:, :].reset_index(drop=True)  # mulai dari baris ke-3

                sku_col = df.iloc[:, 10]
                df['SKU'] = sku_col.apply(
                    lambda x: str(x).split('.')[0].zfill(7).strip()
                    if pd.notna(x) and str(x).strip().lower() != 'nan' else 'no sku'
                )

                stok_dict = dict(zip(ref_df["SKU"], ref_df["Stok"]))
                df['Stok Baru'] = df['SKU'].apply(
                    lambda sku: stok_dict.get(sku, "SKU tidak ditemukan") if sku != "no sku" else "no sku"
                )

                df.iloc[:, 8] = df['Stok Baru']  # kolom stok = kolom I

                result_df = df[['SKU', df.columns[8]]]
                st.success("✅ Data Tokopedia berhasil diperbarui!")
                st.dataframe(result_df)

                output = convert_df_to_excel(result_df)
                st.download_button(
                    label="⬇️ Download Hasil Tokopedia",
                    data=output.getvalue(),
                    file_name="stok-update-tokopedia.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"❌ Gagal membaca file Tokopedia: {e}")
