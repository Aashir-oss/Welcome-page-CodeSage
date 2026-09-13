
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
