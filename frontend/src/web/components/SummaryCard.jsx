import React from "react";
export default function SummaryCard({label,value,note}){return <div className="summary-card"><div className="summary-label">{label}</div><div className="summary-value">{value}</div>{note&&<div className="summary-note">{note}</div>}</div>}
