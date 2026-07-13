const HOST=window.location.hostname;
export const API_BASE=`http://${HOST}:8005`;

export async function api(path,options={}){
  const response=await fetch(`${API_BASE}${path}`,{
    headers:{
      "Content-Type":"application/json",
      ...(options.headers||{})
    },
    ...options
  });

  const data=await response.json().catch(()=>({}));

  if(!response.ok){
    throw new Error(data.detail||data.message||"Request failed");
  }

  return data;
}