import React,{useEffect,useState}from"react";
import AdminLayout from"../components/AdminLayout";
import{api}from"../api";
export default function CasinoSettings(){
 const[form,setForm]=useState({casino_name:"GOLD365 CASINO",casino_short_name:"GOLD365",telegram_admin_id:"",maintenance_mode:false});
 const[msg,setMsg]=useState("");
 useEffect(()=>{api("/api/admin/casino-settings").then(setForm).catch(()=>{})},[]);
 const change=e=>setForm({...form,[e.target.name]:e.target.type==="checkbox"?e.target.checked:e.target.value});
 const save=async()=>{try{await api("/api/admin/casino-settings",{method:"PUT",body:JSON.stringify(form)});setMsg("Saved successfully")}catch(e){setMsg(e.message)}};
 return <AdminLayout title="Casino Settings"><div className="ca-title"><div><h1>Casino Settings</h1><p>Casino name, Telegram admin ID and platform management</p></div></div><div className="ca-grid2"><section className="ca-card"><h2>Casino Basic Settings</h2><label>Casino Name<input name="casino_name" value={form.casino_name||""} onChange={change}/></label><label>Casino Short Name<input name="casino_short_name" value={form.casino_short_name||""} onChange={change}/></label></section><section className="ca-card"><h2>Telegram Admin Settings</h2><label>Telegram Admin ID<input name="telegram_admin_id" value={form.telegram_admin_id||""} onChange={change}/></label><small>Telegram user ID with full admin access.</small></section></div><section className="ca-card ca-mt"><h2>Management</h2><div className="ca-setting-row"><div><b>Maintenance Mode</b><p>Temporarily block game access.</p></div><input type="checkbox" name="maintenance_mode" checked={!!form.maintenance_mode} onChange={change}/></div></section><div className="ca-actions">{msg&&<span>{msg}</span>}<button onClick={save}>Save Changes</button></div></AdminLayout>
}
