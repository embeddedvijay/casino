import React,{useState}from"react";
import"./MobileForgotPassword.css";

export default function MobileForgotPassword(){
const companyName="Gold 365";
const[name,setName]=useState("");
const[mobile,setMobile]=useState("");
const requestReset=()=>{
if(!name.trim()||!mobile.trim()){alert("Name aur mobile number dono bharo");return;}
const msg=encodeURIComponent(`Password Reset Request
Name: ${name}
Mobile: ${mobile}
Company: ${companyName}`);
window.open(`https://t.me/YOUR_TELEGRAM_USERNAME?text=${msg}`,"_blank");
};
return(
<div className="mforgot-page">
<div className="mforgot-bg"/>
<div className="mforgot-shade"/>
<main className="mforgot-box">
<a className="mforgot-back-login" href={`/login${window.location.search}`}>← Back to Login</a>
<div className="mforgot-crown">♛</div>
<h1>{companyName}</h1>
<p>SUPPORT • VERIFY • RESET</p>
<label>Registered Name</label>
<div className="mforgot-input"><span>👤</span><input value={name} onChange={(e)=>setName(e.target.value)} placeholder="Enter registered name"/></div>
<label>Mobile Number</label>
<div className="mforgot-input"><span>🇮🇳 +91</span><input value={mobile} onChange={(e)=>setMobile(e.target.value)} placeholder="Enter mobile number"/></div>
<button className="mforgot-reset-btn" onClick={requestReset}>REQUEST PASSWORD RESET</button>
<a className="mforgot-telegram-support" href="https://t.me/YOUR_TELEGRAM_USERNAME" target="_blank" rel="noreferrer">✈️ Contact Telegram Support</a>
<div className="mforgot-login-row"><span>Remember password?</span><a href={`/login${window.location.search}`}>Login</a></div>
</main>
</div>
);
}
