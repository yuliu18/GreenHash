/* GreenHash — screens part 3: exclusive admin views */
const { useState: usA, useEffect: ueA } = React;
const GA = window.GH;
const { Icons: IcA, Breadcrumb: CrumbA, MOCK_WALLETS, MOCK_AUDIT_LOGS, MOCK_SENSORS, PRODUCTS } = GA;

/* ---------- ADMIN DASHBOARD ---------- */
function AdminDashboard({ go }) {
  const alerts = [
    { id: 1, type: 'critical', msg: 'Intento de inyección SQL bloqueado de IP 192.168.1.100.', time: 'Hace 5m' },
    { id: 2, type: 'warning', msg: 'Billetera w4 (Carlos Díaz) congelada por investigación de saldo.', time: 'Hace 23m' },
  ];

  return (
    <div className="screen">
      <div className="page-head">
        <h1>Panel de Control Administrativo</h1>
        <p>Monitorea la seguridad del sistema GreenHash, gestiona el inventario y audita transacciones.</p>
      </div>

      <div className="quick-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', marginBottom: '24px' }}>
        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '14px', color: '#666666', fontWeight: '500' }}>GC en Circulación</span>
            <IcA.coin size={22} style={{ color: '#2e7d32' }}/>
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', marginTop: '10px' }}>62.5 GC</div>
          <div style={{ fontSize: '12px', color: '#2e7d32', marginTop: '4px' }}>+4.2 GC esta semana</div>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '14px', color: '#666666', fontWeight: '500' }}>Material Reciclado</span>
            <IcA.recycle size={22} style={{ color: '#2e7d32' }}/>
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', marginTop: '10px' }}>420 kg</div>
          <div style={{ fontSize: '12px', color: '#2e7d32', marginTop: '4px' }}>8 Puntos de recogida activos</div>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '14px', color: '#666666', fontWeight: '500' }}>Alertas de Seguridad</span>
            <IcA.bell size={22} style={{ color: '#d32f2f' }}/>
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', marginTop: '10px', color: '#d32f2f' }}>2 Activas</div>
          <div style={{ fontSize: '12px', color: '#d32f2f', marginTop: '4px' }}>Protección WAF activa</div>
        </div>
      </div>

      <div className="two-col">
        <div className="card">
          <div className="card-head"><h3>Incidentes Recientes de Seguridad</h3></div>
          <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', padding: '0', margin: '0', listStyle: 'none' }}>
            {alerts.map(a => (
              <li key={a.id} style={{ display: 'flex', gap: '12px', padding: '12px', borderRadius: '8px', backgroundColor: a.type==='critical'?'#fdecea':'#fff4e5', border: a.type==='critical'?'1px solid #facdca':'1px solid #ffe3c3' }}>
                <IcA.info size={18} style={{ color: a.type==='critical'?'#d32f2f':'#f57c00', flexShrink: 0, marginTop: '2px' }}/>
                <div style={{ flex: 1 }}>
                  <strong style={{ display: 'block', fontSize: '13px', color: a.type==='critical'?'#c62828':'#e65100' }}>{a.type==='critical'?'ALERTA CRÍTICA':'ADVERTENCIA'}</strong>
                  <span style={{ fontSize: '12.5px', color: '#333333' }}>{a.msg}</span>
                </div>
                <span style={{ fontSize: '11px', color: '#666666' }}>{a.time}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="card">
          <div className="card-head"><h3>Acceso Rápido del Administrador</h3></div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button className="btn-primary" onClick={()=>go('admin_audit')}>Ver Historial de Auditoría</button>
            <button className="btn-ghost" onClick={()=>go('admin_wallets')}>Gestionar Billeteras</button>
            <button className="btn-ghost" onClick={()=>go('admin_sensors')}>Inspeccionar Hardware IoT</button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------- AUDIT LOGS VIEWER ---------- */
function AuditLogsViewer() {
  const [logs, setLogs] = usA(MOCK_AUDIT_LOGS);
  const [search, setSearch] = usA('');
  
  const filtered = logs.filter(l => 
    l.action.toLowerCase().includes(search.toLowerCase()) || 
    l.details.toLowerCase().includes(search.toLowerCase()) ||
    l.user.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="screen">
      <CrumbA path={['Admin', 'Registro de Auditoría']} />
      <div className="page-head">
        <h1>Registro de Auditoría de Seguridad</h1>
        <p>Trazabilidad total e inmutable para cumplimiento normativo y análisis forense de transacciones.</p>
      </div>

      <div className="card">
        <div className="toolbar">
          <span className="input-ico grow">
            <span className="ii"><IcA.search size={18}/></span>
            <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Buscar registros por usuario, acción o detalles…"/>
          </span>
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Usuario</th>
              <th>Acción</th>
              <th>Detalles</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(l => {
              const bg = l.type==='error'?'#fdecea': l.type==='warn'?'#fff4e5': l.type==='success'?'#e8f5e9':'#e8f0fe';
              const fg = l.type==='error'?'#d32f2f': l.type==='warn'?'#f57c00': l.type==='success'?'#2e7d32':'#1976d2';
              return (
                <tr key={l.id}>
                  <td className="muted" style={{ whiteSpace: 'nowrap' }}>{l.timestamp}</td>
                  <td><b>{l.user}</b></td>
                  <td>
                    <span className="pill" style={{ backgroundColor: bg, color: fg, border: 'none', fontWeight: '600', fontSize: '11px', textTransform: 'uppercase' }}>
                      {l.action}
                    </span>
                  </td>
                  <td style={{ fontSize: '12.5px' }}>{l.details}</td>
                </tr>
              );
            })}
            {filtered.length === 0 && <tr><td colSpan="4" className="empty">No se encontraron registros de auditoría.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ---------- CATALOG MANAGER ---------- */
function CatalogManager() {
  const [prods, setProds] = usA(PRODUCTS);
  const [modal, setModal] = usA(false);
  
  // New reward state
  const [name, setName] = usA('');
  const [desc, setDesc] = usA('');
  const [price, setPrice] = usA('');

  const handleAdd = (e) => {
    e.preventDefault();
    if (!name || !price) return;
    const p = {
      id: 'p' + (prods.length + 1),
      name: name,
      desc: desc || 'Residuos sostenibles reciclados.',
      price: parseFloat(price),
      tint: '#3F8F4A',
      img: '../static/products/silla.png'
    };
    const updated = [...prods, p];
    setProds(updated);
    PRODUCTS.push(p); // update global reference
    setModal(false);
    setName('');
    setDesc('');
    setPrice('');
  };

  return (
    <div className="screen">
      <CrumbA path={['Admin', 'Gestión de Recompensas']} />
      <div className="page-head with-action">
        <div>
          <h1>Gestión del Catálogo de Recompensas</h1>
          <p>Administra los productos ecológicos disponibles para los recicladores.</p>
        </div>
        <button className="btn-primary" onClick={()=>setModal(true)}>Añadir Nuevo Producto</button>
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>Descripción</th>
              <th className="ta-r">Precio en GC</th>
            </tr>
          </thead>
          <tbody>
            {prods.map(p => (
              <tr key={p.id}>
                <td><b>{p.name}</b></td>
                <td className="muted">{p.desc}</td>
                <td className="ta-r"><b>{p.price.toFixed(1)} GC</b></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="modal-overlay" onClick={()=>setModal(false)}>
          <form className="modal" onClick={e=>e.stopPropagation()} onSubmit={handleAdd}>
            <button className="modal-x" type="button" onClick={()=>setModal(false)}>✕</button>
            <div className="modal-body">
              <h3>Añadir Nuevo Producto</h3>
              
              <label className="field" style={{ width: '100%', marginTop: '12px' }}>
                <span className="field-label">Nombre del Producto</span>
                <input value={name} onChange={e=>setName(e.target.value)} placeholder="Ej. Libreta de papel reciclado" required/>
              </label>

              <label className="field" style={{ width: '100%', marginTop: '12px' }}>
                <span className="field-label">Descripción</span>
                <textarea value={desc} onChange={e=>setDesc(e.target.value)} placeholder="Ej. Cubiertas rígidas de corcho y hojas de papel reciclado." style={{ width: '100%', height: '80px', padding: '10px', border: '1px solid #ccc', borderRadius: '6px' }}/>
              </label>

              <label className="field" style={{ width: '100%', marginTop: '12px', marginBottom: '16px' }}>
                <span className="field-label">Precio (GC)</span>
                <input type="number" step="0.1" value={price} onChange={e=>setPrice(e.target.value)} placeholder="Ej. 1.5" required/>
              </label>

              <div style={{ padding: '10px', borderRadius: '6px', backgroundColor: '#eaf6ed', border: '1px solid #c8e6c9', color: '#2e7d32', fontSize: '12px', lineHeight: '1.4', marginBottom: '16px' }}>
                <strong style={{ display: 'block', marginBottom: '2px' }}>🔒 Transacción de BD Segura</strong>
                Esta operación ejecuta una inserción parametrizada en el catálogo simulando la función <code>modificar_catalogo_recompensas()</code> en <code>rewards.py</code> de forma segura.
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button type="button" className="btn-ghost" onClick={()=>setModal(false)}>Cancelar</button>
                <button type="submit" className="btn-primary">Guardar Producto</button>
              </div>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

/* ---------- WALLET CONTROLLER ---------- */
function WalletController() {
  const [wallets, setWallets] = usA(MOCK_WALLETS);

  const toggleFreeze = (id) => {
    setWallets(ws => ws.map(w => {
      if (w.id === id) {
        const next = w.status === 'Activa' ? 'Congelada' : 'Activa';
        // Add a mock log to audit logs
        MOCK_AUDIT_LOGS.unshift({
          id: 'l' + (MOCK_AUDIT_LOGS.length + 1),
          timestamp: '30/05/2026 22:42:01',
          user: 'admin@greenhash.eco',
          action: next === 'Congelada' ? 'WALLET_FROZEN' : 'WALLET_UNFROZEN',
          details: `Billetera de ${w.name} (${w.email}) fue ${next==='Congelada'?'congelada':'descongelada'} por el Administrador.`,
          type: 'warn'
        });
        return { ...w, status: next };
      }
      return w;
    }));
  };

  return (
    <div className="screen">
      <CrumbA path={['Admin', 'Control de Billeteras']} />
      <div className="page-head">
        <h1>Auditoría y Control de Billeteras</h1>
        <p>Congela carteras ante sospechas de fraude, doble gasto o fallos en sensores físicos (DSM 3/4).</p>
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Correo</th>
              <th>Clave Pública (RSA)</th>
              <th className="ta-r">Saldo actual</th>
              <th className="ta-c">Estado</th>
              <th className="ta-r">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {wallets.map(w => (
              <tr key={w.id}>
                <td><b>{w.name}</b></td>
                <td className="muted">{w.email}</td>
                <td className="mono" style={{ fontSize: '11px', color: '#666666' }}>{w.pubKey}</td>
                <td className="ta-r"><b>{w.balance.toFixed(1)} GC</b></td>
                <td className="ta-c">
                  <span className={'pill ' + (w.status==='Activa'?'ok':'bad')}>
                    {w.status}
                  </span>
                </td>
                <td className="ta-r">
                  <button className={w.status==='Activa'?'btn-ghost sm danger':'btn-primary sm'} onClick={()=>toggleFreeze(w.id)}>
                    {w.status === 'Activa' ? 'Congelar Cartera' : 'Descongelar'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ---------- SENSOR MONITORS ---------- */
function SensorMonitors() {
  const [calibrating, setCalibrating] = usA(false);
  const [sensors, setSensors] = usA(MOCK_SENSORS);

  const triggerCalibration = () => {
    setCalibrating(true);
    // Log active sensor calibration event
    MOCK_AUDIT_LOGS.unshift({
      id: 'l' + (MOCK_AUDIT_LOGS.length + 1),
      timestamp: '30/05/2026 22:43:10',
      user: 'admin@greenhash.eco',
      action: 'SENSOR_CALIBRATION',
      details: 'Calibración manual de balanza IoT completada con éxito. Lecturas estabilizadas.',
      type: 'info'
    });
    setTimeout(() => {
      setCalibrating(false);
    }, 1200);
  };

  return (
    <div className="screen">
      <CrumbA path={['Admin', 'Monitoreo de Sensores']} />
      <div className="page-head">
        <h1>Monitoreo de Sensores e Integridad Física</h1>
        <p>Administración de la seguridad lógica y física de las máquinas recolectoras de residuos (DSM 5/7).</p>
      </div>

      <div className="two-col">
        <div className="card">
          <div className="card-head"><h3>Balanza de Reciclaje (Pesa)</h3></div>
          <p className="muted">La balanza reporta lecturas de pesaje en tiempo real. Realiza calibraciones periódicas.</p>
          
          <dl className="kv" style={{ margin: '16px 0' }}>
            <div><dt>Estado de Sensores</dt><dd style={{ color: '#2e7d32', fontWeight: 'bold' }}>{sensors.weighSensor}</dd></div>
            <div><dt>Desviación registrada</dt><dd>0.00g (Estable)</dd></div>
          </dl>

          <button className="btn-primary full" onClick={triggerCalibration} disabled={calibrating}>
            {calibrating ? 'Calibrando sensores IoT…' : 'Calibrar Balanza a Cero'}
          </button>
        </div>

        <div className="card">
          <div className="card-head"><h3>Monitores del Entorno de Operación</h3></div>
          <dl className="kv">
            <div><dt>Temperatura Interna</dt><dd>{sensors.temperature}°C (Óptima)</dd></div>
            <div><dt>Lector de Tarjetas RFID</dt><dd style={{ color: '#2e7d32', fontWeight: 'bold' }}>{sensors.rfidReader}</dd></div>
            <div><dt>Bloqueo Lógico de Puertos USB</dt><dd style={{ color: '#2e7d32', fontWeight: 'bold' }}>{sensors.usbLock}</dd></div>
          </dl>

          <div style={{ marginTop: '16px', padding: '12px', borderRadius: '8px', backgroundColor: '#e8f5e9', border: '1px solid #c8e6c9', color: '#2e7d32', fontSize: '12.5px', lineHeight: '1.4' }}>
            <strong>🛡️ Protección Física Tamper-Evident</strong>
            Los periféricos lógicos externos y el almacenamiento de claves privadas NFC del recolector están protegidos mediante criptografía asimétrica y exclusión física USB (BadUSB guard).
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window.GH, { AdminDashboard, AuditLogsViewer, CatalogManager, WalletController, SensorMonitors });
