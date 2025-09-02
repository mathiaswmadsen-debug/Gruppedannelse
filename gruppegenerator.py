import streamlit as st
import pandas as pd
import random
from collections import defaultdict
import os

st.title("🎲 Tilfældig Gruppegenerator med billeder")

st.markdown(
    """
    Upload en CSV med dine studerende (to kolonner: **Navn,Semester**).  
    Sørg for at du har en mappe kaldet **billeder af studerende/** med et billede til hver studerende, 
    hvor filnavnet matcher navnet i CSV (fx *Anders.png* eller *Anders.jpg*).
    """
)

# Funktion til at finde billeder (uanset filendelse)
def find_image(name, folder="billeder af studerende"):
    if not os.path.exists(folder):
        st.warning(f"Mappen '{folder}' findes ikke i projektet.")
        return None
    for file in os.listdir(folder):
        base, ext = os.path.splitext(file)
        if base == str(name) and ext.lower() in [".jpg", ".jpeg", ".png"]:
            return os.path.join(folder, file)
    st.caption(f"❓ Intet billede fundet til: {name}")
    return None

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
                    random.shuffle(students)

                    by_semester = defaultdict(list)
                    for name, sem in students:
                        by_semester[sem].append(name)

                    groups = []
                    remaining = students.copy()

                    # Lav grupper med mindst én fra hvert semester
                    while all(by_semester.values()):
                        group = []
                        for sem in list(by_semester.keys()):
                            if by_semester[sem]:
                                group.append(by_semester[sem].pop())
                                remaining = [s for s in remaining if s[0] != group[-1]]
                        while len(group) < group_size and remaining:
                            name, _ = remaining.pop()
                            group.append(name)
                        groups.append(group)

                    if remaining:
                        groups.append([s[0] for s in remaining])

                    # Vis grupperne
                    for i, g in enumerate(groups, 1):
                        st.subheader(f"Gruppe {i}")
                        cols = st.columns(len(g))
                        for col, name in zip(cols, g):
                            with col:
                                st.write(name)
                                img = find_image(name)
                                if img:
                                    st.image(img, width=100)
                                else:
                                    st.caption("❌ Intet billede")
