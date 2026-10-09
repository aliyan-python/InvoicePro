import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime, timedelta

pdfmetrics.registerFont(
    TTFont("DejaVuSans", "DejaVuSans.ttf")
)

pdfmetrics.registerFont(
    TTFont("DejaVuSans-Bold", "DejaVuSans-Bold.ttf")
)

pdfmetrics.registerFont(
    TTFont("NotoSansArabic", "NotoSansArabic-Regular.ttf")
)


def create_invoice_pdf(
    logo,
    business_name,
    business_address,
    business_email,
    business_phone,
    customer_name,
    customer_email,
    customer_address,
    invoice_number,
    invoice_date,
    invoice_time,
    due_date,
    items,
    tax,
    discount,
    currency_symbol
):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    if logo is not None:
        logo.seek(0)
        pdf.drawImage(
            ImageReader(logo),
            150 * mm,
            height - 35 * mm,
            width=35 * mm,
            height=25 * mm,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto"
        )

    pdf.setFont("DejaVuSans-Bold", 24)
    pdf.drawString(20 * mm, height - 25 * mm, "INVOICE")

    pdf.setFont("DejaVuSans-Bold", 12)
    pdf.drawString(20 * mm, height - 40 * mm, business_name)

    pdf.setFont("DejaVuSans", 10)
    pdf.drawString(20 * mm, height - 47 * mm, business_address[:80])
    pdf.drawString(20 * mm, height - 54 * mm, business_email[:80])
    pdf.drawString(20 * mm, height - 61 * mm, business_phone[:40])

    pdf.setFont("DejaVuSans-Bold", 10)
    pdf.drawString(130 * mm, height - 40 * mm, f"Invoice: {invoice_number}")

    pdf.setFont("DejaVuSans", 9)
    pdf.drawString(
        130 * mm, height - 47 * mm,
        f"Date: {invoice_date.strftime('%b %d, %Y')}"
    )
    pdf.drawString(130 * mm, height - 54 * mm, f"Time: {invoice_time}")
    pdf.drawString(
        130 * mm, height - 61 * mm,
        f"Due: {due_date.strftime('%b %d, %Y')}"
    )

    pdf.setFont("DejaVuSans-Bold", 11)
    pdf.drawString(20 * mm, height - 78 * mm, "Bill To:")

    pdf.setFont("DejaVuSans", 10)
    pdf.drawString(20 * mm, height - 85 * mm, customer_name[:80])
    pdf.drawString(20 * mm, height - 92 * mm, customer_email[:80])
    pdf.drawString(20 * mm, height - 99 * mm, customer_address[:80])

    # Items table
    y = height - 120 * mm

    pdf.setFont("DejaVuSans-Bold", 9)
    pdf.drawString(20 * mm, y, "Item / Service")
    pdf.drawString(105 * mm, y, "Qty")
    pdf.drawString(130 * mm, y, "Price")
    pdf.drawString(165 * mm, y, "Total")

    pdf.line(20 * mm, y - 3, 190 * mm, y - 3)
    y -= 15

    pdf.setFont("DejaVuSans", 9)

    valid_items = [
        item for item in items if item["name"].strip()
    ]

    for item in valid_items:
        if y < 65 * mm:
            pdf.showPage()
            y = height - 25 * mm
            pdf.setFont("DejaVuSans-Bold", 9)
            pdf.drawString(20 * mm, y, "Item / Service")
            pdf.drawString(105 * mm, y, "Qty")
            pdf.drawString(130 * mm, y, "Price")
            pdf.drawString(165 * mm, y, "Total")
            pdf.line(20 * mm, y - 3, 190 * mm, y - 3)
            y -= 15
            pdf.setFont("DejaVuSans", 9)

        line_total = item["quantity"] * item["price"]

        pdf.drawString(20 * mm, y, item["name"][:42])
        pdf.drawRightString(120 * mm, y, str(item["quantity"]))
        pdf.drawRightString(
            157 * mm, y,
            f"{currency_symbol}{item['price']:,.2f}"
        )
        pdf.drawRightString(
            190 * mm, y,
            f"{currency_symbol}{line_total:,.2f}"
        )

        y -= 10

    subtotal = sum(
        item["quantity"] * item["price"] for item in valid_items
    )
    discount_amount = subtotal * discount / 100
    after_discount = subtotal - discount_amount
    tax_amount = after_discount * tax / 100
    total = after_discount + tax_amount

    y -= 8
    pdf.setFont("DejaVuSans", 10)

    pdf.drawRightString(
        157 * mm, y, f"Subtotal: {currency_symbol}{subtotal:,.2f}"
    )
    y -= 9
    pdf.drawRightString(
        157 * mm, y,
        f"Discount ({discount}%): -{currency_symbol}{discount_amount:,.2f}"
    )
    y -= 9
    pdf.drawRightString(
        157 * mm, y, f"Tax ({tax}%): {currency_symbol}{tax_amount:,.2f}"
    )
    y -= 12

    pdf.setFont("DejaVuSans-Bold", 12)
    pdf.drawRightString(
        190 * mm, y, f"Total: {currency_symbol}{total:,.2f}"
    )

    pdf.setFont("DejaVuSans", 9)
    pdf.drawString(20 * mm, 20 * mm, "Thank you for your business!")

    pdf.save()
    buffer.seek(0)
    return buffer


st.set_page_config(
    page_title="InvoicePro",
    page_icon="🧾"

)

st.title("🧾 InvoicePro")
st.write("Create A Professional Invoices Quickly And Easily")

st.subheader("🏢 Business Information")

logo = st.file_uploader(
    "Upload Business Logo",
    type=["png", "jpg", "jpeg"]
)

business_name = st.text_input(
    "Business_Name",
    placeholder="Enter Your Business Name"

)


business_address = st.text_input(
    "Business_Address",
    placeholder="Enter Your Business Address"

)


business_email = st.text_input(
    "Business_Email",
    placeholder="Enter Your Business Email"

)


business_phone = st.text_input(
    "Business_Phone",
    placeholder="Enter Your Business Phone"

)

st.subheader("👤 Customer Information")

customer_name = st.text_input(
    "Customer Name",
    placeholder="Enter Customer Name"

)

customer_email = st.text_input(
    "Customer Email",
    placeholder="Enter Customer Email"

)

customer_address = st.text_input(
    "Customer Address",
    placeholder="Enter Customer Address"

)

st.subheader("📄 Invoice Information")

now = datetime.now()

if "invoice_counter" not in st.session_state:
    st.session_state.invoice_counter = 1

invoice_number = f"INV-{st.session_state.invoice_counter:03d}"

invoice_date = now.date()

invoice_time = now.strftime("%I:%M %p")

due_date = invoice_date + timedelta(days=7)

st.write(f"**Invoice Number:** {invoice_number}")
st.write(f"**Invoice Date:** {invoice_date.strftime('%A, %B %d, %Y')}")
st.write(f"**Invoice Time:** {invoice_time}")
st.write(f"**Due Date:** {due_date.strftime('%A, %B %d, %Y')}")


st.subheader("🛒 Invoice Items")

if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = [
        {"name": "", "quantity": 1, "price": 0.0}
    ]

for i, item in enumerate(st.session_state.invoice_items):
    st.markdown(f"**Item {i + 1}**")

    col1, col2, col3 = st.columns(3)

    with col1:
        item["name"] = st.text_input(
            "Item or Service Name",
            value=item["name"],
            key=f"item_name_{i}"
        )

    with col2:
        item["quantity"] = st.number_input(
            "Quantity",
            min_value=1,
            value=item["quantity"],
            step=1,
            key=f"item_quantity_{i}"
        )

    with col3:
        item["price"] = st.number_input(
            "Price per Item",
            min_value=0.0,
            value=item["price"],
            step=0.01,
            key=f"item_price_{i}"
        )

if st.button("➕ Add Another Item"):
    st.session_state.invoice_items.append(
        {"name": "", "quantity": 1, "price": 0.0}
    )
    st.rerun()

currency = st.selectbox(
    "Currency",
    ["USD ($)", "PKR (₨)", "EUR (€)", "GBP (£)", "AED (د.إ)", "SAR (﷼)"]
)

currency_symbols = {
    "USD ($)": "$",
    "PKR (₨)": "₨",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "AED (د.إ)": "د.إ",
    "SAR (﷼)": "﷼"
}

currency_symbol = currency_symbols[currency]

tax = st.number_input(
    "Tax (%)",
    min_value=0.0,
    value=0.0,
    step=0.1
)

discount = st.number_input(
    "Discount (%)",
    min_value=0.0,
    max_value=100.0,
    value=0.0,
    step=0.1
)

if st.button("Calculate Invoice"):

    if not business_name.strip():
        st.warning("Please enter the business name.")

    elif not customer_name.strip():
        st.warning("Please enter the customer name.")

    elif not any(
        item["name"].strip()
        for item in st.session_state.invoice_items
    ):
        st.warning("Please enter at least one item or service.")

    else:
        valid_items = [
            item for item in st.session_state.invoice_items
            if item["name"].strip()
        ]

        subtotal = sum(
            item["quantity"] * item["price"]
            for item in valid_items
        )

        discount_amount = subtotal * (discount / 100)
        after_discount = subtotal - discount_amount
        tax_amount = after_discount * (tax / 100)
        total = after_discount + tax_amount

        st.success("Invoice calculated successfully!")
        st.subheader("💰 Invoice Summary")

        st.write(f"**Subtotal:** {currency_symbol}{subtotal:,.2f}")
        st.write(
            f"**Discount ({discount}%):** "
            f"-{currency_symbol}{discount_amount:,.2f}"
        )
        st.write(
            f"**After Discount:** {currency_symbol}{after_discount:,.2f}"
        )
        st.write(f"**Tax ({tax}%):** {currency_symbol}{tax_amount:,.2f}")
        st.write(f"**Total:** {currency_symbol}{total:,.2f}")

        pdf_file = create_invoice_pdf(
            logo,
            business_name,
            business_address,
            business_email,
            business_phone,
            customer_name,
            customer_email,
            customer_address,
            invoice_number,
            invoice_date,
            invoice_time,
            due_date,
            valid_items,
            tax,
            discount,
            currency_symbol
        )

        st.download_button(
            label="📥 Download Invoice PDF",
            data=pdf_file,
            file_name=f"{invoice_number}.pdf",
            mime="application/pdf"
        )


if st.button("➕ New Invoice"):
    st.session_state.invoice_counter += 1
    st.success("New Invoice Created!")
