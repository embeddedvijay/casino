export const getApi=()=>{
  const host=typeof window!=="undefined"?window.location.hostname:"localhost";
  return `http://${host}:8005`;
};

export const getClientId=()=>{
  if(typeof window==="undefined")return "demo";
  const params=new URLSearchParams(window.location.search);
  return params.get("client_id")||localStorage.getItem("client_id")||"demo";
};

export const saveUserSession=(user)=>{
  if(typeof window==="undefined")return;
  localStorage.setItem("client_id",user?.client_id||"demo");
  localStorage.setItem("user_id",user?.id||"");
  localStorage.setItem("user_name",user?.username||user?.full_name||"DEMO123");
  localStorage.setItem("balance",String(user?.balance??0));
  localStorage.setItem("isDemo",user?.is_demo?"true":"false");
};

export const clearUserSession=()=>{
  if(typeof window==="undefined")return;
  localStorage.removeItem("user_id");
  localStorage.removeItem("user_name");
  localStorage.removeItem("balance");
  localStorage.removeItem("isDemo");
};

export const getLocalUser=()=>{
  if(typeof window==="undefined"){
    return {client_id:"demo",user_id:"",user_name:"DEMO123",balance:0,isDemo:true};
  }
  return {
    client_id:localStorage.getItem("client_id")||"demo",
    user_id:localStorage.getItem("user_id")||"",
    user_name:localStorage.getItem("user_name")||"DEMO123",
    balance:Number(localStorage.getItem("balance")||0),
    isDemo:localStorage.getItem("isDemo")==="true"
  };
};

export const fetchCurrentUser=async()=>{
  const local=getLocalUser();
  if(!local.user_id)return local;
  try{
    const res=await fetch(`${getApi()}/auth/users/${local.user_id}?client_id=${local.client_id}`);
    const data=await res.json();
    if(!res.ok)return local;
    const user=data.user;
    saveUserSession(user);
    return {
      client_id:user.client_id||"demo",
      user_id:user.id||"",
      user_name:user.username||user.full_name||"DEMO123",
      balance:Number(user.balance||0),
      isDemo:user.is_demo||false
    };
  }catch{
    return local;
  }
};

export const getDisplayUser=()=>{
  const user=getLocalUser();
  return {
    name:user.user_name||"DEMO123",
    balance:Number(user.balance||0).toFixed(2)
  };
};