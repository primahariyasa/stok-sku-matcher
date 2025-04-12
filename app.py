import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Stok Updater Shopee & Tokopedia", layout="centered")
st.title("📦 Sistem Pembaruan Stok Shopee & Tokopedia")

tab1, tab2, tab3 = st.tabs(["📘 Panduan", "🟠 Shopee", "🟢 Tokopedia"])

# ============================== #
#        TAB 1 - PANDUAN         #
# ============================== #
with tab1:
    st.header("📘 Panduan Penggunaan Sistem")
    st.markdown("""
**Selamat datang di sistem update stok otomatis oleh Prima Hariyasa!**

### 📌 1. Siapkan File Referensi `copybar.xlsx` to `copybar.csv`
- File berasal dari sistem SIP atau copybar internal, tab **Modul > Export Stok Barang**
- Kolom A: SKU (kode barang)  
- Kolom C: Stok (qty)
- Simpan ulang sebagai **`.csv`**

### 📌 2. Siapkan File Mass Update
- **Shopee:** SKU di kolom F, Stok di kolom H  
  - Menu: `Produk Saya > Pengaturan Massal > Mass Update`
  - Pilih **Informasi Penjualan > Buat > Download**
- **Tokopedia:** SKU di kolom K, Stok di kolom I  
  - Menu: `Daftar Produk > Atur Sekaligus > Ubah Sekaligus`
  - Pilih **Informasi Penjualan & Semua Barang > Buat Template > Download**
- Simpan ulang sebagai `.xlsx` dengan nama baru (misal `mass_update_clean.xlsx`)

### 📌 3. Upload dan Proses
- Buka tab **Shopee** atau **Tokopedia**
- Upload file `copybar.csv` dan file mass update
- Sistem akan mencocokkan SKU dan memperbarui stok

💡 Jika SKU tidak ditemukan, stok akan diisi dengan pesan **“SKU tidak ditemukan”**

### 🌐 Informasi Seputar Program
- Program ini bersifat mix & match saja, data yang ditampilkan perlu diolah lebih lanjut pada file excel mass update, 
bayangkan jika kamu mengupdate produk satu per satu, mencarikan sku dan stok di sip lalu update di 2 platform akan memakan waktu lama, 
setidaknya dengan program ini, proses update stok menjadi lebih efektif
- Hasil outputnya juga bisa dijadikan referensi stok dan perbaikan SKU
- Jika sudah selesai, silakan upload kembali file mass_update dari shopee maupun tokopedia
- Salam Hangat, Prima Hariyasa
    """)

# ============================== #
#      Fungsi Referensi Umum     #
# ============================== #
def read_reference_csv(file):
    try:
        file.seek(0)
        df_raw = pd.read_csv(file, sep=None, engine="python", header=None, dtype=str)
        df = df_raw.iloc[1:, [0, 2]]  # Kolom A dan C
        df.columns = ["SKU", "Stok"]
        df["SKU"] = df["SKU"].astype(str).str.zfill(7).str.strip()
        df["Stok"] = df["Stok"].astype(str).str.strip()
        df.dropna(subset=["SKU", "Stok"], inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Gagal membaca file copybar: {e}")
        return None

# ============================== #
#        TAB 2 - SHOPEE          #
# ============================== #
with tab2:
    st.header("🟠 Update Stok Shopee")

    def read_shopee_mass_update(file):
        try:
            df = pd.read_excel(file, header=None, dtype=str)
            df = df.iloc[6:, :].reset_index(drop=True)
            sku_col_e = df.iloc[:, 4]
            sku_col_f = df.iloc[:, 5]

            def resolve_sku(e, f):
                if pd.isna(e) and pd.isna(f):
                    return 'no sku'
                elif pd.notna(e) and str(e).strip() != '':
                    return str(e).split('.')[0].zfill(7).strip()
                elif pd.notna(f) and str(f).strip() != '':
                    return str(f).split('.')[0].zfill(7).strip()
                else:
                    return 'no sku'

            sku_list = [resolve_sku(e, f) for e, f in zip(sku_col_e, sku_col_f)]
            return pd.DataFrame({"SKU": sku_list})
        except Exception as e:
            st.error(f"❌ Gagal membaca file Shopee: {e}")
            return None

    def match_stok(mass_df, reference_df):
        result = mass_df.copy()
        stok_dict = dict(zip(reference_df["SKU"], reference_df["Stok"]))
        result["Stok"] = result["SKU"].apply(
            lambda sku: stok_dict.get(sku, "no sku" if sku == "no sku" else "SKU tidak ditemukan")
        )
        return result

    mass_file = st.file_uploader("📤 Upload file mass update Shopee (.xlsx)", type=["xlsx"], key="shopee")
    ref_file = st.file_uploader("📤 Upload file copybar hasil convert CSV", type=["csv"], key="shopee_ref")

    if mass_file and ref_file:
        with st.spinner("🔍 Mencocokkan data Shopee..."):
            df_mass = read_shopee_mass_update(mass_file)
            df_ref = read_reference_csv(ref_file)

            if df_mass is not None and df_ref is not None:
                result_df = match_stok(df_mass, df_ref)

                st.subheader("✅ Hasil Pencocokan SKU & Stok:")
                st.dataframe(result_df)

                output = BytesIO()
                result_df.to_excel(output, index=False)
                st.download_button(
                    label="📥 Download Hasil SKU & Stok Shopee",
                    data=output.getvalue(),
                    file_name="hasil_stok_shopee.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# ============================== #
#       TAB 3 - TOKOPEDIA        #
# ============================== #
with tab3:
    st.header("🟢 Update Stok Tokopedia")

    def read_tokopedia_mass_update(file):
        try:
            df = pd.read_excel(file, header=None, dtype=str)
            df = df.iloc[4:, :].reset_index(drop=True)
            return df
        except Exception as e:
            st.error(f"❌ Gagal membaca file Tokopedia: {e}")
            return None

    def generate_preview_tokopedia(df_mass, df_ref):
        sku_series = df_mass.iloc[:, 10]
        sku_list = []

        for sku in sku_series:
            if pd.isna(sku) or str(sku).strip() == '':
                sku_list.append("no sku")
            else:
                sku_list.append(str(sku).split('.')[0].zfill(7).strip())

        stok_dict = dict(zip(df_ref["SKU"], df_ref["Stok"]))
        stok_list = []
        for sku in sku_list:
            if sku == "no sku":
                stok_list.append("no sku")
            else:
                stok_list.append(stok_dict.get(sku, "SKU tidak ditemukan"))

        return pd.DataFrame({
            "SKU": sku_list,
            "Stok": stok_list
        })

    mass_file_tokped = st.file_uploader("📤 Upload file mass update Tokopedia (.xlsx)", type=["xlsx"], key="tokped")
    ref_file_tokped = st.file_uploader("📤 Upload file copybar hasil convert CSV", type=["csv"], key="tokped_ref")

    if mass_file_tokped and ref_file_tokped:
        with st.spinner("🔄 Mencocokkan data Tokopedia..."):
            df_mass_tokped = read_tokopedia_mass_update(mass_file_tokped)
            df_ref_tokped = read_reference_csv(ref_file_tokped)

            if df_mass_tokped is not None and df_ref_tokped is not None:
                result_df = generate_preview_tokopedia(df_mass_tokped, df_ref_tokped)

                st.subheader("✅ Hasil Pencocokan SKU & Stok:")
                st.dataframe(result_df)

                output = BytesIO()
                result_df.to_excel(output, index=False)
                st.download_button(
                    label="📥 Download Hasil SKU & Stok Tokopedia",
                    data=output.getvalue(),
                    file_name="hasil_stok_tokopedia.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
