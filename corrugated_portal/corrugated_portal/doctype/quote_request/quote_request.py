"""Quote Request — Customer quote requests from the portal."""
import frappe
from frappe.model.document import Document
from frappe.utils import today


class QuoteRequest(Document):
    def on_submit(self):
        """Create a Corrugated Estimate from the quote request specs and notify sales."""
        self._create_estimate()
        self._notify_sales()

    def _create_estimate(self):
        """Create a linked Corrugated Estimate from this request's box specs."""
        if frappe.db.exists("DocType", "Corrugated Estimate"):
            try:
                est = frappe.get_doc({
                    "doctype": "Corrugated Estimate",
                    "customer": self.customer,
                    "estimate_date": today(),
                    "box_style": self.box_style,
                    "length": self.length,
                    "width": self.width,
                    "depth": self.depth,
                    "flute": self.flute,
                    "num_colors": self.num_colors,
                    "coating": self.coating,
                    "status": "Draft",
                    "quote_request_ref": self.name,
                })
                est.insert(ignore_permissions=True)

                # Link back
                frappe.db.set_value("Quote Request", self.name,
                                    "corrugated_estimate", est.name)
                frappe.db.commit()
            except Exception:
                frappe.log_error(
                    f"Failed to create estimate from Quote Request {self.name}",
                    "Quote Request"
                )

    def _notify_sales(self):
        """Send email notification to sales about new quote request."""
        try:
            settings = frappe.get_single("Corrugated Portal Settings")
            recipients = settings.contact_email or frappe.db.get_single_value(
                "Website Settings", "email"
            )
            if recipients:
                frappe.sendmail(
                    recipients=[recipients],
                    subject=f"New Quote Request: {self.name}",
                    message=f"""
                        <h3>New Quote Request Submitted</h3>
                        <p><strong>Customer:</strong> {self.customer}</p>
                        <p><strong>Box Style:</strong> {self.box_style}</p>
                        <p><strong>Dimensions:</strong> {self.length} x {self.width} x {self.depth}</p>
                        <p><strong>Quantity:</strong> {self.quantity_needed}</p>
                        <p><strong>Urgency:</strong> {self.urgency}</p>
                        <p><strong>Contact:</strong> {self.contact_name} ({self.contact_email})</p>
                    """,
                    now=True,
                )
        except Exception:
            frappe.log_error(
                f"Failed to send sales notification for {self.name}",
                "Quote Request"
            )
