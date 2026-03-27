"""Controller for /portal/artwork — Artwork upload and management."""
import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access the portal.", frappe.AuthenticationError)

    context.no_cache = 1
    context.active_page = "artwork"
    context.title = "Artwork - Customer Portal"
    return context
