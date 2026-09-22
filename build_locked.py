#!/usr/bin/env python3
"""portfolio.html 을 비밀번호로 암호화한 locked.html 로 빌드한다.

비밀번호는 환경변수 PORTFOLIO_PW 로만 받는다. 파일에 남기지 않는다.
이미지와 PDF는 전부 payload 안에 data URI 로 넣어, 잠금 해제 전에는
어떤 자원도 외부에서 받아갈 수 없게 한다.
"""
import base64, hashlib, io, mimetypes, os, re, sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

BASE = os.path.dirname(os.path.abspath(__file__))
ITER = 250_000

pw = os.environ.get("PORTFOLIO_PW")
if not pw:
    sys.exit("PORTFOLIO_PW 환경변수가 필요합니다.")

src = io.open(os.path.join(BASE, "portfolio.html"), encoding="utf-8").read()

# 1) assets/* 를 data URI 로 인라인
def inline(m):
    path = m.group(1)
    full = os.path.join(BASE, path)
    mime = mimetypes.guess_type(full)[0] or "application/octet-stream"
    b64 = base64.b64encode(open(full, "rb").read()).decode()
    return 'src="data:%s;base64,%s"' % (mime, b64)

payload = re.sub(r'src="(assets/[^"]+)"', inline, src)
left = set(re.findall(r'assets/[\w.]+', payload)) - {"assets/resume.pdf.txt", "assets/portfolio.pdf.txt"}
assert not left, "인라인되지 않은 자원: %s" % left

# 2) AES-GCM 암호화
salt = os.urandom(16)
iv = os.urandom(12)
key = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, ITER, 32)
ct = AESGCM(key).encrypt(iv, payload.encode(), None)

# 3) PDF는 같은 키로 따로 암호화해 파일로 내보낸다 (iv 12바이트 + 암호문)
for name in ("resume", "portfolio"):
    raw = open(os.path.join(BASE, "assets", name + ".pdf"), "rb").read()
    fiv = os.urandom(12)
    blob = base64.b64encode(fiv + AESGCM(key).encrypt(fiv, raw, None))
    open(os.path.join(BASE, "assets", name + ".pdf.txt"), "wb").write(blob)
    print("  %s.pdf.txt %d KB" % (name, len(blob) // 1024))

b64 = lambda b: base64.b64encode(b).decode()

out = """<title>최소희 포트폴리오</title>
<style>
  :root{
    --bg:#F5F6F7; --surface:#FFFFFF; --border:#DFE3E9;
    --ink:#16181C; --ink-3:#565C66; --muted:#787E8A;
    --accent:#0B84F3; --accent-deep:#0A62BC; --accent-tint:#EDF5FE;
    --err:#B42318;
    --font:'Pretendard Variable',Pretendard,-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Noto Sans KR','Malgun Gothic',system-ui,sans-serif;
  }
  *{box-sizing:border-box;}
  body{
    margin:0;min-height:100%%;background:var(--bg);color:var(--ink);
    font-family:var(--font);letter-spacing:-.011em;word-break:keep-all;
    -webkit-font-smoothing:antialiased;
  }
  .gate{min-height:88vh;display:flex;align-items:center;justify-content:center;padding:48px 16px;}
  .gate-card{
    width:100%%;max-width:380px;background:var(--surface);border-radius:18px;padding:36px 32px;
    box-shadow:0 1px 2px rgba(16,24,40,.04),0 8px 28px -12px rgba(16,24,40,.12);
  }
  .gate .lbl{
    display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:700;
    color:var(--accent-deep);letter-spacing:.09em;margin-bottom:14px;
  }
  .gate .lbl::before{content:"";width:16px;height:2px;border-radius:2px;background:var(--accent);}
  .gate h1{margin:0 0 8px;font-size:20px;font-weight:700;letter-spacing:-.03em;line-height:1.4;}
  .gate p{margin:0 0 22px;font-size:14px;color:var(--ink-3);line-height:1.75;}
  .gate label{display:block;font-size:12.5px;font-weight:600;color:var(--ink-3);margin-bottom:7px;}
  .gate input{
    width:100%%;padding:12px 14px;border-radius:10px;border:1px solid var(--border);
    background:#fff;font-family:inherit;font-size:15px;color:var(--ink);letter-spacing:-.01em;
  }
  .gate input:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:var(--accent);}
  .gate button{
    width:100%%;margin-top:12px;padding:12px 18px;border:none;border-radius:10px;cursor:pointer;
    background:var(--ink);color:#fff;font-family:inherit;font-size:14.5px;font-weight:600;
    letter-spacing:-.01em;transition:background .18s ease,transform .16s ease;
  }
  .gate button:hover{background:#000;transform:translateY(-1px);}
  .gate button:disabled{background:var(--muted);cursor:default;transform:none;}
  .gate .msg{margin:12px 0 0;font-size:13px;color:var(--err);min-height:19px;}
  .gate .msg.wait{color:var(--ink-3);}
  @media (prefers-reduced-motion:reduce){ *{transition-duration:.001ms !important;} }
</style>

<div class="gate" id="gate">
  <form class="gate-card" id="gateForm" autocomplete="off">
    <div class="lbl">PORTFOLIO</div>
    <h1>최소희 포트폴리오</h1>
    <p>비밀번호를 입력하면 포트폴리오가 열립니다.</p>
    <label for="pw">비밀번호</label>
    <input type="password" id="pw" name="pw" autocomplete="current-password" autofocus>
    <button type="submit" id="go">열기</button>
    <p class="msg" id="msg" role="status" aria-live="polite"></p>
  </form>
</div>

<script>
(function(){
  var SALT="%s", IV="%s", CT="%s", ITER=%d;
  var form=document.getElementById('gateForm'), pw=document.getElementById('pw'),
      go=document.getElementById('go'), msg=document.getElementById('msg');

  function bin(b64){
    var raw=atob(b64), out=new Uint8Array(raw.length);
    for(var i=0;i<raw.length;i++) out[i]=raw.charCodeAt(i);
    return out;
  }

  async function unlock(pass){
    var enc=new TextEncoder();
    var base=await crypto.subtle.importKey('raw',enc.encode(pass),'PBKDF2',false,['deriveKey']);
    var key=await crypto.subtle.deriveKey(
      {name:'PBKDF2',salt:bin(SALT),iterations:ITER,hash:'SHA-256'},
      base,{name:'AES-GCM',length:256},false,['decrypt']);
    var plain=await crypto.subtle.decrypt({name:'AES-GCM',iv:bin(IV)},key,bin(CT));
    return {html:new TextDecoder().decode(plain),key:key};
  }

  function render(html,key){
    window.__pkey=key;
    document.getElementById('gate').remove();
    var host=document.createElement('div');
    host.innerHTML=html;
    var scripts=Array.prototype.slice.call(host.querySelectorAll('script'));
    scripts.forEach(function(s){ s.remove(); });
    document.body.appendChild(host);
    scripts.forEach(function(s){
      var n=document.createElement('script');
      if(s.type) n.type=s.type;
      if(s.id) n.id=s.id;
      n.textContent=s.textContent;
      document.body.appendChild(n);
    });
    var t=host.querySelector('title');
    if(t) document.title=t.textContent;
    window.scrollTo(0,0);
  }

  pw.addEventListener('keydown',function(e){
    if(e.key==='Enter'||e.key==='Return'||e.keyCode===13){ e.preventDefault(); submit(); }
  });
  form.addEventListener('submit',function(e){ e.preventDefault(); submit(); });

  async function submit(){
    var pass=pw.value;
    if(!pass) return;
    go.disabled=true; msg.className='msg wait'; msg.textContent='확인 중입니다.';
    try{
      var out=await unlock(pass);
      render(out.html,out.key);
    }catch(err){
      go.disabled=false; msg.className='msg'; msg.textContent='비밀번호가 맞지 않습니다.';
      pw.select();
    }
  }
})();
</script>
""" % (b64(salt), b64(iv), b64(ct), ITER)

io.open(os.path.join(BASE, "locked.html"), "w", encoding="utf-8").write(out)
print("locked.html %d KB" % (len(out.encode()) // 1024))

# 4) GitHub Pages 용 단독 문서 (아티팩트가 붙여주던 head 를 직접 넣는다)
site = os.path.join(BASE, "site")
os.makedirs(os.path.join(site, "assets"), exist_ok=True)
standalone = (
    '<!doctype html>\n<html lang="ko">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="robots" content="noindex, nofollow">\n'
    '<meta name="color-scheme" content="light">\n'
    '<style>html{-webkit-text-size-adjust:100%;}body{margin:0;}'
    'img{max-width:100%;}[hidden]{display:none !important;}</style>\n'
    + out
    + '\n</head>\n<body>\n</body>\n</html>\n'
)
# <title>/<style>/<script> 는 head 에, 보이는 요소는 body 에 들어가야 한다
head, _, body = out.partition('<div class="gate"')
standalone = (
    '<!doctype html>\n<html lang="ko">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="robots" content="noindex, nofollow">\n'
    '<meta name="color-scheme" content="light">\n'
    '<style>html{-webkit-text-size-adjust:100%;}body{margin:0;}'
    'img{max-width:100%;}[hidden]{display:none !important;}</style>\n'
    + head
    + '</head>\n<body>\n<div class="gate"' + body + '\n</body>\n</html>\n'
)
io.open(os.path.join(site, "index.html"), "w", encoding="utf-8").write(standalone)
for name in ("resume", "portfolio"):
    src_f = os.path.join(BASE, "assets", name + ".pdf.txt")
    open(os.path.join(site, "assets", name + ".pdf.txt"), "wb").write(open(src_f, "rb").read())
print("site/index.html %d KB" % (len(standalone.encode()) // 1024))
