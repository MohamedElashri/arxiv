const mathOptions = {
    delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$", right: "$", display: false },
        { left: "\\(", right: "\\)", display: false },
        { left: "\\[", right: "\\]", display: true }
    ],
    throwOnError: false,
    macros: {
        "\\RR": "\\mathbb{R}",
        "\\CC": "\\mathbb{C}",
        "\\NN": "\\mathbb{N}",
        "\\ZZ": "\\mathbb{Z}",
        "\\QQ": "\\mathbb{Q}",
        "\\dd": "\\mathrm{d}",
        "\\ee": "\\mathrm{e}",
        "\\ii": "\\mathrm{i}",
        "\\ket": "\\left|#1\\right\\rangle",
        "\\bra": "\\left\\langle#1\\right|",
        "\\braket": "\\left\\langle#1\\right\\rangle",
        "\\norm": "\\left\\|#1\\right\\|",
        "\\abs": "\\left|#1\\right|",
        "\\tr": "\\operatorname{tr}",
        "\\Tr": "\\operatorname{Tr}",
        "\\rank": "\\operatorname{rank}",
        "\\span": "\\operatorname{span}",
        "\\dim": "\\operatorname{dim}",
        "\\det": "\\operatorname{det}",
        "\\sgn": "\\operatorname{sgn}",
        "\\diag": "\\operatorname{diag}",
        "\\Re": "\\operatorname{Re}",
        "\\Im": "\\operatorname{Im}",
        "\\Arg": "\\operatorname{Arg}",
        "\\Log": "\\operatorname{Log}",
        "\\lcm": "\\operatorname{lcm}",
        "\\gcd": "\\operatorname{gcd}",
        "\\ord": "\\operatorname{ord}",
        "\\deg": "\\operatorname{deg}",
        "\\ker": "\\operatorname{ker}",
        "\\hom": "\\operatorname{hom}",
        "\\end": "\\operatorname{end}",
        "\\aut": "\\operatorname{aut}",
        "\\inn": "\\operatorname{inn}",
        "\\out": "\\operatorname{out}",
        "\\Fix": "\\operatorname{Fix}",
        "\\Stab": "\\operatorname{Stab}",
        "\\Orb": "\\operatorname{Orb}",
        "\\supp": "\\operatorname{supp}",
        "\\cl": "\\operatorname{cl}",
        "\\interior": "\\operatorname{int}",
        "\\bd": "\\operatorname{bd}",
        "\\grad": "\\nabla",
        "\\curl": "\\nabla\\times",
        "\\divergence": "\\nabla\\cdot",
        "\\laplacian": "\\nabla^2",
        "\\dalembertian": "\\Box",
        "\\order": "\\mathcal{O}\\left(#1\\right)",
        "\\bigO": "\\mathcal{O}\\left(#1\\right)",
        "\\littleo": "o\\left(#1\\right)",
        "\\expect": "\\left\\langle#1\\right\\rangle",
        "\\expectation": "\\mathbb{E}\\left[#1\\right]",
        "\\var": "\\operatorname{Var}\\left[#1\\right]",
        "\\prob": "\\mathbb{P}\\left(#1\\right)",
        "\\given": "\\mid",
        "\\st": "\\mid",
        "\\defeq": "\\stackrel{\\text{def}}{=}",
        "\\eqdef": "\\stackrel{\\text{def}}{=}",
        "\\const": "\\text{const}",
        "\\half": "\\frac{1}{2}",
        "\\third": "\\frac{1}{3}",
        "\\quarter": "\\frac{1}{4}",
        "\\inv": "^{-1}",
        "\\trans": "^{\\top}",
        "\\adj": "^{\\dagger}",
        "\\conj": "^{*}",
        "\\dual": "^{\\vee}",
        "\\perp": "\\bot",
        "\\parallel": "\\|",
        "\\independent": "\\perp\\!\\!\\!\\perp",
        "\\iid": "\\stackrel{\\text{iid}}{\\sim}",
        "\\dist": "\\stackrel{\\text{d}}{=}",
        "\\convd": "\\stackrel{\\text{d}}{\\to}",
        "\\convp": "\\stackrel{\\text{p}}{\\to}",
        "\\convas": "\\stackrel{\\text{a.s.}}{\\to}",
        "\\weak": "\\rightharpoonup",
        "\\strong": "\\rightarrow",
        "\\floor": "\\left\\lfloor#1\\right\\rfloor",
        "\\ceil": "\\left\\lceil#1\\right\\rceil",
        "\\round": "\\left\\lfloor#1\\right\\rceil",
        "\\set": "\\left\\{#1\\right\\}",
        "\\card": "\\left|#1\\right|",
        "\\powerset": "\\mathcal{P}\\left(#1\\right)",
        "\\range": "\\operatorname{range}\\left(#1\\right)",
        "\\domain": "\\operatorname{domain}\\left(#1\\right)",
        "\\codomain": "\\operatorname{codomain}\\left(#1\\right)",
        "\\image": "\\operatorname{image}\\left(#1\\right)",
        "\\preimage": "\\operatorname{preimage}\\left(#1\\right)"
    }
};

const formula = /\$[^$\n]+\$|\\[([]/;
const typesetElements = new WeakSet();
let mathReady;

function loadMath() {
    const base = 'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/';
    function load(tag, url, integrity) {
        return new Promise((resolve, reject) => {
            const resource = document.createElement(tag);
            resource.crossOrigin = 'anonymous';
            resource.integrity = integrity;
            if (tag === 'link') {
                resource.rel = 'stylesheet';
                resource.href = base + url;
            } else {
                resource.src = base + url;
            }
            resource.addEventListener('load', resolve, { once: true });
            resource.addEventListener('error', reject, { once: true });
            document.head.append(resource);
        });
    }

    return Promise.all([
        load('link', 'katex.min.css', 'sha384-GvrOXuhMATgEsSwCs4smul74iXGOixntILdUW9XmUC6+HX0sLNAK3q71HotJqlAn'),
        load('script', 'katex.min.js', 'sha384-cpW21h6RZv/phavutF+AuVYrr+dA8xD9zs6FwLpaCct6O9ctzYFfFr4dgmgccOTx')
            .then(() => load('script', 'contrib/auto-render.min.js', 'sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05'))
    ]);
}

function renderMath(element) {
    if (!element || typesetElements.has(element) || !formula.test(element.textContent)) return;
    typesetElements.add(element);
    mathReady ??= loadMath();
    mathReady.then(() => window.renderMathInElement(element, mathOptions)).catch(() => {
        // The source notation remains visible if KaTeX cannot load.
    });
}

function renderTitles(category) {
    category.querySelectorAll('.paper-title').forEach(renderMath);
}

const root = document.documentElement;
const main = document.getElementById('main-content');
const themeButton = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');
const themeMeta = document.querySelector('meta[name="theme-color"]');
const shortcuts = document.getElementById('keyboard-shortcuts');
const progress = document.getElementById('reading-progress');
const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
const disclosures = Array.from(main.querySelectorAll('details'));

const themes = [
    { id: 'light', label: 'light', glyph: '◐', color: '#fbfbf8' },
    { id: 'dark', label: 'dark', glyph: '●', color: '#171716' },
    { id: 'eink', label: 'e-ink', glyph: '◯', color: '#ffffff' }
];

let savedTheme;
try {
    savedTheme = localStorage.getItem('theme');
} catch {
    // A browser can disable storage.
}

let themeIndex = 0;

function setTheme(index, save = false) {
    const theme = themes[index];
    const next = themes[(index + 1) % themes.length];
    themeIndex = index;
    root.dataset.theme = theme.id;
    themeMeta.content = theme.color;
    themeIcon.textContent = theme.glyph;
    themeButton.setAttribute('aria-label', `Current theme: ${theme.label}. Switch to ${next.label}.`);
    if (save) {
        savedTheme = theme.id;
        try {
            localStorage.setItem('theme', theme.id);
        } catch {
            // Theme changes still apply to this page.
        }
    }
}

function cycleTheme() {
    setTheme((themeIndex + 1) % themes.length, true);
}

function updateProgress() {
    const distance = root.scrollHeight - window.innerHeight;
    const fraction = distance > 0 ? Math.min(1, Math.max(0, window.scrollY / distance)) : 0;
    progress.style.transform = `scaleX(${fraction})`;
}

const storedIndex = themes.findIndex(theme => theme.id === savedTheme);
setTheme(storedIndex >= 0 ? storedIndex : Number(systemTheme.matches));
themeButton.hidden = false;
themeButton.addEventListener('click', cycleTheme);
systemTheme.addEventListener('change', event => {
    if (!themes.some(theme => theme.id === savedTheme)) setTheme(Number(event.matches));
});

main.querySelectorAll('.category[open]').forEach(renderTitles);
main.addEventListener('toggle', event => {
    const details = event.target;
    if (details.open && details.classList.contains('category')) renderTitles(details);
    if (details.open && details.classList.contains('paper')) renderMath(details.querySelector('.abstract p'));
    updateProgress();
}, true);
window.addEventListener('scroll', updateProgress, { passive: true });
window.addEventListener('resize', updateProgress);
updateProgress();

document.addEventListener('keydown', event => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey ||
        (event.target instanceof Element && event.target.closest('input, textarea, select, [contenteditable]'))) return;

    if (shortcuts.open) return;
    if (event.key === 't') cycleTheme();
    if (['1', '2', '3'].includes(event.key)) setTheme(Number(event.key) - 1, true);
    if (event.key === '?') shortcuts.showModal();
    if (event.key === 'Escape' || event.key === 'e') {
        const open = event.key === 'e' && disclosures.some(item => !item.open);
        disclosures.forEach(item => { item.open = open; });
    }
});

let closedForPrint;
window.addEventListener('beforeprint', () => {
    if (closedForPrint) return;
    closedForPrint = disclosures.filter(item => !item.open);
    closedForPrint.forEach(item => { item.open = true; });
});
window.addEventListener('afterprint', () => {
    closedForPrint?.forEach(item => { item.open = false; });
    closedForPrint = undefined;
});
