/**
 * AI Assistant Overlay - MINIMAL TEST VERSION
 * Step 1: Just show dialog with static text
 */
(function() {
    'use strict';

    class AIAssistantOverlay {
        constructor(adapter) {
            this.adapter = adapter;
            this.dialog = null;
            console.log('[AIAssistantOverlay] STEP 1: Minimal version initialized');
        }

        open() {
            console.log('[AIAssistantOverlay] STEP 1: Opening dialog');
            
            if (!this.dialog) {
                this._createDialog();
            }
            
            this.dialog.open();
        }

        close() {
            if (this.dialog) {
                this.dialog.close();
            }
        }

        _createDialog() {
            console.log('[AIAssistantOverlay] STEP 1: Creating minimal dialog');
            
            this.dialog = new sap.m.Dialog({
                title: "Joule AI Assistant - STEP 1 TEST",
                contentWidth: "400px",
                contentHeight: "300px",
                content: [
                    new sap.ui.core.HTML({
                        content: `
                            <div style="padding: 1rem;">
                                <h2 style="color: red;">TEST: Can you see this RED text?</h2>
                                <p style="color: blue;">This is BLUE text</p>
                                <p style="color: green;">This is GREEN text</p>
                                <p style="background: white; color: black; padding: 1rem;">
                                    BLACK text on WHITE background
                                </p>
                                <p style="background: #0070f2; color: white; padding: 1rem;">
                                    WHITE text on BLUE background
                                </p>
                            </div>
                        `
                    })
                ],
                endButton: new sap.m.Button({
                    text: "Close",
                    press: () => this.close()
                })
            });
            
            console.log('[AIAssistantOverlay] STEP 1: Dialog created');
        }
    }

    window.AIAssistantOverlay = AIAssistantOverlay;
    console.log('[AIAssistantOverlay] STEP 1: Minimal test version loaded');

})();