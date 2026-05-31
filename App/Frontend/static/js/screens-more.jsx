/* GreenHash — screens part 2: Catálogo, Materiales, Historial, Configuración, Ayuda */
const G2 = window.GH;
const { Icons: Ic2, Breadcrumb: Crumb, ProductThumb: Thumb, fmt: fmt2, gc: gc2 } = G2;

/* ---------- CATÁLOGO ---------- */
function Catalogo({ balance, doBuy, products }) {
  const [detail, setDetail] = useState(null);
  const [toast, setToast] = useState(null);
  const buy = (p) => {
    if (p.price > balance) { setToast({ ok: false, msg: 'Saldo insuficiente para ' + p.name }); }
    else { doBuy(p); setToast({ ok: true, msg: '¡Compraste ' + p.name + '!' }); }
    setDetail(null);
    setTimeout(() => setToast(null), 2600);
  };
  return (
    <div className="screen">
      <Crumb path={['Dashboard', 'Catálogo']} />
      <div className="page-head"><h1>Catálogo de Productos</h1><p>Explora productos sostenibles disponibles en la plataforma.</p></div>

      <div className="prod-grid">
        {products.map(p => (
          <div key={p.id} className="card prod-card">
            <Thumb tint={p.tint} name={p.name} img={p.img} />
            <div className="prod-body">
              <strong>{p.name}</strong>
              <p>{p.desc}</p>
              <div className="prod-price">{gc2(p.price)} <span>GC</span></div>
              <button className="btn-primary full" onClick={() => setDetail(p)}>Ver Detalles</button>
            </div>
          </div>
        ))}
      </div>

      {detail && (
        <div className="modal-overlay" onClick={() => setDetail(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <button className="modal-x" onClick={() => setDetail(null)}>✕</button>
            <Thumb tint={detail.tint} name={detail.name} img={detail.img} size="xl" />
            <div className="modal-body">
              <h3>{detail.name}</h3>
              <p>{detail.desc}</p>
              <ul className="spec">
                <li><Ic2.recycle size={16}/> Material reciclado certificado</li>
                <li><Ic2.leaf size={16}/> Bajo impacto de carbono</li>
                <li><Ic2.package size={16}/> Envío neutral en CO₂</li>
              </ul>
              <div className="modal-foot">
                <div className="prod-price lg">{gc2(detail.price)} <span>GC</span></div>
                <button className={'btn-primary btn-lg ' + (detail.price>balance?'is-disabled':'')} onClick={() => buy(detail)}>
                  {detail.price>balance ? 'Saldo insuficiente' : 'Canjear ahora'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {toast && <div className={'toast ' + (toast.ok ? 'ok' : 'bad')}>{toast.ok ? <Ic2.checkCircle size={18}/> : <Ic2.info size={18}/>}{toast.msg}</div>}
    </div>
  );
}

/* ---------- CONSULTA DE MATERIALES ---------- */
function Materiales({ materials, categories }) {
  const [q, setQ] = useState('');
  const [cat, setCat] = useState(categories[0]);
  const [open, setOpen] = useState(false);
  const rows = materials.filter(m =>
    (cat === categories[0] || m.cat === cat) &&
    m.name.toLowerCase().includes(q.toLowerCase()));
  const catIcon = { Plástico: 'package', Metal: 'coin', Textil: 'bag', Vidrio: 'info', Papel: 'history', Mixto: 'recycle' };
  return (
    <div className="screen">
      <Crumb path={['Dashboard', 'Consulta de Materiales']} />
      <div className="page-head"><h1>Consulta de Materiales</h1><p>Busca materiales aceptados y sus recompensas.</p></div>

      <div className="card">
        <div className="toolbar">
          <span className="input-ico grow"><span className="ii"><Ic2.search size={18}/></span>
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Buscar materiales…"/></span>
          <div className="select" onClick={()=>setOpen(o=>!o)} tabIndex={0} onBlur={()=>setOpen(false)}>
            {cat} <Ic2.chevDown size={16}/>
            {open && <ul className="select-menu">{categories.map(c => <li key={c} className={c===cat?'sel':''} onMouseDown={()=>{setCat(c);setOpen(false);}}>{c}</li>)}</ul>}
          </div>
        </div>
        <table className="data-table">
          <thead><tr><th>Material</th><th>Categoría</th><th className="ta-r">Recompensa (GC)</th><th className="ta-r">Estado</th></tr></thead>
          <tbody>
            {rows.map(m => {
              const I = Ic2[catIcon[m.cat] || 'package'];
              const cls = m.status === 'Aceptado' ? 'ok' : m.status === 'En revisión' ? 'warn' : 'bad';
              return (
                <tr key={m.id}>
                  <td><span className="mat-ico"><I size={16}/></span><b>{m.name}</b></td>
                  <td className="muted">{m.cat}</td>
                  <td className="ta-r"><b className={m.reward>0?'pos':'muted'}>{m.reward>0?'+'+m.reward.toFixed(1)+' GC':'—'}</b></td>
                  <td className="ta-r"><span className={'pill ' + cls}>{m.status}</span></td>
                </tr>
              );
            })}
            {rows.length === 0 && <tr><td colSpan="4" className="empty">No se encontraron materiales.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ---------- HISTORIAL ---------- */
function Historial({ history, balance }) {
  const [filter, setFilter] = useState('Todas las actividades');
  const [open, setOpen] = useState(false);
  const [page, setPage] = useState(1);
  const types = ['Todas las actividades', 'Transferencia', 'Recompensa', 'Compra'];
  const filtered = history.filter(h => filter === types[0] || h.type === filter);
  // running balance: newest row shows current balance, older rows subtract
  let run = balance;
  const withBal = history.map(h => { const b = run; run = +(run - h.amount).toFixed(2); return { ...h, bal: b }; });
  const rows = withBal.filter(h => filter === types[0] || h.type === filter);
  const perPage = 6;
  const pages = Math.max(1, Math.ceil(rows.length / perPage));
  const pageRows = rows.slice((page-1)*perPage, page*perPage);
  return (
    <div className="screen">
      <Crumb path={['Dashboard', 'Historial de Actividad']} />
      <div className="page-head"><h1>Historial de Actividad</h1><p>Consulta todas tus transacciones y actividades en la plataforma.</p></div>

      <div className="card">
        <div className="toolbar">
          <div className="select" onClick={()=>setOpen(o=>!o)} tabIndex={0} onBlur={()=>setOpen(false)}>
            {filter} <Ic2.chevDown size={16}/>
            {open && <ul className="select-menu">{types.map(t => <li key={t} className={t===filter?'sel':''} onMouseDown={()=>{setFilter(t);setPage(1);setOpen(false);}}>{t}</li>)}</ul>}
          </div>
          <div className="date-range"><Ic2.calendar size={16}/> 01/05/2024 – 12/05/2024</div>
        </div>
        <table className="data-table">
          <thead><tr><th>Fecha</th><th>Tipo</th><th>Descripción</th><th className="ta-r">Monto</th><th className="ta-r">Balance</th></tr></thead>
          <tbody>
            {pageRows.map(h => (
              <tr key={h.id}>
                <td className="muted">{h.date}</td>
                <td><span className={'pill soft ' + h.type}>{h.type}</span></td>
                <td>{h.desc}</td>
                <td className={'ta-r amt ' + (h.amount<0?'neg':'pos')}>{fmt2(h.amount)}</td>
                <td className="ta-r"><b>{gc2(h.bal)} GC</b></td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="pager">
          <button className="pg-btn" disabled={page===1} onClick={()=>setPage(p=>p-1)}><Ic2.chevLeft size={15}/></button>
          {Array.from({length: Math.min(pages,4)}, (_,i)=>i+1).map(n => (
            <button key={n} className={'pg-btn ' + (n===page?'on':'')} onClick={()=>setPage(n)}>{n}</button>
          ))}
          {pages>4 && <><span className="pg-dots">…</span><button className={'pg-btn '+(page===pages?'on':'')} onClick={()=>setPage(pages)}>{pages}</button></>}
          <button className="pg-btn" disabled={page===pages} onClick={()=>setPage(p=>p+1)}><Ic2.chevRight size={15}/></button>
        </div>
      </div>
    </div>
  );
}

/* ---------- CONFIGURACIÓN ---------- */
function Configuracion({ user }) {
  const [notif, setNotif] = useState({ email: true, push: true, rewards: false });
  const [lang, setLang] = useState('Español');
  return (
    <div className="screen">
      <Crumb path={['Dashboard', 'Configuración']} />
      <div className="page-head"><h1>Configuración</h1><p>Administra tu perfil y preferencias de la cuenta.</p></div>

      <div className="two-col">
        <div className="card">
          <div className="card-head"><h3>Perfil</h3></div>
          <div className="profile-row">
            <span className="profile-av"><Ic2.user size={26}/></span>
            <div><strong>{user.name}</strong><span className="muted">{user.email}</span></div>
            <button className="btn-ghost sm">Cambiar foto</button>
          </div>
          <G2.Field label="Nombre completo"><input defaultValue={user.name + ' Pérez'} /></G2.Field>
          <G2.Field label="Correo electrónico"><input defaultValue={user.email} /></G2.Field>
          <G2.Field label="Institución"><input defaultValue="Campus Universidad" /></G2.Field>
          <button className="btn-primary">Guardar cambios</button>
        </div>

        <div className="stack">
          <div className="card">
            <div className="card-head"><h3>Notificaciones</h3></div>
            {[['email','Correos de actividad'],['push','Notificaciones push'],['rewards','Resumen de recompensas']].map(([k,l]) => (
              <div key={k} className="toggle-row">
                <span>{l}</span>
                <button className={'switch ' + (notif[k]?'on':'')} onClick={()=>setNotif(n=>({...n,[k]:!n[k]}))}><span/></button>
              </div>
            ))}
          </div>
          <div className="card">
            <div className="card-head"><h3>Preferencias</h3></div>
            <div className="toggle-row"><span>Idioma</span>
              <div className="seg">{['Español','English'].map(l => <button key={l} className={lang===l?'on':''} onClick={()=>setLang(l)}>{l}</button>)}</div>
            </div>
            <div className="toggle-row"><span>Moneda</span><b>GreenCoin (GC)</b></div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------- AYUDA ---------- */
function Ayuda() {
  const [open, setOpen] = useState(0);
  const faqs = [
    ['¿Qué son los GreenCoins?', 'Los GreenCoins (GC) son la moneda interna de GreenHash. Los ganas reciclando materiales y puedes usarlos para canjear productos sostenibles o transferirlos a otros usuarios.'],
    ['¿Cómo reciclo materiales?', 'Acércate a una máquina GreenHash, conéctate desde la sección Reciclar, deposita tus materiales limpios y secos, y reclama tu recompensa al finalizar el proceso.'],
    ['¿Qué materiales son aceptados?', 'Consulta la sección "Consulta de Materiales" para ver la lista completa de materiales aceptados, su categoría y la recompensa correspondiente en GC.'],
    ['¿Cómo transfiero GreenCoins?', 'En la sección Transferir, ingresa el destinatario y la cantidad. Se aplica una pequeña tarifa de red que se deduce automáticamente del monto enviado.'],
    ['¿Hay comisiones?', 'Reciclar y recibir recompensas es gratis. Solo las transferencias entre usuarios aplican una tarifa de red mínima de 0.05 GC.'],
  ];
  return (
    <div className="screen">
      <Crumb path={['Dashboard', 'Ayuda']} />
      <div className="page-head"><h1>Centro de Ayuda</h1><p>Encuentra respuestas a las preguntas más frecuentes.</p></div>

      <div className="two-col">
        <div className="card">
          <div className="card-head"><h3>Preguntas frecuentes</h3></div>
          <ul className="faq">
            {faqs.map(([q,a], i) => (
              <li key={i} className={open===i?'open':''}>
                <button onClick={()=>setOpen(open===i?-1:i)}><span>{q}</span><Ic2.chevDown size={18}/></button>
                <div className="faq-a"><p>{a}</p></div>
              </li>
            ))}
          </ul>
        </div>
        <div className="card help-contact">
          <div className="card-head"><h3>¿Aún necesitas ayuda?</h3></div>
          <p className="muted">Nuestro equipo de soporte está disponible para ayudarte.</p>
          <div className="contact-list">
            <div className="contact-item"><span className="ci-ico"><Ic2.bell size={18}/></span><div><strong>Soporte en vivo</strong><span className="muted">Lun–Vie, 9:00–18:00</span></div></div>
            <div className="contact-item"><span className="ci-ico"><Ic2.help size={18}/></span><div><strong>soporte@greenhash.eco</strong><span className="muted">Respuesta en 24h</span></div></div>
          </div>
          <button className="btn-primary full">Contactar soporte</button>
        </div>
      </div>
    </div>
  );
}

/* ---------- BILLETERA AVANZADA (SPLIT / MERGE) ---------- */
function AdvancedWallet({ balance }) {
  const [tab, setTab] = useState('split');
  const [splitCoinId, setSplitCoinId] = useState('GH-COIN-4592');
  const [partitions, setPartitions] = useState('3, 5, 2');
  const [splitResult, setSplitResult] = useState(null);
  const [mergeCoinIds, setMergeCoinIds] = useState('GH-COIN-0128, GH-COIN-1944');
  const [mergeResult, setMergeResult] = useState(null);
  
  const handleSplit = () => {
    setSplitResult({
      success: true,
      original: 10,
      newCoins: [
        { id: 'GH-COIN-4592-A', value: 3 },
        { id: 'GH-COIN-4592-B', value: 5 },
        { id: 'GH-COIN-4592-C', value: 2 },
      ]
    });
  };
  
  const handleMerge = () => {
    setMergeResult({
      success: true,
      mergedValue: 12,
      newCoinId: 'GH-COIN-5502'
    });
  };

  return (
    <div className="screen">
      <Crumb path={['Dashboard', 'Billetera Avanzada']} />
      <div className="page-head">
        <h1>Operaciones de Billetera Avanzada</h1>
        <p>Realiza divisiones (Split) y fusiones (Merge) de tus monedas para la gestión de cambio y prevención de doble gasto.</p>
      </div>
      
      <div className="role-selector" style={{ display: 'flex', gap: '8px', marginBottom: '20px', padding: '4px', backgroundColor: '#e9f6ec', borderRadius: '8px', maxWidth: '360px' }}>
        <button type="button" onClick={()=>setTab('split')} style={{ flex: 1, padding: '8px 12px', border: 'none', borderRadius: '6px', fontSize: '13px', fontWeight: '600', cursor: 'pointer', backgroundColor: tab==='split'?'#2e7d32':'transparent', color: tab==='split'?'#ffffff':'#2e7d32' }}>Fraccionar Monedas (Split)</button>
        <button type="button" onClick={()=>setTab('merge')} style={{ flex: 1, padding: '8px 12px', border: 'none', borderRadius: '6px', fontSize: '13px', fontWeight: '600', cursor: 'pointer', backgroundColor: tab==='merge'?'#2e7d32':'transparent', color: tab==='merge'?'#ffffff':'#2e7d32' }}>Fusionar Monedas (Merge)</button>
      </div>

      <div className="two-col">
        {tab === 'split' ? (
          <div className="card">
            <div className="card-head"><h3>Fraccionar Moneda</h3></div>
            <p className="muted" style={{ marginBottom: '16px' }}>Divide una moneda de alto valor en fracciones más pequeñas para simplificar transferencias exactas.</p>
            
            <G2.Field label="ID de la Moneda a Fraccionar">
              <input value={splitCoinId} onChange={e=>setSplitCoinId(e.target.value)} placeholder="Ej. GH-COIN-XXXX"/>
            </G2.Field>
            
            <G2.Field label="Fracciones a Crear (separadas por comas)" hint="La suma de las fracciones debe coincidir con el valor de la moneda original.">
              <input value={partitions} onChange={e=>setPartitions(e.target.value)} placeholder="Ej. 3, 5, 2"/>
            </G2.Field>
            
            <button className="btn-primary full" onClick={handleSplit}>Ejecutar Fraccionamiento (Split)</button>
            
            {splitResult && (
              <div style={{ marginTop: '16px', padding: '16px', borderRadius: '8px', backgroundColor: '#e8f5e9', border: '1px solid #c8e6c9', color: '#2e7d32' }}>
                <strong style={{ display: 'block', marginBottom: '8px' }}>✅ Simulación de Split Exitosa</strong>
                <p style={{ fontSize: '13px', margin: '0 0 8px 0' }}>Moneda original de <b>10.0 GC</b> fraccionada en:</p>
                <ul style={{ margin: '0 0 12px 16px', padding: '0', fontSize: '13px' }}>
                  {splitResult.newCoins.map(c => <li key={c.id}>{c.id}: <b>{c.value.toFixed(1)} GC</b></li>)}
                </ul>
                <div style={{ padding: '10px', borderRadius: '6px', backgroundColor: '#fff3cd', border: '1px solid #ffeeba', color: '#856404', fontSize: '12px', lineHeight: '1.4' }}>
                  <strong style={{ display: 'block', marginBottom: '2px' }}>⚠️ [STDD ESTADO ROJO]</strong>
                  Esta operación está simulada localmente en el frontend. La función <code>split()</code> en el backend es un stub académico. Implementa la lógica en la rama <code>feature/split</code> en <code>transactions.py</code> para habilitar el fraccionamiento seguro en base de datos.
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="card">
            <div className="card-head"><h3>Fusionar Monedas</h3></div>
            <p className="muted" style={{ marginBottom: '16px' }}>Combina múltiples monedas fraccionadas pequeñas en una sola moneda de mayor valor para consolidar tu billetera.</p>
            
            <G2.Field label="IDs de Monedas a Fusionar (separados por comas)">
              <input value={mergeCoinIds} onChange={e=>setMergeCoinIds(e.target.value)} placeholder="Ej. GH-COIN-XXXX, GH-COIN-YYYY"/>
            </G2.Field>
            
            <button className="btn-primary full" onClick={handleMerge}>Ejecutar Fusión (Merge)</button>
            
            {mergeResult && (
              <div style={{ marginTop: '16px', padding: '16px', borderRadius: '8px', backgroundColor: '#e8f5e9', border: '1px solid #c8e6c9', color: '#2e7d32' }}>
                <strong style={{ display: 'block', marginBottom: '8px' }}>✅ Simulación de Merge Exitosa</strong>
                <p style={{ fontSize: '13px', margin: '0 0 8px 0' }}>Monedas fusionadas en una nueva moneda única:</p>
                <div style={{ fontSize: '13px', marginBottom: '12px' }}>ID: <b>{mergeResult.newCoinId}</b> por un valor total de <b>{mergeResult.mergedValue.toFixed(1)} GC</b></div>
                <div style={{ padding: '10px', borderRadius: '6px', backgroundColor: '#fff3cd', border: '1px solid #ffeeba', color: '#856404', fontSize: '12px', lineHeight: '1.4' }}>
                  <strong style={{ display: 'block', marginBottom: '2px' }}>⚠️ [STDD ESTADO ROJO]</strong>
                  Esta operación está simulada localmente en el frontend. La función <code>merge()</code> en el backend es un stub académico. Implementa la lógica en la rama <code>feature/merge</code> en <code>transactions.py</code> para consolidar saldos en la base de datos de manera definitiva.
                </div>
              </div>
            )}
          </div>
        )}
        
        <div className="card">
          <div className="card-head"><h3>Información de Seguridad del Protocolo</h3></div>
          <ul style={{ display: 'flex', flexDirection: 'column', gap: '14px', padding: '0', margin: '0', listStyle: 'none' }}>
            <li style={{ display: 'flex', gap: '10px' }}>
              <Ic2.checkCircle size={20} style={{ color: '#2e7d32', flexShrink: 0 }}/>
              <span><strong>Prevención de Doble Gasto:</strong> El protocolo valida que el hash de cada moneda de entrada sea inhabilitado de forma permanente en la base de datos central antes de generar las monedas resultantes.</span>
            </li>
            <li style={{ display: 'flex', gap: '10px' }}>
              <Ic2.checkCircle size={20} style={{ color: '#2e7d32', flexShrink: 0 }}/>
              <span><strong>Consistencia y No Repudio:</strong> Al firmar digitalmente cada transacción mediante RSA SHA-256 se garantiza que las monedas no puedan ser duplicadas por atacantes en tránsito.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

Object.assign(window.GH, { Catalogo, Materiales, Historial, AdvancedWallet, Configuracion, Ayuda });
