import React from"react";
import"./MobileCreateAccount.css";

export default function MobileCreateAccount(){
const companyName="Gold 365";
return(
<div className="mcreate-page">
<div className="mcreate-bg"/>
<div className="mcreate-shade"/>
<main className="mcreate-box">
<a className="mcreate-back-login" href={`/login${window.location.search}`}>← Back to Login</a>
<div className="mcreate-crown">♛</div>
<h1>{companyName}</h1>
<p>JOIN NOW • START WINNING</p>
<label>Full Name</label>
<div className="mcreate-input"><span>👤</span><input placeholder="Enter full name"/></div>
<label>Mobile Number</label>
<div className="mcreate-input"><span>🇮🇳 +91</span><input placeholder="Enter mobile number"/></div>
<label>Password</label>
<div className="mcreate-input"><span>🔒</span><input type="password" placeholder="Enter password"/></div>
<label>Confirm Password</label>
<div className="mcreate-input"><span>🔒</span><input type="password" placeholder="Confirm password"/></div>
<button className="mcreate-btn">CREATE ACCOUNT</button>
<div className="mcreate-or"><span/>OR<span/></div>
<div className="mcreate-login-row"><span>Already have an account?</span><a href={`/login${window.location.search}`}>Login</a></div>
</main>
</div>
);
}
