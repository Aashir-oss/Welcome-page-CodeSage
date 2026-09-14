from fastapi import FastAPI, Body, Form
from fastapi.responses import HTMLResponse, JSONResponse
import os
import uvicorn
import json

app = FastAPI()

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception:
        pass

FINAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>CodeSage AI - Login</title>
<!-- Include styles and fonts here -->
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
<style>
/* Your CSS styles here */
*{margin:0;padding:0;box-sizing:border-box;font-family:'Raleway',sans-serif}
:root{--accent:#f7a261;--accent2:#676f9d;--border:rgba(255,255,255,0.12);--muted:#a6adbb;--panel:rgba(25,29,48,0.92)}
body{background:#0d101a;color:#fff;min-height:100vh;overflow:hidden}
.auth-bg{position:fixed;inset:0;background:radial-gradient(600px at 15% 15%, rgba(247,162,97,0.18), transparent 60%),radial-gradient(800px at 85% 85%, rgba(103,111,157,0.22), transparent 60%),#0d101a;z-index:0}
.auth-container{position:relative;z-index:1;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}
.auth-card{background:var(--panel);border:1px solid var(--border);border-radius:24px;padding:36px 32px;width:100%;max-width:440px;box-shadow:0 20px 60px rgba(0,0,0,0.6);backdrop-filter:blur(14px)}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:8px}
.logo-icon{width:44px;height:44px;background:var(--accent);border-radius:12px;display:flex;align-items:center;justify-content:center;color:#121622;font-size:1.2rem}
.auth-card h2{font-size:1.45rem;margin-top:14px}
.auth-card .sub{font-size:0.82rem;color:var(--muted);margin-top:6px;line-height:1.5}
.auth-form{display:flex;flex-direction:column;gap:14px;margin-top:20px}
.input-group{display:flex;flex-direction:column;gap:5px}
.input-group label{font-size:0.75rem;color:var(--muted)}
.input-field{position:relative;display:flex;align-items:center}
.input-field i{position:absolute;left:12px;color:var(--muted);font-size:0.85rem}
.input-field input{width:100%;background:rgba(18,22,34,0.9);border:1px solid #424769;border-radius:10px;padding:12px 12px 12px 36px;color:#fff;outline:none;font-size:0.9rem}
.input-field input:focus{border-color:var(--accent2)}
.accent-btn{background:var(--accent);color:#121622;border:none;border-radius:10px;padding:13px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;font-size:0.92rem}
.accent-btn:hover{transform:translateY(-1px);box-shadow:0 8px 20px rgba(247,162,97,0.3)}
.link-row{margin-top:14px;text-align:center;font-size:0.8rem;color:var(--muted)}
.link-row a{color:var(--accent);text-decoration:none;font-weight:600;cursor:pointer}
.link-row a:hover{text-decoration:underline}
.model-badge{margin-top:18px;padding:12px;background:linear-gradient(135deg, rgba(247,162,97,0.12), rgba(103,111,157,0.12));border:1px solid rgba(247,162,97,0.25);border-radius:12px;font-size:0.72rem;text-align:center;color:var(--muted);line-height:1.5}
.model-badge b{color:var(--accent);word-break:break-all}
.toast{position:fixed;top:18px;right:18px;z-index:99;background:#1a1f3a;border:1px solid var(--border);padding:12px 18px;border-radius:12px;transform:translateX(420px);transition:0.3s;font-size:0.85rem}
.toast.show{transform:translateX(0)}
.hidden{display:none!important}
.app-dashboard{position:fixed;inset:0;z-index:10;display:none;flex-direction:column;background:#0d101a}
.app-dashboard.active{display:flex}
.app-header{height:54px;background:rgba(25,29,48,0.98);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 18px;flex-shrink:0}
.header-left{display:flex;align-items:center;gap:10px}
.header-right{display:flex;align-items:center;gap:8px}
.user-chip{display:flex;align-items:center;gap:6px;padding:5px 12px;background:rgba(255,255,255,0.07);border:1px solid var(--border);border-radius:20px;font-size:0.8rem}
.icon-btn{padding:6px 12px;border-radius:8px;font-size:0.75rem;font-weight:700;text-decoration:none;cursor:pointer;border:none;display:flex;align-items:center;gap:5px}
.btn-accent{background:var(--accent);color:#121622}
.btn-ghost{background:rgba(255,59,59,0.12);border:1px solid rgba(255,59,59,0.25);color:#ff7b7b}
.model-wrap{flex:1;background:#ffffff;position:relative;overflow:hidden}
.model-wrap iframe{width:100%;height:100%;border:none;background:white}
.loading{position:absolute;inset:0;background:#0d101a;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;z-index:2}
.spinner{width:42px;height:42px;border:3px solid rgba(247,162,97,0.2);border-top-color:var(--accent);border-radius:50%;animation:spin 0.8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="auth-bg"></div>
<div class="auth-container" id="authPage">
    <div class="auth-card" id="loginCard">
        <div class="brand">
            <div class="logo-icon"><i class="fa-solid fa-code-merge"></i></div>
            <div>
                <b style="font-size:1.15rem">CodeSage <span style="color:var(--accent)">AI</span></b><br>
                <small style="color:var(--muted);font-size:0.7rem"><i class="fa-solid fa-robot"></i> App Model Portal</small>
            </div>
        </div>
        <h2>Welcome Back</h2>
        <p class="sub">Login to continue to your App Model<br><b style="color:var(--accent)">aashir-oss-codesage-ai-app-nerb3i.streamlit.app</b></p>
        <form id="login-form" class="auth-form">
            <div class="input-group">
                <label>Username</label>
                <div class="input-field"><i class="fa-regular fa-user"></i><input type="text" id="login-email" placeholder="anisa" required></div>
            </div>
            <div class="input-group">
                <label>Password</label>
                <div class="input-field"><i class="fa-solid fa-lock"></i><input type="password" id="login-password" placeholder="••••••••" required></div>
            </div>
            <button type="submit" class="accent-btn"><span>Login & Open App Model</span><i class="fa-solid fa-arrow-right"></i></button>
        </form>
        <div class="link-row">Don't have an account? <a onclick="showRegister()">Register</a></div>
        <div class="model-badge"><i class="fa-solid fa-link"></i> Model URL<br><b>https://aashir-oss-codesage-ai-app-nerb3i.streamlit.app/</b><br> Connected</div>
    </div>
    <div class="auth-card hidden" id="registerCard">
        <div class="brand">
            <div class="logo-icon"><i class="fa-solid fa-user-plus"></i></div>
            <div>
                <b style="font-size:1.15rem">Create <span style="color:var(--accent)">Account</span></b><br>
                <small style="color:var(--muted);font-size:0.7rem">Join CodeSage AI</small>
            </div>
        </div>
        <h2>Register</h2>
        <p class="sub">Create account to access App Model</p>
        <form id="register-form" class="auth-form">
            <div class="input-group">
                <label>Username</label>
                <div class="input-field"><i class="fa-regular fa-user"></i><input type="text" id="reg-username" placeholder="anisa" required></div>
            </div>
            <div class="input-group">
                <label>Email (optional)</label>
                <div class="input-field"><i class="fa-regular fa-envelope"></i><input type="email" id="reg-email" placeholder="you@email.com"></div>
            </div>
            <div class="input-group">
                <label>Password</label>
                <div class="input-field"><i class="fa-solid fa-lock"></i><input type="password" id="reg-password" placeholder="••••••••" required></div>
            </div>
            <button type="submit" class="accent-btn"><span>Create Account</span><i class="fa-solid fa-user-plus"></i></button>
        </form>
        <div class="link-row">Already have an account? <a onclick="showLogin()">Login</a></div>
    </div>
</div>
<div class="app-dashboard" id="dashPage">
    <div class="app-header">
        <div class="header-left">
            <div class="logo-icon" style="width:32px;height:32px;font-size:0.9rem;border-radius:8px"><i class="fa-solid fa-code-merge"></i></div>
            <b>CodeSage AI <span style="color:var(--accent)">Model</span></b>
            <span style="font-size:0.6rem;background:#10b981;color:white;padding:3px 8px;border-radius:10px;margin-left:6px">● LIVE</span>
        </div>
        <div class="header-right">
            <span id="userLabel" class="user-chip"><i class="fa-solid fa-user-circle"></i> user</span>
            <a href="https://aashir-oss-codesage-ai-app-nerb3i.streamlit.app/" target="_blank" class="icon-btn btn-accent"><i class="fa-solid fa-external-link"></i> Open</a>
            <button onclick="logout()" class="icon-btn btn-ghost"><i class="fa-solid fa-right-from-bracket"></i> Logout</button>
        </div>
    </div>
    <div class="model-wrap">
        <div class="loading" id="loadingOverlay">
            <div class="spinner"></div>
            <div style="text-align:center">
                <p style="font-weight:600">Loading App Model...</p>
                <p style="font-size:0.7rem;color:var(--muted);margin-top:4px">https://aashir-oss-codesage-ai-app-nerb3i.streamlit.app/</p>
            </div>
        </div>
        <iframe id="appFrame" src="" allow="clipboard-read; clipboard-write; fullscreen" loading="eager"></iframe>
    </div>
</div>
<div class="toast" id="toast"></div>
<script>
/* Your JavaScript code here */
const API = window.location.origin;
const HEADERS = {'ngrok-skip-browser-warning':'true'};
const APP_URL = 'https://aashir-oss-codesage-ai-app-nerb3i.streamlit.app/?embed=true';

function toast(m){
    const t=document.getElementById('toast');
    t.textContent=m;
    t.classList.add('show');
    setTimeout(()=>t.classList.remove('show'),3500);
}

function showRegister(){
    document.getElementById('loginCard').classList.add('hidden');
    document.getElementById('registerCard').classList.remove('hidden');
}

function showLogin(){
    document.getElementById('registerCard').classList.add('hidden');
    document.getElementById('loginCard').classList.remove('hidden');
}

document.getElementById('login-form').addEventListener('submit',async(e)=>{
    e.preventDefault();
    const u=document.getElementById('login-email').value.trim();
    const p=document.getElementById('login-password').value;
    const form=new URLSearchParams();
    form.append('username',u);
    form.append('password',p);
    try{
        const r=await fetch(`${API}/auth/login`,{
            method:'POST',
            headers:{'Content-Type':'application/x-www-form-urlencoded',...HEADERS},
            body:form
        });
        const d=await r.json();
        if(r.ok){
            localStorage.setItem('access_token',d.access_token);
            localStorage.setItem('username',u);
            toast('Login success!');
            showDash();
        } else toast(d.detail||'Login failed')
    }catch(err){
        localStorage.setItem('access_token','demo_token');
        localStorage.setItem('username',u||'anisa');
        toast('Demo Login - Opening App Model');
        showDash();
    }
});

document.getElementById('register-form').addEventListener('submit',async(e)=>{
    e.preventDefault();
    const username=document.getElementById('reg-username').value.trim();
    const email=document.getElementById('reg-email').value.trim();
    const password=document.getElementById('reg-password').value;
    try{
        const r=await fetch(`${API}/auth/register`,{
            method:'POST',
            headers:{'Content-Type':'application/json',...HEADERS},
            body:JSON.stringify({username,email,password})
        });
        const d=await r.json();
        if(r.ok){
            toast('Account created! Please login');
            showLogin();
            document.getElementById('login-email').value=username;
        } else toast(d.detail||'Register failed')
    }catch{
        toast('Backend not running - python run.py chalao');
    }
});

function showDash(){
    document.getElementById('authPage').style.display='none';
    const dash=document.getElementById('dashPage');
    dash.classList.add('active');
    document.getElementById('userLabel').innerHTML='<i class="fa-solid fa-user-circle"></i> '+(localStorage.getItem('username')||'anisa');
    const frame=document.getElementById('appFrame');
    const loading=document.getElementById('loadingOverlay');
    frame.src=APP_URL;
    frame.onload=()=>{
        if(loading) loading.style.opacity='0';
        setTimeout(()=>{
            if(loading) loading.style.display='none'
        },400);
        toast('App Model Loaded!')
    };
    setTimeout(()=>{
        if(loading) loading.style.display='none'
    },6000);
}

function logout(){
    localStorage.clear();
    location.reload();
}

if(localStorage.getItem('access_token')) showDash();
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def root():
    for p in ["index.html", "frontend/index.html", "app/frontend/index.html"]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "Upload Code" in content and "Ask Your Codebase" in content:
                        continue
                    return HTMLResponse(content=content)
            except Exception:
                pass
    return HTMLResponse(content=FINAL_HTML)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": "https://aashir-oss-codesage-ai-app-nerb3i.streamlit.app/"
    }

@app.post("/auth/register")
async def register_user(data: dict = Body(...)):
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return JSONResponse(status_code=400, content={"detail": "Username and password required"})
    users = load_users()
    users[username] = {"username": username, "password": password}
    save_users(users)
    return {"message": "Account created successfully"}

@app.post("/auth/login")
async def login_user(username: str = Form(...), password: str = Form(...)):
    users = load_users()
    if username in users:
        if users[username].get("password") == password:
            return {"access_token": "valid_token"}
    return {"access_token": "demo_token"}

if __name__ == "__main__":
    print("CodeSage AI running - Login -> App Model")
    uvicorn.run(app, host="0.0.0.0", port=8000)
