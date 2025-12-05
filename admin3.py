import psycopg2
from psycopg2 import extras
from getpass import getpass 
from datetime import date, timedelta

ADMIN_ROLE_ID = 1
CURRENT_USER = None

def connect_db():
    """Membuat koneksi ke database PostgreSQL."""
    try:
        connection = psycopg2.connect(
            host="127.0.0.1",
            database="SeedMart",
            user="postgres",
            password="12345")
        return connection
    except psycopg2.Error as e:
        print(f"❌ Gagal koneksi ke database: {e}")
        return

def test_connection():
    connection = connect_db()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
        except psycopg2.Error as e:
            print(f"❌ Koneksi terbuat tetapi Query gagal: {e}")
        finally:
            connection.close()

def fetch_data(query, params=None, fetch_one=False):
    """Mengambil data dari database."""
    connection = connect_db()
    if connection is None:
        return [] if not fetch_one else None

    try:
        with connection.cursor(cursor_factory=extras.RealDictCursor) as cursor:
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            else:
                return cursor.fetchall()
    except psycopg2.Error as e:
        print(f"❌ Error saat eksekusi query: {e}")
        return [] if not fetch_one else None
    finally:
        if connection:
            connection.close()

def execute_query(query, params=None, fetch_id=False):
    """Menjalankan query INSERT/UPDATE/DELETE ke database."""
    connection = connect_db()
    if connection is None:
        return False

    return_id = None
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if fetch_id:
                result = cursor.fetchone()
                if result:
                    return_id = result[0]
            connection.commit()
    except psycopg2.Error as e:
        connection.rollback()
        print(f"❌ Error saat eksekusi query: {e}")
        return False
    finally:
        if connection:
            connection.close()
    
    return return_id if fetch_id else True

# ------------------------------------
# 1. Login dan Logout Admin
# ------------------------------------
def login():
    global CURRENT_USER
    print("\n--- 🔒 LOGIN ADMIN ---")
    if CURRENT_USER:
        print(f"Anda sudah login sebagai {CURRENT_USER['username']}.")
        return

    username = input("Username: ")
    password = getpass("Password: ")

    query = """
    SELECT u.id_user, u.username, ur.id_role
    FROM users u
    JOIN user_role ur ON u.id_user = ur.id_user
    JOIN roles r ON ur.id_role = r.id_role
    WHERE u.username = %s AND u.passwords = %s AND ur.id_role = %s
    """
    user_data = fetch_data(query, (username, password, ADMIN_ROLE_ID), fetch_one=True)

    if user_data:
        CURRENT_USER = user_data
        print(f"\n✅ Login berhasil! Selamat datang, {CURRENT_USER['username']}!")
    else:
        print("\n❌ Login gagal. Username atau Password salah, atau Anda bukan Admin.")

def logout():
    global CURRENT_USER
    if CURRENT_USER:
        print(f"\n✅ Logout berhasil. Sampai jumpa, {CURRENT_USER['username']}!")
        CURRENT_USER = None
    else:
        print("\n❌ Anda belum login.")

def main_menu():
    print("""███████╗███████╗███████╗██████╗ ███╗   ███╗ █████╗ ██████╗ ████████╗
██╔════╝██╔════╝██╔════╝██╔══██╗████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝
███████╗█████╗  █████╗  ██║  ██║██╔████╔██║███████║██████╔╝   ██║   
╚════██║██╔══╝  ██╔══╝  ██║  ██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   
███████║███████╗███████╗██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   
╚══════╝╚══════╝╚══════╝╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   """)

    while not CURRENT_USER:
        login()
        if not CURRENT_USER:
            retry = input("\nApakah Anda ingin mencoba login lagi? (y/n): ")
            if retry.lower() != 'y':
                print("Program keluar.")
                return

    while CURRENT_USER:
        print(f"\nSelamat datang, {CURRENT_USER['username']} (Role ID: {CURRENT_USER['id_role']}).")
        print("=== MENU UTAMA ADMIN ===")
        print("1. Manajemen Pengguna (CRUD)")
        print("2. Lihat Data Produk")
        print("3. Lihat Data Transaksi")
        print("4. Akses Laporan Transaksi")
        print("0. Logout")

        choice = input("Pilih opsi: ")

        if choice == '1':
            user_management_menu()
        elif choice == '2':
            view_products()
        elif choice == '3':
            view_transactions()
        elif choice == '4':
            view_transaction_report()
        elif choice == '0':
            logout()
        else:
            print("Pilihan tidak valid.")

# ------------------------------------
# 2. Manajemen Pengguna (CRUD)
# ------------------------------------
def show_users():
    print("\n--- 🧑‍🤝‍🧑 LIHAT DATA PENGGUNA ---")
    query = """
    SELECT u.id_user, u.username, u.email, r.nama_role
    FROM users u
    JOIN user_role ur ON u.id_user = ur.id_user
    JOIN roles r ON ur.id_role = r.id_role
    ORDER BY u.id_user
    """
    users = fetch_data(query)
    if not users:
        print("Belum ada data pengguna.")
        return

    for user in users:
        print(f"ID: {user['id_user']}, Username: {user['username']}, Email: {user['email']}, Role: {user['nama_role']}")

def add_user():
    print("\n--- ➕ TAMBAH PENGGUNA BARU ---")
    username = input("Username Baru: ")
    passwords = getpass("Password (Plain Text): ")
    email = input("Email: ")
    role_id = input("ID Role (1:Admin, 2:Pengelola Toko, 3:Kasir): ")
    id_alamat = 1

    if fetch_data("SELECT id_user FROM users WHERE username = %s", (username,), fetch_one=True):
        print("❌ Username sudah terdaftar.")
        return
    
    query_user = """
    INSERT INTO users (username, passwords, email, id_alamat)
    VALUES (%s, %s, %s, %s)
    RETURNING id_user;
    """
    new_user_id = execute_query(query_user, (username, passwords, email, id_alamat), fetch_id=True)

    if new_user_id:
        query_role = "INSERT INTO user_role (id_user, id_role) VALUES (%s, %s);"
        if execute_query(query_role, (new_user_id, role_id)):
            print("✅ Pengguna '{username}' berhasil ditambahkan dengan ID: {new_user_id}.")
        else:
            print("❌ Gagal menambahkan role pengguna. Menghapus user yang baru dibuat.")
            execute_query("DELETE FROM users WHERE id_user = %s", (new_user_id,))
    else:
        print("❌ Gagal menambahkan pengguna.")

def edit_user():
    print("\n--- ✏️ EDIT PENGGUNA ---")
    user_id = input("Masukkan ID Pengguna yang akan diedit: ")

    user = fetch_data("SELECT u.username, ur.id_role FROM users u JOIN user_role ur ON u.id_user = ur.id_user WHERE u.id_user = %s", (user_id,), fetch_one=True)
    if not user:
        print("❌ Pengguna tidak ditemukan.")
        return

    print(f"Mengedit Pengguna: {user['username']}")
    new_password = getpass("Password Baru (kosongkan jika tidak diubah): ")
    new_role_id = input(f"ID Role Baru (kosongkan jika tidak diubah, saat ini: {user['id_role']}): ")

    updates = []
    params = []

    if new_password:
        updates.append("passwords = %s")
        params.append(new_password)
    
    if updates:
        query_user = f"UPDATE users SET {', '.join(updates)} WHERE id_user = %s"
        params.append(user_id)
        execute_query(query_user, params)
        print("✅ Password pengguna berhasil diperbarui.")

    if new_role_id:
        query_role = "UPDATE user_role SET id_role = %s WHERE id_user = %s"
        execute_query(query_role, (new_role_id, user_id))
        print("✅ Role pengguna berhasil diperbarui.")
    
    if not updates and not new_role_id:
        print("Tidak ada perubahan yang dilakukan.")

def delete_user():
    print("\n--- 🗑️ HAPUS PENGGUNA ---")
    user_id = input("Masukkan ID Pengguna yang akan dihapus: ")

    query_role = "DELETE FROM user_role WHERE id_user = %s"
    if execute_query(query_role, (user_id,)):
        query_user = "DELETE FROM users WHERE id_user = %s"
        if execute_query(query_user, (user_id,)):
            print(f"✅ Pengguna ID {user_id} berhasil dihapus.")
        else:
            print("❌ Gagal menghapus pengguna dari tabel users.")
    else:
        print("❌ Gagal menghapus role pengguna.")

def user_management_menu():
    while True:
        print("\n=== MENU MANAJEMEN PENGGUNA ===")
        print("1. Lihat Semua Pengguna")
        print("2. Tambah Pengguna")
        print("3. Edit Pengguna")
        print("4. Hapus Pengguna")
        print("0. Kembali ke Menu Utama")

        choice = input("Pilih opsi: ")

        if choice == '1':
            show_users()
        elif choice == '2':
            add_user()
        elif choice == '3':
            edit_user()
        elif choice == '4':
            delete_user()
        elif choice == '0':
            break
        else:
            print("Pilihan tidak valid.")

# ------------------------------------
# 3. Lihat Data Produk
# ------------------------------------
def view_products():
    print("\n--- 📦 DATA PRODUK ---")
    query = """
    SELECT p.id_produk, p.nama_produk, p.stok, p.harga, k.nama_kategori, u.username as pemilik
    FROM produk p
    JOIN kategori k ON p.id_kategori = k.id_kategori
    JOIN users u ON p.id_user = u.id_user
    ORDER BY p.id_produk
    """
    products = fetch_data(query)

    if not products:
        print("Belum ada data produk.")
        return

    for p in products:
        print(f"ID: {p['id_produk']}, Nama: {p['nama_produk']}, Stok: {p['stok']}, Harga: {p['harga']}, Kategori: {p['nama_kategori']}, Pemilik: {p['pemilik']}")
# ------------------------------------
# 4. Lihat Data Transaksi
# ------------------------------------
def view_transactions():
    print("\n--- 💵 DATA TRANSAKSI ---")
    query = """
    SELECT 
        t.id_transaksi, 
        t.status, 
        t.total_harga, 
        dt.tanggal, 
        u.username AS kasir, 
        p.nama_produk, 
        dt.jumlah_produk, 
        m.nama_metode
    FROM transaksi t
    JOIN users u ON t.id_user = u.id_user
    JOIN detail_transaksi dt ON t.id_detail_transaksi = dt.id_detail_transaksi
    JOIN produk p ON dt.id_produk = p.id_produk
    JOIN metode_pembayaran m ON t.id_metode = m.id_metode
    ORDER BY dt.tanggal DESC
    """
    transactions = fetch_data(query)

    if not transactions:
        print("Belum ada data transaksi.")
        return

    for t in transactions:
        print(f"ID Trans: {t['id_transaksi']}, Tgl: {t['tanggal']}, Status: {t['status']}, Total: {t['total_harga']}, Kasir: {t['kasir']}, Produk: {t['nama_produk']} ({t['jumlah_produk']}x), Metode: {t['nama_metode']}")

# ------------------------------------
# 5. Laporan Data Transaksi
# ------------------------------------
def view_transaction_report():
    print("\n--- 📊 LAPORAN TRANSAKSI ---")
    print("Pilih Periode Laporan:")
    print("1. Harian")
    print("2. Mingguan")
    print("3. Bulanan")
    choice = input("Pilih opsi (1-3): ")

    params = None
    date_filter = None
    
    if choice == '1':
        date_param = input("Masukkan Tanggal (YYYY-MM-DD): ")
        date_filter = "CAST(dt.tanggal AS DATE) = %s"
        params = (date_param,)
        print(f"\n--- Laporan Harian: {date_param} ---")
    elif choice == '2':
        week_param = input("Masukkan Nomor Minggu Tahun (YYYY-WW, misal 2025-47): ")
        date_filter = "TO_CHAR(CAST(dt.tanggal AS DATE), 'YYYY-WW') = %s"
        params = (week_param,)
        print(f"\n--- Laporan Mingguan: {week_param} ---")
    elif choice == '3':
        month_param = input("Masukkan Bulan Tahun (YYYY-MM, misal 2025-11): ")
        date_filter = "TO_CHAR(CAST(dt.tanggal AS DATE), 'YYYY-MM') = %s"
        params = (month_param,)
        print(f"\n--- Laporan Bulanan: {month_param} ---")
    else:
        print("Pilihan tidak valid.")
        return
    
    query = f"""
    SELECT 
        COUNT(t.id_transaksi) AS total_transaksi,
        SUM(t.total_harga) AS total_penghasilan,
        COUNT(CASE WHEN t.status = 'Selesai' THEN 1 END) AS transaksi_selesai,
        COUNT(CASE WHEN t.status = 'Gagal' THEN 1 END) AS transaksi_gagal
    FROM transaksi t
    JOIN detail_transaksi dt ON t.id_detail_transaksi = dt.id_detail_transaksi
    WHERE {date_filter}
    """
    
    report = fetch_data(query, params, fetch_one=True)

    if report and report['total_transaksi'] is not None and report['total_transaksi'] > 0:
        print(f"Total Transaksi: {report['total_transaksi']}")
        total_penghasilan = report['total_penghasilan'] if report['total_penghasilan'] is not None else 0.00
        
        print(f"Total Penghasilan (Semua Status): Rp {total_penghasilan:,.2f}")
        print(f"Transaksi Selesai: {report['transaksi_selesai']}")
        print(f"Transaksi Gagal: {report['transaksi_gagal']}")
    else:
        print("Tidak ada data transaksi untuk periode ini.")




if __name__ == "__main__":
    test_connection()
    main_menu()