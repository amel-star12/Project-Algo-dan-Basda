# Program Kasir Lengkap dengan Fitur Transaksi
# Simpan file ini dengan nama: sistem_kasir.py

import psycopg2
from psycopg2 import Error, sql
from datetime import datetime
import os

def konek():
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="123",
            host="127.0.0.1",
            port="5432",
            database="database_projek"
        )
        cursor = connection.cursor()
        return connection, cursor
    except (Exception, Error) as error:
        print(f"Error koneksi database: {error}")
        return None, None

def komit(connection, cursor):
    connection.commit()
    boolean = cursor.rowcount
    cursor.close()
    connection.close()
    return boolean

# Data pengguna dengan role berbeda
data_pengguna = {
    'admin': {'password': 'admin123', 'nama': 'Administrator', 'role': 'Admin'},
    'pengelola1': {'password': 'pengelola123', 'nama': 'Andi Wijaya', 'role': 'Pengelola'},
    'pengelola2': {'password': 'pengelola456', 'nama': 'Dewi Lestari', 'role': 'Pengelola'},
    'kasir1': {'password': '123', 'nama': 'Budi Santoso', 'role': 'Kasir'},
    'kasir2': {'password': '456', 'nama': 'Siti Aminah', 'role': 'Kasir'},
    'kasir3': {'password': '789', 'nama': 'Joko Susilo', 'role': 'Kasir'}
}

# Data transaksi (disimpan dalam list)
data_transaksi = []

# Nama kasir default
NAMA_KASIR = "Kasir Toko"
USERNAME_LOGIN = None

def clear_screen():
    """Fungsi untuk membersihkan layar"""
    os.system('cls' if os.name == 'nt' else 'clear')

def tampilkan_header(judul):
    """Fungsi untuk menampilkan header"""
    print("=" * 60)
    print(f" {judul}")
    print("=" * 60)
    print()

def validasi_huruf(teks, nama_field):
    """Fungsi untuk validasi input harus huruf"""
    while True:
        nilai = input(f"{nama_field}: ").strip()
        
        if not nilai:
            print("Input tidak boleh kosong!")
            continue
            
        if nilai.lower() == 'selesai':
            return 'selesai'
        
        # Cek apakah mengandung huruf (boleh ada spasi)
        if any(c.isalpha() for c in nilai):
            return nilai
        else:
            print("Input harus mengandung huruf! Silakan coba lagi.")

def validasi_angka(teks, nama_field, tipe='int'):
    """Fungsi untuk validasi input harus angka"""
    while True:
        try:
            nilai = input(f"{nama_field}: ").strip()
            
            if not nilai:
                print("❌ Input tidak boleh kosong!")
                continue
            
            if tipe == 'int':
                angka = int(nilai)
                if angka <= 0:
                    print("❌ Jumlah harus lebih dari 0!")
                    continue
                return angka
            elif tipe == 'float':
                angka = float(nilai)
                if angka <= 0:
                    print("❌ Harga harus lebih dari 0!")
                    continue
                return angka
        except ValueError:
            print("❌ Input harus berupa angka! Silakan coba lagi.")

def tampilkan_menu():
    """Fungsi untuk menampilkan menu utama"""
    print("\n" + "=" * 60)
    print(" MENU UTAMA")
    print("=" * 60)
    print("1. Lihat Data Transaksi Hari Ini")
    print("2. Tambah Transaksi Baru")
    print("3. Logout")
    print("=" * 60)

def lihat_transaksi():
    """Fungsi untuk melihat transaksi hari ini"""
    clear_screen()
    tampilkan_header("DATA TRANSAKSI HARI INI")
    
    tanggal_hari_ini = datetime.now().strftime("%d-%m-%Y")
    transaksi_hari_ini = [t for t in data_transaksi if t['tanggal'] == tanggal_hari_ini]
    
    if not transaksi_hari_ini:
        print("Belum ada transaksi hari ini.\n")
    else:
        print(f"Tanggal: {tanggal_hari_ini}")
        print(f"Total Transaksi: {len(transaksi_hari_ini)}\n")
        print("-" * 60)
        
        total_pendapatan = 0
        for i, transaksi in enumerate(transaksi_hari_ini, 1):
            print(f"\nTransaksi #{i}")
            print(f"Waktu: {transaksi['waktu']}")
            print(f"Kasir: {transaksi['kasir']}")
            print(f"Metode Pembayaran: {transaksi['metode_pembayaran']}")
            print(f"Total: Rp {transaksi['total_harga']:,.2f}")
            print("-" * 60)
            total_pendapatan += transaksi['total_harga']
        
        print(f"\nTotal Pendapatan Hari Ini: Rp {total_pendapatan:,.2f}")
    
    input("\nTekan Enter untuk kembali...")

def input_item():
    """Fungsi untuk input data item dengan validasi"""
    items = []
    
    print("\nMasukkan data item (ketik 'selesai' pada jenis untuk mengakhiri)")
    print("-" * 60)
    
    while True:
        print(f"\n{'='*60}")
        print(f"Item ke-{len(items) + 1}")
        print("=" * 60)
        
        # Input jenis barang (harus huruf)
        jenis = validasi_huruf("", "Jenis Barang")
        
        if jenis == 'selesai':
            if len(items) == 0:
                print("\nMinimal harus ada 1 item!")
                continue
            break
        
        # Input jumlah (harus angka integer)
        jumlah = validasi_angka("", "Jumlah", 'int')
        
        # Input harga satuan (harus angka)
        harga = validasi_angka("", "Harga Satuan (Rp)", 'float')
        
        # Hitung total item
        total_item = jumlah * harga
        
        item = {
            'jenis': jenis,
            'jumlah': jumlah,
            'harga': harga,
            'total': total_item
        }
        
        items.append(item)
        print(f"\nItem ditambahkan!")
        print(f"   {jenis} x {jumlah} = Rp {total_item:,.2f}")
        
        # Tanya apakah ingin menambah item lagi
        print("\n" + "-" * 60)
        tambah_lagi = input("Tambah item lagi? (y/n): ").lower()
        if tambah_lagi != 'y':
            break
    
    return items

def pilih_metode_pembayaran():
    """Fungsi untuk memilih metode pembayaran"""
    print("\n" + "=" * 60)
    print(" METODE PEMBAYARAN")
    print("=" * 60)
    print("1. Tunai")
    print("2. QRIS")
    print("3. Transfer Bank")
    print("=" * 60)
    
    while True:
        pilihan = input("\nPilih metode pembayaran (1-3): ").strip()
        
        if pilihan == '1':
            return "Tunai"
        elif pilihan == '2':
            return "QRIS"
        elif pilihan == '3':
            return "Transfer Bank"
        else:
            print("Pilihan tidak valid! Pilih 1-3.")

def tampilkan_struk(transaksi):
    """Fungsi untuk menampilkan struk digital"""
    clear_screen()
    print("\n" + "=" * 60)
    print(" STRUK PEMBAYARAN")
    print("=" * 60)
    print(f"Tanggal: {transaksi['tanggal']}")
    print(f"Waktu: {transaksi['waktu']}")
    print(f"Kasir: {transaksi['kasir']}")
    print("=" * 60)
    print(f"{'ITEM':<25} {'QTY':<8} {'HARGA':<12} {'TOTAL':<12}")
    print("-" * 60)
    
    for item in transaksi['items']:
        jenis = item['jenis'][:24]
        print(f"{jenis:<25} {item['jumlah']:<8} Rp {item['harga']:>9,.0f} Rp {item['total']:>9,.0f}")
    
    print("-" * 60)
    print(f"{'TOTAL PEMBAYARAN':<48} Rp {transaksi['total_harga']:>9,.0f}")
    print(f"Metode Pembayaran: {transaksi['metode_pembayaran']}")
    print("=" * 60)
    print(" TERIMA KASIH ATAS KUNJUNGAN ANDA!")
    print("=" * 60)

def tambah_transaksi():
    """Fungsi untuk menambah transaksi baru"""
    clear_screen()
    tampilkan_header("TAMBAH TRANSAKSI BARU")
    
    # Input items
    items = input_item()
    
    if not items:
        print("\nTidak ada item yang dimasukkan!")
        input("\nTekan Enter untuk kembali...")
        return
    
    # Hitung total
    total_harga = sum(item['total'] for item in items)
    
    # Pilih metode pembayaran
    metode_pembayaran = pilih_metode_pembayaran()
    
    # Buat data transaksi
    transaksi = {
        'tanggal': datetime.now().strftime("%d-%m-%Y"),
        'waktu': datetime.now().strftime("%H:%M:%S"),
        'kasir': NAMA_KASIR,
        'items': items,
        'total_harga': total_harga,
        'metode_pembayaran': metode_pembayaran
    }
    
    # Simpan transaksi
    data_transaksi.append(transaksi)
    
    # Tampilkan struk
    tampilkan_struk(transaksi)
    
    print("\nTransaksi berhasil disimpan!")
    input("\nTekan Enter untuk kembali...")

def login():
    """Fungsi untuk melakukan login"""
    tampilkan_header("SISTEM LOGIN KASIR")
    
    print("Silakan login terlebih dahulu\n")
    
    username = input("Username: ").strip()
    password = input("Password: ")
    
    if username in data_pengguna:
        if data_pengguna[username]['password'] == password:
            return True, username
        else:
            print("\nPassword salah!")
            return False, None
    else:
        print("\nUsername tidak ditemukan!")
        return False, None

def dashboard(username):
    """Fungsi untuk menampilkan dashboard"""
    global NAMA_KASIR, USERNAME_LOGIN
    NAMA_KASIR = data_pengguna[username]['nama']
    USERNAME_LOGIN = username
    
    while True:
        clear_screen()
        
        print("=" * 60)
        print(" DASHBOARD KASIR")
        print("=" * 60)
        print(f"\nKasir: {NAMA_KASIR}")
        print(f"Role: {data_pengguna[username]['role']}")
        print(f"Tanggal: {datetime.now().strftime('%d-%m-%Y')}")
        print(f"Waktu: {datetime.now().strftime('%H:%M:%S')}")
        
        tampilkan_menu()
        
        pilihan = input("\nPilih menu (1-3): ").strip()
        
        if pilihan == '1':
            lihat_transaksi()
        elif pilihan == '2':
            tambah_transaksi()
        elif pilihan == '3':
            print("\nLogout berhasil. Terima kasih!")
            break
        else:
            print("\nPilihan tidak valid!")
            input("\nTekan Enter untuk kembali...")

def main():
    """Fungsi utama program"""
    while True:
        clear_screen()
        
        berhasil, username = login()
        
        if berhasil:
            input("\nLogin berhasil! Tekan Enter untuk melanjutkan...")
            dashboard(username)
            
            coba_lagi = input("\nLogin dengan akun lain? (y/n): ").lower()
            if coba_lagi != 'y':
                print("\nTerima kasih telah menggunakan sistem kasir!")
                break
        else:
            coba_lagi = input("\nCoba login lagi? (y/n): ").lower()
            if coba_lagi != 'y':
                print("\nTerima kasih!")
                break

if __name__ == "__main__":
    clear_screen()
    print("\n" + "=" * 60)
    print(" SELAMAT DATANG DI SISTEM KASIR")
    print("=" * 60)
    print("\nINFO AKUN DEMO:")
    print("-" * 60)
    print("ADMIN:")
    print("   Username: admin      | Password: admin123")
    print("\nPENGELOLA:")
    print("   Username: pengelola1 | Password: pengelola123")
    print("   Username: pengelola2 | Password: pengelola456")
    print("\nKASIR:")
    print("   Username: kasir1     | Password: 123")
    print("   Username: kasir2     | Password: 456")
    print("   Username: kasir3     | Password: 789")
    print("-" * 60)
    input("\nTekan Enter untuk memulai...")
    
    main()
