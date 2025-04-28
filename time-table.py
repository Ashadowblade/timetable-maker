import streamlit as st
import pandas as pd
import random
import io

st.title("🗓️ Teacher Timetable Maker")

# Constants
subjects_list = [
    "English", "Maths", "Social Studies", "Biology", "PhysicsChemistry",
    "Telugu", "Hindi", "Computers", "ArtCraft", "Music", "Sports", "Dance", "Yoga"
]

exclude_class_teacher_subjects = [
    "Telugu", "Hindi", "ArtCraft", "Computers", "Music", "Sports", "Dance", "Yoga"
]

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
periods_per_day = 9
teaching_periods_per_day = 6

# Step 1: Input teachers and their assigned rooms
teachers_data = {}

for subject in subjects_list:
    st.subheader(f"Assign Teachers for {subject}")
    teacher_names = st.text_input(f"Enter teachers for {subject} (comma separated)", key=f"teacher_{subject}").split(',')

    for teacher in teacher_names:
        teacher = teacher.strip()
        if teacher:
            rooms = st.text_input(f"Enter rooms visited by {teacher} for {subject} (comma separated)", key=f"rooms_{subject}_{teacher}").split(',')
            rooms = [room.strip() for room in rooms if room]
            if subject not in teachers_data:
                teachers_data[subject] = []
            teachers_data[subject].append({
                'teacher': teacher,
                'rooms': rooms
            })

st.divider()

# Step 2: Generate Timetable
generate = st.button("Generate Timetable (Excel Only)")

if generate:
    # Prepare the full timetable as a list of dicts
    timetable_entries = []

    for subject, teacher_list in teachers_data.items():
        for teacher_info in teacher_list:
            teacher = teacher_info['teacher']
            rooms = teacher_info['rooms']

            is_class_teacher = subject not in exclude_class_teacher_subjects
            class_teacher_room = rooms[0] if is_class_teacher and rooms else None

            for day in days_of_week:
                available_periods = list(range(1, periods_per_day + 1))
                day_schedule = []

                # Assign first period for class teachers
                if class_teacher_room:
                    day_schedule.append({
                        'Day': day,
                        'Period': 1,
                        'Teacher': teacher,
                        'Subject': subject,
                        'Room': class_teacher_room,
                        'Type': 'Class Teacher'
                    })
                    available_periods.remove(1)

                # Remaining periods
                teaching_needed = 6 if subject not in ["Music", "Dance", "ArtCraft", "Yoga"] else 1
                if subject == "Sports":
                    teaching_needed = 2  # 2 classes per week for Sports

                periods_to_assign = random.sample(available_periods, min(teaching_needed, len(available_periods)))

                for period in periods_to_assign:
                    # Special handling for Sports periods (not 1-3 or 9)
                    if subject == "Sports" and period in [1, 2, 3, 9]:
                        continue

                    assigned_room = random.choice(rooms) if rooms else "No Room"
                    day_schedule.append({
                        'Day': day,
                        'Period': period,
                        'Teacher': teacher,
                        'Subject': subject,
                        'Room': assigned_room,
                        'Type': 'Normal'
                    })

                # Fill leisure periods
                scheduled_periods = [entry['Period'] for entry in day_schedule]
                leisure_periods = [p for p in range(1, periods_per_day + 1) if p not in scheduled_periods]

                for period in leisure_periods:
                    day_schedule.append({
                        'Day': day,
                        'Period': period,
                        'Teacher': teacher,
                        'Subject': "Leisure",
                        'Room': "-",
                        'Type': 'Leisure'
                    })

                # Sort periods properly
                day_schedule = sorted(day_schedule, key=lambda x: x['Period'])

                timetable_entries.extend(day_schedule)

    # Create a DataFrame
    df = pd.DataFrame(timetable_entries)

    # Create an Excel file in memory
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Timetable")
        
        workbook = writer.book
        worksheet = writer.sheets['Timetable']

        # Define formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#DDEBF7', 'border': 1})
        class_teacher_format = workbook.add_format({'bg_color': '#C9DAF8'})
        leisure_format = workbook.add_format({'bg_color': '#F2F2F2'})
        normal_format = workbook.add_format({'bg_color': '#FFFFFF'})

        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Apply color formatting based on Type
        for row_num, type_value in enumerate(df['Type'], start=1):
            if type_value == 'Class Teacher':
                worksheet.set_row(row_num, cell_format=class_teacher_format)
            elif type_value == 'Leisure':
                worksheet.set_row(row_num, cell_format=leisure_format)
            else:
                worksheet.set_row(row_num, cell_format=normal_format)

    excel_file.seek(0)

    # Offer download
    st.download_button(
        label="📥 Download Timetable (Excel)",
        data=excel_file,
        file_name="teacher_timetable.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
