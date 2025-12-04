/**
 * ArXiv Daily Papers - Reader-Optimized JavaScript
 * Handles theme switching, collapsible sections, and reading enhancements
 */

// ============================================
// Theme Management with E-ink Support
// ============================================

class ThemeManager {
    constructor() {
        // Available themes: light, dark, eink
        this.themes = ['light', 'dark', 'eink'];
        this.currentThemeIndex = 0;
        this.theme = this.getInitialTheme();
        this.init();
    }

    getInitialTheme() {
        // Check localStorage first
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme && this.themes.includes(savedTheme)) {
            this.currentThemeIndex = this.themes.indexOf(savedTheme);
            return savedTheme;
        }
        
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.currentThemeIndex = 1;
            return 'dark';
        }
        
        return 'light';
    }

    init() {
        // Set initial theme
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateThemeIcon();

        // Add event listener to theme toggle button
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.cycleTheme());
        }

        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    this.theme = e.matches ? 'dark' : 'light';
                    this.currentThemeIndex = this.themes.indexOf(this.theme);
                    document.documentElement.setAttribute('data-theme', this.theme);
                    this.updateThemeIcon();
                }
            });
        }
    }

    cycleTheme() {
        // Cycle through: light -> dark -> eink -> light
        this.currentThemeIndex = (this.currentThemeIndex + 1) % this.themes.length;
        this.theme = this.themes[this.currentThemeIndex];
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        this.updateThemeIcon();
        
        // Announce theme change for screen readers
        this.announceThemeChange();
    }

    setTheme(themeName) {
        if (this.themes.includes(themeName)) {
            this.theme = themeName;
            this.currentThemeIndex = this.themes.indexOf(themeName);
            document.documentElement.setAttribute('data-theme', this.theme);
            localStorage.setItem('theme', this.theme);
            this.updateThemeIcon();
        }
    }

    updateThemeIcon() {
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            switch (this.theme) {
                case 'light':
                    themeIcon.className = 'ri-sun-line';
                    break;
                case 'dark':
                    themeIcon.className = 'ri-moon-line';
                    break;
                case 'eink':
                    themeIcon.className = 'ri-contrast-2-line';
                    break;
            }
        }
        
        // Update button aria-label
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            const nextTheme = this.themes[(this.currentThemeIndex + 1) % this.themes.length];
            themeToggle.setAttribute('aria-label', `Current theme: ${this.theme}. Click to switch to ${nextTheme}`);
        }
    }

    announceThemeChange() {
        // Create or update live region for screen readers
        let liveRegion = document.getElementById('theme-announcement');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'theme-announcement';
            liveRegion.setAttribute('role', 'status');
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.style.cssText = 'position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden;';
            document.body.appendChild(liveRegion);
        }
        
        const themeNames = {
            light: 'Light mode',
            dark: 'Dark mode',
            eink: 'E-ink reading mode'
        };
        liveRegion.textContent = `Switched to ${themeNames[this.theme]}`;
    }
}

// ============================================
// Collapsible Sections Management
// ============================================

class CollapsibleManager {
    constructor() {
        this.init();
    }

    init() {
        // Initialize all collapsible sections as collapsed
        this.collapseAll();
    }

    collapseAll() {
        // Collapse all dates
        document.querySelectorAll('.date-content').forEach(content => {
            content.style.display = 'none';
        });

        // Collapse all categories
        document.querySelectorAll('.category-content').forEach(content => {
            content.style.display = 'none';
        });

        // Collapse all papers
        document.querySelectorAll('.paper-content').forEach(content => {
            content.style.display = 'none';
        });

        // Reset all toggle icons and ARIA states
        document.querySelectorAll('.toggle-icon').forEach(icon => {
            icon.textContent = '▶';
            icon.classList.remove('expanded');
        });

        document.querySelectorAll('[aria-expanded]').forEach(el => {
            el.setAttribute('aria-expanded', 'false');
        });
    }

    expandAll() {
        // Expand all dates
        document.querySelectorAll('.date-content').forEach(content => {
            content.style.display = 'block';
        });

        // Expand all categories
        document.querySelectorAll('.category-content').forEach(content => {
            content.style.display = 'block';
        });

        // Expand all papers
        document.querySelectorAll('.paper-content').forEach(content => {
            content.style.display = 'block';
        });

        // Update all toggle icons and ARIA states
        document.querySelectorAll('.toggle-icon').forEach(icon => {
            icon.textContent = '▼';
            icon.classList.add('expanded');
        });

        document.querySelectorAll('[aria-expanded]').forEach(el => {
            el.setAttribute('aria-expanded', 'true');
        });

        // Trigger math rendering for all content
        this.triggerMathRendering(document.body);
    }

    toggleElement(header, content) {
        const toggleIcon = header.querySelector('.toggle-icon');
        const isExpanded = content.style.display !== 'none';

        if (isExpanded) {
            // Collapse
            content.style.display = 'none';
            if (toggleIcon) {
                toggleIcon.textContent = '▶';
                toggleIcon.classList.remove('expanded');
            }
            header.setAttribute('aria-expanded', 'false');
        } else {
            // Expand
            content.style.display = 'block';
            if (toggleIcon) {
                toggleIcon.textContent = '▼';
                toggleIcon.classList.add('expanded');
            }
            header.setAttribute('aria-expanded', 'true');
            
            // Trigger math rendering for newly visible content
            this.triggerMathRendering(content);
        }
    }

    triggerMathRendering(element) {
        // KaTeX auto-render
        if (typeof renderMathInElement !== 'undefined') {
            try {
                renderMathInElement(element, {
                    delimiters: [
                        {left: '$$', right: '$$', display: true},
                        {left: '$', right: '$', display: false},
                        {left: '\\(', right: '\\)', display: false},
                        {left: '\\[', right: '\\]', display: true}
                    ],
                    throwOnError: false
                });
            } catch (e) {
                console.log('KaTeX render error:', e.message);
            }
        }
        
        // MathJax fallback
        if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
            MathJax.typesetPromise([element]).catch((err) => {
                console.log('MathJax typeset error:', err.message);
            });
        }
    }
}

// ============================================
// Global Toggle Functions
// ============================================

function toggleDate(dateHeader) {
    const dateContent = dateHeader.nextElementSibling;
    window.collapsibleManager.toggleElement(dateHeader, dateContent);
}

function toggleCategory(categoryHeader) {
    const categoryContent = categoryHeader.nextElementSibling;
    window.collapsibleManager.toggleElement(categoryHeader, categoryContent);
}

function togglePaper(paperHeader) {
    const paperContent = paperHeader.nextElementSibling;
    window.collapsibleManager.toggleElement(paperHeader, paperContent);
}

// ============================================
// Reading Progress Indicator
// ============================================

class ReadingProgress {
    constructor() {
        this.init();
    }

    init() {
        // Create progress bar element
        const progressBar = document.createElement('div');
        progressBar.id = 'reading-progress';
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: var(--color-accent);
            z-index: 9999;
            transition: width 100ms ease-out;
        `;
        document.body.appendChild(progressBar);

        // Update on scroll
        window.addEventListener('scroll', () => this.updateProgress(), { passive: true });
    }

    updateProgress() {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        
        const progressBar = document.getElementById('reading-progress');
        if (progressBar) {
            progressBar.style.width = `${Math.min(100, progress)}%`;
        }
    }
}

// ============================================
// Keyboard Shortcuts
// ============================================

class KeyboardManager {
    constructor() {
        this.allExpanded = false;
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    handleKeydown(e) {
        // Ignore if user is typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        // Escape: Collapse all sections
        if (e.key === 'Escape') {
            e.preventDefault();
            window.collapsibleManager.collapseAll();
            this.allExpanded = false;
        }

        // 'e' key: Expand/collapse all
        if (e.key === 'e' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            this.allExpanded = !this.allExpanded;
            if (this.allExpanded) {
                window.collapsibleManager.expandAll();
            } else {
                window.collapsibleManager.collapseAll();
            }
        }

        // 't' key: Cycle theme
        if (e.key === 't' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            window.themeManager.cycleTheme();
        }

        // '1', '2', '3' keys: Direct theme selection
        if (e.key === '1' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            window.themeManager.setTheme('light');
        }
        if (e.key === '2' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            window.themeManager.setTheme('dark');
        }
        if (e.key === '3' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            window.themeManager.setTheme('eink');
        }

        // '?' key: Show keyboard shortcuts
        if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            this.showShortcutsHelp();
        }
    }

    showShortcutsHelp() {
        // Check if help modal already exists
        let helpModal = document.getElementById('shortcuts-help');
        if (helpModal) {
            helpModal.remove();
            return;
        }

        helpModal = document.createElement('div');
        helpModal.id = 'shortcuts-help';
        helpModal.innerHTML = `
            <div style="
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            " onclick="this.parentElement.remove()">
                <div style="
                    background: var(--color-bg);
                    border: 1px solid var(--color-border);
                    border-radius: 8px;
                    padding: 24px;
                    max-width: 400px;
                    width: 90%;
                    color: var(--color-text);
                    font-family: var(--font-heading);
                " onclick="event.stopPropagation()">
                    <h3 style="margin: 0 0 16px 0; font-size: 1.25rem;">Keyboard Shortcuts</h3>
                    <dl style="margin: 0; font-size: 0.9rem; line-height: 1.8;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <dt><kbd style="background: var(--color-bg-muted); padding: 2px 8px; border-radius: 4px; font-family: monospace;">t</kbd></dt>
                            <dd style="margin: 0; color: var(--color-text-secondary);">Cycle theme</dd>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <dt><kbd style="background: var(--color-bg-muted); padding: 2px 8px; border-radius: 4px; font-family: monospace;">1</kbd> <kbd style="background: var(--color-bg-muted); padding: 2px 8px; border-radius: 4px; font-family: monospace;">2</kbd> <kbd style="background: var(--color-bg-muted); padding: 2px 8px; border-radius: 4px; font-family: monospace;">3</kbd></dt>
                            <dd style="margin: 0; color: var(--color-text-secondary);">Light / Dark / E-ink</dd>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <dt><kbd style="background: var(--color-bg-muted); padding: 2px 8px; border-radius: 4px; font-family: monospace;">e</kbd></dt>
                            <dd style="margin: 0; color: var(--color-text-secondary);">Expand/collapse all</dd>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <dt><kbd style="background: var(--color-bg-muted); padding: 2px 8px; border-radius: 4px; font-family: monospace;">Esc</kbd></dt>
                            <dd style="margin: 0; color: var(--color-text-secondary);">Collapse all</dd>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <dt><kbd style="background: var(--color-bg-muted); padding: 2px 8px; border-radius: 4px; font-family: monospace;">?</kbd></dt>
                            <dd style="margin: 0; color: var(--color-text-secondary);">Toggle this help</dd>
                        </div>
                    </dl>
                    <button onclick="this.closest('#shortcuts-help').remove()" style="
                        margin-top: 16px;
                        padding: 8px 16px;
                        background: var(--color-accent);
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 0.9rem;
                    ">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(helpModal);

        // Close on Escape
        const closeOnEscape = (e) => {
            if (e.key === 'Escape') {
                helpModal.remove();
                document.removeEventListener('keydown', closeOnEscape);
            }
        };
        document.addEventListener('keydown', closeOnEscape);
    }
}

// ============================================
// Accessibility Enhancements
// ============================================

class AccessibilityManager {
    constructor() {
        this.init();
    }

    init() {
        this.enhanceKeyboardNavigation();
        this.addAriaLabels();
        this.addSkipLink();
    }

    enhanceKeyboardNavigation() {
        // Make headers focusable and keyboard-accessible
        const headers = document.querySelectorAll('.date-header, .category-header, .paper-header');
        headers.forEach(header => {
            header.setAttribute('tabindex', '0');
            header.setAttribute('role', 'button');
            header.setAttribute('aria-expanded', 'false');
            
            header.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    header.click();
                }
            });
        });
    }

    addAriaLabels() {
        // Date headers
        document.querySelectorAll('.date-header').forEach(header => {
            const dateText = header.querySelector('span:last-child')?.textContent || 'Date';
            header.setAttribute('aria-label', `Toggle papers for ${dateText}`);
        });

        // Category headers
        document.querySelectorAll('.category-header').forEach(header => {
            const categoryName = header.querySelector('h2')?.textContent || 'Category';
            header.setAttribute('aria-label', `Toggle ${categoryName} papers`);
        });

        // Paper headers
        document.querySelectorAll('.paper-header').forEach(header => {
            const paperTitle = header.querySelector('.paper-title')?.textContent || 'Paper';
            header.setAttribute('aria-label', `Toggle details for: ${paperTitle}`);
        });
    }

    addSkipLink() {
        // Add skip to main content link
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link';
        skipLink.textContent = 'Skip to main content';
        document.body.insertBefore(skipLink, document.body.firstChild);

        // Add id to first date section
        const firstDateSection = document.querySelector('.date-section');
        if (firstDateSection) {
            firstDateSection.id = 'main-content';
        }
    }

    updateAriaExpanded(header, isExpanded) {
        header.setAttribute('aria-expanded', isExpanded.toString());
    }
}

// ============================================
// Mobile Optimizations
// ============================================

class MobileManager {
    constructor() {
        this.isMobile = window.innerWidth <= 768;
        this.isTablet = window.innerWidth > 768 && window.innerWidth <= 1024;
        this.init();
    }

    init() {
        this.handleViewportChanges();
        this.addTouchFeedback();
        
        // Listen for resize and orientation changes
        window.addEventListener('resize', () => this.handleViewportChanges());
        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.handleViewportChanges(), 100);
        });
    }

    handleViewportChanges() {
        const newIsMobile = window.innerWidth <= 768;
        const newIsTablet = window.innerWidth > 768 && window.innerWidth <= 1024;
        
        if (newIsMobile !== this.isMobile || newIsTablet !== this.isTablet) {
            this.isMobile = newIsMobile;
            this.isTablet = newIsTablet;
            this.updateLayoutClasses();
        }
    }

    updateLayoutClasses() {
        document.body.classList.toggle('mobile-layout', this.isMobile);
        document.body.classList.toggle('tablet-layout', this.isTablet);
    }

    addTouchFeedback() {
        // Add subtle touch feedback for interactive elements
        const clickables = document.querySelectorAll('.category-header, .paper-header, .date-header, .theme-switch');
        
        clickables.forEach(element => {
            element.addEventListener('touchstart', () => {
                element.style.opacity = '0.8';
            }, { passive: true });
            
            element.addEventListener('touchend', () => {
                setTimeout(() => {
                    element.style.opacity = '';
                }, 100);
            }, { passive: true });
            
            element.addEventListener('touchcancel', () => {
                element.style.opacity = '';
            }, { passive: true });
        });
    }
}

// ============================================
// Search Functionality (for future use)
// ============================================

class SearchManager {
    constructor() {
        this.papers = [];
        this.init();
    }

    init() {
        this.cachePapers();
    }

    cachePapers() {
        const paperElements = document.querySelectorAll('.paper');
        this.papers = Array.from(paperElements).map(paper => ({
            element: paper,
            title: (paper.querySelector('.paper-title')?.textContent || '').toLowerCase(),
            authors: (paper.querySelector('.authors')?.textContent || '').toLowerCase(),
            abstract: (paper.querySelector('.abstract p')?.textContent || '').toLowerCase()
        }));
    }

    search(query) {
        const searchTerm = query.toLowerCase().trim();
        
        if (!searchTerm) {
            this.papers.forEach(paper => {
                paper.element.style.display = '';
            });
            return;
        }

        this.papers.forEach(paper => {
            const matches = paper.title.includes(searchTerm) ||
                           paper.authors.includes(searchTerm) ||
                           paper.abstract.includes(searchTerm);
            
            paper.element.style.display = matches ? '' : 'none';
        });
    }
}

// ============================================
// Utility Functions
// ============================================

const Utils = {
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Failed to copy to clipboard:', err);
            return false;
        }
    },

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// ============================================
// Initialize Application
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all managers
    window.themeManager = new ThemeManager();
    window.collapsibleManager = new CollapsibleManager();
    window.keyboardManager = new KeyboardManager();
    window.accessibilityManager = new AccessibilityManager();
    window.mobileManager = new MobileManager();
    window.searchManager = new SearchManager();
    window.readingProgress = new ReadingProgress();
    
    // Make Utils available globally
    window.Utils = Utils;

    // Add click handler for title to refresh page
    const titleElement = document.querySelector('.header-title');
    if (titleElement) {
        titleElement.style.cursor = 'pointer';
        titleElement.addEventListener('click', () => {
            window.location.reload();
        });
        titleElement.setAttribute('title', 'Click to refresh page');
    }

    console.log('ArXiv Daily Papers initialized. Press ? for keyboard shortcuts.');
});

// ============================================
// Export for Module Use
// ============================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ThemeManager,
        CollapsibleManager,
        SearchManager,
        Utils
    };
}
