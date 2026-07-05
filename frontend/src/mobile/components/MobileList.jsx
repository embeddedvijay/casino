import React from "react";
export default function MobileList({items}){return <div className="m-list">{items.map((it,i)=><div className="m-list-item" key={i}>{it.map((x,j)=><div key={j} className={j===0?"m-main":"m-sub"}>{x}</div>)}</div>)}</div>}
