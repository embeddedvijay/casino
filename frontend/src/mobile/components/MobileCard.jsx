import React from "react";
export default function MobileCard({label,value,note}){return <div className="m-card"><span>{label}</span><strong>{value}</strong>{note&&<small>{note}</small>}</div>}
