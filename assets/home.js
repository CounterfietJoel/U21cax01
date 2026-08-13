document.addEventListener('DOMContentLoaded',()=>{
  const tabs=[...document.querySelectorAll('[role="tab"]')];
  const activate=tab=>{
    tabs.forEach(item=>{const selected=item===tab;item.setAttribute('aria-selected',String(selected));item.tabIndex=selected?0:-1;document.getElementById(item.getAttribute('aria-controls')).hidden=!selected});
    try{sessionStorage.setItem('u21cax01-unit',tab.id)}catch(error){}
  };
  tabs.forEach((tab,index)=>{
    tab.addEventListener('click',()=>activate(tab));
    tab.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();let next=index;if(event.key==='ArrowRight')next=(index+1)%tabs.length;if(event.key==='ArrowLeft')next=(index-1+tabs.length)%tabs.length;if(event.key==='Home')next=0;if(event.key==='End')next=tabs.length-1;activate(tabs[next]);tabs[next].focus()});
  });
  try{const saved=document.getElementById(sessionStorage.getItem('u21cax01-unit'));if(saved)activate(saved)}catch(error){}
});
