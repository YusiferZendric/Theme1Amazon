/*
* https://gitgud.io/ahsk/clewd
* https://github.com/h-a-s-k/clewd
*/"use strict";const{genericFixes:z}=require("./clewd-utils.js"),K={user:"Human",assistant:"Assistant",system:"",example_user:"H",example_assistant:"A"},M=[...new Set([...Object.values(K).join(""),..."\n",...":",..."\\n"])].filter((e=>" "!==e)).sort(),Q=["[Start a new Chat]","[Example Chat]"],U=e=>null!=e.name&&["assistant","user"].includes(e.role)&&!(e.name in K),V=e=>Q.some((t=>t.toLowerCase()===e.content.toLowerCase()));module.exports={Replacements:K,DangerChars:M,hasCustomName:U,isSTDivider:V,messagesToPrompt:({messages:e,promptType:t,stripSystem:s,model:n,Config:r})=>{t??="r";s??=false;const i=/^\[Circumstances and context of the dialogue: ([\s\S]+?)\.?\]$/i,a=/^\[([\s\S]+?)'s personality: ([\s\S]+?)\]$/i,o=JSON.parse(JSON.stringify(e)),c=o.filter((e=>"system"===e.role&&!("name"in e))),l=o.filter((e=>["user","assistant"].includes(e.role))),m=o.filter((e=>"name"in e)),d=[...m,...l];let u=null;for(let e=d.length-1;e>=0;e--){const t=d[e];if(t.discard)continue;const s=d.length-e<=r.Settings.SendImageDepth;if(Array.isArray(t.content)){const e=t.content.find((e=>"text"===e.type)),n=t.content.find((e=>"image_url"===e.type)),i=e?.text||"",a=n?.image_url?.url;a&&(u||r.Settings.SendImageDepth>0&&s&&(u=a));t.content=i}}d.forEach(((e,t)=>{if(e.discard)return;const s=d[t+1];e.customname=U(e);if(s){const t=e.content.endsWith("\n")?"":"\n";if("name"in e&&"name"in s){if(e.name===s.name){e.content+=`${t}${s.content}`;s.discard=true}}else if(["user","assistant"].includes(s.role)){if(s.role===e.role){e.content+=`${t}${s.content}`;s.discard=true}}else{e.content+=`${t}${s.content}`;s.discard=true}}}));c.forEach((e=>{if(e.discard)return;if(s){e.discard=true;return}const t=e.content.match(i),n=e.content.match(a);if(2===t?.length){e.content=r.ScenarioFormat.replace(/{{scenario}}/gim,t[1]);e.scenario=true}if(3===n?.length){e.content=r.PersonalityFormat.replace(/{{char}}/gim,n[1]).replace(/{{personality}}/gim,n[2]);e.personality=true}" "===e.content&&(e.discard=true);e.content}));l.find((e=>!e.discard&&"assistant"===e.role));const f=l.findLast((e=>!e.discard&&"assistant"===e.role)),p=(l.find((e=>!e.discard&&"user"===e.role)),l.findLast((e=>!e.discard&&"user"===e.role))),g=(l.find((e=>!e.discard)),l.findLast((e=>!e.discard))),S=(o.find((e=>!e.discard)),o.findLast((e=>!e.discard)),c.find(((e,t)=>0===t))),h=c.findLast(((e,t)=>t===c.length-1));S&&!V(S)&&(S.main=true);h&&!V(h)&&(h.jailbreak=true);g===f&&r.Settings.StripAssistant&&(f.strip=true);g===p&&r.Settings.StripHuman&&(p.strip=true);r.Settings.AllSamples&&!r.Settings.NoSamples&&l.forEach((e=>{if(!e.discard&&![f,p].includes(e))if("user"===e.role){e.name="example_user";e.role="system"}else if("assistant"===e.role){e.name="example_assistant";e.role="system"}else if(!e.customname)throw Error("Invalid message "+JSON.stringify(e))}));r.Settings.NoSamples&&!r.Settings.AllSamples&&m.forEach((e=>{if(!e.discard){if("example_user"===e.name)e.role="user";else if("example_assistant"===e.name)e.role="assistant";else if(!e.customname)throw Error("Invalid message "+JSON.stringify(e));e.customname||delete e.name}}));let y=[];if(!["r","R"].includes(t)){c.forEach((e=>{e.discard||(e.discard="c-c"===t?!e.jailbreak:"c-r"!==t||!e.main&&!e.jailbreak)}));y=c.filter((e=>!e.discard)).map((e=>`"${e.content.substring(0,25).replace(/\n/g,"\\n").trim()}..."`));l.forEach((e=>{e.discard||(g===e?e===g&&g===p&&(p.strip=true):e.discard=true)}))}const x=o.map(((e,t)=>{if(e.discard||e.content.length<1)return"";let s,n="";t>0&&(n="spacing"in e?"":"name"in e&&"system"===e.role?"\n":"\n\n");if(e.strip)s="";else if(e.customname)s=e.name.replaceAll("_"," ")+": ";else{if(!(e.role in K))throw Error("Couldn't find valid prefix "+JSON.stringify(e));s="name"in e&&e.name in K?K[e.name]+": ":"system"!==e.role?K[e.role]+": ":""}c.includes(e)||(e.content=e.content.trim());return`${n}${s}${e.content}`}));return{prompt:""+z(x.join("")).trim(),systems:y,image:u}}};