import streamlit as st
import pandas as pd
import random
from collections import defaultdict
import os

st.title("🎲 Tilfældig Gruppegenerator med billeder")

st.markdown(
    """
    Upload en CSV med dine studerende (to kolonner: **Navn,Semester**).  
    Sørg for at du har en mappe kaldet **billeder/** med et billede til hver studerende, 
    hvor filnavnet matcher navnet i CSV (fx *Anders.jpg*).
    """
)

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

            image_folder = "billeder"  # mappe med billeder
            presence = {}

            for _, row in df.iterrows():
                navn, sem = row["Navn"], row["Semester"]
                col1, col2 = st.columns([1, 3])

                with col1:
                    image_path = os.path.join(image_folder, f"{navn}.jpg")
                    if os.path.exists(image_path):
                        st.image(image_path, width=80)
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
                                image_path = os.path.join(image_folder, f"{name}.jpg")
                                if os.path.exists(image_path):
                                    st.image(image_path, width=100)
