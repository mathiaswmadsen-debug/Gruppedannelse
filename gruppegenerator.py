import streamlit as st
import pandas as pd
import random
from collections import defaultdict

st.title("🎲 Tilfældig Gruppegenerator")

st.markdown(
    """
    Upload en CSV med dine studerende (to kolonner: **Navn,Semester**).  
    Vælg hvem der er til stede, indstil gruppestørrelse, og tryk på knappen for at få tilfældige grupper, 
    hvor hvert semester er repræsenteret.
    """
)

# Upload CSV
file = st.file_uploader("Upload CSV", type=["csv"])

if file:
    try:
        # Automatisk detektering af separator (virker til både , og ;)
        df = pd.read_csv(file, sep=None, engine="python")
        # Rens kolonnenavne (fjerner BOM og mellemrum)
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
            # Liste med checkboxes til tilstedeværelse
            st.subheader("✔️ Vælg hvilke studerende der er til stede i dag")
            presence = {}
            for _, row in df.iterrows():
                navn, sem = row["Navn"], row["Semester"]
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

                    # Tilføj evt. resterende studerende
                    if remaining:
                        groups.append([s[0] for s in remaining])

                    # Vis grupperne
                    for i, g in enumerate(groups, 1):
                        st.subheader(f"Gruppe {i}")
                        st.write(", ".join(g))
