/* GreenHash — mock data */

const PRODUCTS = [
  { id: 'p1', name: 'Silla Algas', price: 2.5, desc: 'Hecho de plástico reciclado y residuos marinos.', tint: '#3F8F4A', img: '../static/products/silla.png' },
  { id: 'p2', name: 'Mochila Eco', price: 1.8, desc: 'Tela reciclada resistente y diseño sobrio.', tint: '#5C7A52', img: '../static/products/mochila.png' },
  { id: 'p3', name: 'Botella Verde', price: 1.2, desc: 'Botella reutilizable de aluminio reciclado.', tint: '#6FA36A', img: '../static/products/botella.png' },
  { id: 'p4', name: 'Maceta Bio', price: 1.5, desc: 'Bioplástico biodegradable para tus plantas.', tint: '#8AA77E', img: '../static/products/maceta.png' },
];

const MATERIALS = [
  { id: 'm1', name: 'Plástico PET', cat: 'Plástico', reward: 1.0, status: 'Aceptado' },
  { id: 'm2', name: 'Plástico HDPE', cat: 'Plástico', reward: 1.2, status: 'Aceptado' },
  { id: 'm3', name: 'Aluminio', cat: 'Metal', reward: 1.5, status: 'Aceptado' },
  { id: 'm4', name: 'Ropa Usada', cat: 'Textil', reward: 0.5, status: 'Aceptado' },
  { id: 'm5', name: 'Vidrio', cat: 'Vidrio', reward: 0.7, status: 'Aceptado' },
  { id: 'm6', name: 'Papel', cat: 'Papel', reward: 0.3, status: 'Aceptado' },
  { id: 'm7', name: 'Cartón', cat: 'Papel', reward: 0.4, status: 'Aceptado' },
  { id: 'm8', name: 'Latas de Acero', cat: 'Metal', reward: 1.3, status: 'Aceptado' },
  { id: 'm9', name: 'Tetra Pak', cat: 'Mixto', reward: 0.6, status: 'En revisión' },
  { id: 'm10', name: 'Poliestireno (EPS)', cat: 'Plástico', reward: 0.0, status: 'No aceptado' },
];

const CATEGORIES = ['Todas las categorías', 'Plástico', 'Metal', 'Textil', 'Vidrio', 'Papel', 'Mixto'];

/* seed history — newest first */
const SEED_HISTORY = [
  { id: 'h1', date: '12/05/2024 10:15', type: 'Transferencia', desc: 'Enviado a Profesor', amount: -3.0 },
  { id: 'h2', date: '12/05/2024 09:42', type: 'Recompensa', desc: 'Reciclaje: Plástico PET', amount: +1.0 },
  { id: 'h3', date: '11/05/2024 16:30', type: 'Compra', desc: 'Silla Algas', amount: -2.5 },
  { id: 'h4', date: '10/05/2024 09:10', type: 'Recompensa', desc: 'Reciclaje: Aluminio', amount: +1.5 },
  { id: 'h5', date: '10/05/2024 14:20', type: 'Transferencia', desc: 'Enviado a Ana', amount: -1.0 },
  { id: 'h6', date: '10/05/2024 08:50', type: 'Recompensa', desc: 'Reciclaje: Ropa Usada', amount: +0.5 },
  { id: 'h7', date: '09/05/2024 11:05', type: 'Recompensa', desc: 'Reciclaje: Vidrio', amount: +0.7 },
  { id: 'h8', date: '08/05/2024 17:40', type: 'Compra', desc: 'Botella Verde', amount: -1.2 },
];

const NAV = [
  { id: 'dashboard', label: 'Dashboard', icon: 'dashboard' },
  { id: 'transferir', label: 'Transferir', icon: 'send' },
  { id: 'reciclar', label: 'Reciclar', icon: 'recycle' },
  { id: 'catalogo', label: 'Catálogo', icon: 'bag' },
  { id: 'materiales', label: 'Consulta de Materiales', icon: 'search' },
  { id: 'historial', label: 'Historial de Actividad', icon: 'history' },
  { id: 'configuracion', label: 'Configuración', icon: 'settings' },
  { id: 'ayuda', label: 'Ayuda', icon: 'help' },
];

const NAV_ADMIN = [
  { id: 'admin_dashboard', label: 'Panel Control', icon: 'dashboard' },
  { id: 'admin_audit', label: 'Registro Auditoría', icon: 'history' },
  { id: 'admin_catalog', label: 'Gestión Catálogo', icon: 'bag' },
  { id: 'admin_wallets', label: 'Control Billeteras', icon: 'user' },
  { id: 'admin_sensors', label: 'Sensores y Puertos', icon: 'settings' },
];

const MOCK_WALLETS = [
  { id: 'w1', name: 'Juan Pérez', email: 'juan@campus.edu', balance: 3.0, status: 'Activa', pubKey: 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Yh...' },
  { id: 'w2', name: 'Ana Gómez', email: 'ana@campus.edu', balance: 14.5, status: 'Activa', pubKey: 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1Za...' },
  { id: 'w3', name: 'Profesor Martínez', email: 'profesor@campus.edu', balance: 45.0, status: 'Activa', pubKey: 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8Vf...' },
  { id: 'w4', name: 'Carlos Díaz', email: 'carlos@campus.edu', balance: 0.0, status: 'Congelada', pubKey: 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA9Xz...' },
];

const MOCK_AUDIT_LOGS = [
  { id: 'l1', timestamp: '30/05/2026 22:30:15', user: 'admin@greenhash.eco', action: 'LOGIN_SUCCESS', details: 'Inicio de sesión administrativo exitoso desde IP 192.168.1.45. Rol: Administrador.', type: 'info' },
  { id: 'l2', timestamp: '30/05/2026 22:28:40', user: 'Invitado', action: 'SECURITY_BLOCKED', details: 'Ataque SQL Injection detectado en campo correo: "admin\' OR \'1\'=\'1". Petición bloqueada por WAF.', type: 'error' },
  { id: 'l3', timestamp: '30/05/2026 22:25:12', user: 'juan@campus.edu', action: 'TX_SIGNED', details: 'Transacción de transferencia firmada con firma RSA SHA-256 válida. ID: GHX4F...C3D4.', type: 'success' },
  { id: 'l4', timestamp: '30/05/2026 22:20:05', user: 'Invitado', action: 'SECURITY_ALERT', details: 'Filtro XSS bloqueó código malicioso en campo comentario: "<script>alert(1)</script>". Entrada sanitizada.', type: 'warn' },
  { id: 'l5', timestamp: '30/05/2026 22:15:30', user: 'carlos@campus.edu', action: 'WALLET_FROZEN', details: 'Billetera temporalmente congelada por el Administrador debido a auditoría de doble gasto.', type: 'warn' },
  { id: 'l6', timestamp: '30/05/2026 22:08:14', user: 'Mantenimiento', action: 'SENSOR_CALIBRATION', details: 'Sensor de pesaje en Punto de Recogida GH-RC-001 calibrado a cero. Desviación: 0.02g.', type: 'info' },
];

const MOCK_SENSORS = {
  activePoints: 4,
  weighSensor: 'Calibrado',
  temperature: 24.5,
  usbLock: 'Bloqueado',
  rfidReader: 'Activo',
};

const fmt = (n) => (n > 0 ? '+' : '') + n.toFixed(n % 1 === 0 ? 0 : (Math.round(n*100)%10===0?1:2)) + ' GC';
const gc = (n) => n.toFixed(Math.abs(n % 1) < 1e-9 ? 0 : 2).replace(/\.?0+$/, m => m.includes('.') ? '' : m);

window.GH = window.GH || {};
Object.assign(window.GH, { PRODUCTS, MATERIALS, CATEGORIES, SEED_HISTORY, NAV, NAV_ADMIN, MOCK_WALLETS, MOCK_AUDIT_LOGS, MOCK_SENSORS, fmt, gc });
