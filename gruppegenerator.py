import streamlit as st
import pandas as pd
import random
import os

st.title("🎲 Tilfældig Gruppegenerator med billeder")

st.markdown(
    """
    Upload en CSV med dine studerende (to kolonner: **Navn,Semester**).  
    Sørg for at du har en mappe kaldet **Billeder af studerende/** med et billede til hver studerende, 
    hvor filnavnet matcher navnet i CSV (fx *Anders.png* eller *Anders.jpg*).
    """
)

# Funktion til at finde billeder (uanset filendelse)
def find_image(name, folder="Billeder af studerende"):
    if not os.path.exists(folder):
        st.warning(f"Mappen '{folder}' findes ikke i projektet.")
        return None
    for file in os.listdir(folder):
        base, ext = os.path.splitext(file)
        if base == str(name) and ext.lower() in [".jpg", ".jpeg", ".png"]:
            return os.path.join(folder, file)
    return None

# Funktion til at lave grupper uden rester
def make_groups(students, group_size):
    random.shuffle(students)
    groups = [students[i:i + group_size] for i in range(0, len(students), group_size)]

    # Hvis sidste gruppe er meget lille, fordel resterne ud i de andre grupper
    if len(groups) > 1 and len(groups[-1]) < group_size // 2:
        leftovers = groups.pop()
        for i, student in enumerate(leftovers):
            groups[i % len(groups)].append(student)

    return groups

# Upload CSV
file = st.file_uploader("Upload CSV", type=["csv"])

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
                    img = find_image(navn)
                    if img:
                        st.image(img, width=80)
                    else:
                        st.caption("❌ Intet billede")

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
                    groups = make_groups(students, group_size)

                    # Vis grupperne
                    for i, g in enumerate(groups, 1):
                        st.subheader(f"Gruppe {i}")
                        cols = st.columns(len(g))
                        for col, (name, _) in zip(cols, g):
                            with col:
                                st.write(name)
                                img = find_image(name)
                                if img:
                                    st.image(img, width=120)
                                else:
                                    st.caption("❌ Intet billede")
