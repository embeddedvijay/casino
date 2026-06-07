import React,{useState}from"react";
import"./LoginPage.css";
import{saveUserSession,getClientId,getApi}from"../shared/userSession";

const getRedirect=()=>new URLSearchParams(window.location.search).get("redirect")||"/";

export default function LoginPage(){
const[companyName]=useState("Gold 365");
const[mobile,setMobile]=useState("");
const[password,setPassword]=useState("");
const[loading,setLoading]=useState(false);
const[demoLoading,setDemoLoading]=useState(false);

const login=async()=>{
if(!mobile.trim()||!password.trim()){alert("Mobile number aur password bharo");return;}
try{
setLoading(true);
const res=await fetch(`${getApi()}/auth/login`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({client_id:getClientId(),mobile:mobile.trim(),password:password})});
const data=await res.json();
if(!res.ok){alert(data.detail||"Login failed");return;}
saveUserSession(data.user);
window.location.href=getRedirect();
}catch(err){alert("Backend connect nahi ho raha");}finally{setLoading(false);}
};

const loginDemo=async()=>{
try{
setDemoLoading(true);
const res=await fetch(`${getApi()}/auth/demo-login?client_id=${getClientId()}`,{method:"POST"});
const data=await res.json();
if(!res.ok){alert(data.detail||"Demo login failed");return;}
saveUserSession(data.user);
window.location.href=getRedirect();
}catch(err){
localStorage.setItem("client_id",getClientId());
localStorage.setItem("user","DEMO123");
localStorage.setItem("user_name","DEMO123");
localStorage.setItem("balance","0");
localStorage.setItem("isDemo","true");
window.location.href=getRedirect();
}finally{setDemoLoading(false);}
};

return(
<div className="login-page">
<div className="login-bg"/>
<div className="login-shade"/>
<main className="login-box">
<div className="login-crown">♛</div>
<h1>{companyName}</h1>
<p>PLAY • WIN • REPEAT</p>
<label>Mobile Number</label>
<div className="login-input"><span>🇮🇳 +91</span><input value={mobile} onChange={(e)=>setMobile(e.target.value)} placeholder="Enter mobile number"/></div>
<label>Password</label>
<div className="login-input"><span>🔒</span><input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" placeholder="Enter password"/><button type="button">◉</button></div>
<a className="forgot" href={`/forgot-password${window.location.search}`}>Forgot Password?</a>
<button className="login-btn" onClick={login} disabled={loading}>{loading?"PLEASE WAIT...":"LOGIN"}</button>
<div className="or"><span/>OR<span/></div>
<button className="demo-btn" onClick={loginDemo} disabled={demoLoading}>👤 {demoLoading?"PLEASE WAIT...":"LOGIN WITH DEMO ID"}</button>
<div className="signup-row"><span>Don't have an account?</span><a href={`/create-account${window.location.search}`} className="create-account-link">Create Account</a></div>
</main>
<footer className="login-footer">
<a href="https://wa.me/919999999999" target="_blank" rel="noreferrer">🎧 Support</a>
<a href="/terms">📄 Terms & Conditions</a>
<a href="/privacy">🛡 Privacy Policy</a>
<span>© 2024 {companyName}. All rights reserved.</span>
</footer>
</div>
);
}