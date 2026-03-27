import socket
import re
import base64

def check_tcp(host, port):
    try:
        with socket.create_connection((host, port), timeout=5):
            return True
    except:
        return False

def extract_host_port(link):
    # Для ссылок типа vless://..., vmess://..., ss://...
    try:
        # Убираем протокол
        content = link.split('://')[1]
        # Находим часть с хостом и портом (между @ и ?)
        if '@' in content:
            server_part = content.split('@')[1].split('?')[0].split('#')[0]
            if ':' in server_part:
                host, port = server_part.split(':')
                return host, int(port)
    except:
        pass
    return None, None

def main():
    with open('list.txt', 'r') as f:
        links = f.readlines()

    alive_links = []
    for link in links:
        link = link.strip()
        if not link: continue
        
        host, port = extract_host_port(link)
        if host and port:
            print(f"Проверка {host}:{port}...", end="")
            if check_tcp(host, port):
                print(" РАБОТАЕТ ✅")
                alive_links.append(link)
            else:
                print(" МЕРТВ ❌")
        else:
            # Если это не ссылка на сервер, оставляем как есть
            alive_links.append(link)

    with open('list.txt', 'w') as f:
        f.write('\n'.join(alive_links) + '\n')

if __name__ == "__main__":
    main()
