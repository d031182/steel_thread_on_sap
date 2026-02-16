/**
 * Markdown Formatter for AI Assistant Responses
 * Uses marked.js - Industry standard markdown parser
 * Non-module version that works with SAPUI5
 */

(function() {
    'use strict';
    
    window.MarkdownFormatter = {
        _initialized: false,
        
        /**
         * Initialize marked.js with secure configuration
         */
        _initializeMarked: function() {
            if (typeof marked === 'undefined') {
                console.error('marked.js library not loaded');
                return false;
            }

            // Configure marked.js for security and proper rendering
            marked.setOptions({
                gfm: true,
                breaks: true,
                pedantic: false,
                sanitize: false
            });

            return true;
        },
        
        /**
         * Sanitize HTML to prevent XSS attacks
         */
        _sanitizeHtml: function(html) {
            if (!html) return '';

            const temp = document.createElement('div');
            temp.innerHTML = html;

            // Remove script tags
            const scripts = temp.querySelectorAll('script');
            scripts.forEach(script => script.remove());

            // Remove event handler attributes
            const allElements = temp.querySelectorAll('*');
            allElements.forEach(element => {
                Array.from(element.attributes).forEach(attr => {
                    if (attr.name.startsWith('on')) {
                        element.removeAttribute(attr.name);
                    }
                });

                if (element.hasAttribute('href')) {
                    const href = element.getAttribute('href');
                    if (href && href.toLowerCase().startsWith('javascript:')) {
                        element.setAttribute('href', '#');
                    }
                }
                if (element.hasAttribute('src')) {
                    const src = element.getAttribute('src');
                    if (src && src.toLowerCase().startsWith('javascript:')) {
                        element.removeAttribute('src');
                    }
                }
            });

            return temp.innerHTML;
        },
        
        /**
         * Format markdown text to HTML
         */
        format: function(text) {
            if (!text) return '';

            if (!this._initialized) {
                this._initialized = this._initializeMarked();
                if (!this._initialized) {
                    console.warn('Falling back to plain text rendering');
                    return this._escapeHtml(text);
                }
            }

            try {
                const html = marked.parse(text);
                const sanitized = this._sanitizeHtml(html);
                return sanitized;
            } catch (error) {
                console.error('Error parsing markdown:', error);
                return this._escapeHtml(text);
            }
        },
        
        /**
         * Escape HTML for fallback
         */
        _escapeHtml: function(text) {
            const escapeMap = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            };
            return text.replace(/[&<>"']/g, char => escapeMap[char]);
        }
    };
    
    console.log('[MarkdownFormatter] Loaded and available on window object');
})();