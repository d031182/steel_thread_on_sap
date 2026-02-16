/**
 * Markdown Formatter for AI Assistant Responses
 * Uses marked.js - Industry standard markdown parser
 * 
 * @module MarkdownFormatter
 */

export class MarkdownFormatter {
    /**
     * Initialize marked.js with secure configuration
     * @private
     */
    static _initializeMarked() {
        if (typeof marked === 'undefined') {
            console.error('marked.js library not loaded');
            return false;
        }

        // Configure marked.js for security and proper rendering
        marked.setOptions({
            // Sanitize HTML to prevent XSS attacks
            sanitize: false, // We'll use DOMPurify for sanitization
            
            // Enable GitHub Flavored Markdown
            gfm: true,
            
            // Support line breaks like GitHub
            breaks: true,
            
            // Use <br> for single line breaks
            pedantic: false,
            
            // Highlight code blocks (can be extended with syntax highlighter)
            highlight: null,
            
            // Add target="_blank" to links
            renderer: this._createCustomRenderer()
        });

        return true;
    }

    /**
     * Create custom renderer for marked.js
     * @private
     */
    static _createCustomRenderer() {
        const renderer = new marked.Renderer();

        // Override link rendering to add target="_blank" and security attributes
        renderer.link = function(href, title, text) {
            const titleAttr = title ? ` title="${title}"` : '';
            return `<a href="${href}"${titleAttr} target="_blank" rel="noopener noreferrer">${text}</a>`;
        };

        // Add custom classes to elements for styling
        renderer.code = function(code, language) {
            const lang = language || 'plaintext';
            return `<pre class="markdown-code-block"><code class="language-${lang}">${code}</code></pre>`;
        };

        renderer.codespan = function(text) {
            return `<code class="markdown-inline-code">${text}</code>`;
        };

        renderer.list = function(body, ordered, start) {
            const type = ordered ? 'ol' : 'ul';
            const startAttr = (ordered && start !== 1) ? ` start="${start}"` : '';
            return `<${type} class="markdown-list"${startAttr}>${body}</${type}>`;
        };

        renderer.listitem = function(text) {
            return `<li class="markdown-list-item">${text}</li>`;
        };

        renderer.heading = function(text, level) {
            return `<h${level} class="markdown-header markdown-h${level}">${text}</h${level}>`;
        };

        renderer.paragraph = function(text) {
            return `<p class="markdown-paragraph">${text}</p>`;
        };

        renderer.strong = function(text) {
            return `<strong class="markdown-bold">${text}</strong>`;
        };

        renderer.em = function(text) {
            return `<em class="markdown-italic">${text}</em>`;
        };

        return renderer;
    }

    /**
     * Sanitize HTML to prevent XSS attacks
     * Basic sanitization - removes script tags and dangerous attributes
     * @param {string} html - HTML to sanitize
     * @returns {string} Sanitized HTML
     * @private
     */
    static _sanitizeHtml(html) {
        if (!html) return '';

        // Create a temporary div to parse HTML
        const temp = document.createElement('div');
        temp.innerHTML = html;

        // Remove script tags
        const scripts = temp.querySelectorAll('script');
        scripts.forEach(script => script.remove());

        // Remove event handler attributes
        const allElements = temp.querySelectorAll('*');
        allElements.forEach(element => {
            // Remove all on* attributes (onclick, onerror, etc.)
            Array.from(element.attributes).forEach(attr => {
                if (attr.name.startsWith('on')) {
                    element.removeAttribute(attr.name);
                }
            });

            // Remove javascript: in href and src
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
    }

    /**
     * Format markdown text to HTML using marked.js
     * @param {string} text - Raw markdown text
     * @returns {string} HTML formatted text
     */
    static format(text) {
        if (!text) return '';

        // Initialize marked.js if not already done
        if (!this._initialized) {
            this._initialized = this._initializeMarked();
            if (!this._initialized) {
                // Fallback to plain text if marked.js not available
                console.warn('Falling back to plain text rendering');
                return this._escapeHtml(text);
            }
        }

        try {
            // Parse markdown to HTML using marked.js
            const html = marked.parse(text);

            // Sanitize the HTML for security
            const sanitized = this._sanitizeHtml(html);

            return sanitized;
        } catch (error) {
            console.error('Error parsing markdown:', error);
            // Fallback to plain text on error
            return this._escapeHtml(text);
        }
    }

    /**
     * Escape HTML for fallback rendering
     * @private
     */
    static _escapeHtml(text) {
        const escapeMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return text.replace(/[&<>"']/g, char => escapeMap[char]);
    }

    /**
     * Format a complete message with sender styling
     * @param {Object} message - Message object with role and content
     * @returns {string} Formatted HTML
     */
    static formatMessage(message) {
        if (!message || !message.content) return '';

        const formattedContent = this.format(message.content);
        const role = message.role || 'assistant';
        
        return `<div class="message-content message-${role}">${formattedContent}</div>`;
    }
}

// Static initialization flag
MarkdownFormatter._initialized = false;

// Make available globally for non-module scripts
if (typeof window !== 'undefined') {
    window.MarkdownFormatter = MarkdownFormatter;
}

// Export as default for ES6 modules
export default MarkdownFormatter;
