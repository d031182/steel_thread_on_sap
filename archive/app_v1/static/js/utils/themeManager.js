/**
 * Theme Manager
 * Handles theme switching between Custom and SAPUI5 + Fiori themes
 * Stores user preference in localStorage
 */

export class ThemeManager {
    constructor() {
        this.STORAGE_KEY = 'p2p_theme_preference';
        this.THEMES = {
            CUSTOM: 'custom',
            FIORI: 'fiori'
        };
        this.currentTheme = this.loadTheme();
        this.applyTheme(this.currentTheme);
    }

    /**
     * Load saved theme from localStorage or use default
     * @returns {string} Theme name
     */
    loadTheme() {
        const saved = localStorage.getItem(this.STORAGE_KEY);
        return saved || this.THEMES.CUSTOM;
    }

    /**
     * Save theme preference to localStorage
     * @param {string} theme - Theme name
     */
    saveTheme(theme) {
        localStorage.setItem(this.STORAGE_KEY, theme);
    }

    /**
     * Apply theme to document body
     * @param {string} theme - Theme name
     */
    applyTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        this.saveTheme(theme);
        this.updateThemeButton();
    }

    /**
     * Toggle between themes
     * Switches visual styling between Custom and Fiori Horizon themes
     */
    toggleTheme() {
        const newTheme = this.currentTheme === this.THEMES.CUSTOM 
            ? this.THEMES.FIORI 
            : this.THEMES.CUSTOM;
        
        this.applyTheme(newTheme);
        
        // Show toast notification
        const themeName = newTheme === this.THEMES.FIORI 
            ? 'SAP Fiori Horizon' 
            : 'Custom Theme';
        
        if (window.showToast) {
            window.showToast('🎨', `Switched to ${themeName}`);
        }
    }

    /**
     * Update theme switcher button text and icon
     */
    updateThemeButton() {
        const button = document.getElementById('themeSwitcherButton');
        if (!button) return;

        const icon = button.querySelector('.themeIcon');
        const label = button.querySelector('.themeLabel');

        if (this.currentTheme === this.THEMES.FIORI) {
            if (icon) icon.textContent = '🎨';
            if (label) label.textContent = 'Fiori';
            button.title = 'Switch to Custom Theme';
        } else {
            if (icon) icon.textContent = '🎨';
            if (label) label.textContent = 'Custom';
            button.title = 'Switch to SAP Fiori Theme';
        }
    }

    /**
     * Get current theme
     * @returns {string} Current theme name
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Check if current theme is Fiori
     * @returns {boolean}
     */
    isFioriTheme() {
        return this.currentTheme === this.THEMES.FIORI;
    }

    /**
     * Get theme display name
     * @param {string} theme - Theme name
     * @returns {string} Display name
     */
    getThemeDisplayName(theme) {
        return theme === this.THEMES.FIORI 
            ? 'SAP Fiori Horizon' 
            : 'Custom Theme';
    }
}

// Create singleton instance
export const themeManager = new ThemeManager();
