import socket
import os
import sys

# On definit l'adresse d'ecoute et le port
# 0.0.0.0 permet d'ecouter sur toutes les interfaces (indispensable pour une VM)
HOST = "0.0.0.0"
PORT = 4444

def gerer_client(conn, addr):
    print(f"[+] Nouvelle connexion depuis {addr}")
    
    # Boucle infinie pour discuter avec le client
    while True:
        try:
            # On affiche un prompt avec l'IP du client pour faire pro
            cmd = input(f"{addr} > ")
            
            # Si on tape exit, on envoie l'ordre de fermeture au client
            if cmd == "exit":
                conn.send(b"exit")
                break
                
            # Envoi de la commande (on doit l'encoder en bytes pour le reseau)
            conn.send(cmd.encode("utf-8"))
            
            # Reception de la reponse (max 4096 octets pour eviter de saturer)
            reponse = conn.recv(4096).decode("utf-8")
            
            # Si la reponse est vide, c'est que le client a crash ou s'est deconnecte
            if not reponse:
                print("[-] Le client a ferme la connexion.")
                break
                
            print(reponse)
            
        except Exception as e:
            print(f"[-] Erreur avec le client : {e}")
            break

    # On ferme proprement la connexion
    conn.close()
    
    # sys.exit(0) est TRES important ici. 
    # Comme on est dans un processus "enfant" (cree par fork), 
    # ca tue uniquement l'enfant et pas le serveur principal.
    sys.exit(0)

def main():
    # Creation du socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Option pour eviter l'erreur "Address already in use" quand on relance le script
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(5) # File d'attente de 5 clients max
        print(f"[*] Serveur en ecoute sur le port {PORT}...")
    except Exception as e:
        print(f"[-] Impossible de demarrer le serveur : {e}")
        sys.exit(1)

    # Boucle principale pour accepter les connexions
    while True:
        # Le serveur attend qu'un client se connecte
        conn, addr = server.accept()
        
        # --- CREATION DU PROCESSUS ENFANT (demande par le prof) ---
        pid = os.fork()
        
        if pid == 0:
            # Code du processus ENFANT
            # L'enfant n'a pas besoin d'ecouter sur le port, on le ferme
            server.close() 
            gerer_client(conn, addr)
        else:
            # Code du processus PARENT
            # Le parent n'a pas besoin de gerer la discussion, on ferme la connexion
            conn.close()
            print(f"[*] Processus fils cree (PID: {pid}) pour le client {addr}")

if __name__ == "__main__":
    main()