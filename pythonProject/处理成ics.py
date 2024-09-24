from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event

# 日期缩写转换
day_map = {'M': 'MO', 'T': 'TU', 'W': 'WE', 'R': 'TH', 'F': 'FR'}

# 处理在线讲座的特殊情况
def handle_virtual_lecture(course_name, description, start_date, end_date):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    current_date = start_datetime

    # 查找该周的星期天作为在线讲座记录时间
    while current_date <= end_datetime:
        if current_date.weekday() == 6:  # 6表示星期天
            event = Event()
            event.add("summary", f"{course_name} - World Wide Web Virtual Lecture")
            event.add("dtstart", pytz.timezone("America/Los_Angeles").localize(current_date))
            event.add("dtend", pytz.timezone("America/Los_Angeles").localize(current_date + timedelta(days=1)))
            event.add("description", description)
            event.add("location", "Online")
            return event
        current_date += timedelta(days=1)

# 处理没有时间安排的课程
def handle_no_time_schedule(course_name, description, start_date, end_date):
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    event = Event()
    event.add("summary", course_name)
    event.add("dtstart", start_datetime)
    event.add("dtend", start_datetime + timedelta(days=1))  # 全天事件
    event.add("description", description)
    event.add("location", "Location: Not Specified")
    return event

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

            # 处理在线讲座
            if line.startswith("World Wide Web Virtual Lecture:"):
                virtual_event = handle_virtual_lecture(course_name, meeting_info, start_date, end_date)
                if virtual_event:
                    calendar.add_component(virtual_event)
                continue

            try:
                # 尝试解析课程类型和时间
                details, location = meeting_info.split(" at ")
                days, time_range = details.split(" ", 1)
                start_time, end_time = [datetime.strptime(t.strip(), "%I:%M %p") for t in time_range.split("-")]

                # 根据开始和结束日期创建事件
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

                current_date = start_datetime
                while current_date <= end_datetime:
                    if any(day_map[day] in current_date.strftime("%a").upper()[:2] for day in days):
                        event = Event()
                        event.add("summary", f"{course_name} - {line.split(':')[0]}")
                        event.add("dtstart", timezone.localize(datetime.combine(current_date, start_time.time())))
                        event.add("dtend", timezone.localize(datetime.combine(current_date, end_time.time())))
                        event.add("location", location)
                        #event.add("description", f"Course Type: {line.split(':')[0]}\nLocation: {location}")
                        calendar.add_component(event)
                    current_date += timedelta(days=1)
            except ValueError:
                # 如果解析失败，创建没有时间安排的事件
                no_time_event = handle_no_time_schedule(course_name, meeting_info, start_date, end_date)
                calendar.add_component(no_time_event)

    # 将日历内容保存到ICS文件中
    with open(output_file, 'wb') as f:
        f.write(calendar.to_ical())

# 使用示例：
# txt_file 是输入文件，包含课程信息的txt文件路径
# meeting_types_file 是输入文件，包含所有课程类型的txt文件路径
# ics_file 是输出文件，生成的ICS文件路径
# start_date 和 end_date 分别是课程的起始和结束日期，格式为 "YYYY-MM-DD"
txt_file = "course_info.txt"
meeting_types_file = "meeting_types.txt"
ics_file = "course_schedule.ics"
start_date = "2024-09-25"
end_date = "2024-12-08"
create_ics_from_txt(txt_file, meeting_types_file, ics_file, start_date, end_date)
