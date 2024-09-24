from bs4 import BeautifulSoup

# 文件路径
html_file_path = 'Ruizhi.html'

# 读取文件内容
with open(html_file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# 使用BeautifulSoup解析HTML内容
soup = BeautifulSoup(content, 'html.parser')

# 创建集合存储所有授课类型
meeting_types = set()

# 获取所有课程条目
course_items = soup.find_all('div', class_='CourseItem')

# 遍历每个课程条目，提取信息
courses = []

for item in course_items:
    # 获取课程名称
    course_name = item.find('div', class_='classTitle').text.strip()

    # 获取授课信息
    meetings = []
    for meeting in item.find_all('div', class_='meeting'):
        # 提取授课类型
        meeting_type = meeting.find('div', class_='smallTitle').text.strip()
        meeting_types.add(meeting_type)  # 将类型加入集合

        # 提取时间、日期和地点信息
        meeting_time = meeting.find_all('div')[1].text.strip()
        meeting_days = meeting.find_all('div')[2].text.strip()
        meeting_location = meeting.find_all('div')[3].text.strip()

        # 拼接授课信息字符串
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
