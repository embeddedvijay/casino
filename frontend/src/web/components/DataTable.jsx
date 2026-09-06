import React from "react";
export default function DataTable({columns,rows}){return <div className="table-wrap"><table className="data-table"><thead><tr>{columns.map((c,i)=><th key={i}>{c}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}>{r.map((v,j)=><td key={j}>{v}</td>)}</tr>)}</tbody></table></div>}
