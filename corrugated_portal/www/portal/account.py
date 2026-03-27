"""Controller for /portal/account — Account summary with invoices and payments."""
import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access the portal.", frappe.AuthenticationError)

    context.no_cache = 1
    context.active_page = "account"
    context.title = "Account - Customer Portal"
    return context
