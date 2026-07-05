import React from "react";
export default function MobileHeader({title,subtitle}){return <div className="m-header"><div className="m-topbar"><button className="m-icon-btn">☰</button><div className="m-logo">LOGO</div><button className="m-icon-btn">🔔</button></div><h2>{title}</h2>{subtitle&&<p>{subtitle}</p>}</div>}
