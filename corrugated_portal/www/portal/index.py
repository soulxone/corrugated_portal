"""Controller for /portal — Portal Home page."""
import frappe


def get_context(context):
    """Provide context for the portal home page."""
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access the portal.", frappe.AuthenticationError)

    context.no_cache = 1
    context.active_page = "home"
    context.title = "Customer Portal"
    return context
