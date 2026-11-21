
import streamlit as st
import pandas as pd

from automata.infix import recognize_infix, get_infix_transitions
from automata.postfix import recognize_postfix

st.set_page_config(
    page_title="Expression PDA",
    page_icon="🔤",
    layout="wide"
)

st.title("🔤 Expression Automata")
st.caption(
    "Pengenal ekspresi Infix dan Postfix menggunakan konsep "
    "Pushdown Automaton (PDA)."
)

mode = st.radio(
    "Pilih jenis ekspresi:",
    ["Infix", "Postfix"],
    horizontal=True
)

if mode == "Infix":
    st.subheader("PDA Infix berbasis CFG")

    st.markdown("""
    **CFG yang digunakan:**

    - `E → T E'`
    - `E' → + T E' | - T E' | ε`
    - `T → F T'`
    - `T' → * F T' | / F T' | ε`
    - `F → ( E ) | 0 | 1 | 2 | ... | 9`

    PDA menggunakan satu state pemrosesan `q1`.
    Self-loop `q1` menangani ekspansi produksi CFG
    dan pencocokan terminal.
    """)

    expression = st.text_input(
        "Masukkan ekspresi infix:",
        placeholder="Contoh: 2 + 3 * (4 - 1)"
    )

    st.caption(
        "Operand menggunakan satu digit angka 0–9. "
        "Spasi boleh digunakan atau dihilangkan."
    )

else:
    st.subheader("PDA Postfix")

    expression = st.text_input(
        "Masukkan ekspresi postfix:",
        placeholder="Contoh: 23+4*"
    )

    st.caption(
        "Operand menggunakan satu digit angka 0–9. "
        "Contoh: 23+ berarti 2 + 3."
    )


if st.button("Jalankan PDA", type="primary"):

    if mode == "Infix":
        accepted, log, message = recognize_infix(expression)
    else:
        accepted, log, message = recognize_postfix(expression)

    if accepted:
        st.success("DITERIMA — " + message)
    else:
        st.error("DITOLAK — " + message)

    if log:
        st.subheader("Log Transisi")

        df = pd.DataFrame(log)

        df = df.rename(columns={
            "step": "Step",
            "state": "State",
            "input_read": "Input dibaca",
            "action": "Aksi / Transisi",
            "stack": "Stack",
            "remaining": "Input tersisa",
        })

        df["Stack"] = df["Stack"].apply(
            lambda value: " ".join(value)
            if isinstance(value, list)
            else str(value)
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        if mode == "Infix":
            st.info(
                "Untuk Infix, top of stack berada di sebelah kiri."
            )
        else:
            st.info(
                "Untuk Postfix, top of stack berada di sebelah kanan."
            )


if mode == "Infix":

    with st.expander("Lihat daftar transisi PDA Infix"):

        transitions = get_infix_transitions()

        df_t = pd.DataFrame(
            transitions,
            columns=[
                "From",
                "Input",
                "Top Stack",
                "Replacement",
                "To",
                "Keterangan"
            ]
        )

        st.dataframe(
            df_t,
            use_container_width=True,
            hide_index=True
        )


with st.expander("Contoh Pengujian"):

    if mode == "Infix":

        st.markdown("""
        **Contoh Ekspresi yang Diterima:**

        - `2`
        - `2+3`
        - `5-2`
        - `3*4`
        - `8/2`
        - `2+3*4`
        - `(2+3)*4`
        - `8/2-1`
        - `2*(3+4)`
        - `1+2*3-4/2`

        **Contoh Ekspresi yang Ditolak:**

        - `2+`
        - `+2`
        - `2++3`
        - `2**3`
        - `(2+3`
        - `2+3)`
        - `()`
        - `2 3`
        - `A+B`
        - `2+a`
        """)

    else:

        st.markdown("""
        **Contoh Ekspresi yang Diterima:**

        - `2`
        - `23+`
        - `23+4*`
        - `234*+`
        - `23+45+*`
        - `2345+*-`

        **Contoh Ekspresi yang Ditolak:**

        - `23`
        - `2+`
        - `23++`
        - `23+4`
        - `23+4*/`
        - `AB+`
        """)
