import React,{useState}from"react";
import"./MobileLoginPage.css";

export default function MobileLoginPage(){
const[companyName]=useState("Gold 365");
const loginDemo=()=>{const redirect=new URLSearchParams(window.location.search).get("redirect")||"/";localStorage.setItem("user","DEMO123");localStorage.setItem("isDemo","true");window.location.href=redirect;};
return(
<div className="mlogin-page">
<div className="mlogin-bg"/>
<div className="mlogin-shade"/>
<main className="mlogin-box">
<div className="mlogin-crown">♛</div>
<h1>{companyName}</h1>
<p>PLAY • WIN • REPEAT</p>
<label>Mobile Number</label>
<div className="mlogin-input"><span>🇮🇳 +91</span><input placeholder="Enter mobile number"/></div>
<label>Password</label>
<div className="mlogin-input"><span>🔒</span><input type="password" placeholder="Enter password"/><button>◉</button></div>
<a className="mlogin-forgot" href={`/forgot-password${window.location.search}`}>Forgot Password?</a>
<button className="mlogin-btn">LOGIN</button>
<div className="mlogin-or"><span/>OR<span/></div>
<button className="mlogin-demo-btn" onClick={loginDemo}>👤 LOGIN WITH DEMO ID</button>
<div className="mlogin-signup-row">
<span>Don't have an account?</span>
<a href={`/create-account${window.location.search}`} className="mlogin-create-account-link">Create Account</a>
</div>
</main>
</div>
);
}
