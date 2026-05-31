/* GreenHash — App shell, sidebar, topbar, routing + shared state */
const A = window.GH;
const { Icons: IcA, Brandmark: Mark, NAV, NAV_ADMIN, PRODUCTS, MATERIALS, CATEGORIES, SEED_HISTORY, gc: gcA } = A;
const { useState, useEffect } = React;

function Sidebar({ route, go, role }) {
  const currentNav = role === 'admin' ? NAV_ADMIN : NAV.concat({ id: 'advanced_wallet', label: 'Billetera Avanzada', icon: 'coin' });
  return (
    <aside className="sidebar">
      <div className="side-brand"><A.Logo size={54} uid="side"/></div>
      <nav className="side-nav">
        {currentNav.map(n => {
          const I = IcA[n.icon];
          return (
            <button key={n.id} className={'nav-item ' + (route===n.id?'active':'')} onClick={()=>go(n.id)}>
              <I size={20}/><span>{n.label}</span>
            </button>
          );
        })}
      </nav>
      <div className="side-foot"><span className="sf-leaf"><IcA.leaf size={16}/></span>Juntos construimos un campus sostenible.</div>
    </aside>
  );
}

function Topbar({ user, balance, onToggle, onLogout, go }) {
  const [menu, setMenu] = useState(false);
  const nav = (r) => { setMenu(false); go(r); };
  return (
    <header className="topbar">
      <button className="icon-btn nav-toggle" onClick={onToggle} title="Mostrar/ocultar menú"><IcA.menu /></button>
      <div className="top-spacer" />
      <div className="balance-pill"><IcA.leaf size={16}/> Saldo: <strong>{gcA(balance)} GreenCoins</strong></div>
      <div className="user-menu" tabIndex={0} onBlur={()=>setMenu(false)}>
        <button className="user-btn" onClick={()=>setMenu(m=>!m)}>
          <span className="user-av"><IcA.user size={18}/></span>
          <span className="user-name">{user.name}</span>
          <IcA.chevDown size={15}/>
        </button>
        {menu && (
          <ul className="user-dropdown">
            <li className="ud-head">
              <span className="ud-av"><IcA.user size={20}/></span>
              <div><strong>{user.name}</strong><span>{user.email}</span></div>
            </li>
            <li onMouseDown={()=>nav('configuracion')}><IcA.user size={16}/> Mi cuenta</li>
            <li onMouseDown={()=>nav('configuracion')}><IcA.settings size={16}/> Configuración</li>
            <li onMouseDown={()=>nav('ayuda')}><IcA.help size={16}/> Ayuda</li>
            <li className="ud-sep" aria-hidden="true"></li>
            <li className="ud-danger" onMouseDown={onLogout}><IcA.logout size={16}/> Cerrar sesión</li>
          </ul>
        )}
      </div>
    </header>
  );
}

function randTxid() {
  const h = '0123456789ABCDEF';
  const r = (n) => Array.from({length:n}, function(){ return h[Math.floor(Math.random()*16)]; }).join('');
  return 'GHX' + r(1) + '...' + r(4) + 'C3D4';
}
function now() {
  const p = (n) => String(n).padStart(2,'0');
  return '12/05/2024 ' + p(10+Math.floor(Math.random()*3)) + ':' + p(Math.floor(Math.random()*60));
}

function App() {
  const [authed, setAuthed] = useState(false);
  const [userRole, setUserRole] = useState('user');
  const [currentUser, setCurrentUser] = useState({ name: 'Juan', email: 'juan@campus.edu' });
  const [route, setRoute] = useState('dashboard');
  const [navOpen, setNavOpen] = useState(typeof window !== 'undefined' ? window.innerWidth > 820 : true);
  const [balance, setBalance] = useState(3.0);
  const [history, setHistory] = useState(SEED_HISTORY);

  const go = (r) => { setRoute(r); if (window.innerWidth <= 820) setNavOpen(false); const s = document.querySelector('.main-scroll'); if (s) s.scrollTo(0,0); };
  const push = (entry) => setHistory(h => [Object.assign({ id: 'h'+Date.now() }, entry)].concat(h));

  const doTransfer = (to, amount, fee) => {
    setBalance(b => +(b - amount - fee).toFixed(2));
    push({ date: now(), type: 'Transferencia', desc: 'Enviado a ' + to, amount: -amount });
    return { from: currentUser.name, to: to, amount: amount, fee: fee, date: now(), txid: randTxid() };
  };
  const doRecycle = () => {
    const accepted = MATERIALS.filter(m => m.status === 'Aceptado');
    const m = accepted[Math.floor(Math.random()*accepted.length)];
    setBalance(b => +(b + m.reward).toFixed(2));
    const date = now();
    push({ date: date, type: 'Recompensa', desc: 'Reciclaje: ' + m.name, amount: +m.reward });
    return { material: m.name, reward: m.reward, date: date };
  };
  const doBuy = (p) => {
    setBalance(b => +(b - p.price).toFixed(2));
    push({ date: now(), type: 'Compra', desc: p.name, amount: -p.price });
  };

  if (!authed) return (
    <A.Login onLogin={(role) => {
      setAuthed(true);
      setUserRole(role);
      if (role === 'admin') {
        setCurrentUser({ name: 'Administrador', email: 'admin@greenhash.eco' });
        setRoute('admin_dashboard');
      } else {
        setCurrentUser({ name: 'Juan', email: 'juan@campus.edu' });
        setRoute('dashboard');
      }
    }} />
  );

  const screens = {
    // Reciclador screens
    dashboard: <A.Dashboard user={currentUser} balance={balance} history={history} go={go} />,
    transferir: <A.Transferir balance={balance} doTransfer={doTransfer} />,
    reciclar: <A.Reciclar doRecycle={doRecycle} />,
    catalogo: <A.Catalogo balance={balance} doBuy={doBuy} products={PRODUCTS} />,
    materiales: <A.Materiales materials={MATERIALS} categories={CATEGORIES} />,
    historial: <A.Historial history={history} balance={balance} />,
    advanced_wallet: <A.AdvancedWallet balance={balance} />,
    configuracion: <A.Configuracion user={currentUser} />,
    ayuda: <A.Ayuda />,

    // Admin screens
    admin_dashboard: <A.AdminDashboard go={go} />,
    admin_audit: <A.AuditLogsViewer />,
    admin_catalog: <A.CatalogManager />,
    admin_wallets: <A.WalletController />,
    admin_sensors: <A.SensorMonitors />,
  };

  return (
    <div className={'app' + (navOpen ? ' nav-open' : '')}>
      <Sidebar route={route} go={go} role={userRole} />
      {navOpen && <div className="scrim" onClick={()=>setNavOpen(false)} />}
      <div className="app-main">
        <Topbar user={currentUser} balance={balance} onToggle={()=>setNavOpen(o=>!o)} onLogout={()=>setAuthed(false)} go={go} />
        <main className="main-scroll">{screens[route]}</main>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
