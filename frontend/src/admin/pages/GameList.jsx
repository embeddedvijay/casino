import React,{useEffect,useState}from"react";
import AdminLayout from"../components/AdminLayout";
import{api}from"../api";
export default function GameList(){
 const[games,setGames]=useState([]);const load=()=>api("/api/admin/games").then(setGames).catch(()=>{});useEffect(load,[]);
 const toggle=async g=>{await api(`/api/admin/games/${g.key}`,{method:"PATCH",body:JSON.stringify({enabled:!g.enabled})});load()};
 return <AdminLayout title="Game Settings"><div className="ca-title"><div><h1>Game Settings</h1><p>Open an individual game to manage its settings.</p></div></div><section className="ca-card"><table className="ca-table"><thead><tr><th>Game</th><th>Key</th><th>Status</th><th>Action</th><th></th></tr></thead><tbody>{games.map(g=><tr key={g.key}><td>{g.name}</td><td><code>{g.key}</code></td><td><span className={g.enabled?"ca-badge on":"ca-badge off"}>{g.enabled?"Active":"Inactive"}</span></td><td><input type="checkbox" checked={!!g.enabled} onChange={()=>toggle(g)}/></td><td><a className="ca-link" href={`/casino-admin/games/${g.key}`}>Manage</a></td></tr>)}</tbody></table></section></AdminLayout>
}
