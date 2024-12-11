from typing import Optional

from pydantic import BaseModel, Field


class Item(BaseModel):
    """Individual line item from the invoice"""

    cases: int = Field(
        description="Extract the number of boxes/cases exactly as shown in the line item"
    )
    code: str = Field(
        description="Extract product reference code/SKU exactly as shown on invoice"
    )
    goods_descriptions: str = Field(
        description="Extract full product description exactly as written on invoice with no modifications"
    )
    quantity: str = Field(
        description="Extract total weight/quantity exactly as written, preserving all decimals and units"
    )
    unit_value: float = Field(
        description="Extract price per unit exactly as shown on invoice"
    )
    item_total_value: float = Field(
        description="Extract total monetary value exactly as shown on invoice"
    )


class Address(BaseModel):
    """Complete postal address information"""

    city: Optional[str] = Field(
        None,
        description="Extract city name exactly as written on invoice. Do not extract city from street line.",
    )
    country: Optional[str] = Field(
        None,
        description="Extract country name or code exactly as shown on invoice, do not standardize",
    )
    state: Optional[str] = Field(
        None, description="Extract state/province exactly as written on invoice"
    )
    street: Optional[str] = Field(
        None,
        description="Extract complete street address line exactly as written on invoice, including any city/location information if present on same line (e.g., '999 Lake Drive, Seattle'). Do not split or modify the line in any way.",
    )
    zip_code: Optional[str] = Field(
        None, description="Extract postal/ZIP code exactly as shown on invoice"
    )


class Invoice(BaseModel):
    """Complete invoice data extracted from PDF document"""

    aquachile_address: Optional[Address] = Field(
        None, description="Extract Aquachile address exactly as shown on invoice"
    )
    container: Optional[str] = Field(
        None,
        description="Extract shipping container number exactly as written if present",
    )
    currency: Optional[str] = Field(
        None, description="Extract currency code/name exactly as shown on invoice"
    )
    customer_address: Optional[Address] = Field(
        None, description="Extract customer address exactly as shown on invoice"
    )
    customer_id: Optional[str] = Field(
        None,
        description="Extract customer identifier/account number exactly as written",
    )
    date: Optional[str] = Field(
        None, description="Extract invoice date exactly as written on document"
    )
    due_date: Optional[str] = Field(
        None, description="Extract payment due date exactly as written on document"
    )
    incoterms: Optional[str] = Field(
        None, description="Extract shipping terms exactly as written on invoice"
    )
    invoice_number: Optional[str] = Field(
        None, description="Extract invoice identifier exactly as shown"
    )
    items: Optional[list[Item]] = Field(
        None, description="Extract all invoice line items preserving original values"
    )
    messers: Optional[str] = Field(
        None, description="Extract customer's business name exactly as written"
    )
    origin: Optional[str] = Field(
        None, description="Extract origin country/location exactly as shown"
    )
    payment_terms: Optional[str] = Field(
        None, description="Extract payment terms exactly as written"
    )
    po_number: Optional[str] = Field(
        None, description="Extract PO reference number exactly as shown"
    )
    sale_conditions: list[str] = Field(
        description="Extract terms and conditions exactly as written on invoice"
    )
    sales_order: Optional[str] = Field(
        None, description="Extract sales order reference exactly as written"
    )
    sap_number: Optional[str] = Field(
        None, description="Extract SAP reference number exactly as shown"
    )
    total_cases: int = Field(
        description="Extract total number of cases exactly as shown"
    )
    total_quantity: str = Field(
        description="Extract total quantity exactly as written, preserving format"
    )
    total_value: float = Field(
        description="Extract total monetary value exactly as shown"
    )
