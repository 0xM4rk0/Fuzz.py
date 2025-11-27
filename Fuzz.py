#!/usr/bin/env python3

import os
import sys
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import random

# Colores ANSI
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
RESET   = "\033[0m"

# Lista de User-Agent aleatorios
agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Linux; Android 11)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Kali Linux x86_64)",
]

print('''

███████╗██╗   ██╗███████╗███████╗   ██████╗ ██╗   ██╗
██╔════╝██║   ██║╚══███╔╝╚══███╔╝   ██╔══██╗╚██╗ ██╔╝
█████╗  ██║   ██║  ███╔╝   ███╔╝    ██████╔╝ ╚████╔╝ 
██╔══╝  ██║   ██║ ███╔╝   ███╔╝     ██╔═══╝   ╚██╔╝  
██║     ╚██████╔╝███████╗███████╗██╗██║        ██║   
╚═╝      ╚═════╝ ╚══════╝╚══════╝╚═╝╚═╝        ╚═╝   

''')

def fuzz_url(url, word, timeout, save_file):
    objetivo = url + word
    headers = {"User-Agent": random.choice(agents)}

    try:
        response = requests.get(objetivo, timeout=timeout, headers=headers)
        code = response.status_code
        size = len(response.content)

        # Guardar resultados válidos
        if code < 400:
            with open(save_file, "a") as f:
                f.write(f"{code} | {size} bytes | {objetivo}\n")

        # Impresión con colores
        if code == 200:
            print(GREEN + f"[200] {objetivo} ({size} bytes)" + RESET)
        elif 300 <= code < 400:
            print(YELLOW + f"[3XX] {objetivo} ({size} bytes)" + RESET)
        elif 400 <= code < 500:
            print(RED + f"[4XX] {objetivo} ({size} bytes)" + RESET)
        elif 500 <= code < 600:
            print(MAGENTA + f"[5XX] {objetivo} ({size} bytes)" + RESET)
        else:
            print(CYAN + f"[{code}] {objetivo} ({size} bytes)" + RESET)

    except requests.exceptions.RequestException:
        return


def main():
    parser = argparse.ArgumentParser(description="Quick fuzz.py")

    parser.add_argument("-u", "--url", required=True, help="URL objetivo (terminada en /)")
    parser.add_argument("-w", "--wordlist", required=True, help="Ruta de la wordlist")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Número de hilos")
    parser.add_argument("-to", "--timeout", type=int, default=5, help="Timeout por request")
    parser.add_argument("-o", "--output", default="results.txt", help="Archivo para guardar resultados")

    args = parser.parse_args()

    # Validar URL
    if not args.url.endswith("/"):
        args.url += "/"

    # Validar wordlist
    if not os.path.isfile(args.wordlist):
        print(RED + "[-] La wordlist no existe." + RESET)
        sys.exit(1)

    print("\n[+] Cargando wordlist...\n")
    with open(args.wordlist, "r", errors="ignore") as f:
        words = [x.strip() for x in f if x.strip()]

    print(f"[+] {len(words)} palabras cargadas.")
    print(f"[+] Hilos: {args.threads}")
    print(f"[+] Guardando resultados en: {args.output}\n")

    # Limpiar archivo previo
    open(args.output, "w").close()

    print("[+] Iniciando fuzzing...\n")

    # Barra de progreso + multihilo
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        list(tqdm(
            executor.map(lambda w: fuzz_url(args.url, w, args.timeout, args.output), words),
            total=len(words),
            desc="Progreso"
        ))

    print("\n\n[+] Finalizado.")
    print(f"[+] Resultados guardados en: {args.output}\n")


if __name__ == "__main__":
    main()
