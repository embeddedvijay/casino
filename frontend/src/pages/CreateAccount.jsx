import React,{useState}from"react";
import"./CreateAccount.css";

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

export default function CreateAccount(){
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
const res=await fetch(`${API}/auth/create-account`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({client_id:getClientId(),full_name:fullName.trim(),mobile:mobile.trim(),password:password,confirm_password:confirmPassword})});
const data=await res.json();
if(!res.ok){alert(data.detail||"Account create nahi hua");return;}
alert("Account created successfully");
window.location.href=`/login${window.location.search}`;
}catch(err){alert("Backend connect nahi ho raha");}finally{setLoading(false);}
};
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
<div className="create-input"><span>👤</span><input value={fullName} onChange={(e)=>setFullName(e.target.value)} placeholder="Enter full name"/></div>
<label>Mobile Number</label>
<div className="create-input"><span>🇮🇳 +91</span><input value={mobile} onChange={(e)=>setMobile(e.target.value)} placeholder="Enter mobile number"/></div>
<label>Password</label>
<div className="create-input"><span>🔒</span><input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" placeholder="Enter password"/></div>
<label>Confirm Password</label>
<div className="create-input"><span>🔒</span><input value={confirmPassword} onChange={(e)=>setConfirmPassword(e.target.value)} type="password" placeholder="Confirm password"/></div>
<button className="create-btn" onClick={createAccount} disabled={loading}>{loading?"PLEASE WAIT...":"CREATE ACCOUNT"}</button>
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