# FastAPI Event Loop Blocking Demo

## Cerita di Balik Project Ini

Jadi ceritanya waktu itu gue lagi santai nonton YouTube, tiba-tiba Slack rame. Di channel community, temen gue nge-tag gue bilang kalo API production down. Semua endpoint return 502.

Gue langsung cek server. CPU idle di 5%, memory kepake cuma 30%. Traffic dashboard malah nunjukkin RPS 0. Lah kok bisa? Server sepi tapi timeout?

Gue buka log, isinya cuma gini:
```
[WARNING] Request timeout after 30s: GET /api/user/profile
[WARNING] Request timeout after 30s: GET /api/products/list
[ERROR] 502 Bad Gateway - Upstream timeout
```

Tiga jam gue debug, tracing, buka satu-satu endpoint. Sampe akhirnya ketemu biang keroknya di salah satu service. Ada function begini:

```python
@router.get("/analytics/report")
async def generate_report():
    time.sleep(5)
    return {"report": "generated"}
```

Ternyata ada temen satu tim yang nambahin `time.sleep(5)` buat simulasi "loading lama". Dia kira cuma ngaruh ke request yang akses endpoint itu doang. Padahal realitanya? Satu baris itu bikin seluruh server freeze selama 5 detik.

FastAPI tuh pake single thread buat event loop. Jadi kalo ada satu aja operasi blocking kayak `time.sleep()` atau `requests.get()` di async function, event loop-nya langsung stuck. Request lain numpuk, timeout, user dapet 502. Padahal CPU nganggur, cuma nungguin sleep doang.

Dari pengalaman pahit itu, gue bikin project ini buat nunjukkin ke tim, dan siapa aja yang pake FastAPI, kenapa blocking di async context itu fatal banget.

## Kenapa Lu Harus Peduli

Bayangin lu punya API yang handle 1000 request per detik. Terus ada 1 endpoint yang pake `time.sleep(3)`. Begitu ada user akses endpoint itu:

- Detik 0-3: Semua request baru antri, timeout satu-satu
- RPS: Langsung drop dari 1000 ke 0
- User: Dapet 502 semua, bahkan yang akses endpoint berbeda
- Monitoring: CPU santai, memory santai, tapi API mati total

Pernah ngalamin kan, server sepi tapi response timeout semua? Nah itu ciri-ciri event loop blocking.

## Cara Install dan Jalanin

Biar ga ribet, ikutin aja langkah ini:

```bash
# Clone dulu
git clone git@github.com:ZalStack/fastapi-blocking-demo.git
cd fastapi-blocking-demo

# Bikin virtual environment
python -m venv venv
source venv/bin/activate  # Kalo Windows: venv\Scripts\activate

# Install yang dibutuhin
pip install -r requirements.txt
pip install requests  # Ini buat nunjukkin blocking, jangan ditiru di production ya

# Jalanin servernya
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Buka `http://localhost:8000/docs` buat liat daftar endpoint yang tersedia.

## Gimana Cara Buktiin Masalahnya

Lu pasti penasaran kan, emang iya 1 request bisa nge-block semua? Coba aja sendiri.

### Test Blocking (yang bermasalah)

Buka 2 terminal. Di terminal pertama, jalanin:

```bash
time curl http://localhost:8000/blocking/db-query
```

Pas masih loading (ada waktu 2 detik), cepetan ke terminal kedua, jalanin:

```bash
time curl http://localhost:8000/health
```

Normalnya health check cuma butuh 0.04 detik. Tapi karena event loop lagi ke-block sama request pertama, health check lu bakal nunggu. Bisa jadi 2 detik lebih. Padahal beda endpoint loh.

### Test Non-Blocking (solusinya)

Sekarang coba yang bener:

```bash
python tests/test_blocking.py
```

Nanti keliatan bedanya:
- Blocking: 10 request butuh 20 detik (antri satu-satu)
- Non-Blocking: 10 request cuma butuh 2 detik (jalan bareng)

### Load Test Kalo Mau Ngerasain Parahnya

```bash
python tests/load_test.py
```

Lu bakal liat simulasi 10 user akses barengan. Di blocking endpoint, user pertama bikin semua user lain nunggu. Di non-blocking, semua happy ga ada yang timeout.

## Hasil Test

Blocking endpoint (database query + sleep 2 detik):
```
time curl http://localhost:8000/blocking/db-query
Total: 2.076 detik, CPU cuma kepake 1%
```
CPU cuma 1% karena servernya nganggur, nungguin sleep doang. Bukan ngolah data.

Health check saat blocking lagi jalan:
```
time curl http://localhost:8000/health  
Harusnya 0.046 detik, tapi ini jadi 2+ detik
```
Ini bukti kalo event loop lagi di-block.

Non-blocking parallel (3 operasi bareng):
```
time curl http://localhost:8000/non-blocking/parallel
Total: 3.35 detik (jalanin 3 task async bersamaan)
```

Health check saat non-blocking lagi jalan:
```
time curl http://localhost:8000/health
Tetep 0.046 detik, ga keganggu
```

## Aturan Main yang Wajib Diinget

Begini, kalo lu kerja pake FastAPI atau framework async lainnya, ini rules yang ga boleh dilanggar:

```python
# HARAM HUKUMNYA pake ini di async function
time.sleep(5)              # Block event loop
requests.get(url)          # Block event loop
open("file.txt").read()    # Block event loop (kalo file gede)
db.query(User).all()      # Block event loop (sync ORM)

# INI YANG BENER
await asyncio.sleep(5)                         # Non-blocking delay
async with aiohttp.get(url) as resp:           # Non-blocking HTTP
await anyio.open_file("file.txt")              # Non-blocking file I/O
await async_db.execute("SELECT * FROM users")  # Non-blocking DB
await asyncio.to_thread(heavy_cpu_work)        # CPU task di thread terpisah
```

Intinya: kalo ada operasi yang bikin nunggu, pake await. Jangan pake synchronous call di async function.

## Tools dan Library yang Dipake

- FastAPI - Framework async-nya
- Uvicorn - Server ASGI
- aiomysql - MySQL driver async
- aiohttp - HTTP client async
- SQLAlchemy - ORM (sync version, buat contoh blocking)
- httpx - HTTP client, support sync dan async

---

Kalo ada yang ngalamin case blocking lain, atau pengen nambahin contoh yang lebih ekstrim, fork aja dan bikin PR. Tambahin endpoint baru di `routers/blocking.py` kalo mau nunjukin cara yang salah, atau di `routers/non_blocking.py` kalo punya solusi.

Gue personally udah ngalamin production down 2 kali gara-gara ini. Iya, keras kepala emang. Jadi percaya deh, ini masalah yang sering disepelein tapi dampaknya fatal banget.

**TL;DR**: Jangan pake `time.sleep()` di async FastAPI. 1 request nunggu = semua request timeout. Lu bisa bikin outage total cuma gara-gara 1 baris kode.