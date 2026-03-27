frappe.ui.form.on("Artwork Upload", {
    refresh(frm) {
        if (frm.doc.status === "Pending Review") {
            frm.add_custom_button(__("Approve"), function () {
                frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: "Artwork Upload",
                        name: frm.doc.name,
                        fieldname: {
                            status: "Approved",
                            reviewer: frappe.session.user,
                            review_date: frappe.datetime.get_today(),
                        },
                    },
                    callback: () => frm.reload_doc(),
                });
            }, __("Actions"));

            frm.add_custom_button(__("Request Revision"), function () {
                frappe.prompt(
                    { fieldtype: "Text", label: "Revision Notes", fieldname: "notes", reqd: 1 },
                    function (values) {
                        frappe.call({
                            method: "frappe.client.set_value",
                            args: {
                                doctype: "Artwork Upload",
                                name: frm.doc.name,
                                fieldname: {
                                    status: "Revision Needed",
                                    reviewer: frappe.session.user,
                                    review_date: frappe.datetime.get_today(),
                                    review_notes: values.notes,
                                },
                            },
                            callback: () => frm.reload_doc(),
                        });
                    },
                    __("Request Revision"),
                    __("Submit")
                );
            }, __("Actions"));
        }

        // Color the status indicator
        const color_map = {
            "Pending Review": "orange",
            Approved: "green",
            "Revision Needed": "red",
            Archived: "gray",
        };
        if (frm.doc.status && color_map[frm.doc.status]) {
            frm.page.set_indicator(frm.doc.status, color_map[frm.doc.status]);
        }
    },
});
