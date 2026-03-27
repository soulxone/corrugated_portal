"""Controller for /portal/orders — Orders list page."""
import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access the portal.", frappe.AuthenticationError)

    context.no_cache = 1
    context.active_page = "orders"
    context.title = "Orders - Customer Portal"
    return context
