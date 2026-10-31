
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:5000/students"

st.set_page_config(page_title="Student Management System")

st.title("Student Management System")

# Retrieve students
def get_students():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    return []

# Display all students
st.header("All Students")

students = get_students()

if students:
    st.dataframe(pd.DataFrame(students), use_container_width=True)
else:
    st.info("No student records found.")

# Add student
st.header("Add New Student")

with st.form("add_student"):
    name = st.text_input("Student Name")
    department = st.text_input("Department")
    email = st.text_input("Email")

    submit = st.form_submit_button("Add Student")

    if submit:
        response = requests.post(API_URL, json={
            "name": name,
            "department": department,
            "email": email
        })

        if response.status_code == 201:
            st.success("Student added successfully!")
            st.rerun()
        else:
            st.error(response.json().get("error", "Unable to add student"))

# Update student
st.header("Update Student")

students = get_students()

if students:
    student_ids = [s["id"] for s in students]

    selected_id = st.selectbox(
        "Select Student ID",
        student_ids
    )

    selected = next(
        s for s in students if s["id"] == selected_id
    )

    with st.form("update_student"):
        new_name = st.text_input("Name", value=selected["name"])
        new_department = st.text_input(
            "Department", value=selected["department"]
        )
        new_email = st.text_input("Email", value=selected["email"])

        update = st.form_submit_button("Update Student")

        if update:
            response = requests.put(
                f"{API_URL}/{selected_id}",
                json={
                    "name": new_name,
                    "department": new_department,
                    "email": new_email
                }
            )

            if response.status_code == 200:
                st.success("Student updated successfully!")
                st.rerun()
            else:
                st.error(response.json().get("error", "Update failed"))

# Delete student
st.header("Delete Student")

students = get_students()

if students:
    delete_id = st.selectbox(
        "Select Student to Delete",
        [s["id"] for s in students],
        key="delete_id"
    )

    if st.button("Delete Student"):
        response = requests.delete(f"{API_URL}/{delete_id}")

        if response.status_code == 200:
            st.success("Student deleted successfully!")
            st.rerun()
        else:
            st.error("Unable to delete student")

# Refresh
if st.button("Refresh Records"):
    st.rerun()
