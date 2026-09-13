import os, json, secrets
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")

DEFAULT_URI = "mongodb+srv://anisazargara_db_user:FVaA7zauPgd089BP@cluster0.k3qfhxz.mongodb.net/code_rag_db?appName=Cluster0"

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CodeSage AI — Developer Portal</title>
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700&family=Fira+Code:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Raleway',sans-serif}
:root{--bg:#0d101a;--panel:rgba(25,29,48,0.8);--border:rgba(255,255,255,0.12);--accent:#f7a261;--accent2:#676f9d;--muted:#a6adbb;--input:rgba(18,22,34,0.9)}
body{background:#0d101a;color:#fff;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;position:relative}
/* LIGHT BACKGROUND - NO 3D, NO BLUR, NO ANIMATION */
body::before{content:'';position:fixed;inset:0;z-index:0;background:
radial-gradient(600px at 20% 20%, rgba(247,162,97,0.15), transparent 60%),
radial-gradient(800px at 80% 80%, rgba(103,111,157,0.18), transparent 60%),
#0d101a}
.auth-container{position:relative;z-index:1;width:100%;max-width:460px}
.auth-card{background:var(--panel);border:1px solid var(--border);border-radius:24px;padding:36px 32px;box-shadow:0 20px 60px rgba(0,0,0,0.6)}
.brand-box{display:flex;align-items:center;gap:12px;margin-bottom:20px}
.logo-icon{width:42px;height:42px;background:var(--accent);border-radius:10px;display:flex;align-items:center;justify-content:center;color:#121622;font-size:1.2rem}
.brand-text h2{font-size:1.15rem;font-weight:700} .brand-text h2 span{color:var(--accent)} .brand-text p{font-size:0.72rem;color:var(--muted)}
.tab-switch{display:flex;gap:18px;border-bottom:1px solid var(--border);padding-bottom:10px;margin-bottom:18px}
.tab-btn{background:transparent;border:none;color:var(--muted);font-weight:600;cursor:pointer;padding-bottom:8px;border-bottom:3px solid transparent}
.tab-btn.active{color:#fff;border-bottom-color:var(--accent)}
.welcome-head h1{font-size:1.5rem} .welcome-head p{font-size:0.8rem;color:var(--muted);margin-top:4px}
.auth-form{display:none;flex-direction:column;gap:14px;margin-top:16px} .auth-form.active{display:flex}
.input-group{display:flex;flex-direction:column;gap:5px} .input-group label{font-size:0.75rem;color:var(--muted)}
.input-field{position:relative;display:flex;align-items:center}
.field-icon{position:absolute;left:12px;color:var(--muted);font-size:0.85rem} .toggle-pwd{position:absolute;right:12px;color:var(--muted);cursor:pointer;font-size:0.85rem}
.input-field input{width:100%;background:var(--input);border:1px solid #424769;border-radius:10px;padding:11px 12px 11px 36px;color:#fff;font-size:0.88rem;outline:none}
.input-field input:focus{border-color:var(--accent2)}
.accent-btn{background:var(--accent);color:#121622;border:none;border-radius:10px;padding:12px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px}
.accent-btn:disabled{opacity:0.6}
.status-pill{margin-top:20px;background:rgba(18,22,34,0.8);border:1px solid var(--border);border-radius:20px;padding:8px 12px;display:flex;align-items:center;justify-content:center;gap:8px;font-size:0.7rem;color:var(--muted)}
.dot{width:7px;height:7px;background:#10b981;border-radius:50%}
.dashboard{position:relative;z-index:1;width:100%;max-width:1100px;display:none;grid-template-columns:300px 1fr;gap:16px}
.dashboard.active{display:grid}
.dash-card{background:var(--panel);border:1px solid var(--border);border-radius:20px;padding:18px}
.toast{position:fixed;top:18px;right:18px;z-index:99;background:#1a1f3a;border:1px solid var(--border);padding:10px 16px;border-radius:10px;font-size:0.85rem;transform:translateX(400px);transition:0.3s}
.toast.show{transform:translateX(0)}
@media(max-width:900px){.dashboard{grid-template-columns:1fr}}
</style>
</head>
<body>
<main class="auth-container" id="authPage">
<div class="auth-card">
<div class="brand-box"><div class="logo-icon"><i class="fa-solid fa-code-merge"></i></div><div class="brand-text"><h2>CodeSage <span>AI</span></h2><p>Snippet Vault & Dev Workspace</p></div></div>
<div class="tab-switch"><button class="tab-btn active" id="login-tab" onclick="switchTab('login')">Sign In</button><button class="tab-btn" id="signup-tab" onclick="switchTab('signup')">Sign Up</button></div>
<div class="welcome-head"><h1 id="welcome-title">Welcome back!</h1><p id="welcome-sub">Enter your credentials to access your workspace</p></div>
<form id="login-form" class="auth-form active">
<div class="input-group"><label>Username</label><div class="input-field"><i class="fa-regular fa-user field-icon"></i><input type="text" id="login-email" placeholder="ahmed" required></div></div>
<div class="input-group"><label>Password</label><div class="input-field"><i class="fa-solid fa-lock field-icon"></i><input type="password" id="login-password" placeholder="••••••••" required><i class="fa-regular fa-eye toggle-pwd" onclick="togglePasswordVisibility('login-password',this)"></i></div></div>
<button type="submit" class="accent-btn"><span>Continue to Workspace</span><i class="fa-solid fa-arrow-right"></i></button>
</form>
<form id="signup-form" class="auth-form">
<div class="input-group"><label>Full Name</label><div class="input-field"><i class="fa-regular fa-user field-icon"></i><input type="text" id="signup-name" placeholder="Alex Morgan"></div></div>
<div class="input-group"><label>Username</label><div class="input-field"><i class="fa-regular fa-user field-icon"></i><input type="text" id="signup-email" placeholder="ahmed" required></div></div>
<div class="input-group"><label>Password</label><div class="input-field"><i class="fa-solid fa-lock field-icon"></i><input type="password" id="signup-password" placeholder="Min 8 chars" minlength="8" required><i class="fa-regular fa-eye toggle-pwd" onclick="togglePasswordVisibility('signup-password',this)"></i></div></div>
<button type="submit" class="accent-btn"><span>Create Account</span><i class="fa-solid fa-arrow-right"></i></button>
</form>
<div class="status-pill"><div class="dot"></div><span>Fast & Encrypted Developer Workspace</span></div>
</div>
</main>
<div class="dashboard" id="dashPage">
<div class="dash-card"><h3><i class="fa-solid fa-user"></i> <span id="userLabel"></span></h3><button class="accent-btn" style="width:100%;margin-top:12px" onclick="logout()">Logout</button><hr style="margin:14px 0;border-color:rgba(255,255,255,0.1)"><h4>Upload Code</h4><input type="file" id="fileInput" style="margin:8px 0"><button class="accent-btn" style="width:100%" onclick="uploadFile()">Upload & Index</button><div id="myCodes" style="margin-top:16px;font-size:0.8rem"></div></div>
<div class="dash-card"><h3>Ask Your Codebase</h3><div id="chatBox" style="height:300px;overflow-y:auto;background:rgba(0,0,0,0.25);border-radius:10px;padding:12px;margin:12px 0;font-size:0.85rem">Upload your code and ask anything!</div><div style="display:flex;gap:8px"><input id="question" placeholder="e.g. where is login function?" style="flex:1;padding:10px;border-radius:8px;border:1px solid #424769;background:rgba(18,22,34,0.9);color:white"><button class="accent-btn" onclick="ask()">Ask</button></div></div>
</div>
<div class="toast" id="toast"></div>
<script src="script.js"></script>
</body>
</html>
"""
SCRIPT_JS = """
// FIXED: Public link pe bhi backend chalega!
const API = window.location.origin;  // Ab localhost nahi, jo link hai usi se backend lega

// ngrok ke liye header add karna zaroori hai warna signup block hota hai
const NGROK_HEADERS = {
  'ngrok-skip-browser-warning': 'true'
};

function toast(msg){
  const t=document.getElementById('toast');
  t.textContent=msg;
  t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),3500)
}

function switchTab(tab){
  const lf=document.getElementById('login-form'),
        sf=document.getElementById('signup-form'),
        lb=document.getElementById('login-tab'),
        sb=document.getElementById('signup-tab'),
        title=document.getElementById('welcome-title'),
        sub=document.getElementById('welcome-sub');
  if(tab==='login'){
    lf.classList.add('active');sf.classList.remove('active');
    lb.classList.add('active');sb.classList.remove('active');
    title.innerText='Welcome back!';
    sub.innerText='Enter your credentials to access your workspace'
  }else{
    sf.classList.add('active');lf.classList.remove('active');
    sb.classList.add('active');lb.classList.remove('active');
    title.innerText='Create Account';
    sub.innerText='Join CodeSage AI developer environment'
  }
}

function togglePasswordVisibility(id,icon){
  const inp=document.getElementById(id);
  if(inp.type==='password'){
    inp.type='text';
    icon.classList.replace('fa-eye','fa-eye-slash')
  }else{
    inp.type='password';
    icon.classList.replace('fa-eye-slash','fa-eye')
  }
}

document.getElementById('signup-form').addEventListener('submit',async(e)=>{
  e.preventDefault();
  const username=document.getElementById('signup-email').value.trim(),
        password=document.getElementById('signup-password').value;
  if(password.length < 8) return toast('Password min 8 characters!');
  try{
    const r=await fetch(`${API}/auth/register`,{
      method:'POST',
      headers:{'Content-Type':'application/json', ...NGROK_HEADERS},
      body:JSON.stringify({username,password})
    });
    const d=await r.json();
    if(r.ok){
      toast('✅ Account created! Now login');
      switchTab('login')
    }else{
      toast(d.detail||'Signup failed: '+JSON.stringify(d))
    }
  }catch(err){
    console.error(err);
    toast('❌ Backend not running - python run.py on rakho!')
  }
})

document.getElementById('login-form').addEventListener('submit',async(e)=>{
  e.preventDefault();
  const username=document.getElementById('login-email').value.trim(),
        password=document.getElementById('login-password').value;
  const form=new URLSearchParams();
  form.append('username',username);
  form.append('password',password);
  try{
    const r=await fetch(`${API}/auth/login`,{
      method:'POST',
      headers:{'Content-Type':'application/x-www-form-urlencoded', ...NGROK_HEADERS},
      body:form
    });
    const d=await r.json();
    if(r.ok){
      localStorage.setItem('access_token',d.access_token);
      localStorage.setItem('username',username);
      toast('✅ Login success!');
      showDash()
    }else{
      toast(d.detail||'Login failed')
    }
  }catch(err){
    console.error(err);
    toast('❌ Backend not running - python run.py karo')
  }
})

function showDash(){
  document.getElementById('authPage').style.display='none';
  document.getElementById('dashPage').classList.add('active');
  document.getElementById('userLabel').innerText=localStorage.getItem('username');
  loadCodes()
}

function logout(){
  localStorage.clear();
  document.getElementById('authPage').style.display='flex';
  document.getElementById('dashPage').classList.remove('active')
}

async function uploadFile(){
  const f=document.getElementById('fileInput').files[0];
  if(!f) return toast('File select karo');
  const fd=new FormData();
  fd.append('file',f);
  try{
    const r=await fetch(`${API}/code/upload`,{
      method:'POST',
      headers:{Authorization:`Bearer ${localStorage.getItem('access_token')}`, ...NGROK_HEADERS},
      body:fd
    });
    const d=await r.json();
    if(r.ok){toast('✅ Uploaded!');loadCodes()}
    else toast(d.detail)
  }catch(e){toast('Upload failed - backend check karo')}
}

async function loadCodes(){
  try{
    const r=await fetch(`${API}/code/my-codes`,{
      headers:{Authorization:`Bearer ${localStorage.getItem('access_token')}`, ...NGROK_HEADERS}
    });
    const d=await r.json();
    document.getElementById('myCodes').innerHTML=`<b>My Codes (${d.length||0}):</b><br>`+(d.map?d.map(c=>`• ${c.filename||c.name}`).join('<br>'):'');
  }catch(e){
    console.log('loadCodes error', e)
  }
}

async function ask(){
  const q=document.getElementById('question').value;
  if(!q) return;
  const box=document.getElementById('chatBox');
  box.innerHTML+=`<div><b>You:</b> ${q}</div>`;
  try{
    const r=await fetch(`${API}/code/chat`,{
      method:'POST',
      headers:{'Content-Type':'application/json', Authorization:`Bearer ${localStorage.getItem('access_token')}`, ...NGROK_HEADERS},
      body:JSON.stringify({question:q})
    });
    const d=await r.json();
    box.innerHTML+=`<div style="margin:8px 0;padding:8px;background:rgba(247,162,97,0.1);border-radius:6px"><b>Sage:</b> ${d.answer||d.detail||JSON.stringify(d)}</div>`;
    box.scrollTop=box.scrollHeight
  }catch(e){
    box.innerHTML+='<div>❌ Error - backend check karo</div>'
  }
}

if(localStorage.getItem('access_token')) showDash();
"""

try:
    import bcrypt
    HAS_BCRYPT = True
except:
    HAS_BCRYPT = False

def hash_password(pwd: str) -> str:
    if HAS_BCRYPT:
        return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
    return pwd

def verify_password(plain: str, hashed: str) -> bool:
    try:
        if hashed.startswith("$2b$") or hashed.startswith("$2a$"):
            return bcrypt.checkpw(plain.encode(), hashed.encode()) if HAS_BCRYPT else False
        return plain == hashed
    except:
        return False

MONGO_URI = os.getenv("MONGODB_URI") or DEFAULT_URI
USE_MONGO = False
mongo_db = None

print("\n" + "="*70)
print("Checking MongoDB...")
if MONGO_URI:
    preview = MONGO_URI[:35] + "***" + MONGO_URI[-25:]
    print(f"URI: {preview}")
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000)
        client.admin.command('ping')
        mongo_db = client["code_rag_db"]
        count = mongo_db.users.count_documents({})
        print(f"✅ MongoDB CONNECTED! DB: {mongo_db.name} Users: {count}")
        for u in mongo_db.users.find({}, {"username": 1}).limit(10):
            print(f"   - {u.get('username')}")
        USE_MONGO = True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        USE_MONGO = False
print("="*70 + "\n")

def load_json():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

json_db = load_json()

def get_user(username):
    if USE_MONGO:
        return mongo_db.users.find_one({"username": username})
    return json_db.get(username)

def create_user(username, password):
    hashed = hash_password(password)
    if USE_MONGO:
        if mongo_db.users.find_one({"username": username}):
            return False
        mongo_db.users.insert_one({"username": username, "password": hashed, "created": str(datetime.now())})
        print(f"✅ Saved {username} to MongoDB")
        return True
    else:
        if username in json_db:
            return False
        json_db[username] = {"username": username, "password": hashed, "created": str(datetime.now())}
        save_json(json_db)
        return True

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class RegisterRequest(BaseModel):
    username: str
    password: str

@app.get("/", response_class=HTMLResponse)
async def root():
    html = INDEX_HTML.replace('<script src="script.js"></script>', f'<script>\n{SCRIPT_JS}\n</script>')
    return HTMLResponse(html)

@app.get("/script.js")
async def script():
    return Response(content=SCRIPT_JS, media_type="application/javascript")

@app.get("/health")
async def health():
    if USE_MONGO:
        users = list(mongo_db.users.find({}, {"username": 1, "_id": 0, "created": 1}))
        return {"status": "ok", "database": "MongoDB Atlas ✅ code_rag_db", "users_count": len(users), "users": users, "message": "Saving to MongoDB!"}
    else:
        return {"status": "ok", "database": "JSON fallback ⚠️", "users_count": len(json_db), "users": list(json_db.keys())}

@app.get("/debug/users")
async def debug():
    if USE_MONGO:
        users = list(mongo_db.users.find({}))
        for u in users:
            u["_id"] = str(u["_id"])
        return {"database": "code_rag_db.users", "count": len(users), "users": users}
    else:
        return {"database": "JSON", "count": len(json_db), "users": json_db}

@app.post("/auth/register")
async def register(req: RegisterRequest):
    username = req.username.strip()
    password = req.password
    print(f"REGISTER: {username} -> {'MongoDB' if USE_MONGO else 'JSON'}")
    if len(username) < 2:
        raise HTTPException(400, "Username too short")
    if len(password) < 8:
        raise HTTPException(400, "Password 8+ chars")
    if get_user(username):
        raise HTTPException(400, f"'{username}' already exists")
    create_user(username, password)
    return {"message": f"Created in {mongo_db.name if USE_MONGO else 'JSON'}", "username": username}

@app.post("/auth/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    username = form.username.strip()
    password = form.password
    user = get_user(username)
    if not user:
        raise HTTPException(401, f"User '{username}' not found")
    if not verify_password(password, user["password"]):
        raise HTTPException(401, "Wrong password")
    return {"access_token": secrets.token_urlsafe(32), "token_type": "bearer"}

@app.post("/code/upload")
async def upload(): return {"message": "ok"}
@app.get("/code/my-codes")
async def codes(): return []
@app.post("/code/chat")
async def chat(q: dict): return {"answer": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)