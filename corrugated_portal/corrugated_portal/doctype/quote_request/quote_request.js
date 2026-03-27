frappe.ui.form.on("Quote Request", {
    refresh(frm) {
        // Status workflow buttons
        if (frm.doc.docstatus === 1) {
            if (frm.doc.status === "New") {
                frm.add_custom_button(__("Mark Under Review"), function () {
                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Quote Request",
                            name: frm.doc.name,
                            fieldname: "status",
                            value: "Under Review",
                        },
                        callback: () => frm.reload_doc(),
                    });
                }, __("Actions"));
            }

            if (["New", "Under Review"].includes(frm.doc.status)) {
                frm.add_custom_button(__("Create Estimate"), function () {
                    frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: "Corrugated Estimate",
                            filters: { quote_request_ref: frm.doc.name },
                            limit: 1,
                        },
                        callback(r) {
                            if (r.message && r.message.length) {
                                frappe.set_route("Form", "Corrugated Estimate", r.message[0].name);
                            } else {
                                frappe.msgprint("No linked estimate found. Submit the request first.");
                            }
                        },
                    });
                }, __("Actions"));

                frm.add_custom_button(__("Send Quote"), function () {
                    frappe.prompt(
                        { fieldtype: "Currency", label: "Quoted Price", fieldname: "price", reqd: 1 },
                        function (values) {
                            frappe.call({
                                method: "frappe.client.set_value",
                                args: {
                                    doctype: "Quote Request",
                                    name: frm.doc.name,
                                    fieldname: { status: "Quoted", quoted_price: values.price },
                                },
                                callback: () => frm.reload_doc(),
                            });
                        },
                        __("Send Quote to Customer"),
                        __("Send")
                    );
                }, __("Actions"));
            }

            if (frm.doc.status === "Quoted") {
                frm.add_custom_button(__("Mark Accepted"), function () {
                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Quote Request",
                            name: frm.doc.name,
                            fieldname: "status",
                            value: "Accepted",
                        },
                        callback: () => frm.reload_doc(),
                    });
                }, __("Actions"));

                frm.add_custom_button(__("Mark Declined"), function () {
                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Quote Request",
                            name: frm.doc.name,
                            fieldname: "status",
                            value: "Declined",
                        },
                        callback: () => frm.reload_doc(),
                    });
                }, __("Actions"));
            }
        }

        // Color the status indicator
        const color_map = {
            New: "blue",
            "Under Review": "orange",
            Quoted: "purple",
            Accepted: "green",
            Declined: "red",
        };
        if (frm.doc.status && color_map[frm.doc.status]) {
            frm.page.set_indicator(frm.doc.status, color_map[frm.doc.status]);
        }
    },
});
