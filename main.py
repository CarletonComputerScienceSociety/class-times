# Import beautifulsoup4
from bs4 import BeautifulSoup

# Load the html file from data/comp.html
with open("data/comp.html") as fp:
    soup = BeautifulSoup(fp, "html.parser")

# Find all the courses. A course can be found as a font element with color blue,
# and starting text COMP. The course code is the text of the font element.
#
# Course example:
# <td align="left" width="8%" style="word-wrap: break-word">
#     <a href="bwysched.p_display_course_s?wsea_code=INT&term_code=202310&disp=18134927&crn=11151"
#         target="_blank">
#         <font color="blue">COMP 1005</font>
#     </a>
# </td>
courses = soup.find_all("font", color="blue", text=lambda t: t and t.startswith("COMP"))

# Set up the markdown string. It needs to contain headers for the course,
# professor, and schedule.
readme_markdown_string = """
# COMP Course Times

<!-- *Do not edit this file, it gets generated by main.py* -->

This is a list of all the COMP courses and their times.

The data folder is .gitignored so that you don't commit your student number by
accident. If you want to run this script, you'll need to download the html file
from Carleton Central, probably at the url
`https://central.carleton.ca/prod/bwysched.p_course_search` or something. The
path to get there should be `Registration > Build Your Timetable/Registration >
(select the term) > Proceed to Search > (change subject to COMP) > Search`. Then
download this file and put it in the data folder with the title "comp.html".

## COMP Courses
| Course | Professor | Schedule |
| --- | --- | --- |
"""
readme_markdown_bin = {}

# Set up the GitHub Issue Template markdown string.
issue_template_markdown_string = """---
name: Class advertising checklist
about: For making sure that different classes are advertised to for events.
title: ''
labels: ''
assignees: ''

---

This is a checklist of all the COMP courses and their times. Check off sections
that have been advertised to.

"""
issue_template_markdown_bin = {}

course_list = []
date_list = {}


# Go through each course and get the professor. Professor example:
#
# <td align="left" width="9%">Connor Hillen</td>
#
# Next, get the schedule. Schedule example:
#
# <tr bgcolor="#C0C0C0">
#     <td>&nbsp;</td>
#     <td colspan="15"> <b>Meeting Date:</b> Jan 09, 2023 to Apr 12, 2023 <b>Days:</b> Tue Thu
#         <b>Time:</b> 11:35 - 12:55 <b>Building:</b> Health Science Building <b>Room:</b> 1301</td>
# </tr>
for course in courses:
    # Ignore any grad courses, make sure that the course code is a 4000 level or
    # less.
    if int(course.text.split(" ")[1]) > 5000:
        continue

    # Get the course section
    course_section = course.parent.parent.find_next_sibling("td").text

    # Ignore any tutorials. A tutorial contains a number after the section code.
    # TODO: Add them to a different table?
    if len(course_section) > 1:
        continue

    # Get the professor
    professor = course.parent.parent.parent.findChildren()[-1].text

    # Get the schedule
    schedule_node = course.parent.parent.parent.find_next_sibling("tr")

    # Stripping lambda
    def strip(field):
        text = schedule_node.find("b", text=f"{field}:").next_sibling
        if text == None:
            return "?"

        # Remove any newlines and extra spaces
        text = text.replace("\n", "").strip()
        return text

    days = strip("Days")
    time = strip("Time")
    building = strip("Building")
    room = strip("Room")

    course_string = f"| {course.text} {course_section} | {professor} | {days} {time} {building} {room} |\n"
    course_list.append(course_string)

    if days not in issue_template_markdown_bin:
        issue_template_markdown_bin[days] = []
    issue_template_markdown_bin[days].append(
        [
            course.text,
            course_section,
            professor,
            days,
            time,
            building,
            room,
        ]
    )

    # Add the course, professor, and schedule to the markdown string
    readme_markdown_line = f"| {course.text} {course_section} | {professor} | {days} {time} {building} {room} |\n"
    readme_markdown_string += f"{readme_markdown_line}"
    if days not in readme_markdown_bin:
        readme_markdown_bin[days] = []
    readme_markdown_bin[days].append(readme_markdown_line)

    # # Add the course to the GitHub Issue Template markdown string
    # issue_template_string = f"- [ ] {course.text} {course_section} ({professor}, {days} {time} {building} {room})"
    # # issue_template_markdown_string += f"{issue_template_string}\n"
    # if days not in issue_template_markdown_bin:
    #     issue_template_markdown_bin[days] = []
    # issue_template_markdown_bin[days].append(issue_template_string)


# Write the markdown string to the README.md file
with open("README.md", "w") as fp:
    fp.write(readme_markdown_string)

sorted_days = [
    "Mon",
    "Mon Wed",
    "Tue",
    "Tue Thu",
    "Wed",
    "Wed Fri",
    "Thu",
    "Fri",
]

# Write the markdown string to the
# .github/ISSUE_TEMPLATE/class-advertising-checklist.md file
with open(".github/ISSUE_TEMPLATE/class-advertising-checklist.md", "w") as fp:
    fp.write(issue_template_markdown_string)
    for day in sorted_days:
        if day not in issue_template_markdown_bin:
            continue

        fp.write(f"## {day}\n")
        days_courses = issue_template_markdown_bin[day]
        # Sort by the first time in the time string
        sorted_days = sorted(days_courses, key=lambda x: int(x[4].split(" ")[0].split(":")[0]))
        for course in sorted_days:
            fp.write(f"- [ ] {course[0]} {course[1]} ({course[2]}, {course[4]} {course[5]} {course[6]})\n")
