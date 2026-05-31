/* GreenHash — Logo + Icon set (stroke icons, 24px grid, currentColor) */

const Emblem = ({ size = 32, uid = 'em' }) => (
  <svg width={size} height={size} viewBox="0 0 240 240" fill="none" aria-label="GreenHash">
    <defs>
      <linearGradient id={uid+'-a'} x1="40" y1="40" x2="200" y2="200" gradientUnits="userSpaceOnUse">
        <stop offset="0" stopColor="#4ED04A"/><stop offset="1" stopColor="#1E9E78"/>
      </linearGradient>
      <linearGradient id={uid+'-l'} x1="60" y1="56" x2="180" y2="200" gradientUnits="userSpaceOnUse">
        <stop offset="0" stopColor="#7BDA45"/><stop offset="1" stopColor="#2E9E3C"/>
      </linearGradient>
      <clipPath id={uid+'-c'}><path d="M190 60 C150 56 92 78 64 132 C56 148 68 182 104 196 C152 186 194 126 190 60 Z"/></clipPath>
    </defs>
    {[0,120,240].map(a => (
      <g key={a} transform={'rotate('+a+' 120 120)'}>
        <path d="M120 48 A 72 72 0 0 1 182 84" fill="none" stroke={'url(#'+uid+'-a)'} strokeWidth="13" strokeLinecap="round"/>
        <path d="M120 48 l -18 -9 l 2 24 Z" fill={'url(#'+uid+'-a)'}/>
      </g>
    ))}
    <g transform="translate(120 123) scale(0.53) translate(-127 -128)">
      <path d="M190 60 C150 56 92 78 64 132 C56 148 68 182 104 196 C152 186 194 126 190 60 Z" fill={'url(#'+uid+'-l)'}/>
      <path d="M104 190 C138 170 174 122 188 64 C182 120 150 168 110 184 Z" fill="#ffffff" opacity="0.94"/>
      <g clipPath={'url(#'+uid+'-c)'}>
        <g transform="rotate(-34 120 120)" stroke="#235C16" strokeWidth="10" strokeLinecap="round" opacity="0.9">
          <line x1="104" y1="94" x2="95" y2="148"/><line x1="132" y1="94" x2="123" y2="148"/>
          <line x1="87" y1="111" x2="143" y2="111"/><line x1="83" y1="131" x2="139" y2="131"/>
        </g>
      </g>
    </g>
  </svg>
);

const Logo = ({ size = 32, uid = 'logo' }) => (
  <span className="gh-logo" style={{ display: 'inline-flex', alignItems: 'center', gap: 11 }}>
    <Emblem size={size} uid={uid}/>
    <span className="gh-word"><span className="gh-w1">Green</span><span className="gh-w2">Hash</span></span>
  </span>
);

const Brandmark = ({ size = 32, uid = 'mark' }) => <Emblem size={size} uid={uid}/>;

const ic = (paths) => ({ size = 20, stroke = 1.8, className = '' } = {}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
       strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" className={className}>
    {paths}
  </svg>
);

const Icons = {
  dashboard: ic(<><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></>),
  transfer: ic(<><path d="M3 12l4-4M3 12l4 4M3 12h12"/><path d="M21 6l-4 4M21 6l-4-4M21 6H9"/></>),
  send: ic(<><path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4 20-7Z"/></>),
  recycle: ic(<><path d="M7 19H4.8a2 2 0 0 1-1.7-3l1.5-2.6"/><path d="m14 16-3 3 3 3"/><path d="M8.3 7.3 6.8 9.9"/><path d="m5.2 12-2-3.5a2 2 0 0 1 .7-2.7L7 4"/><path d="m9 7 3-5 3 5"/><path d="m12.5 5.5 1.5 2.6"/><path d="M17 16h2.2a2 2 0 0 0 1.7-3l-1.3-2.3"/><path d="m21 12-3 5h-6"/></>),
  bag: ic(<><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></>),
  search: ic(<><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></>),
  history: ic(<><path d="M3 12a9 9 0 1 0 9-9 9 9 0 0 0-6.4 2.6L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/></>),
  settings: ic(<><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/></>),
  help: ic(<><circle cx="12" cy="12" r="9"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></>),
  user: ic(<><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/></>),
  chevDown: ic(<path d="m6 9 6 6 6-6"/>),
  chevRight: ic(<path d="m9 6 6 6-6 6"/>),
  chevLeft: ic(<path d="m15 6-6 6 6 6"/>),
  logout: ic(<><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/></>),
  menu: ic(<><path d="M3 6h18M3 12h18M3 18h18"/></>),
  coin: ic(<><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></>),
  leaf: ic(<><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6"/></>),
  check: ic(<path d="M20 6 9 17l-5-5"/>),
  checkCircle: ic(<><circle cx="12" cy="12" r="9"/><path d="m9 12 2 2 4-4"/></>),
  info: ic(<><circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/></>),
  calendar: ic(<><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></>),
  signal: ic(<><path d="M2 20h.01M7 20v-4M12 20v-8M17 20V8M22 4v16"/></>),
  bell: ic(<><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></>),
  google: ({ size = 18 } = {}) => (
    <svg width={size} height={size} viewBox="0 0 24 24"><path fill="#4285F4" d="M22.5 12.2c0-.7-.1-1.4-.2-2H12v3.9h5.9a5 5 0 0 1-2.2 3.3v2.7h3.6c2.1-2 3.2-4.9 3.2-7.9Z"/><path fill="#34A853" d="M12 23c2.9 0 5.4-1 7.2-2.6l-3.6-2.7c-1 .7-2.3 1.1-3.6 1.1-2.8 0-5.1-1.9-6-4.4H2.3v2.8A11 11 0 0 0 12 23Z"/><path fill="#FBBC05" d="M6 14.3a6.6 6.6 0 0 1 0-4.2V7.3H2.3a11 11 0 0 0 0 9.8L6 14.3Z"/><path fill="#EA4335" d="M12 5.5c1.6 0 3 .5 4.1 1.6l3.1-3.1A11 11 0 0 0 2.3 7.3L6 10.1c.9-2.6 3.2-4.6 6-4.6Z"/></svg>
  ),
  microsoft: ({ size = 18 } = {}) => (
    <svg width={size} height={size} viewBox="0 0 24 24"><path fill="#F25022" d="M3 3h8.5v8.5H3z"/><path fill="#7FBA00" d="M12.5 3H21v8.5h-8.5z"/><path fill="#00A4EF" d="M3 12.5h8.5V21H3z"/><path fill="#FFB900" d="M12.5 12.5H21V21h-8.5z"/></svg>
  ),
  linkedin: ic(<><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 0 1 4 0v4"/></>),
  instagram: ic(<><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17 7h.01"/></>),
  twitter: ic(<path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2Z"/>),
  package: ic(<><path d="M16.5 9.4 7.5 4.2"/><path d="M21 16V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5M12 22V12"/></>),
  sun: ic(<><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></>),
  arrowRight: ic(<><path d="M5 12h14M13 6l6 6-6 6"/></>),
};

window.GH = window.GH || {};
Object.assign(window.GH, { Logo, Brandmark, Emblem, Icons });
