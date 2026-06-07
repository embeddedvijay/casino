import React,{useState}from"react";
import"./MobileCreateAccount.css";
import{getClientId,getApi}from"../shared/userSession";

export default function MobileCreateAccount(){
const companyName="Gold 365";
const[fullName,setFullName]=useState("");
const[mobile,setMobile]=useState("");
const[password,setPassword]=useState("");
const[confirmPassword,setConfirmPassword]=useState("");
const[loading,setLoading]=useState(false);

const createAccount=async()=>{
if(!fullName.trim()||!mobile.trim()||!password.trim()||!confirmPassword.trim()){alert("Sab field bharo");return;}
if(password!==confirmPassword){alert("Password match nahi hai");return;}
try{
setLoading(true);
const res=await fetch(`${getApi()}/auth/create-account`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({client_id:getClientId(),full_name:fullName.trim(),mobile:mobile.trim(),password:password,confirm_password:confirmPassword})});
const data=await res.json();
if(!res.ok){alert(data.detail||"Account create nahi hua");return;}
alert("Account created successfully");
window.location.href=`/login${window.location.search}`;
}catch(err){alert("Backend connect nahi ho raha");}finally{setLoading(false);}
};

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
<div className="mcreate-input"><span>👤</span><input value={fullName} onChange={(e)=>setFullName(e.target.value)} placeholder="Enter full name"/></div>
<label>Mobile Number</label>
<div className="mcreate-input"><span>🇮🇳 +91</span><input value={mobile} onChange={(e)=>setMobile(e.target.value)} placeholder="Enter mobile number"/></div>
<label>Password</label>
<div className="mcreate-input"><span>🔒</span><input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" placeholder="Enter password"/></div>
<label>Confirm Password</label>
<div className="mcreate-input"><span>🔒</span><input value={confirmPassword} onChange={(e)=>setConfirmPassword(e.target.value)} type="password" placeholder="Confirm password"/></div>
<button className="mcreate-btn" onClick={createAccount} disabled={loading}>{loading?"PLEASE WAIT...":"CREATE ACCOUNT"}</button>
<div className="mcreate-or"><span/>OR<span/></div>
<div className="mcreate-login-row"><span>Already have an account?</span><a href={`/login${window.location.search}`}>Login</a></div>
</main>
</div>
);
}