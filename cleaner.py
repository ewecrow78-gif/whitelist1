import socket
import re
import base64
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# Настройки
INPUT_FILE = 'list.txt'
OUTPUT_FILE = 'list.txt'
TIMEOUT = 2.5
THREADS = 100

def decode_vmess(s):
    try:
        return json.loads(base64.b64decode(s + '=' * (-len(s) % 4)).decode('utf-8'))
    except:
        return None

def extract_host_port(link):
    try:
        if link.startswith('vmess://'):
            d = decode_vmess(link[8:])
            if d: return d.get('add'), int(d.get('port'))
        match = re.search(r'@([^:/?#\s]+):(\d+)', link)
        if match:
            return match.group(1), int(match.group(2))
    except:
        pass
    return None, None

def check_link(link):
    link = link.strip()
    if not link or link.startswith('#'): return None
    
    host, port = extract_host_port(link)
    if host and port:
        try:
            import time
            start = time.time()
            with socket.create_connection((host, port), timeout=TIMEOUT):
                latency = int((time.time() - start) * 1000)
                return {"link": link, "latency": latency, "host": host}
        except:
            return None
    return None

def main():
    print("Чтение списка...")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            lines = list(set(f.readlines())) # Сразу убираем дубликаты строк
    except FileNotFoundError:
        return

    print(f"Проверка {len(lines)} серверов в {THREADS} потоков...")
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        results = list(filter(None, executor.map(check_link, lines)))

    # СОРТИРОВКА ПО ПИНГУ
    results.sort(key=lambda x: x['latency'])

    # ДЕДУПЛИКАЦИЯ ПО IP (чтобы не забивать память v2rayNG одинаковыми серверами)
    unique_results = []
    seen_hosts = set()
    for item in results:
        if item['host'] not in seen_hosts:
            seen_hosts.add(item['host'])
            unique_results.append(item)

    final_output = []
    # Заголовки для красоты и инфо
    final_output.append(f"# profile-title: 🏳️ Gh0st_WhiteList 🏳️")
    final_output.append(f"vless://ghost@127.0.0.1:443?encryption=none&security=none#{urllib.parse.quote(f'✅ Чисто: {len(unique_results)} серверов')}")

    for i, item in enumerate(unique_results):
        link = item['link']
        new_ps = f"🌐 Gh0st #{i+1}"
        
        if link.startswith('vmess://'):
            d = decode_vmess(link[8:])
            if d:
                d['ps'] = new_ps
                # Очистка VMess от лишнего мусора для легкости
                clean_vmess = {k: v for k, v in d.items() if k in ["v","ps","add","port","id","aid","net","type","host","path","tls","sni","alpn"]}
                encoded = base64.b64encode(json.dumps(clean_vmess).encode('utf-8')).decode('utf-8')
                final_output.append(f"vmess://{encoded}")
        else:
            base_url = link.split('#')[0]
            final_output.append(f"{base_url}#{urllib.parse.quote(new_ps)}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_output) + '\n')
    
    # Создаем файл статуса для GitHub
    with open('status.json', 'w', encoding='utf-8') as f:
        json.dump({"count": f"{len(unique_results)} рабочих"}, f)

    print(f"Готово! Сохранено {len(unique_results)} уникальных серверов.")

if __name__ == "__main__":
    main()
