import pdfkit
import streamlit as st
from jinja2 import Environment, FileSystemLoader, select_autoescape

# st.set_page_config(layout="centered", page_icon="💰", page_title="Invoice Generator")
st.title("💰 Bill Generator")

st.write(
    "Easily Print Your Bills With No Extra Charges !!!"
)


env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
template = env.get_template("invoice_template.html")


with st.form("template_form"):
    left, right = st.columns((1, 10))
    color = left.color_picker("Color", value="#b4cffa")
    Hosptial_name = right.text_input("Hosptial name", value="Sanjivani")
    left, right = st.columns(2)
    Patient_name = left.text_input("Patient name", value="")
    Patient_address = right.text_input("Patient address", value="")
    Treatment_type = left.selectbox("Treatment type", ["Ayurvedic", "Aleopathic"])
    quantity = right.number_input("Quantity", 1, 10)
    Treatment_Cost = st.slider("Treatment Cost", 1, 100, 60)
    total = Treatment_Cost * quantity
    submit = st.form_submit_button()

if submit:
    html = template.render(
        color=color,
        Hosptial_name=Hosptial_name,
        Patient_name=Patient_name,
        Patient_address=Patient_address,
        Treatment_type=Treatment_type,
        quantity=quantity,
        Treatment_Cost=Treatment_Cost,
        total=total,
    )

    pdf = pdfkit.from_string(html, False)

    st.success("🎉 Your invoice was generated!")

    st.download_button(
        "⬇️ Download PDF",
        data=pdf,
        file_name="invoice.pdf",
        mime="application/octet-stream",
    )
