from setuptools import setup, find_packages

setup(
    name="corrugated_portal",
    version="0.1.0",
    author="Welchwyse",
    author_email="info@welchwyse.com",
    description="Customer self-service portal for corrugated packaging orders",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["frappe", "erpnext"],
)
