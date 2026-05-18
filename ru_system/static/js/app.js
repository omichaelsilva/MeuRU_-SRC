/**
 * app.js — Funções utilitárias do sistema RU
 */

// ─── Toasts ───────────────────────────────────────────────────────────────

function showToast(mensagem, tipo = 'info', duracao = 3500) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const cores = { sucesso: 'bg-green-600', erro: 'bg-red-600', aviso: 'bg-yellow-500', info: 'bg-blue-600' };
    const icones = { sucesso: '[OK]', erro: '[X]', aviso: '[!]', info: '[i]' };

    const toast = document.createElement('div');
    toast.className = `toast ${cores[tipo] || 'bg-gray-700'} text-white px-5 py-3 rounded-xl shadow-lg flex items-center gap-3 max-w-sm text-sm`;
    toast.innerHTML = `<span>${icones[tipo] || '[i]'}</span><span>${mensagem}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('saindo');
        setTimeout(() => toast.remove(), 300);
    }, duracao);
}


// ─── Loading em botões ────────────────────────────────────────────────────

/**
 * Mostra estado de loading no botão SEM desabilitá-lo antes do submit.
 * btn.disabled = true SÍNCRONO cancela o submit em alguns browsers.
 */
function setLoading(btn) {
    const textoEl = btn.querySelector('.btn-text');
    const loadingEl = btn.querySelector('.btn-loading');
    if (textoEl) textoEl.classList.add('hidden');
    if (loadingEl) loadingEl.classList.remove('hidden');

    // Desabilita APÓS o browser processar o submit (assíncrono)
    setTimeout(() => { btn.disabled = true; }, 100);
}


// ─── Toggle visibilidade de senha ─────────────────────────────────────────

function toggleSenha(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';

    const eyeOpen   = document.getElementById('eye-open-'   + inputId);
    const eyeClosed = document.getElementById('eye-closed-' + inputId);
    if (eyeOpen)   eyeOpen.classList.toggle('hidden', isPassword);
    if (eyeClosed) eyeClosed.classList.toggle('hidden', !isPassword);
}


// ─── Modais ───────────────────────────────────────────────────────────────

function abrirModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('hidden');
        // Foca no primeiro input do modal
        setTimeout(() => {
            const input = modal.querySelector('input:not([type=hidden])');
            if (input) input.focus();
        }, 100);
    }
}

function fecharModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add('hidden');
}

// Fecha modal ao clicar fora dele
document.addEventListener('click', function(e) {
    document.querySelectorAll('[id^="modal-"]').forEach(modal => {
        if (e.target === modal) modal.classList.add('hidden');
    });
});

// Fecha modal com Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.querySelectorAll('[id^="modal-"]').forEach(m => m.classList.add('hidden'));
    }
});


// ─── Menu mobile (admin) ──────────────────────────────────────────────────

function toggleMenuMobile() {
    const menu = document.getElementById('menu-mobile');
    if (menu) menu.classList.toggle('hidden');
}


// ─── Dark Mode ────────────────────────────────────────────────────────────

function toggleDarkMode() {
    const html = document.documentElement;
    const isDark = html.classList.toggle('dark');
    localStorage.setItem('ru-theme', isDark ? 'dark' : 'light');
    document.querySelectorAll('.dm-icon').forEach(el => {
        el.innerHTML = isDark ? _iconSun() : _iconMoon();
    });
}

function _iconMoon() {
    return `<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1111.21 3a7 7 0 109.79 9.79z"/>
    </svg>`;
}

function _iconSun() {
    return `<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z"/>
    </svg>`;
}

// Sincroniza ícone ao carregar
document.addEventListener('DOMContentLoaded', function() {
    const isDark = document.documentElement.classList.contains('dark');
    document.querySelectorAll('.dm-icon').forEach(el => {
        el.innerHTML = isDark ? _iconSun() : _iconMoon();
    });
});


// ─── Busca com debounce ───────────────────────────────────────────────────

let debounceTimer;
const campoBusca = document.getElementById('campo-busca');
if (campoBusca) {
    campoBusca.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            // Submete o formulário pai após 300ms sem digitar
            const form = this.closest('form');
            if (form) form.submit();
        }, 500);
    });
}


// ─── Validação de formato de valor monetário ──────────────────────────────

document.querySelectorAll('input[name="valor"]').forEach(input => {
    input.addEventListener('input', function() {
        // Remove caracteres não numéricos exceto vírgula e ponto
        let val = this.value.replace(/[^0-9,\.]/g, '');
        this.value = val;
    });
});


// ─── Auto-remove mensagens de sucesso ─────────────────────────────────────

document.addEventListener('DOMContentLoaded', function() {
    // Remove mensagens de sucesso após 4 segundos
    document.querySelectorAll('[id^="msg-sucesso"]').forEach(el => {
        setTimeout(() => {
            el.style.transition = 'opacity 0.5s';
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 500);
        }, 4000);
    });
});
