"""Controller for /portal/track — Shipment tracking page."""
import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access the portal.", frappe.AuthenticationError)

    context.no_cache = 1
    context.active_page = "tracking"
    context.title = "Track Shipments - Customer Portal"
    return context
