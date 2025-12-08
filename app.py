import os
import sys

def main():
    while True:
        print("=== Sistem Login ===")
        print("1. Login sebagai Admin")
        print("2. Login sebagai Kasir")
        print("3. Login sebagai Pengelola")
        print("4. Keluar")

        pilihan = input("Pilih menu (1/2/3/4): ")
        if pilihan == "1":
            # Menjalankan admin3.py
            os.system(f"{sys.executable} admin3.py")

        elif pilihan == "2":
            # Menjalankan transaksi.py
            os.system(f"{sys.executable} transaksi.py")

        elif pilihan == "3":
            # Menjalankan pengelola.py
            os.system(f"{sys.executable} pengelola.py")

        elif pilihan == "4":
            print("Keluar dari program...")
            break

        else:
            print("Pilihan tidak valid, coba lagi!\n")

if __name__ == "__main__":
    main()
