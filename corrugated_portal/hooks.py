app_name = "corrugated_portal"
app_title = "Corrugated Portal"
app_publisher = "Welchwyse"
app_description = "Customer self-service portal for corrugated packaging orders"
app_version = "0.1.0"
required_apps = ["frappe", "erpnext"]

website_route_rules = [
    {"from_route": "/portal", "to_route": "portal_home"},
    {"from_route": "/portal/orders", "to_route": "portal_orders"},
    {"from_route": "/portal/track", "to_route": "portal_tracking"},
    {"from_route": "/portal/request-quote", "to_route": "portal_quote_request"},
    {"from_route": "/portal/artwork", "to_route": "portal_artwork"},
    {"from_route": "/portal/account", "to_route": "portal_account"},
]

# Guest access to portal pages requires login
guest_allowed = []
