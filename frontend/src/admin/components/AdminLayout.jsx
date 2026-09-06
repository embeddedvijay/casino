import React from"react";
import"../styles/admin.css";
const nav=[
{label:"Dashboard",path:"/casino-admin",icon:"⌂"},
{label:"Management",path:"/casino-admin/management",icon:"📊"},
{label:"Casino Settings",path:"/casino-admin/settings",icon:"🏛"},
{label:"Game Settings",path:"/casino-admin/games",icon:"🎮"}
];
export default function AdminLayout({title,children}){
 const path=window.location.pathname;
 return <div className="ca-shell"><aside className="ca-sidebar"><div className="ca-logo">♛ <span>GOLD365</span><small>CASINO ADMIN</small></div><nav>{nav.map(n=><a key={n.path} className={path===n.path||path.startsWith(n.path+"/")?"active":""} href={n.path}><i>{n.icon}</i>{n.label}</a>)}</nav></aside><section className="ca-page"><header className="ca-top"><button className="ca-menu">☰</button><strong>{title}</strong><span>Admin</span></header><main className="ca-content">{children}</main></section></div>
}
