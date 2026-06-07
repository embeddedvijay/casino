import React,{useState}from"react";
import"./ForgotPassword.css";
import{getClientId,getApi}from"../shared/userSession";

export default function ForgotPassword(){
const companyName="Gold 365";
const[name,setName]=useState("");
const[mobile,setMobile]=useState("");
const[loading,setLoading]=useState(false);

const requestReset=async()=>{
if(!name.trim()||!mobile.trim()){alert("Name aur mobile number dono bharo");return;}
try{
setLoading(true);
const res=await fetch(`${getApi()}/auth/forgot-password`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({client_id:getClientId(),name:name.trim(),mobile:mobile.trim()})});
const data=await res.json();
if(!res.ok){alert(data.detail||"Reset request submit nahi hua");return;}
alert("Password reset request submitted");
}catch(err){alert("Backend connect nahi ho raha");}finally{setLoading(false);}
};

return(
<div className="forgot-page">
<div className="forgot-bg"/>
<div className="forgot-shade"/>
<main className="forgot-box">
<a className="back-login" href={`/login${window.location.search}`}>← Back to Login</a>
<div className="forgot-crown">♛</div>
<h1>{companyName}</h1>
<p>SUPPORT • VERIFY • RESET</p>
<label>Registered Name</label>
<div className="forgot-input"><span>👤</span><input value={name} onChange={(e)=>setName(e.target.value)} placeholder="Enter registered name"/></div>
<label>Mobile Number</label>
<div className="forgot-input"><span>🇮🇳 +91</span><input value={mobile} onChange={(e)=>setMobile(e.target.value)} placeholder="Enter mobile number"/></div>
<button className="reset-btn" onClick={requestReset} disabled={loading}>{loading?"PLEASE WAIT...":"REQUEST PASSWORD RESET"}</button>
<a className="telegram-support" href="https://t.me/YOUR_TELEGRAM_USERNAME" target="_blank" rel="noreferrer">✈️ Contact Telegram Support</a>
<div className="login-row"><span>Remember password?</span><a href={`/login${window.location.search}`}>Login</a></div>
</main>
<footer className="forgot-footer">
<a href="https://t.me/YOUR_TELEGRAM_USERNAME" target="_blank" rel="noreferrer">✈️ Telegram Support</a>
<a href="/terms">📄 Terms & Conditions</a>
<a href="/privacy">🛡 Privacy Policy</a>
<span>© 2024 {companyName}. All rights reserved.</span>
</footer>
</div>
);
}