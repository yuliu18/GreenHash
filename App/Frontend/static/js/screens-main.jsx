/* GreenHash — screens part 1: Login, Dashboard, Transferir, Reciclar */
const { useState, useEffect, useRef } = React;
const G1 = window.GH;
const { Icons, Brandmark, Logo, fmt, gc } = G1;

/* ---------- shared bits ---------- */
function ProductThumb({ tint, name, img, size = 'lg' }) {
  return (
    <div className={'prod-thumb ' + size}>
      <img src={img} alt={name} className="prod-photo"/>
    </div>
  );
}

function Field({ label, hint, children }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}

/* ---------- LOGIN ---------- */
function Login({ onLogin }) {
  const [role, setRole] = useState('user');
  const [email, setEmail] = useState('juan@campus.edu');
  const [pwd, setPwd] = useState('greenhash');
  
  const selectRole = (r) => {
    setRole(r);
    if (r === 'admin') {
      setEmail('admin@greenhash.eco');
      setPwd('admin123');
    } else {
      setEmail('juan@campus.edu');
      setPwd('greenhash');
    }
  };

  const submit = (e) => { e.preventDefault(); onLogin(role); };
  return (
    <div className="login-page">
      <header className="login-top">
        <Logo size={46} uid="ltop" />
        <div className="login-top-right">
          <button className="icon-btn" title="Tema"><Icons.sun /></button>
          <a className="muted-link">¿Necesitas ayuda?</a>
        </div>
      </header>

      <main className="login-main">
        <section className="login-hero">
          <h1 className="login-h1">Bienvenido a<br/><span className="grad-word">GreenHash</span></h1>
          <p className="login-sub">La plataforma que impulsa un futuro<br/>más <strong className="g">sostenible</strong>, juntos.</p>
          <ul className="login-points">
            {[
              ['leaf', 'Impacto real', 'Transforma tus acciones en un impacto positivo para el planeta.'],
              ['recycle', 'Fácil y transparente', 'Gestiona tus GreenCoins y actividades de forma clara y sencilla.'],
              ['coin', 'Recompensas sostenibles', 'Gana recompensas mientras cuidas el medio ambiente.'],
            ].map(([ic, t, d]) => {
              const I = Icons[ic];
              return (
                <li key={t} className="login-point">
                  <span className="lp-ico"><I /></span>
                  <span><strong>{t}</strong><em>{d}</em></span>
                </li>
              );
            })}
          </ul>
          <div className="login-social-proof">
            <p>Únete a miles de personas que ya están<br/><strong>marcando la diferencia.</strong></p>
            <div className="sp-right">
              <div className="avatars">
              {[1,2,3,4].map(i => (
                <span key={i} className="av"><img src={'../static/avatars/face'+i+'.png'} alt="Usuario"/></span>
              ))}
            </div>
              <div className="sp-count"><strong>+12K</strong><em>usuarios activos</em></div>
            </div>
          </div>
        </section>

        <div className="login-illus" aria-hidden="true">
          <img src={window.LOGIN_ILLUS_SRC} alt=""/>
        </div>

        <section className="login-card-wrap">
          <form className="login-card" onSubmit={submit}>
            <h2>Iniciar sesión</h2>
            
            <div className="role-selector" style={{ display: 'flex', gap: '8px', marginBottom: '20px', padding: '4px', backgroundColor: '#f4f6f5', borderRadius: '8px' }}>
              <button type="button" onClick={()=>selectRole('user')} style={{ flex: 1, padding: '8px 12px', border: 'none', borderRadius: '6px', fontSize: '13px', fontWeight: '600', cursor: 'pointer', backgroundColor: role==='user'?'#ffffff':'transparent', color: role==='user'?'#2e7d32':'#666666', boxShadow: role==='user'?'0 2px 4px rgba(0,0,0,0.06)':'' }}>Usuario Reciclador</button>
              <button type="button" onClick={()=>selectRole('admin')} style={{ flex: 1, padding: '8px 12px', border: 'none', borderRadius: '6px', fontSize: '13px', fontWeight: '600', cursor: 'pointer', backgroundColor: role==='admin'?'#ffffff':'transparent', color: role==='admin'?'#2e7d32':'#666666', boxShadow: role==='admin'?'0 2px 4px rgba(0,0,0,0.06)':'' }}>Administrador</button>
            </div>

            <p className="card-sub">Accede a tu cuenta para continuar</p>
            <Field label="Correo electrónico">
              <span className="input-ico"><span className="ii"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg></span>
                <input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="ejemplo@correo.com"/></span>
            </Field>
            <div className="field">
              <div className="field-row">
                <span className="field-label">Contraseña</span>
                <a className="link-g">¿Olvidaste tu contraseña?</a>
              </div>
              <span className="input-ico"><span className="ii"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><rect x="4" y="11" width="16" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg></span>
                <input type="password" value={pwd} onChange={e=>setPwd(e.target.value)} placeholder="••••••••"/></span>
            </div>
            <button type="submit" className="btn-primary btn-lg">Iniciar sesión <Icons.arrowRight size={18}/></button>
            <div className="divider"><span>o continúa con</span></div>
            <div className="oauth-row">
              <button type="button" className="btn-ghost"><Icons.google /> Google</button>
              <button type="button" className="btn-ghost"><Icons.microsoft /> Microsoft</button>
            </div>
            <p className="card-foot">¿No tienes cuenta? <a className="link-g strong">Regístrate</a></p>
          </form>
        </section>
      </main>

      <footer className="login-foot">
        <Logo size={24} uid="lfoot" />
        <nav className="lf-links"><a>Términos y condiciones</a><a>Política de privacidad</a></nav>
        <div className="lf-social"><span>Síguenos en</span>
          <a className="soc"><Icons.linkedin size={16}/></a><a className="soc"><Icons.instagram size={16}/></a><a className="soc"><Icons.twitter size={16}/></a>
        </div>
        <p className="lf-copy">© 2024 GreenHash. Todos los derechos reservados.</p>
      </footer>
    </div>
  );
}

/* ---------- DASHBOARD ---------- */
function Dashboard({ user, balance, history, go }) {
  const quick = [
    ['transferir', 'send', 'Transferir', 'Envía GreenCoins a otros usuarios.', 'Ir a Transferir'],
    ['reciclar', 'recycle', 'Reciclar', 'Conecta con la máquina y obtén recompensas.', 'Ir a Reciclar'],
    ['catalogo', 'bag', 'Catálogo', 'Explora productos sostenibles y gasta tus GreenCoins.', 'Ir al Catálogo'],
    ['materiales', 'search', 'Consulta de Materiales', 'Busca materiales aceptados y sus recompensas.', 'Consultar'],
  ];
  const typeIcon = (t) => t === 'Transferencia' ? 'send' : t === 'Compra' ? 'bag' : 'recycle';
  return (
    <div className="screen">
      <div className="page-head">
        <h1>Bienvenido, {user.name}</h1>
        <p>Gestiona tus GreenCoins y contribuye al medio ambiente.</p>
      </div>

      <div className="balance-card">
        <div>
          <span className="bc-label">Saldo Actual</span>
          <div className="bc-amount"><strong>{gc(balance)}</strong> GreenCoins</div>
        </div>
        <span className="bc-leaf"><Icons.leaf size={34}/></span>
      </div>

      <div className="quick-grid">
        {quick.map(([id, ic, t, d, cta]) => {
          const I = Icons[ic];
          return (
            <button key={id} className="quick-card" onClick={() => go(id)}>
              <span className="qc-ico"><I size={26}/></span>
              <strong>{t}</strong>
              <em>{d}</em>
              <span className="qc-cta">{cta} <Icons.chevRight size={15}/></span>
            </button>
          );
        })}
      </div>

      <div className="dash-bottom">
        <div className="card recent-card">
          <div className="card-head"><h3>Actividad Reciente</h3></div>
          <table className="mini-table">
            <thead><tr><th>Tipo</th><th>Descripción</th><th>Fecha</th><th className="ta-r">Monto</th></tr></thead>
            <tbody>
              {history.slice(0, 4).map(h => (
                <tr key={h.id}>
                  <td><span className={'tic ' + h.type}>{(()=>{const I=Icons[typeIcon(h.type)];return <I size={16}/>;})()}</span></td>
                  <td><strong>{h.type}</strong><span className="sub">{h.desc}</span></td>
                  <td className="muted">{h.date}</td>
                  <td className={'ta-r amt ' + (h.amount<0?'neg':'pos')}>{fmt(h.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className="link-row" onClick={() => go('historial')}>Ver historial completo <Icons.arrowRight size={15}/></button>
        </div>

        <div className="card impact-card">
          <div className="impact-art" aria-hidden="true">
            <svg viewBox="0 0 240 150" width="100%">
              <rect width="240" height="150" rx="14" fill="#E9F6EC"/>
              <g fill="#ffffff"><ellipse cx="56" cy="34" rx="22" ry="9"/><ellipse cx="74" cy="29" rx="14" ry="7"/></g>
              <g fill="#ffffff" opacity="0.92"><ellipse cx="190" cy="40" rx="18" ry="8"/><ellipse cx="178" cy="36" rx="11" ry="6"/></g>
              <rect x="37" y="98" width="6" height="30" rx="2" fill="#5FA86E"/>
              <circle cx="40" cy="100" r="21" fill="#9AD6A8"/>
              <rect x="203" y="96" width="6" height="34" rx="2" fill="#5FA86E"/>
              <circle cx="206" cy="98" r="25" fill="#9AD6A8"/>
              <path d="M0 122 Q70 106 132 118 T240 118 L240 150 L0 150 Z" fill="#C7E6CE"/>
              <g transform="translate(120 80) scale(2.3)"><RSym color="#46B45A" sw={2.6}/></g>
            </svg>
          </div>
          <h3>Tu impacto importa</h3>
          <p>Cada acción cuenta para construir un futuro más limpio y sostenible.</p>
          <button className="btn-soft" onClick={()=>go('reciclar')}>Conoce más</button>
        </div>
      </div>
    </div>
  );
}

/* ---------- TRANSFERIR ---------- */
function Transferir({ balance, doTransfer }) {
  const [to, setTo] = useState('');
  const [amt, setAmt] = useState('');
  const [tx, setTx] = useState(null);
  const [err, setErr] = useState('');
  const fee = 0.05;
  const num = parseFloat(amt) || 0;
  const confirm = () => {
    setErr('');
    if (!to.trim()) return setErr('Ingresa un destinatario.');
    if (num <= 0) return setErr('Ingresa una cantidad válida.');
    if (num + fee > balance) return setErr('Saldo insuficiente para esta transferencia.');
    const result = doTransfer(to.trim(), num, fee);
    setTx(result);
  };
  return (
    <div className="screen">
      <Breadcrumb path={['Dashboard', 'Transferir']} />
      <div className="page-head with-action">
        <div><h1>Transferir GreenCoins</h1><p>Envía GreenCoins a otros usuarios de la plataforma.</p></div>
      </div>

      <div className="two-col">
        <div className="card">
          <div className="card-head"><h3>Formulario de Transferencia</h3></div>
          <Field label="Destinatario">
            <span className="input-ico"><span className="ii"><Icons.user size={18}/></span>
              <input value={to} onChange={e=>setTo(e.target.value)} placeholder="Ej. Profesor"/></span>
          </Field>
          <Field label="Cantidad (GC)">
            <span className="input-ico"><span className="ii"><Icons.coin size={18}/></span>
              <input type="number" min="0" step="0.5" value={amt} onChange={e=>setAmt(e.target.value)} placeholder="0"/></span>
          </Field>
          <div className="info-note">
            <Icons.info size={18}/>
            <span><strong>Tarifa de Red</strong>La tarifa de red se calcula automáticamente y se deducirá del monto enviado.</span>
          </div>
          {err && <div className="form-err">{err}</div>}
          <button className="btn-primary btn-lg full" onClick={confirm}>Confirmar Transferencia</button>
        </div>

        <div className="card status-card">
          <div className="card-head"><h3>Estado de la Transacción</h3></div>
          {!tx ? (
            <div className="status-idle">
              <span className="status-coin"><Icons.send size={30}/></span>
              <strong>En espera</strong>
              <p>Completa el formulario y confirma para ver el resumen de tu transferencia.</p>
            </div>
          ) : (
            <div className="status-done">
              <span className="status-check"><Icons.check size={40}/></span>
              <strong>Éxito</strong>
              <p>La transferencia se ha completado correctamente.</p>
              <dl className="kv">
                <div><dt>De</dt><dd>{tx.from}</dd></div>
                <div><dt>Para</dt><dd>{tx.to}</dd></div>
                <div><dt>Cantidad</dt><dd>{gc(tx.amount)} GC</dd></div>
                <div><dt>Tarifa de Red</dt><dd>{tx.fee} GC</dd></div>
                <div><dt>Fecha</dt><dd>{tx.date}</dd></div>
                <div><dt>Tx ID</dt><dd className="mono">{tx.txid}</dd></div>
              </dl>
              <div style={{ marginTop: '16px', padding: '12px', borderRadius: '8px', backgroundColor: '#fff3cd', border: '1px solid #ffeeba', color: '#856404', fontSize: '13px', lineHeight: '1.4' }}>
                <strong style={{ display: 'block', marginBottom: '4px', color: '#b58105' }}>⚠️ [STDD ESTADO ROJO]</strong>
                La transferencia se ha simulado localmente para la interfaz, pero la función <code>transferencia()</code> en <code>transactions.py</code> es un stub académico. Implementa la lógica en la rama <code>feature/transferencia</code> para descontar el impuesto estatal del 2% y validar la firma criptográfica en la base de datos.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ---------- RECICLAR ---------- */
function RSym({ color = '#ffffff', sw = 3 }) {
  return (
    <g fill={color} stroke={color} strokeWidth={sw} strokeLinejoin="round" strokeLinecap="round">
      {[0,120,240].map(a => (
        <g key={a} transform={'rotate('+a+')'}>
          <path d="M3 -12 A 12 12 0 0 1 11 2.5" fill="none"/>
          <path d="M11 2.5 l 5.5 -1.5 l -3 8 l -5.5 -3 z"/>
        </g>
      ))}
    </g>
  );
}

function Reciclar({ doRecycle }) {
  const [busy, setBusy] = useState(false);
  const [last, setLast] = useState(null);
  const process = () => {
    if (busy) return;
    setBusy(true);
    setTimeout(() => { setLast(doRecycle()); setBusy(false); }, 1400);
  };
  return (
    <div className="screen">
      <Breadcrumb path={['Dashboard', 'Reciclar']} />
      <div className="page-head"><h1>Sistema de Reciclaje</h1><p>Conecta con la máquina de reciclaje para depositar materiales y obtener recompensas.</p></div>

      <div className="recycle-panel">
        <div className="recycle-col">
          <h3 className="rc-title">Estado de la Conexión</h3>
          <ul className="conn-list">
            <li><span className="dot live"/>Conectado a la máquina</li>
            <li><em>ID de Máquina:</em> <b>GH-RC-001</b></li>
            <li><em>Ubicación:</em> <b>Campus Universidad</b></li>
            <li><em>Señal:</em> <b className="g">Excelente</b> <Icons.signal size={15}/></li>
          </ul>
          {last && (
            <div className="reward-note">
              <span className="rn-ico"><Icons.checkCircle size={22}/></span>
              <div className="rn-text"><strong>Última Recompensa</strong>
                <span>Material: {last.material} · <b className="pos">{fmt(last.reward)}</b></span>
                <em>{last.date}</em></div>
            </div>
          )}
        </div>

        <div className="recycle-col machine-col">
          <div className={'machine ' + (busy ? 'working' : '')} aria-hidden="true">
            <svg viewBox="0 0 240 220" width="186">
              <ellipse cx="116" cy="206" rx="84" ry="8" fill="#E6F1E9"/>
              <path d="M170 56 L188 42 L188 182 L170 196 Z" fill="#3E9A50"/>
              <path d="M52 56 L70 42 L188 42 L170 56 Z" fill="#4AA45C"/>
              <rect x="52" y="56" width="118" height="140" rx="7" fill="#56B266"/>
              <rect x="52" y="56" width="118" height="140" rx="7" fill="none" stroke="#3E9A50" strokeWidth="3"/>
              <rect x="52" y="56" width="118" height="15" rx="6" fill="#48A65A"/>
              <g transform="translate(156,49) scale(0.34)"><RSym color="#EAF6ED" sw={4}/></g>
              <rect x="62" y="82" width="46" height="96" rx="6" fill="#368A49"/>
              <rect x="114" y="82" width="46" height="96" rx="6" fill="#368A49"/>
              <g transform="translate(137,124) scale(1.18)"><RSym color="#EAF6ED" sw={3}/></g>
              <g className="bottle" transform="translate(72,118)">
                <rect x="0" y="8" width="14" height="40" rx="6" fill="#BFE3C8"/>
                <rect x="4" y="0" width="6" height="10" rx="2" fill="#BFE3C8"/>
                <rect x="3" y="-5" width="8" height="6" rx="2" fill="#9AD6A8"/>
              </g>
              <g className="bottle b2" transform="translate(90,126)">
                <rect x="0" y="6" width="13" height="34" rx="6" fill="#A6D9B4"/>
                <rect x="4" y="-2" width="5" height="9" rx="2" fill="#A6D9B4"/>
                <rect x="2" y="-6" width="8" height="6" rx="2" fill="#86C699"/>
              </g>
              <rect x="62" y="196" width="14" height="14" rx="3" fill="#3E9A50"/>
              <rect x="146" y="196" width="14" height="14" rx="3" fill="#3E9A50"/>
            </svg>
          </div>
        </div>

        <div className="recycle-col">
          <h3 className="rc-title">Instrucciones</h3>
          <ol className="instr-list">
            <li><span className="instr-n">1</span><span className="instr-t">Deposita plásticos limpios y secos.</span></li>
            <li><span className="instr-n">2</span><span className="instr-t">La máquina detectará el material.</span></li>
            <li><span className="instr-n">3</span><span className="instr-t">Espera a que se procese.</span></li>
            <li><span className="instr-n">4</span><span className="instr-t">Reclama tu recompensa.</span></li>
          </ol>
        </div>
      </div>

      {last && (
        <div style={{ marginTop: '20px', marginBottom: '20px', padding: '16px', borderRadius: '12px', backgroundColor: '#fff3cd', border: '1px solid #ffeeba', color: '#856404', fontSize: '13.5px', display: 'flex', gap: '12px', alignItems: 'center', lineHeight: '1.4' }}>
          <Icons.info size={24} style={{ flexShrink: 0, color: '#b58105' }}/>
          <div>
            <strong style={{ display: 'block', marginBottom: '4px', color: '#b58105' }}>⚠️ [STDD ESTADO ROJO - COMPROBACIÓN ACADÉMICA]</strong>
            El saldo local de GreenCoins ha aumentado para simular la interfaz, pero la función <code>registrar_recompensa_reciclaje()</code> en el backend es un stub académico. Implementa la lógica en la rama <code>feature/rewards</code> en <code>rewards.py</code> para leer los datos reales de pesaje del sensor físico de forma segura.
          </div>
        </div>
      )}

      <div className="recycle-actions">
        <button className="btn-primary btn-lg" onClick={process} disabled={busy}>
          {busy ? 'Procesando material…' : 'Procesar y Reclamar Recompensa'}
        </button>
        <button className="btn-ghost btn-lg">Finalizar Operación</button>
      </div>
    </div>
  );
}

function Breadcrumb({ path }) {
  return (
    <nav className="crumb">
      {path.map((p, i) => (
        <span key={p}>{i>0 && <Icons.chevRight size={14}/>}<a className={i===path.length-1?'cur':''}>{p}</a></span>
      ))}
    </nav>
  );
}

Object.assign(window.GH, { Login, Dashboard, Transferir, Reciclar, Breadcrumb, ProductThumb, Field });
