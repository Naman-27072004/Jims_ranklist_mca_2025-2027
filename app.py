import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="MCA Result Processing System",
    layout="wide"
)

st.title("🎓 MCA Result Processing & Analytics System")
st.caption("Based on official grading & examination scheme")


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_excel("Result.xlsx")


df = load_data()

# -----------------------------
# SUBJECT COLUMNS
# -----------------------------
subject_cols = [101, 103, 105, 107, 109,
                161, 163, 165, 167, 169, 171]

# -----------------------------
# CREDITS (FROM SCHEME OF EXAMINATION)
# -----------------------------
CREDITS = {
    101: 4,
    103: 3,
    105: 3,
    107: 3,
    109: 3,
    161: 1,
    163: 1,
    165: 1,
    167: 1,
    169: 3,
    171: 1
}

SUBJECT_NAMES = {
    101: "Discrete Structures",
    103: "Computer Networks",
    105: "Operating Systems with Linux",
    107: "Database Management Systems",
    109: "Object Oriented Programming with Java",
    161: "Computer Networks Lab",
    163: "Operating Systems Lab",
    165: "DBMS Lab",
    167: "OOP with Java Lab",
    169: "Minor Project – I",
    171: "Professional Proficiency – I"
}

# -----------------------------
# CLEAN MARKS (HANDLE AB / TEXT)
# -----------------------------
for col in subject_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)


# -----------------------------
# GRADE & GRADE POINT LOGIC
# -----------------------------
def grade_and_point(marks):
    if marks >= 90:
        return "O", 10
    elif marks >= 75:
        return "A+", 9
    elif marks >= 65:
        return "A", 8
    elif marks >= 55:
        return "B+", 7
    elif marks >= 50:
        return "B", 6
    elif marks >= 45:
        return "C", 5
    elif marks >= 40:
        return "P", 4
    else:
        return "F", 0


# -----------------------------
# APPLY GRADES
# -----------------------------
for col in subject_cols:
    df[f"{col}_Grade"] = df[col].apply(lambda x: grade_and_point(x)[0])
    df[f"{col}_GP"] = df[col].apply(lambda x: grade_and_point(x)[1])


# -----------------------------
# SGPA CALCULATION
# SGPA = Σ(Ci × Gi) / ΣCi
# -----------------------------
def calculate_sgpa(row):
    total_ci_gi = 0
    total_credits = 0

    for sub in subject_cols:
        credit = CREDITS[sub]
        gp = row[f"{sub}_GP"]
        total_ci_gi += credit * gp
        total_credits += credit

    return round(total_ci_gi / total_credits, 2)


df["SGPA"] = df.apply(calculate_sgpa, axis=1)
df["CGPA"] = df["SGPA"]  # Single semester

# -----------------------------
# PASS / FAIL
# -----------------------------
df["Result"] = df[[f"{s}_GP" for s in subject_cols]] \
    .min(axis=1) \
    .apply(lambda x: "PASS" if x >= 4 else "FAIL")

# -----------------------------
# RANK SYSTEM
# -----------------------------
df["Rank"] = df["SGPA"].rank(ascending=False, method="dense").astype(int)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("🔍 Student Search")

student_name = st.sidebar.selectbox(
    "Search Student by Name",
    options=sorted(df["Name"].unique())
)

student_df = df[df["Name"] == student_name].iloc[0]

# -----------------------------
# STUDENT SUMMARY
# -----------------------------
st.subheader("📄 Student Academic Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Roll No", student_df["Roll No"])
c2.metric("Name", student_df["Name"])
c3.metric("SGPA", student_df["SGPA"])
c4.metric("Rank", student_df["Rank"])

st.markdown(
    f"### Result Status: "
    f"{'🟢 PASS' if student_df['Result'] == 'PASS' else '🔴 FAIL'}"
)

# -----------------------------
# SUBJECT-WISE TABLE
# -----------------------------
st.subheader("📚 Subject-wise Performance")

subject_table = []

for sub in subject_cols:
    subject_table.append({
        "Subject Code": sub,
        "Subject Name": SUBJECT_NAMES[sub],
        "Marks": student_df[sub],
        "Grade": student_df[f"{sub}_Grade"],
        "Grade Point": student_df[f"{sub}_GP"],
        "Credits": CREDITS[sub]
    })

st.dataframe(pd.DataFrame(subject_table), use_container_width=True)

# -----------------------------
# CLASS ANALYTICS
# -----------------------------
st.subheader("🏫 Class Analytics")

fail_counts = {
    SUBJECT_NAMES[sub]: (df[f"{sub}_GP"] == 0).sum()
    for sub in subject_cols
}

st.dataframe(
    pd.DataFrame.from_dict(
        fail_counts,
        orient="index",
        columns=["Fail Count"]
    )
)

# -----------------------------
# OVERALL TOPPER LIST
# -----------------------------
st.subheader("🏆 Overall Topper List (SGPA Rank-wise)")

topper_df = df.sort_values(
    by=["SGPA", "Name"],
    ascending=[False, True]
).reset_index(drop=True)

topper_df["Overall Rank"] = topper_df.index + 1

st.dataframe(
    topper_df[[
        "Overall Rank",
        "Roll No",
        "Name",
        "SGPA",
        "CGPA",
        "Result"
    ]],
    use_container_width=True
)

# -----------------------------
# SUBJECT-WISE TOPPER LIST
# -----------------------------
st.subheader("📚 Subject-wise Topper List")

selected_subject = st.selectbox(
    "Select Subject",
    options=subject_cols,
    format_func=lambda x: f"{x} - {SUBJECT_NAMES[x]}"
)

subject_topper_df = df.sort_values(
    by=[selected_subject, "Name"],
    ascending=[False, True]
).reset_index(drop=True)

subject_topper_df["Subject Rank"] = subject_topper_df.index + 1

st.dataframe(
    subject_topper_df[[
        "Subject Rank",
        "Roll No",
        "Name",
        selected_subject,
        f"{selected_subject}_Grade"
    ]].rename(columns={
        selected_subject: "Marks",
        f"{selected_subject}_Grade": "Grade"
    }),
    use_container_width=True
)

