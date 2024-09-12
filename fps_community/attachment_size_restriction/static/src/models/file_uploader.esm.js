/** @odoo-module **/

import {registerPatch} from "@mail/model/model_core";
import session from "web.session";
import Dialog from "web.Dialog"; // eslint-disable-line sort-imports
import {_t} from "web.core";
import {human_size} from "web.utils";

registerPatch({
    name: "FileUploader",
    // Added the patch on existing register model and inherit '_performUpload' method
    recordMethods: {
        /**
         * @inherit
         */
        // Inherit the method to define max_attachment_size and
        // restrict if attachment size exceeded default size is 10 Mb

        // eslint-disable-next-line no-unused-vars
        async _performUpload({files}) {
            var max_attachment_size = session.max_attachment_size || 10 * 1024 * 1024;
            var larger_files = [];
            for (const file of files) {
                if (file.size > max_attachment_size) {
                    larger_files.push(file);
                }
            }
            // Raise the validation error.
            if (larger_files.length !== 0) {
                Dialog.alert(
                    this,
                    _.str.sprintf(
                        _t("The selected file exceeds the maximum file size of %s"),
                        human_size(max_attachment_size)
                    ),
                    {title: _t("Validation Error")}
                );
                return false;
            }
            return this._super(...arguments);
        },
    },
});
