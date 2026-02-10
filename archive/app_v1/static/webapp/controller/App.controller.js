sap.ui.define([
    "sap/ui/core/mvc/Controller"
], function (Controller) {
    "use strict";

    return Controller.extend("p2p.dataproducts.controller.App", {
        /**
         * Called when the controller is instantiated.
         * @public
         */
        onInit: function () {
            // Apply content density class based on device
            this.getView().addStyleClass(this.getOwnerComponent().getContentDensityClass());
        }
    });
});
