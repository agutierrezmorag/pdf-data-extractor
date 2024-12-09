from typing import Optional

from pydantic import BaseModel, Field


class Item(BaseModel):
    """Individual line item from the invoice"""

    cases: int = Field(
        description="Number of boxes/cases for this specific item line (e.g., 55)"
    )
    code: str = Field(description="Product reference code/SKU (e.g., 1115615)")
    goods_descriptions: str = Field(
        description="Full product description including specifications, size, and packaging details"
    )
    quantity: str = Field(
        description="Total weight/quantity with decimal places and unit (e.g., '600.010 LB')"
    )

    unit_value: float = Field(
        description="Price per unit/lb in invoice currency (e.g., 6.65)"
    )


class Address(BaseModel):
    """Complete postal address information"""

    city: Optional[str] = Field(
        None, description="Full city name without abbreviations (e.g., 'Miami')"
    )
    country: Optional[str] = Field(
        None,
        description="Full country name or standard country code (e.g., 'US' or 'United States'), should be as-is from the invoice",
    )
    phone: Optional[str] = Field(
        None,
        description="Complete phone number (e.g., '786-522-8400')",
    )
    state: Optional[str] = Field(
        None, description="State or province name/code (e.g., 'FL' for Florida)"
    )
    street: Optional[str] = Field(
        None,
        description="Complete street address including building number, suite/unit number if applicable (e.g., '5200 Blue Lagoon Drive # Suite 750')",
    )
    zip_code: Optional[str] = Field(
        None,
        description="Postal/ZIP code in country-appropriate format (e.g., '33126' for US)",
    )


class Invoice(BaseModel):
    """Complete invoice data extracted from PDF document"""

    address: Optional[Address] = Field(
        None,
        description="Company (Aquachile Inc.) complete mailing address and contact details",
    )
    container: Optional[str] = Field(
        None, description="Shipping container identification number if applicable"
    )
    currency: Optional[str] = Field(
        None, description="Three-letter currency code (e.g., 'USD' for US Dollars)"
    )
    customer_address: Optional[Address] = Field(
        None, description="Customer's complete mailing address and contact information"
    )
    customer_id: Optional[str] = Field(
        None,
        description="Unique customer identifier/account number (e.g., '0100021610')",
    )
    date: Optional[str] = Field(
        None,
        description="Invoice issuance date in DD/MM/YYYY format (e.g., '13/06/2024')",
    )
    due_date: Optional[str] = Field(
        None, description="Payment due date in DD/MM/YYYY format (e.g., '13/07/2024')"
    )
    incoterms: Optional[str] = Field(
        None,
        description="International Commercial Terms defining shipping arrangement (e.g., 'FOB')",
    )
    invoice_number: Optional[str] = Field(
        None, description="Unique invoice identifier (e.g., '00090522')"
    )
    items: Optional[list[Item]] = Field(
        None,
        description="Detailed list of all products/items being invoiced, including quantities and prices",
    )
    messers: Optional[str] = Field(
        None, description="Customer's business/trading name as shown on invoice"
    )
    origin: Optional[str] = Field(
        None, description="Country or location of goods origin (e.g., 'CHILE')"
    )
    payment_terms: Optional[str] = Field(
        None,
        description="Payment deadline in number of days from invoice date (e.g., '30')",
    )
    po_number: Optional[str] = Field(
        None, description="Customer's Purchase Order reference number"
    )
    sales_order: Optional[str] = Field(
        None, description="Internal sales order reference number (e.g., '300281120')"
    )
    sap_number: Optional[str] = Field(
        None, description="SAP system reference number (e.g., '961226658')"
    )
    total_cases: int = Field(
        description="Sum of all cases across all line items in the invoice"
    )
    total_quantity: str = Field(
        description="Sum of all quantities across all line items with unit (e.g., '1,697.680 LB')"
    )
    total_value: float = Field(
        description="Total monetary value for every item in invoice currency"
    )
