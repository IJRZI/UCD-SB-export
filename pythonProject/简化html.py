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


from bs4 import BeautifulSoup#好用

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

