import requests
from bs4 import BeautifulSoup as bs
import re
import control_bot
import datetime,time
from multiprocessing import Process, Queue

post_ip = [0 for _ in range(2)]#post 전송 시 ip
post_pw = [0 for _ in range(2)]#post 전송 시 pw

my_course_id = [] #과목번호
my_class_no = [] #과목분반
my_corse_name = [] #과목이름
my_corse_num =0 #수강 과목 갯수
ID="" #아이디
PW="" #비번
my_homework = [] #모든 과목의 과제 리스트
my_announcement = []#모든 과목의 공지사항
my_resource = []#모든 자료실 리스트
my_homework_submit = []
login_state=False #로그인 상태
my_name = ""#내이름
my_major="" #내전공

soup=""
s=""
LOGIN_INFO = {
    'user_id':ID,
    'user_password': PW,
    'is_local':'Y',
    'group_cd':'UN',
    'sub_group_cd': ''
}
LOGIN_INFO_2 = {
    'user_id':ID,
    'user_password':post_pw[0],
    'user_ip': post_ip[0],
    'group_cd':'UN',
    'sub_group_cd': ''
}

MY_CLASS_FORM={
    'class_no':"",
    'course_id':"",
    'mnid':  "201008254671"
}
MY_RESOURCE_FORM={
    'mnid':"20100863099",
    'board_no':'6'
}
#과제제출란
HOMEWORK_SUBMIT={
    "req_asp_id": "ASP00001",
    "page":"1",
    "rows":"10000",
    "sidx":"1",
    "sord":"asc",
    "mode": "U",            #동적
    "report_no" : "22523", #동적
    "apply_yn"	: "N",        #동적
    "report_seq": "1",      #동적
    "report_modify_yn":"N", #동적
    "course_id":"201810UN0037733D0000000",  #동적
    "class_no":"00",        #동적
    "ie_version" :"IE10"    #동적
}
#실제 과제제출 폼
REAL_SUBMIT_FORM={
    "mode":"U",
    "req_asp_id":"ASP00001",
    "report_no":"22523",
    "report_seq":"1",
    "course_id":"201810UN0037733D0000000",
    "class_no":"00",
    "file_cnt":"0",
    "report_file_save_nm":"",
    "report_file_nm":"",
    "report_file_size":"",
    "apply_file_save_nm":"",
    "apply_file_nm":"",
    "apply_file_size":"",
    "apply_yn":"N",
    "report_modify_yn":"Y",
    "ucc_url":"",
    "page" : "1",
    "rows" : "10000",
    "sidx" : "1",
    "sord" : "asc",
    "user_id" : "201202166",
    "user_nm":"김인섭",
    "apply_file_yn":"N",
    "ie_version":"IE10",
    "apply_content":"ㅎㅇㅎㅇ"
}
def Login(s): #사이버캠퍼스에 로그인
    global post_ip,post_pw,my_announcement,my_homework,my_resource,my_name,login_state,my_major,soup
    #로그인 폼 전송1
    for key in LOGIN_INFO.keys():
        if key == "user_id":
            LOGIN_INFO[key] = ID
            if key == "user_password":
                LOGIN_INFO[key] = PW
    req = s.post('http://e-learn.cnu.ac.kr/login/doGetUserCountId.dunet', data=LOGIN_INFO)
    try:
        #폼 비번
        splited_pw = req.text.split('user_password":"')
        post_pw= splited_pw[1].split('"')
    except IndexError as e:
        control_bot.bot.sendMessage(chat_id=control_bot.chat_id,text="존재하지 않는 학번입니다.\n")
        login_state=False
        control_bot.resource=""
        control_bot.announcement=""
        control_bot.homework=""
        my_name=""
        my_major=""
        print(e)
        return
    #폼 아이피주소
    splited_ip = req.text.split('client_ip":"')
    post_ip = splited_ip[1].split('"')
    #로그인 폼 전송2
    for key in LOGIN_INFO_2.keys():
        if key == "user_id":
            LOGIN_INFO_2[key] = ID
    s.post('http://e-learn.cnu.ac.kr/login/doLogin.dunet', data=LOGIN_INFO_2)
    login_state=True

def my_name_fuc(s): # 내 이름 파싱
    global my_name
    my_page = s.get('http://e-learn.cnu.ac.kr/lms/myLecture/doListView.dunet?mnid=201008840728')  # 강의목록확인
    soup = bs(my_page.text, 'html.parser')
    my_name_span = soup.find("span", {"class": "login_after"})
    my_name = my_name_span.find("strong").text
    control_bot.name = my_name
    print(my_name)



def my_course_fuc(s): ##강의실 ID 파싱
    global my_corse_num,my_corse_name,my_course_id,my_class_no
    my_page = s.get('http://e-learn.cnu.ac.kr/lms/myLecture/doListView.dunet?mnid=201008840728')  # 강의목록확인
    soup = bs(my_page.text, 'html.parser')
    temp = soup.findAll("a", {"class": "classin2"})
    count = temp.__len__()
    my_corse_num = count
    temp2 = temp.__str__()

    p = re.compile('course.id..\w{23}.')  ##정규포현식 사용
    p2 = re.compile('class_no..\d\d')
    m = p.findall(temp2)
    m2 = p2.findall(temp2)

    name_splited_temp = temp2.split("<br/>")

    # 과목번호, 분반, 과목명을 추출한다.
    for i in range(count):
        my_course_id.append(m[i].split('"')[1])
        my_class_no.append(m2[i].split('"')[1])
        my_corse_name.append(name_splited_temp[i].split('"">')[1].strip())



def my_major_fuc(s): #내 전공 파싱
    global my_major
    my_info_home = s.get("http://e-learn.cnu.ac.kr/lms/front/member/info/doViewMemberInfo.dunet")
    soup = bs(my_info_home.text, 'html.parser')
    my_info = soup.select("#con > table > tbody")
    p = re.compile('부서명..th.\s+.td\scolspan..\d..\w+')
    m3 = p.findall(my_info.__str__())
    my_major = m3[0].split(">")[2] # 내 전공 파싱
    control_bot.major = my_major

def my_all_list(s): #공지,자료실,과제 리스트 모두 가져온다
    # 모든 강의실 접속해서 과제,공지,자료실 내용 가져오기
    for i in range(my_corse_num):
        for key in MY_CLASS_FORM.keys():
            if key == "class_no":
                MY_CLASS_FORM[key] = my_class_no.__getitem__(i)
            if key == "course_id":
                MY_CLASS_FORM[key] = my_course_id.__getitem__(i)
        s.post('http://e-learn.cnu.ac.kr/lms/class/classroom/doViewClassRoom_new.dunet', data=MY_CLASS_FORM)

        # 특정 강의홈 입장
        homework_page = s.get('http://e-learn.cnu.ac.kr/lms/class/classroom/doViewClassRoom_new.dunet')
        soup = bs(homework_page.text, 'html.parser')

        my_homework_list_fuc(soup,my_corse_name.__getitem__(i))
        my_announcement_list_fuc(soup,my_corse_name.__getitem__(i))
        my_resource_list_fuc(s,my_corse_name.__getitem__(i))



def my_announcement_list_fuc(soup,my_corse_name): # 공지 리스트 가져오기

    announcement_table = soup.find_all('table', {'class': 'datatable fs_s bo_lrn'})[1]
    announcement_table_body = announcement_table.find('tbody')
    rows = announcement_table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        cols.insert(0, my_corse_name)
        my_announcement.append([ele for ele in cols if ele])  # Get rid of empty values

def my_resource_list_fuc(s,my_corse_name):  # 자료실입장해서 리스트 가져오기

    resorce_page = s.post("http://e-learn.cnu.ac.kr/lms/class/boardItem/doListView.dunet", data=MY_RESOURCE_FORM)
    soup = bs(resorce_page.text, 'html.parser')
    resorce_page_table = soup.find('table', {'class': 'list'})
    resorce_page_tbody = resorce_page_table.find('tbody')
    rows = resorce_page_tbody.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        cols.insert(0, my_corse_name)
        my_resource.append([ele for ele in cols if ele])  # Get rid of empty values

def my_homework_list_fuc(soup,my_corse_name): #내 모든 과제 내용 파싱
        # 과제제출란 입장
        # submit_homework_page = s.get("http://e-learn.cnu.ac.kr/lms/class/report/stud/doListView.dunet")
        # submit = s.post("http://e-learn.cnu.ac.kr/lms/class/report/stud/doFormReport.dunet", data = HOMEWORK_SUBMIT)
        # gg = s.post("http://e-learn.cnu.ac.kr/lms/class/report/stud/doModifyReport.dunet",data=REAL_SUBMIT_FORM)
        # soup2 = bs(gg.text, 'html.parser')
        # print(soup2)

        # 과제 리스트 가져오기
        homework_table = soup.find('table', {'class': 'datatable mg_t15'})
        homework_table_body = homework_table.find('tbody')
        rows = homework_table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            cols.insert(0, my_corse_name)
            my_homework.append([ele for ele in cols if ele]) # Get rid of empty values




def equals_announement(ai): #공지사항 과목 중복 비교
    count=0
    for i in range(ai):
        if my_announcement[i][0] == my_announcement[ai][0]:
            count=count+1
    return count

def equals_resource(ai): #자료실 과목 중복 비교
    count=0
    for i in range(ai):
        if my_resource[i][0] == my_resource[ai][0]:
            count=count+1
    return count

def my_all_homework_fuc(): #내 과제 정렬
    my_all_homework=""
    for i in range(my_homework.__len__()):
        for j in range(my_homework[i].__len__()):
            if my_homework[i].__len__() == 6:
                if ongoing_homework(my_homework.__getitem__(i)[4]): # 과제제출이 진행중이면
                    if j == 0:
                        my_all_homework = my_all_homework + "\n♥" + my_homework.__getitem__(i)[j] + "\n"
                    elif j == 2:
                        my_all_homework = my_all_homework + "\b-\b" + my_homework.__getitem__(i)[j] + "\b"
                    elif j == 3:
                        my_all_homework = my_all_homework + "[" + my_homework.__getitem__(i)[j] + "~"
                    elif j == 4:
                        my_all_homework = my_all_homework + my_homework.__getitem__(i)[j] + "]"
                    elif j == 5:
                        my_all_homework = my_all_homework + "\b_(" + my_homework.__getitem__(i)[j] + ")\n"
            else:
                if ongoing_homework(my_homework.__getitem__(i)[3]):  # 과제제출이 진행중이면
                    if j == 0:
                        my_all_homework = my_all_homework + "\n♥" + my_homework.__getitem__(i)[j] + "\n"
                    elif j == 1:
                        my_all_homework = my_all_homework + "\b-\b" + my_homework.__getitem__(i)[j] + "\b"
                    elif j == 2:
                        my_all_homework = my_all_homework + "[" + my_homework.__getitem__(i)[j] + "~"
                    elif j == 3:
                        my_all_homework = my_all_homework + my_homework.__getitem__(i)[j] + "]"
                    elif j == 4:
                        my_all_homework = my_all_homework + "\b_(" + my_homework.__getitem__(i)[j] + ")\n"
    if my_all_homework =="":
        my_all_homework="\n※과제가 없습니다.\n"
    control_bot.homework = my_all_homework
    my_all_homework=""

def my_all_announcement_fuc(): #내 공지 정렬
    my_all_announcement=""
    for i in range(my_announcement.__len__()):
        if my_announcement.__getitem__(i).__len__()==3:
            if latest_date(my_announcement.__getitem__(i)[2],7):
                for j in range(3):
                    count = equals_announement(i)# 공지 과목이름중복 체크
                    if count is 0:
                        if j == 0:
                            my_all_announcement = my_all_announcement + "\n♥" + my_announcement.__getitem__(i)[j] + "\n"
                        elif j == 1:
                            my_all_announcement = my_all_announcement + "\b-\b" + my_announcement.__getitem__(i)[j]
                    elif j == 1:
                        my_all_announcement = my_all_announcement + "\b-\b" + my_announcement.__getitem__(i)[j]
                    if j == 2:
                        if latest_date(my_announcement.__getitem__(i)[j],0):
                            my_all_announcement = my_all_announcement + "\b[" + my_announcement.__getitem__(i)[j]  + "]★TODAY★\n"
                        elif latest_date(my_announcement.__getitem__(i)[j],2):
                            my_all_announcement = my_all_announcement + "\b[" + my_announcement.__getitem__(i)[j]  + "]★UP★\n"
                        else:
                            my_all_announcement = my_all_announcement + "\b[" + my_announcement.__getitem__(i)[j] + "]\n"
    if my_all_announcement =="":
        my_all_announcement="\n※공지가 없습니다.\n"
    control_bot.announcement = my_all_announcement
    my_all_announcement=""

def my_all_resource_fuc(): #내 자료실 정렬
    my_all_resource=""
    p= re.compile("\s{56}")
    for i in range(my_resource.__len__()):
        if my_resource.__getitem__(i).__len__()==7:
            for j in range(7):
                if latest_date(my_resource.__getitem__(i)[5],7):
                    count = equals_resource(i)
                    if count == 0 and j==0 : # 과목 이름 맨 첫번째면
                        my_all_resource = my_all_resource +"\n♥" + my_resource.__getitem__(i)[j]+"\n"
                    elif j==2:
                        if p.search(my_resource.__getitem__(i)[j]) is not None:
                            my_resource.__getitem__(i)[j]=re.split('\s{56}',my_resource.__getitem__(i)[j])[0]
                        my_all_resource = my_all_resource +"\b-\b"+ my_resource.__getitem__(i)[j]
                    elif j==5:
                        if latest_date(my_resource.__getitem__(i)[j],0):
                            my_all_resource = my_all_resource + "\b[" + my_resource.__getitem__(i)[j] + "]★TODAY★\n"
                        elif latest_date(my_resource.__getitem__(i)[j],2):
                            my_all_resource = my_all_resource + "\b[" + my_resource.__getitem__(i)[j] + "]★UP★\n"
                        else:
                            my_all_resource = my_all_resource + "\b[" + my_resource.__getitem__(i)[j] + "]\n"
                        '''
        if my_resource.__getitem__(i).__len__()==6:
            my_all_resource = my_all_resource + "\b└Re." + my_resource.__getitem__(i)[1]
            if latest_date(my_resource.__getitem__(i)[4]):
                my_all_resource = my_all_resource + "\b[" + my_resource.__getitem__(i)[4] + "]★NEW★\n"
            else:
                my_all_resource = my_all_resource + "\b[" + my_resource.__getitem__(i)[4] + "]\n"'''
    for i in range(my_resource.__len__()):
        print(my_resource.__getitem__(i))
    print("")
    if my_all_resource =="":
        my_all_resource="\n※자료가 없습니다.\n"
    control_bot.resource = my_all_resource
    my_all_resource=""

def latest_date(date,start): #start만큼의 기간동안 공지, 자료실에 대한 내용을 보여준다.
    date_array = date.split(".")
    yy = int(date_array[0])
    mm = int(date_array[1])
    dd = int(date_array[2])
    date= datetime.date(yy,mm,dd)
    date_gap = datetime.date.today()-date
    if  date_gap.days <= start:
        return True
    else:
        return False


def ongoing_homework(date_end):  #현재 진행중인 과제 표시

    date_end_array = date_end.split(".")

    date_end=""
    for i in range(3):
        date_end = date_end + date_end_array[i]
    end_date = int(date_end)
    now_date = int(time.strftime("%Y%m%d"))
    if now_date <= end_date:
        return True
    else:
        return False
def initialization():
    global  my_course_id, my_class_no,my_corse_name, my_corse_num, ID  , PW , my_homework , my_announcement  , my_resource   , my_homework_submit ,my_name   , my_major , soup ,  s

    my_course_id = []  # 과목번호
    my_class_no = []  # 과목분반
    my_corse_name = []  # 과목이름
    my_corse_num = 0  # 수강 과목 갯수
    ID = ""  # 아이디
    PW = ""  # 비번
    my_homework = []  # 모든 과목의 과제 리스트
    my_announcement = []  # 모든 과목의 공지사항
    my_resource = []  # 모든 자료실 리스트
    my_homework_submit = []
    my_name = ""  # 내이름
    my_major = ""  # 내전공
    soup = ""
    s = ""
def start_bot():
    control_bot.contol_main()  # 봇 실행

def creat_session():
    # 세션 생성

    global s
    with requests.Session() as s:
        Login(s)  # 사이버캠퍼스에 로그인

        my_name_fuc(s) #내 이름 파싱
        my_course_fuc(s) #내 과목분반,과목id,과목이름 파싱
        my_major_fuc(s)# 개인정보홈 입장
        my_all_list(s) # 내 공지,자료,과제 리스트 파싱

        my_all_homework_fuc()
        my_all_announcement_fuc()
        my_all_resource_fuc()

        initialization()

if __name__ == "__main__":
    start_bot() #봇 시작
    #result = Queue()

    #print(result.qsize())

    #print("z")

