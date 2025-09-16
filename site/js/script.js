/**
 * JavaScript for ArXiv Daily Papers site
 * Handles theme switching and collapsible sections
 */

// Theme management
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        // Set initial theme
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateThemeIcon();

        // Add event listener to theme toggle button
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.theme);
        localStorage.setItem('theme', this.theme);
        this.updateThemeIcon();
    }

    updateThemeIcon() {
        const themeIcon = document.getElementById("theme-icon");
        if (themeIcon) {
            themeIcon.className = this.theme === 'light' ? "ri-sun-line" : "ri-moon-line";
        }
    }
}

// Collapsible sections management
class CollapsibleManager {
    constructor() {
        this.init();
    }

    init() {
        // Initialize all collapsible sections as collapsed
        this.collapseAll();
    }

    collapseAll() {
        // Collapse all categories
        const categoryContents = document.querySelectorAll('.category-content');
        categoryContents.forEach(content => {
            content.style.display = 'none';
        });

        // Collapse all papers
        const paperContents = document.querySelectorAll('.paper-content');
        paperContents.forEach(content => {
            content.style.display = 'none';
        });

        // Reset all toggle icons
        const toggleIcons = document.querySelectorAll('.toggle-icon');
        toggleIcons.forEach(icon => {
            icon.textContent = '▶';
            icon.classList.remove('expanded');
        });
    }

    toggleElement(element, content) {
        const toggleIcon = element.querySelector('.toggle-icon');
        const isExpanded = content.style.display !== 'none';

        if (isExpanded) {
            // Collapse
            content.style.display = 'none';
            toggleIcon.textContent = '▶';
            toggleIcon.classList.remove('expanded');
        } else {
            // Expand
            content.style.display = 'block';
            toggleIcon.textContent = '▼';
            toggleIcon.classList.add('expanded');
            
            // Trigger MathJax re-rendering for newly visible content
            if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
                MathJax.typesetPromise([content]).catch((err) => {
                    console.log('MathJax typeset error:', err.message);
                });
            }
        }
    }
}

// Global functions for onclick handlers
function toggleCategory(categoryHeader) {
    const categoryContent = categoryHeader.nextElementSibling;
    window.collapsibleManager.toggleElement(categoryHeader, categoryContent);
}

function togglePaper(paperHeader) {
    const paperContent = paperHeader.nextElementSibling;
    window.collapsibleManager.toggleElement(paperHeader, paperContent);
}

// Utility functions
class Utils {
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    static copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            // Could add a toast notification here
            console.log('Copied to clipboard:', text);
        }).catch(err => {
            console.error('Failed to copy to clipboard:', err);
        });
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Search functionality (for future enhancement)
class SearchManager {
    constructor() {
        this.searchInput = null;
        this.papers = [];
        this.init();
    }

    init() {
        // This could be enhanced to add search functionality
        this.cachePapers();
    }

    cachePapers() {
        // Cache all papers for potential search functionality
        const paperElements = document.querySelectorAll('.paper');
        this.papers = Array.from(paperElements).map(paper => {
            const title = paper.querySelector('.paper-title')?.textContent || '';
            const authors = paper.querySelector('.authors')?.textContent || '';
            const abstract = paper.querySelector('.abstract p')?.textContent || '';
            
            return {
                element: paper,
                title: title.toLowerCase(),
                authors: authors.toLowerCase(),
                abstract: abstract.toLowerCase()
            };
        });
    }

    search(query) {
        const searchTerm = query.toLowerCase().trim();
        
        if (!searchTerm) {
            // Show all papers
            this.papers.forEach(paper => {
                paper.element.style.display = 'block';
            });
            return;
        }

        // Filter papers based on search term
        this.papers.forEach(paper => {
            const matches = paper.title.includes(searchTerm) ||
                           paper.authors.includes(searchTerm) ||
                           paper.abstract.includes(searchTerm);
            
            paper.element.style.display = matches ? 'block' : 'none';
        });
    }
}

// Keyboard shortcuts
class KeyboardManager {
    constructor() {
        this.expanded = false;
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => {
            // TAB key: Expand/Collapse all details
            if (e.key === 'Tab' && !e.ctrlKey && !e.metaKey && !e.altKey && !e.shiftKey) {
                e.preventDefault();
                this.expanded = !this.expanded;
                document.querySelectorAll("details").forEach(detail => {
                    detail.open = this.expanded;
                });
                return false;
            }

            // Ctrl/Cmd + D: Toggle theme
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                window.themeManager.toggleTheme();
            }

            // Escape: Collapse all sections
            if (e.key === 'Escape') {
                window.collapsibleManager.collapseAll();
            }
        });
    }
}

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.init();
    }

    init() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
        });
    }
}

// Accessibility enhancements
class AccessibilityManager {
    constructor() {
        this.init();
    }

    init() {
        // Add ARIA labels and keyboard navigation
        this.enhanceKeyboardNavigation();
        this.addAriaLabels();
    }

    enhanceKeyboardNavigation() {
        // Make category and paper headers focusable
        const headers = document.querySelectorAll('.category-header, .paper-header');
        headers.forEach(header => {
            header.setAttribute('tabindex', '0');
            header.setAttribute('role', 'button');
            
            header.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    header.click();
                }
            });
        });
    }

    addAriaLabels() {
        // Add ARIA labels for better screen reader support
        const categoryHeaders = document.querySelectorAll('.category-header');
        categoryHeaders.forEach(header => {
            const categoryName = header.querySelector('h2')?.textContent || 'Category';
            header.setAttribute('aria-label', `Toggle ${categoryName} section`);
        });

        const paperHeaders = document.querySelectorAll('.paper-header');
        paperHeaders.forEach(header => {
            const paperTitle = header.querySelector('.paper-title')?.textContent || 'Paper';
            header.setAttribute('aria-label', `Toggle details for: ${paperTitle}`);
        });

        // Add aria-expanded attributes
        const allHeaders = document.querySelectorAll('.category-header, .paper-header');
        allHeaders.forEach(header => {
            header.setAttribute('aria-expanded', 'false');
        });
    }

    updateAriaExpanded(header, isExpanded) {
        header.setAttribute('aria-expanded', isExpanded.toString());
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all managers
    window.themeManager = new ThemeManager();
    window.collapsibleManager = new CollapsibleManager();
    window.searchManager = new SearchManager();
    window.keyboardManager = new KeyboardManager();
    window.performanceMonitor = new PerformanceMonitor();
    window.accessibilityManager = new AccessibilityManager();

    // Enhanced theme switching with checkbox support
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    if (toggleSwitch) {
        function switchTheme(e) {
            if (e.target.checked) {
                document.documentElement.setAttribute('data-theme', 'light');
                const themeIcon = document.getElementById("theme-icon");
                if (themeIcon) themeIcon.className = "ri-sun-line";
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                const themeIcon = document.getElementById("theme-icon");
                if (themeIcon) themeIcon.className = "ri-moon-line";
                localStorage.setItem('theme', 'dark');
            }
        }

        toggleSwitch.addEventListener('change', switchTheme, false);
        
        // Set initial state based on current theme
        const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : 'dark';
        if (currentTheme) {
            document.documentElement.setAttribute('data-theme', currentTheme);
            if (currentTheme === 'light') {
                toggleSwitch.checked = true;
            }
        }
    }

    // Build timestamp functionality (if element exists)
    const timestamp = document.getElementById("build-timestamp");
    if (timestamp) {
        const timestamp_local = new Date(timestamp.getAttribute("datetime")).toLocaleString();
        const badge = document.getElementById("build-timestamp-badge");
        if (badge) {
            badge.src = `https://img.shields.io/github/actions/workflow/status/NotCraft/ArxivDaily/update-feed.yml?label=${timestamp_local}&style=for-the-badge`;
        }
    }

    // Add refresh functionality to title
    const titleElement = document.querySelector('header h1');
    if (titleElement) {
        titleElement.addEventListener('click', () => {
            window.location.reload();
        });
        titleElement.setAttribute('title', 'Click to refresh page');
    }

    // Override the toggle functions to include accessibility updates
    const originalToggleCategory = window.toggleCategory;
    window.toggleCategory = function(categoryHeader) {
        const categoryContent = categoryHeader.nextElementSibling;
        const wasExpanded = categoryContent.style.display !== 'none';
        
        originalToggleCategory(categoryHeader);
        
        // Update ARIA attribute
        window.accessibilityManager.updateAriaExpanded(categoryHeader, !wasExpanded);
    };

    const originalTogglePaper = window.togglePaper;
    window.togglePaper = function(paperHeader) {
        const paperContent = paperHeader.nextElementSibling;
        const wasExpanded = paperContent.style.display !== 'none';
        
        originalTogglePaper(paperHeader);
        
        // Update ARIA attribute
        window.accessibilityManager.updateAriaExpanded(paperHeader, !wasExpanded);
    };

    console.log('ArXiv Daily Papers site with Nord theme initialized successfully!');
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ThemeManager,
        CollapsibleManager,
        SearchManager,
        Utils
    };
}
