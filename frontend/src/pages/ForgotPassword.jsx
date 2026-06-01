import React,{useState}from"react";
import"./ForgotPassword.css";

export default function ForgotPassword(){
const companyName="Gold 365";
const[name,setName]=useState("");
const[mobile,setMobile]=useState("");
const requestReset=()=>{
if(!name.trim()||!mobile.trim()){alert("Name aur mobile number dono bharo");return;}
const msg=encodeURIComponent(`Password Reset Request\nName: ${name}\nMobile: ${mobile}\nCompany: ${companyName}`);
window.open(`https://t.me/YOUR_TELEGRAM_USERNAME?text=${msg}`,"_blank");
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
<button className="reset-btn" onClick={requestReset}>REQUEST PASSWORD RESET</button>
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