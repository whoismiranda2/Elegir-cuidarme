// ── Google Analytics: helper de eventos ──────────────────────
function registrarEvento(nombre, categoria) {
  if (typeof gtag === 'function') {
    gtag('event', nombre, { categoria: categoria });
  }
}

// ── Menú responsive ──────────────────────────────────────────
function toggleMenu() {
  document.getElementById('navLinks').classList.toggle('open');
}

// ── Modo oscuro ───────────────────────────────────────────────
function initDarkMode() {
  const saved = localStorage.getItem('ec_tema');
  applyDark(saved === 'dark');
}

function toggleDarkMode() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  applyDark(!isDark);
}

function applyDark(on) {
  document.documentElement.setAttribute('data-theme', on ? 'dark' : 'light');
  localStorage.setItem('ec_tema', on ? 'dark' : 'light');
  const btn = document.getElementById('darkToggle');
  if (btn) {
    btn.innerHTML = on ? '<i data-lucide="sun"></i>' : '<i data-lucide="moon"></i>';
    btn.setAttribute('aria-label', on ? 'Modo claro' : 'Modo oscuro');
    lucide.createIcons();
  }
}

// ── Perfiles multiusuario ─────────────────────────────────────
const AVATARES = ['🌻','🦋','🌙','⭐','🎵','🌊','🔥','💫'];

function getPerfiles() {
  try { return JSON.parse(localStorage.getItem('ec_perfiles')) || []; }
  catch { return []; }
}

function getSesion() {
  try { return JSON.parse(localStorage.getItem('ec_sesion')); }
  catch { return null; }
}

function initPerfil() {
  const sesion = getSesion();
  if (sesion) { mostrarNavPerfil(sesion); return; }
  const perfiles = getPerfiles();
  abrirModalAuth(perfiles.length > 0 ? 'login' : 'crear');
}

function abrirModalAuth(tabInicial) {
  document.getElementById('profileModal')?.classList.remove('hidden');
  renderAvataresCrear();
  const perfiles = getPerfiles();
  // Solo muestra las tabs si ya hay al menos un perfil guardado
  document.getElementById('modalTabs').style.display = perfiles.length > 0 ? 'flex' : 'none';
  switchTab(tabInicial);
}

function switchTab(tab) {
  document.getElementById('panelCrear').style.display = tab === 'crear' ? '' : 'none';
  document.getElementById('panelLogin').style.display = tab === 'login' ? '' : 'none';
  document.getElementById('tabCrear').classList.toggle('active', tab === 'crear');
  document.getElementById('tabLogin').classList.toggle('active', tab === 'login');
  document.getElementById('createError')?.classList.add('hidden');
  document.getElementById('loginError')?.classList.add('hidden');
  if (tab === 'login') renderPerfilesList();
}

// ── Crear nueva cuenta ────────────────────────────────────────
function renderAvataresCrear() {
  const grid = document.getElementById('avatarGridCrear');
  if (!grid) return;
  grid.innerHTML = AVATARES.map((a, i) =>
    `<button class="avatar-opt${i === 0 ? ' selected' : ''}" data-avatar="${a}"
             onclick="seleccionarAvatarEn(this,'avatarGridCrear')" type="button">${a}</button>`
  ).join('');
}

function seleccionarAvatarEn(btn, gridId) {
  document.querySelectorAll(`#${gridId} .avatar-opt`).forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
}

function crearCuenta() {
  const nombre  = document.getElementById('createName')?.value.trim();
  const pass    = document.getElementById('createPass')?.value;
  const errEl   = document.getElementById('createError');

  if (!nombre) { document.getElementById('createName').focus(); return; }
  if (!pass || pass.length < 4) {
    mostrarErrorModal(errEl, 'La contraseña debe tener al menos 4 caracteres.');
    return;
  }
  const perfiles = getPerfiles();
  if (perfiles.find(p => p.nombre.toLowerCase() === nombre.toLowerCase())) {
    mostrarErrorModal(errEl, 'Ese nombre ya existe. Elige otro.');
    return;
  }
  const avatar = document.querySelector('#avatarGridCrear .avatar-opt.selected')?.dataset.avatar || '🌻';
  perfiles.push({ nombre, avatar, pass });
  localStorage.setItem('ec_perfiles', JSON.stringify(perfiles));
  iniciarSesionCon({ nombre, avatar });
}

// ── Iniciar sesión ────────────────────────────────────────────
function renderPerfilesList() {
  const list = document.getElementById('profileList');
  if (!list) return;
  const perfiles = getPerfiles();
  window._loginIndex = 0;
  list.innerHTML = perfiles.map((p, i) =>
    `<button class="profile-item${i === 0 ? ' selected' : ''}" data-index="${i}"
             onclick="seleccionarPerfilLogin(this)" type="button">
       <span class="profile-item-avatar">${p.avatar}</span>
       <span>${p.nombre}</span>
     </button>`
  ).join('');
}

function seleccionarPerfilLogin(btn) {
  document.querySelectorAll('.profile-item').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  window._loginIndex = parseInt(btn.dataset.index);
  document.getElementById('loginError')?.classList.add('hidden');
}

function iniciarSesion() {
  const perfiles = getPerfiles();
  const perfil   = perfiles[window._loginIndex ?? 0];
  const pass     = document.getElementById('loginPass')?.value;
  const errEl    = document.getElementById('loginError');
  if (!perfil) return;
  if (perfil.pass !== pass) {
    mostrarErrorModal(errEl, 'Contraseña incorrecta.');
    document.getElementById('loginPass')?.select();
    return;
  }
  iniciarSesionCon({ nombre: perfil.nombre, avatar: perfil.avatar });
}

function iniciarSesionCon(sesion) {
  localStorage.setItem('ec_sesion', JSON.stringify(sesion));
  document.getElementById('profileModal')?.classList.add('hidden');
  mostrarNavPerfil(sesion);
}

function cerrarSesion() {
  localStorage.removeItem('ec_sesion');
  cerrarProfileMenu();
  location.reload();
}

function mostrarErrorModal(el, msg) {
  if (!el) return;
  el.textContent = msg;
  el.classList.remove('hidden');
}

// ── Navbar: mostrar perfil activo ─────────────────────────────
function mostrarNavPerfil(sesion) {
  const btn = document.getElementById('navProfile');
  if (!btn) return;
  btn.innerHTML = `${sesion.avatar} <span>Hola, ${sesion.nombre}</span> <i data-lucide="chevron-down"></i>`;
  btn.style.display = 'flex';
  lucide.createIcons();
  renderDropdownAvatares(sesion.avatar);
}

// ── Dropdown de perfil ────────────────────────────────────────
function toggleProfileMenu() {
  const menu = document.getElementById('profileMenu');
  if (!menu) return;
  const opening = menu.classList.contains('hidden');
  menu.classList.toggle('hidden');
  if (opening) {
    const sesion = getSesion();
    if (sesion) renderDropdownAvatares(sesion.avatar);
  }
}

function cerrarProfileMenu() {
  document.getElementById('profileMenu')?.classList.add('hidden');
}

function renderDropdownAvatares(currentAvatar) {
  const grid = document.getElementById('dropdownAvatarGrid');
  if (!grid) return;
  grid.innerHTML = AVATARES.map(a =>
    `<button class="avatar-opt${a === currentAvatar ? ' selected' : ''}" data-avatar="${a}"
             onclick="cambiarIcono('${a}')" type="button">${a}</button>`
  ).join('');
}

function cambiarIcono(avatar) {
  const sesion = getSesion();
  if (!sesion) return;
  // Actualiza también en la lista de perfiles guardados
  const perfiles = getPerfiles();
  const p = perfiles.find(p => p.nombre === sesion.nombre);
  if (p) { p.avatar = avatar; localStorage.setItem('ec_perfiles', JSON.stringify(perfiles)); }
  sesion.avatar = avatar;
  localStorage.setItem('ec_sesion', JSON.stringify(sesion));
  mostrarNavPerfil(sesion);
}

// ── Mascota Flora ─────────────────────────────────────────────
function initMascota() {
  const el = document.getElementById('mascotMsg');
  if (!el) return;
  const container = el.closest('[data-frases]');
  if (!container) return;
  try {
    const frases = JSON.parse(container.dataset.frases);
    if (frases.length) el.textContent = frases[Math.floor(Math.random() * frases.length)];
  } catch { /* sin frases no pasa nada */ }
}

// ── Selector de emociones ─────────────────────────────────────
function seleccionarEmocion(emocion, btn) {
  document.querySelectorAll('.emocion-btn').forEach(b => b.classList.remove('seleccionado'));
  btn.classList.add('seleccionado');
  window.emocionSeleccionada = emocion;
}

// ── Guardar emoción del día ───────────────────────────────────
async function guardarEmocion() {
  const emocion = window.emocionSeleccionada;
  if (!emocion) { mostrarFeedback('Primero elige cómo te sientes hoy 😊', 'advertencia'); return; }
  registrarEvento('emocion_guardada', emocion);
  const texto = document.getElementById('emocionTexto')?.value || '';
  try {
    const resp = await fetch('/api/emocion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ emocion, texto }),
    });
    const data = await resp.json();
    mostrarFeedback(data.mensaje, 'ok');
    if (document.getElementById('emocionTexto')) document.getElementById('emocionTexto').value = '';
  } catch {
    mostrarFeedback('Hubo un problema. Intenta de nuevo.', 'error');
  }
}

function mostrarFeedback(mensaje, tipo) {
  const banner = document.getElementById('feedbackBanner');
  if (!banner) return;
  banner.textContent = mensaje;
  banner.classList.add('visible');
  banner.style.background = tipo === 'advertencia' ? 'var(--amarillo-lite)' : 'var(--verde-lite)';
  banner.style.borderColor = tipo === 'advertencia' ? 'var(--amarillo)' : 'var(--verde)';
  banner.style.color       = tipo === 'advertencia' ? '#6B4500' : '#2D6A4F';
  clearTimeout(window.feedbackTimeout);
  window.feedbackTimeout = setTimeout(() => banner.classList.remove('visible'), 5000);
}

// ── Toggle mito/realidad ──────────────────────────────────────
function toggleMito(index) {
  registrarEvento('mito_revelado', 'mito_' + index);
  document.getElementById('realidad-' + index)?.classList.toggle('visible');
}

// ── Filtro de videos ──────────────────────────────────────────
function filtrarVideos(categoria) {
  document.querySelectorAll('.video-card').forEach(c => {
    c.style.display = (categoria === 'todos' || c.dataset.categoria === categoria) ? '' : 'none';
  });
  document.querySelectorAll('.filtro-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.categoria === categoria));
}

// ── Filtro de técnicas ────────────────────────────────────────
function filtrarTecnicas(emocion) {
  document.querySelectorAll('.tecnica-card').forEach(c => {
    const para = c.dataset.para ? c.dataset.para.split(',') : [];
    c.style.display = (emocion === 'todos' || para.includes(emocion)) ? '' : 'none';
  });
  document.querySelectorAll('.filtro-emocion-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.emocion === emocion));
}

// ── Init ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initDarkMode();
  initPerfil();
  initMascota();

  // Cierra el dropdown al hacer clic fuera
  document.addEventListener('click', e => {
    const wrap = document.getElementById('navProfileWrap');
    if (wrap && !wrap.contains(e.target)) cerrarProfileMenu();
  });

  // Enter en campo contraseña de login
  document.getElementById('loginPass')?.addEventListener('keydown', e => {
    if (e.key === 'Enter') iniciarSesion();
  });
  document.getElementById('createPass')?.addEventListener('keydown', e => {
    if (e.key === 'Enter') crearCuenta();
  });
});
