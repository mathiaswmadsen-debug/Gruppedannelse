import streamlit as st
import pandas as pd
import random
import os
import base64

st.set_page_config(layout="wide")  # udnyt hele skærmbredden

st.title("🎲 Tilfældig Gruppegenerator med billeder")

st.markdown(
    """
    Upload en CSV med dine studerende (to kolonner: **Navn,Semester**).  
    Sørg for at du har en mappe kaldet **Billeder af studerende/** med et billede til hver studerende, 
    hvor filnavnet matcher navnet i CSV (fx *Anders.png* eller *Anders.jpg*).
    """
)

# Minimal CSS for pæn præsentation
st.markdown("""
<style>
.group-title { text-align:center; font-size:18px; font-weight:700; margin: 4px 0 10px; }
.person { display:flex; flex-direction:column; align-items:center; gap:6px; margin: 0 0 14px; }
.person img { width:72px; height:72px; border-radius:12px; object-fit:cover; display:block; margin:0 auto; }
.person .name { font-size:14px; color:#444; text-align:center; margin:0; line-height:1.15; }
.placeholder { width:72px; height:72px; border-radius:12px; background:#eee; display:flex; align-items:center; justify-content:center; font-size:20px; color:#999; }
</style>
""", unsafe_allow_html=True)

def find_image(name, folder="Billeder af studerende"):
    """Find filsti til navnets billede uanset endelse."""
    if not os.path.exists(folder):
        return None
    for file in os.listdir(folder):
        base, ext = os.path.splitext(file)
        if base == str(name) and ext.lower() in [".jpg", ".jpeg", ".png"]:
            return os.path.join(folder, file)
    return None

def img_figure_html(path, name):
    """Returnér centreret <figure> med inline base64-billede + navn."""
    if not path:
        return f"""<figure class="person">
            <div class="placeholder">❌</div>
            <figcaption class="name">{name}</figcaption>
        </figure>"""
    ext = os.path.splitext(path)[1].lower().replace(".", "")  # jpg/jpeg/png
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"""<figure class="person">
        <img src="data:image/{ext};base64,{b64}" alt="{name}" />
        <figcaption class="name">{name}</figcaption>
    </figure>"""

def make_groups(students, group_size):
    """Lav grupper og fordel evt. rester ud på eksisterende grupper."""
    random.shuffle(students)
    groups = [students[i:i + group_size] for i in range(0, len(students), group_size)]
    if len(groups) > 1 and len(groups[-1]) < group_size // 2:
        leftovers = groups.pop()
        for i, student in enumerate(leftovers):
            groups[i % len(groups)].append(student)
    return groups

# Upload CSV
file = st.file_uploader("Upload CSV", type=["csv"])

# Session state til at gemme grupper
if "groups" not in st.session_state:
    st.session_state["groups"] = None

if file:
    try:
        df = pd.read_csv(file, sep=None, engine="python")
        df.columns = df.columns.str.strip().str.replace("\ufeff", "")
    except Exception as e:
        st.error(f"Kunne ikke læse CSV-filen: {e}")
        df = None

    if df is not None:
        if not {"Navn", "Semester"}.issubset(df.columns):
            st.error(
                "CSV skal indeholde kolonnerne 'Navn' og 'Semester'. "
                f"Jeg fandt i stedet: {list(df.columns)}"
            )
        else:
            st.subheader("✔️ Vælg hvilke studerende der er til stede i dag")

            presence = {}
            for _, row in df.iterrows():
                navn, sem = row["Navn"], row["Semester"]
                col1, col2 = st.columns([1, 3])

                with col1:
                    path = find_image(navn)
                    st.markdown(img_figure_html(path, navn), unsafe_allow_html=True)

                with col2:
                    presence[navn] = st.checkbox(f"{navn} (Semester {sem})", value=True)

            # Filtrér de studerende som er til stede
            students = [(row["Navn"], row["Semester"])
                        for _, row in df.iterrows() if presence[row["Navn"]]]

            st.markdown("---")
            group_size = st.number_input(
                "Hvor mange personer pr. gruppe?", min_value=2, max_value=10, value=3
            )

            if st.button("Lav grupper"):
                if not students:
                    st.warning("Ingen studerende er valgt som til stede.")
                else:
                    st.session_state["groups"] = make_groups(students, group_size)

# Præsentationsmode – vis grupperne i grid (8 per række)
if st.session_state["groups"]:
    groups = st.session_state["groups"]
    st.markdown("## 📺 Præsentationsmode")

    cols_per_row = 8
    for i in range(0, len(groups), cols_per_row):
        row = st.columns(cols_per_row)
        for col, (j, g) in zip(row, enumerate(groups[i:i+cols_per_row], start=i+1)):
            with col:
                st.markdown(f"<div class='group-title'>Gruppe {j}</div>", unsafe_allow_html=True)
                for name, _ in g:
                    st.markdown(img_figure_html(find_image(name), name), unsafe_allow_html=True)
