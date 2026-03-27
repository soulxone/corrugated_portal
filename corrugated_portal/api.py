"""Corrugated Portal API -- Customer-facing endpoints."""
import frappe
from frappe.utils import today, flt, cint


def _get_customer_for_user():
    """Get the Customer linked to the current logged-in user."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("Please log in to access the portal.")
    # Find Contact -> Customer link
    contact = frappe.db.get_value("Contact", {"user": user}, "name")
    if contact:
        links = frappe.get_all(
            "Dynamic Link",
            filters={"parent": contact, "link_doctype": "Customer"},
            fields=["link_name"],
            limit=1,
        )
        if links:
            return links[0].link_name
    # Fallback: check Customer directly
    customer = frappe.db.get_value("Customer", {"portal_user": user}, "name")
    return customer


@frappe.whitelist()
def get_portal_home():
    """Home page data: recent orders, open estimates, quick stats."""
    customer = _get_customer_for_user()
    if not customer:
        return {"customer": None, "error": "No customer linked to your account."}

    recent_orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer, "docstatus": 1},
        fields=["name", "transaction_date", "grand_total", "status", "delivery_status"],
        order_by="transaction_date desc",
        limit=5,
    )

    open_estimates = frappe.get_all(
        "Corrugated Estimate",
        filters={"customer": customer, "status": ["in", ["Draft", "Sent"]]},
        fields=["name", "estimate_date", "box_style", "status"],
        order_by="estimate_date desc",
        limit=5,
    )

    return {
        "customer": customer,
        "customer_name": frappe.db.get_value("Customer", customer, "customer_name"),
        "recent_orders": recent_orders,
        "open_estimates": open_estimates,
        "total_orders": frappe.db.count(
            "Sales Order", {"customer": customer, "docstatus": 1}
        ),
    }


@frappe.whitelist()
def get_customer_orders(status_filter=None, search=None, page=0):
    """List Sales Orders for the portal user."""
    customer = _get_customer_for_user()
    if not customer:
        return []
    filters = {"customer": customer, "docstatus": 1}
    if status_filter and status_filter != "All":
        filters["status"] = status_filter

    or_filters = {}
    if search:
        or_filters = {"name": ["like", f"%{search}%"]}

    orders = frappe.get_all(
        "Sales Order",
        filters=filters,
        or_filters=or_filters if search else None,
        fields=[
            "name",
            "transaction_date",
            "grand_total",
            "status",
            "delivery_status",
            "total_qty",
        ],
        order_by="transaction_date desc",
        limit_page_length=20,
        limit_start=cint(page) * 20,
    )
    return orders


@frappe.whitelist()
def get_order_detail(order_name):
    """Get full order detail for portal view."""
    customer = _get_customer_for_user()
    so = frappe.get_doc("Sales Order", order_name)
    if so.customer != customer:
        frappe.throw("Access denied.")

    items = []
    for item in so.items:
        items.append(
            {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "rate": item.rate,
                "amount": item.amount,
            }
        )

    # Get shipment info
    shipments = frappe.get_all(
        "Delivery Note",
        filters={"against_sales_order": order_name, "docstatus": 1},
        fields=["name", "posting_date", "status"],
    )

    return {
        "name": so.name,
        "date": so.transaction_date,
        "status": so.status,
        "grand_total": so.grand_total,
        "items": items,
        "shipments": shipments,
        "delivery_status": so.delivery_status,
    }


@frappe.whitelist()
def submit_quote_request(
    box_style,
    length=0,
    width=0,
    depth=0,
    quantity_needed=0,
    num_colors=0,
    wall_type="Single Wall",
    flute="C",
    coating="None",
    special_requirements="",
    contact_name="",
    contact_email="",
    urgency="Standard",
):
    """Submit a quote request from the portal."""
    customer = _get_customer_for_user()

    qr = frappe.get_doc(
        {
            "doctype": "Quote Request",
            "customer": customer,
            "contact_name": contact_name or frappe.session.user,
            "contact_email": contact_email or frappe.session.user,
            "box_style": box_style,
            "length": flt(length),
            "width": flt(width),
            "depth": flt(depth),
            "quantity_needed": cint(quantity_needed),
            "num_colors": cint(num_colors),
            "wall_type": wall_type,
            "flute": flute,
            "coating": coating,
            "special_requirements": special_requirements,
            "urgency": urgency,
            "status": "New",
        }
    )
    qr.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        "request": qr.name,
        "message": "Quote request submitted successfully!",
    }


@frappe.whitelist()
def get_tracking_info():
    """Get shipment tracking for the portal user."""
    customer = _get_customer_for_user()
    if not customer:
        return []

    # Get delivery notes for this customer
    deliveries = frappe.get_all(
        "Delivery Note",
        filters={"customer": customer, "docstatus": 1},
        fields=[
            "name",
            "status",
            "posting_date",
            "total_qty",
            "grand_total",
            "transporter_name",
            "lr_no",
            "lr_date",
        ],
        order_by="posting_date desc",
        limit=20,
    )

    # Also try Load Tag if it exists
    loads = []
    if frappe.db.exists("DocType", "Load Tag"):
        loads = frappe.get_all(
            "Load Tag",
            filters={
                "destination_customer": customer,
                "status": ["in", ["In Transit", "Delivered"]],
            },
            fields=[
                "name",
                "status",
                "trailer_number",
                "ship_date",
                "total_pallets",
                "total_pieces",
                "last_gps_lat",
                "last_gps_lng",
                "last_gps_time",
                "expected_delivery_date",
            ],
            order_by="ship_date desc",
            limit=20,
        )

    return {"deliveries": deliveries, "loads": loads}


@frappe.whitelist()
def get_account_summary():
    """Get invoice and payment summary."""
    customer = _get_customer_for_user()
    if not customer:
        return {}

    outstanding = frappe.get_all(
        "Sales Invoice",
        filters={"customer": customer, "docstatus": 1, "outstanding_amount": [">", 0]},
        fields=[
            "name",
            "posting_date",
            "grand_total",
            "outstanding_amount",
            "due_date",
        ],
        order_by="due_date asc",
    )

    total_outstanding = sum(flt(inv.outstanding_amount) for inv in outstanding)

    recent_payments = frappe.get_all(
        "Payment Entry",
        filters={"party": customer, "party_type": "Customer", "docstatus": 1},
        fields=["name", "posting_date", "paid_amount", "reference_no"],
        order_by="posting_date desc",
        limit=10,
    )

    return {
        "customer": customer,
        "outstanding_invoices": outstanding,
        "total_outstanding": total_outstanding,
        "recent_payments": recent_payments,
    }


@frappe.whitelist()
def get_artwork_uploads():
    """Get artwork uploads for the portal user."""
    customer = _get_customer_for_user()
    if not customer:
        return []

    uploads = frappe.get_all(
        "Artwork Upload",
        filters={"customer": customer},
        fields=[
            "name",
            "artwork_name",
            "status",
            "file_type",
            "uploaded_date",
            "revision_number",
            "review_notes",
        ],
        order_by="uploaded_date desc",
    )
    return uploads


@frappe.whitelist()
def upload_artwork(artwork_name, file_url, file_type="Other", sales_order=None, estimate=None):
    """Upload artwork from the portal."""
    customer = _get_customer_for_user()

    art = frappe.get_doc(
        {
            "doctype": "Artwork Upload",
            "artwork_name": artwork_name,
            "customer": customer,
            "sales_order": sales_order,
            "corrugated_estimate": estimate,
            "file": file_url,
            "file_type": file_type,
            "uploaded_by": frappe.session.user,
            "uploaded_date": today(),
            "status": "Pending Review",
            "revision_number": 1,
        }
    )
    art.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"status": "success", "name": art.name, "message": "Artwork uploaded successfully!"}


@frappe.whitelist()
def reorder(sales_order_name, new_quantity=0):
    """Create a new estimate from a past Sales Order (reorder)."""
    customer = _get_customer_for_user()
    so = frappe.get_doc("Sales Order", sales_order_name)
    if so.customer != customer:
        frappe.throw("Access denied.")

    # Find linked estimate
    est_ref = frappe.db.get_value(
        "Corrugated Estimate", {"sales_order_ref": sales_order_name}, "name"
    )

    if est_ref:
        old_est = frappe.get_doc("Corrugated Estimate", est_ref)
        new_est = frappe.copy_doc(old_est)
        new_est.status = "Draft"
        new_est.sales_order_ref = None
        new_est.estimate_date = today()
        if cint(new_quantity) > 0 and new_est.quantities:
            new_est.quantities[0].quantity = cint(new_quantity)
        new_est.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success", "estimate": new_est.name}

    return {"status": "error", "message": "No linked estimate found for this order."}
