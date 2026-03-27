"""Controller for /portal/request-quote — Quote request form."""
import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access the portal.", frappe.AuthenticationError)

    context.no_cache = 1
    context.active_page = "quote"
    context.title = "Request a Quote - Customer Portal"
    return context
