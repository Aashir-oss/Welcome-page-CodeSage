// CodeSage AI - App Model Only - FINAL CLEAN VERSION
// App Model: https://aashir-oss-codesage-ai-app-nerb3i.streamlit.app/
// Old interface deleted: Upload Code, My Codes, Ask Your Codebase

const API = window.location.origin;
const HEADERS = { 'ngrok-skip-browser-warning': 'true' };
const APP_MODEL_URL = 'https://aashir-oss-codesage-ai-app-nerb3i.streamlit.app/?embed=true';

function toast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3500);
}

const loginForm = document.getElementById('login-form');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    const form = new URLSearchParams();
    form.append('username', username);
    form.append('password', password);
    try {
      const r = await fetch(API + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', ...HEADERS },
        body: form
      });
      const d = await r.json();
      if (r.ok) {
        localStorage.setItem('access_token', d.access_token);
        localStorage.setItem('username', username);
        toast('Login success! Loading App Model...');
        showDash();
      } else {
        toast(d.detail || 'Login failed');
      }
    } catch (err) {
      toast('Backend not running - python run.py chalao!');
    }
  });
}

function showDash() {
  const authPage = document.getElementById('authPage');
  const dashPage = document.getElementById('dashPage');
  const userLabel = document.getElementById('userLabel');
  const frame = document.getElementById('appFrame') || document.getElementById('appModelFrame');
  const loading = document.getElementById('loadingOverlay');
  if (authPage) authPage.style.display = 'none';
  if (dashPage) dashPage.classList.add('active');
  if (userLabel) userLabel.textContent = localStorage.getItem('username') || 'anisa';
  if (frame) {
    frame.src = APP_MODEL_URL;
    frame.onload = () => {
      if (loading) {
        loading.style.opacity = '0';
        setTimeout(() => { loading.style.display = 'none'; }, 400);
      }
      toast('App Model Loaded!');
    };
    setTimeout(() => { if (loading) loading.style.display = 'none'; }, 6000);
  }
}

function logout() {
  localStorage.clear();
  location.reload();
}

if (localStorage.getItem('access_token')) {
  showDash();
}

console.log('CodeSage AI - App Model Linked: https://aashir-oss-codesage-ai-app-nerb3i.streamlit.app/?embed=true');
