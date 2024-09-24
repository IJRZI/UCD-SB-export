from bs4 import BeautifulSoup#好用
import pytz
from icalendar import Calendar, Event
from datetime import datetime, timedelta










start_date = datetime(2024, 9, 25)
end_date = datetime(2024, 12, 8)









def find_content_in_file(file_path, target_content):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            position = content.find(target_content)
            if position!= -1:
                new_content = content[:position + len(target_content)]
                with open(file_path, 'w') as new_file:
                    new_file.write(new_content)
                print(f"在文件 {file_path} 中找到 '{target_content}'，并已删除其出现后的所有文字。")

    except FileNotFoundError:
        print(f"文件 {file_path} 不存在。")

file_path = "Schedule Builder.html"
target_content = "Previously Saved Courses"
find_content_in_file(file_path, target_content)












html_file_path = 'Schedule Builder.html'
#读入文件
with open(html_file_path, 'r', encoding='utf-8') as file:
    content = file.read()

soup = BeautifulSoup(content, 'html.parser')#解析html

meeting_types = set()#课程类型
course_items = soup.find_all('div', class_='CourseItem')
#遍历课程
courses = []
for item in course_items:
    # 找名称
    course_name = item.find('div', class_='classTitle').text.strip()

    # 找信息
    meetings = []
    for meeting in item.find_all('div', class_='meeting'):
        # 提取授课类型
        meeting_type = meeting.find('div', class_='smallTitle').text.strip()
        meeting_types.add(meeting_type)  # 将类型加入集合

        # 时间日期地点
        meeting_time = meeting.find_all('div')[1].text.strip()
        meeting_days = meeting.find_all('div')[2].text.strip()
        meeting_location = meeting.find_all('div')[3].text.strip()

        # 拼接 授课信息字符串
        meetings.append(f"{meeting_type}: {meeting_days} {meeting_time} at {meeting_location}")
    # 将课程信息加入列表
    courses.append({
        'Course Name': course_name,
        'Meeting Info': '\n'.join(meetings),
    })

# 将课程信息输出到文件
with open('course_info.txt', 'w', encoding='utf-8') as output_file:
    for course in courses:
        output_file.write(f"Course Name: {course['Course Name']}\n")
        output_file.write(f"Meeting Info:\n{course['Meeting Info']}\n")
        output_file.write("-" * 40 + '\n')

# 将所有授课类型输出到另一个文件，每行一个类型
with open('meeting_types.txt', 'w', encoding='utf-8') as meeting_file:
    for meeting_type in sorted(meeting_types):  # 使用sorted将类型排序输出
        meeting_file.write(f"{meeting_type}\n")













def weeks_between_dates(start_date, end_date):
    # 计算两个日期之间的天数
    delta = end_date - start_date
    # 计算完整的周数
    full_weeks = delta.days // 7
    return full_weeks


# 计算两日期间的完整周数
full_weeks = weeks_between_dates(start_date, end_date)

# 日期缩写转换
day_map = {'M': 'MO', 'T': 'TU', 'W': 'WE', 'R': 'TH', 'F': 'FR'}
# 从文件中读取课程类型
def read_meeting_types(meeting_types_file):
    with open(meeting_types_file, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]


def create_ics_from_txt(input_file, meeting_types_file, output_file, start_date, end_date):
    calendar = Calendar()
    timezone = pytz.timezone("America/Los_Angeles")

    # 读取课程类型
    meeting_types = read_meeting_types(meeting_types_file)

    with open(input_file, 'r') as file:
        lines = file.readlines()

    course_name = ""
    for line in lines:
        line = line.strip()

        # 解析课程名称
        if line.startswith("Course Name:"):
            course_name = line.split(":", 1)[1].strip()
            continue

        # 解析课程安排
        if any(line.startswith(f"{meeting_type}:") for meeting_type in meeting_types):
            meeting_info = line.split(":", 1)[1].strip()

            try:
                # 尝试解析课程类型和时间
                details, location = meeting_info.split(" at ")
                days, time_range = details.split(" ", 1)
                start_time, end_time = [datetime.strptime(t.strip(), "%I:%M %p") for t in time_range.split("-")]

                # 根据开始和结束日期创建事件
                current_date = start_date
                while current_date <= end_date:
                    # 检查当前日期是否为指定的某天
                    if any(current_date.strftime("%a").upper().startswith(day_map[day]) for day in days):
                        event = Event()
                        event.add("summary", f"{course_name} - {line.split(':')[0]}")
                        event.add("dtstart", timezone.localize(datetime.combine(current_date, start_time.time())))
                        event.add("dtend", timezone.localize(datetime.combine(current_date, end_time.time())))
                        event.add("location", location)
                        calendar.add_component(event)
                    current_date += timedelta(days=1)
            except ValueError:
                print()
    # 将日历内容保存到ICS文件中
    with open(output_file, 'wb') as f:
        f.write(calendar.to_ical())


# txt_file 是输入文件，包含课程信息的txt文件路径
# meeting_types_file 是输入文件，包含所有课程类型的txt文件路径
# ics_file 是输出文件，生成的ICS文件路径
# start_date 和 end_date 分别是课程的起始和结束日期，格式为 "YYYY-MM-DD"
txt_file = "course_info.txt"
meeting_types_file = "meeting_types.txt"
ics_file = "course_schedule.ics"

create_ics_from_txt(txt_file, meeting_types_file, ics_file, start_date, end_date)








