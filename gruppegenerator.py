import streamlit as st
import pandas as pd
import random
from collections import defaultdict

st.title("🎲 Tilfældig Gruppegenerator")

st.markdown(
    """
    Upload en CSV med dine studerende (to kolonner: **Navn,Semester**).  
    Vælg gruppestørrelse og tryk på knappen for at få tilfældige grupper, 
    hvor hvert semester er repræsenteret.
    """
)

# Upload CSV
file = st.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
    if not {"Navn", "Semester"}.issubset(df.columns):
        st.error("CSV skal indeholde kolonnerne 'Navn' og 'Semester'")
    else:
        students = [(row["Navn"], row["Semester"]) for _, row in df.iterrows()]

        group_size = st.number_input(
            "Hvor mange personer pr. gruppe?", min_value=2, max_value=10, value=3
        )

        if st.button("Lav grupper"):
            random.shuffle(students)

            by_semester = defaultdict(list)
            for name, sem in students:
                by_semester[sem].append(name)

            groups = []
            remaining = students.copy()

            while all(by_semester.values()):
                group = []
                # Tag én fra hvert semester
                for sem in list(by_semester.keys()):
                    if by_semester[sem]:
                        group.append(by_semester[sem].pop())
                        # Fjern også fra remaining
                        remaining = [s for s in remaining if s[0] != group[-1]]
                # Fyld op hvis nødvendigt
                while len(group) < group_size and remaining:
                    name, _ = remaining.pop()
                    group.append(name)
                groups.append(group)

            # Hvis der er rester tilbage
            if remaining:
                groups.append([s[0] for s in remaining])

            # Vis grupperne
            for i, g in enumerate(groups, 1):
                st.subheader(f"Gruppe {i}")
                st.write(", ".join(g))
