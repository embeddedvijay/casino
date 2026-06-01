import React,{useState}from"react";
import"./LoginPage.css";

export default function LoginPage(){
const[companyName]=useState("Gold 365");
const loginDemo=()=>{const redirect=new URLSearchParams(window.location.search).get("redirect")||"/";localStorage.setItem("user","DEMO123");localStorage.setItem("isDemo","true");window.location.href=redirect;};
return(
<div className="login-page">
<div className="login-bg"/>
<div className="login-shade"/>
<main className="login-box">
<div className="login-crown">♛</div>
<h1>{companyName}</h1>
<p>PLAY • WIN • REPEAT</p>
<label>Mobile Number</label>
<div className="login-input"><span>🇮🇳 +91</span><input placeholder="Enter mobile number"/></div>
<label>Password</label>
<div className="login-input"><span>🔒</span><input type="password" placeholder="Enter password"/><button>◉</button></div>
<a className="forgot" href={`/forgot-password${window.location.search}`}>Forgot Password?</a>
<button className="login-btn">LOGIN</button>
<div className="or"><span/>OR<span/></div>
<button className="demo-btn" onClick={loginDemo}>👤 LOGIN WITH DEMO ID</button>
<div className="signup-row">
  <span>Don't have an account?</span>
  <a href={`/create-account${window.location.search}`} className="create-account-link">
    Create Account
  </a>
</div>
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