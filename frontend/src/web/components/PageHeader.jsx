import React from "react";
export default function PageHeader({title,subtitle,button}){return <div className="page-top"><div><h2 className="page-title">{title}</h2>{subtitle&&<p className="page-subtitle">{subtitle}</p>}</div>{button&&<button className="primary-btn">{button}</button>}</div>}
