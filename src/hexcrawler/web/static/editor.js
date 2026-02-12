let mode = 'paint';
const grid = document.getElementById('grid');
const log = document.getElementById('log');

async function api(path, data){
  return fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)}).then(r=>r.json());
}

async function refresh(){
  const w = await fetch('/api/world').then(r=>r.json());
  grid.innerHTML='';
  for (const cell of w.terrain){
    const d = document.createElement('button');
    d.className = `hex ${cell.t}`;
    d.textContent = `${cell.q},${cell.r}`;
    d.onclick = ()=> onHex(cell.q, cell.r);
    grid.appendChild(d);
  }
  log.textContent = `tick=${w.tick}\nsites=${w.sites.length}\nspawners=${w.spawners.length}\nroutes=${w.routes.length}\nrumors=${w.rumors.length}\nunrest=${JSON.stringify(w.regional_unrest)}`;
}

async function onHex(q,r){
  if(mode==='paint') await api('/api/paint',{q,r,terrain:document.getElementById('terrain').value});
  if(mode==='site') await api('/api/site',{q,r,kind:document.getElementById('siteKind').value});
  if(mode==='spawn') await api('/api/spawner',{q,r,table:'wilds_basic'});
  await refresh();
}

async function saveRoute(){
  await api('/api/route',{q1:+document.getElementById('q1').value,r1:+document.getElementById('r1').value,q2:+document.getElementById('q2').value,r2:+document.getElementById('r2').value});
  await refresh();
}

async function saveEncounter(){ await api('/api/encounter',{id:'wilds_basic', first_weight:document.getElementById('weight').value}); await refresh(); }
async function saveRumorTemplate(){ await api('/api/rumor-template',{id:'raid_rumor', ttl_ticks:document.getElementById('rumorTtl').value, max_hops:document.getElementById('rumorHops').value}); await refresh(); }
async function saveWeapon(){ await api('/api/weapon',{id:'spear', penetration:document.getElementById('weaponPen').value}); await refresh(); }
async function saveArmor(){ await api('/api/armor',{armor_id:'mail', damage_type:'pierce', arc:'front', value:document.getElementById('armorThreshold').value}); await refresh(); }
async function saveWound(){ await api('/api/wound',{id:'slash', mobility_delta:document.getElementById('woundMob').value, dexterity_delta:document.getElementById('woundDex').value}); await refresh(); }
async function saveFaction(){ await api('/api/faction',{id:'settlers', settlement:document.getElementById('settlement').value}); await refresh(); }
async function simulateDays(){ await api('/api/simulate',{days:document.getElementById('days').value}); await refresh(); }

refresh();
