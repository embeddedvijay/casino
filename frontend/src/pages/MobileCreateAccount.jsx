import React from"react";
import"./CreateAccount.css";

export default function CreateAccount(){
const companyName="Gold 365";
const loginDemo=()=>{const redirect=new URLSearchParams(window.location.search).get("redirect")||"/";localStorage.setItem("user","DEMO123");localStorage.setItem("isDemo","true");window.location.href=redirect;};
return(
<div className="create-page">
<div className="create-bg"/>
<div className="create-shade"/>
<main className="create-box">
<a className="back-login" href={`/login${window.location.search}`}>← Back to Login</a>
<div className="create-crown">♛</div>
<h1>{companyName}</h1>
<p>JOIN NOW • START WINNING</p>
<label>Full Name</label>
<div className="create-input"><span>👤</span><input placeholder="Enter full name"/></div>
<label>Mobile Number</label>
<div className="create-input"><span>🇮🇳 +91</span><input placeholder="Enter mobile number"/></div>
<label>Password</label>
<div className="create-input"><span>🔒</span><input type="password" placeholder="Enter password"/></div>
<label>Confirm Password</label>
<div className="create-input"><span>🔒</span><input type="password" placeholder="Confirm password"/></div>
<button className="create-btn">CREATE ACCOUNT</button>
<div className="or"><span/>OR<span/></div>
<div className="login-row"><span>Already have an account?</span><a href={`/login${window.location.search}`}>Login</a></div>
</main>
<footer className="create-footer">
<a href="https://wa.me/919999999999" target="_blank" rel="noreferrer">🎧 Support</a>
<a href="/terms">📄 Terms & Conditions</a>
<a href="/privacy">🛡 Privacy Policy</a>
<span>© 2024 {companyName}. All rights reserved.</span>
</footer>
</div>
);
}