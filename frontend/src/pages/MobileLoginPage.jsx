import React,{useState}from"react";
import"./MobileLoginPage.css";

const HOST=window.location.hostname;
const API=`http://${HOST}:8005`;
const getClientId=()=>{
const params=new URLSearchParams(window.location.search);
return params.get("client_id")||localStorage.getItem("client_id")||"demo";
};
const getRedirect=()=>new URLSearchParams(window.location.search).get("redirect")||"/";
const saveUser=(user,isDemo=false)=>{
localStorage.setItem("client_id",user?.client_id||getClientId());
localStorage.setItem("user",user?.username||user?.mobile||"DEMO123");
localStorage.setItem("user_id",user?.id||"");
localStorage.setItem("user_name",user?.full_name||user?.username||"");
localStorage.setItem("user_mobile",user?.mobile||"");
localStorage.setItem("balance",String(user?.balance??0));
localStorage.setItem("isDemo",String(isDemo));
};

export default function MobileLoginPage(){
const[companyName]=useState("Gold 365");
const[mobile,setMobile]=useState("");
const[password,setPassword]=useState("");
const[loading,setLoading]=useState(false);
const[demoLoading,setDemoLoading]=useState(false);
const login=async()=>{
if(!mobile.trim()||!password.trim()){alert("Mobile number aur password bharo");return;}
try{
setLoading(true);
const res=await fetch(`${API}/auth/login`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({client_id:getClientId(),mobile:mobile.trim(),password:password})});
const data=await res.json();
if(!res.ok){alert(data.detail||"Login failed");return;}
saveUser(data.user,false);
window.location.href=getRedirect();
}catch(err){alert("Backend connect nahi ho raha");}finally{setLoading(false);}
};
const loginDemo=async()=>{
try{
setDemoLoading(true);
const res=await fetch(`${API}/auth/demo-login?client_id=${getClientId()}`,{method:"POST"});
const data=await res.json();
if(!res.ok){alert(data.detail||"Demo login failed");return;}
saveUser(data.user,true);
window.location.href=getRedirect();
}catch(err){
localStorage.setItem("client_id",getClientId());
localStorage.setItem("user","DEMO123");
localStorage.setItem("isDemo","true");
window.location.href=getRedirect();
}finally{setDemoLoading(false);}
};
return(
<div className="mlogin-page">
<div className="mlogin-bg"/>
<div className="mlogin-shade"/>
<main className="mlogin-box">
<div className="mlogin-crown">♛</div>
<h1>{companyName}</h1>
<p>PLAY • WIN • REPEAT</p>
<label>Mobile Number</label>
<div className="mlogin-input"><span>🇮🇳 +91</span><input value={mobile} onChange={(e)=>setMobile(e.target.value)} placeholder="Enter mobile number"/></div>
<label>Password</label>
<div className="mlogin-input"><span>🔒</span><input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" placeholder="Enter password"/><button type="button">◉</button></div>
<a className="mlogin-forgot" href={`/forgot-password${window.location.search}`}>Forgot Password?</a>
<button className="mlogin-btn" onClick={login} disabled={loading}>{loading?"PLEASE WAIT...":"LOGIN"}</button>
<div className="mlogin-or"><span/>OR<span/></div>
<button className="mlogin-demo-btn" onClick={loginDemo} disabled={demoLoading}>👤 {demoLoading?"PLEASE WAIT...":"LOGIN WITH DEMO ID"}</button>
<div className="mlogin-signup-row"><span>Don't have an account?</span><a href={`/create-account${window.location.search}`} className="mlogin-create-account-link">Create Account</a></div>
</main>
</div>
);
}