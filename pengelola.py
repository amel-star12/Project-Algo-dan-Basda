import psycopg2
import getpass

# -----------------------------------------------------
# KONEKSI DATABASE
# -----------------------------------------------------
def get_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        database="SeedMart",
        user="postgres",
        password="12345"
    )


# -----------------------------------------------------
# LOGIN
# -----------------------------------------------------
def login():
    conn = get_connection()
    cursor = conn.cursor()

    print("=== LOGIN ===")
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    query = """
    SELECT u.id_user, u.username, ur.id_role
    FROM users u
    JOIN user_role ur ON u.id_user = ur.id_user
    WHERE u.username = %s AND u.passwords = %s
    """
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        id_user, user_name, id_role = result

        if id_role == 2:
            print(f"\nLogin berhasil! Selamat datang {user_name}.")
            return id_user
        else:
            print("\n❌ Akses ditolak. Role Anda bukan 2.")
            return None
    else:
        print("\n❌ Username atau password salah.")
        return None


# -----------------------------------------------------
# TAMBAH PRODUK
# -----------------------------------------------------
def tambah_produk(id_user):
    conn = get_connection()
    cursor = conn.cursor()

    print("\n=== TAMBAH PRODUK ===")
    nama = input("Nama produk: ")
    stok = int(input("Stok: "))
    harga = int(input("Harga: "))
    id_kategori = int(input("ID kategori: "))
    diskon = float(input("Diskon (misal 0.1 untuk 10%): "))

    query = """
    INSERT INTO produk (nama_produk, stok, harga, id_kategori, id_user, diskon)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (nama, stok, harga, id_kategori, id_user, diskon))
    conn.commit()

    print("✔ Produk berhasil ditambahkan.")

    cursor.close()
    conn.close()


# -----------------------------------------------------
# EDIT PRODUK
# -----------------------------------------------------
def edit_produk(id_user):
    conn = get_connection()
    cursor = conn.cursor()

    print("\n=== EDIT PRODUK ===")
    id_produk = int(input("Masukkan ID produk yang ingin diedit: "))

    # Ambil data lama
    cursor.execute("""
        SELECT nama_produk, stok, harga, id_kategori, diskon
        FROM produk
        WHERE id_produk = %s AND id_user = %s
    """, (id_produk, id_user))

    row = cursor.fetchone()

    if row is None:
        print("❌ Produk tidak ditemukan atau bukan milik Anda.")
        return

    old_nama, old_stok, old_harga, old_kategori, old_diskon = row

    print("\nTekan ENTER untuk tidak mengubah field.\n")

    # Input baru (boleh kosong)
    nama = input(f"Nama produk ({old_nama}): ") or old_nama
    stok_input = input(f"Stok ({old_stok}): ")
    harga_input = input(f"Harga ({old_harga}): ")
    kategori_input = input(f"ID kategori ({old_kategori}): ")
    diskon_input = input(f"Diskon ({old_diskon}): ")

    # Konversi jika diisi
    stok = int(stok_input) if stok_input else old_stok
    harga = int(harga_input) if harga_input else old_harga
    id_kategori = int(kategori_input) if kategori_input else old_kategori
    diskon = float(diskon_input) if diskon_input else old_diskon

    # Update
    query = """
        UPDATE produk
        SET nama_produk = %s,
            stok = %s,
            harga = %s,
            id_kategori = %s,
            diskon = %s
        WHERE id_produk = %s AND id_user = %s
    """

    cursor.execute(query, (nama, stok, harga, id_kategori, diskon, id_produk, id_user))
    conn.commit()

    print("✔ Produk berhasil diupdate.")

    cursor.close()
    conn.close()



# -----------------------------------------------------
# HAPUS PRODUK
# -----------------------------------------------------
def hapus_produk(id_user):
    conn = get_connection()
    cursor = conn.cursor()

    print("\n=== HAPUS PRODUK ===")
    id_produk = int(input("Masukkan ID produk yang ingin dihapus: "))

    # cek kepemilikan produk
    cursor.execute("SELECT id_produk FROM produk WHERE id_produk = %s AND id_user = %s",
                   (id_produk, id_user))
    if cursor.fetchone() is None:
        print("❌ Produk tidak ditemukan atau bukan milik Anda.")
        return

    cursor.execute("DELETE FROM produk WHERE id_produk = %s AND id_user = %s",
                   (id_produk, id_user))
    conn.commit()

    print("✔ Produk berhasil dihapus.")

    cursor.close()
    conn.close()


    # -----------------------------------------------------
# LIHAT PRODUK
# -----------------------------------------------------
def lihat_produk(id_user):
    conn = get_connection()
    cursor = conn.cursor()

    print("\n=== DAFTAR PRODUK ANDA ===")

    query = """
    SELECT id_produk, nama_produk, stok, harga, id_kategori, diskon
    FROM produk
    WHERE id_user = %s
    ORDER BY id_produk
    """
    cursor.execute(query, (id_user,))
    rows = cursor.fetchall()

    if not rows:
        print("Tidak ada produk.")
    else:
        print("\nID | Nama Produk | Stok | Harga | Kategori | Diskon")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")

    cursor.close()
    conn.close()



# -----------------------------------------------------
# MENU UTAMA
# -----------------------------------------------------
def menu(id_user):
    while True:
        print("\n=== MENU PRODUK ===")
        print("1. Tambah Produk")
        print("2. Edit Produk")
        print("3. Hapus Produk")
        print("4. Lihat Produk")
        print("5. Keluar")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_produk(id_user)
        elif pilihan == "2":
            edit_produk(id_user)
        elif pilihan == "3":
            hapus_produk(id_user)
        elif pilihan == "4":
            lihat_produk(id_user)
        elif pilihan == "5":
            print("Keluar...")
            break
        else:
            print("❌ Pilihan tidak valid.")



# -----------------------------------------------------
# MAIN PROGRAM
# -----------------------------------------------------
if __name__ == "__main__":
    user_id = login()
    if user_id:
        menu(user_id)
