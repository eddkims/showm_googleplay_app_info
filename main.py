import os
import sys
import re
import time
import ctypes
import subprocess
import datetime
from datetime import timedelta, date
import configparser
from time import gmtime
try :
    from google_play_scraper import app, reviews, Sort
except ImportError:
    subprocess.run(['python', '-m', 'pip', 'install', '--upgrade', 'google_play_scraper'])
    from google_play_scraper import reviews, Sort

try:
    from scode.util import *
except ImportError:
    subprocess.run(['python', '-m', 'pip', 'install', '--upgrade', 'scode'])
    from scode.util import *

from scode.paramiko import *

# ===============================================================================
#                               Definitions
# ===============================================================================
debug = False
config = configparser.ConfigParser()

try :
    config.read('dev.txt',encoding='cp949')
    if config['DEFAULT']['date'] == '' :
        time_delta = 60
    else:
        time_delta = int(config['DEFAULT']['date'])
except Exception as e  :
    print(f'dev.txt 파일이 없거나, 파일 내에 데이터가 입력 되지 않았습니다. 확인 후 다시 실행 해주세요. Error : {e}')
    sys.exit()


def err_logging(input_data, program_title=None, path='./error.txt'):
    '''
    Write error_log in 'error.txt'
    If raise error, Send telegram message
    '''
    import sys
    import os
    import re
    from datetime import datetime
    import requests
    try:
        import telegram as tel
    except:
        os.system('pip install python-telegram-bot')
    # Send result message
    telegram_send_message = ''
    error_str = ''

    if '__title__' in globals():
        telegram_send_message += f'프로그램명 : {__title__}\n'
    else:
        if program_title == None:
            pwd = os.getcwd()
            program_title = pwd.split('\\')[-1]
            telegram_send_message += f'프로그램명 : {program_title}\n'
        else:
            telegram_send_message += f'프로그램명 : {program_title}\n'

    try:
        ip_check = requests.get('https://wkwk.kr/ip/')
        ip_address = ip_check.text
        ip_check.close()
    except:
        ip_address = 'None("https://wkwk.kr/ip/"와 연결이 되지 않아 ip를 확인 할 수 없습니다.)'
    telegram_send_message += f'IP : {ip_address}\n'

    # Get now datetime
    now = datetime.now().strftime('%y-%m-%d %H:%M:%S')
    error_str += f'------------------------{now}------------------------\n'
    if not isinstance(input_data,(list,dict)):
        raise Exception('Input_data type error : "input_data" is not list and not dict')

    # if input_data is list
    if isinstance(input_data,list):
        for data_dict in input_data:
            for data_key, data_value in data_dict.items():
                error_str += f'{data_key} : {data_value}\n'
                telegram_send_message += f'{data_key} : {data_value}\n'
    # if input_data is dict
    elif isinstance(input_data,dict):
        for data_key, data_value in input_data.items():
            error_str += f'{data_key} : {data_value}\n'
            telegram_send_message += f'{data_key} : {data_value}\n'

    # Get error script
    error_flag = sys.exc_info()
    if isinstance(error_flag,tuple):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        prob_file = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        prob_line_num = exc_tb.tb_lineno
        err_class = re.search("'.*'",str(exc_type).split(' ')[1]).group()
        err_script = str(exc_obj)
    else:
        prob_file = 'None'
        prob_line_num = 'None'
        err_class = 'It is not Error'
        err_script = 'It is not Error'

    error_str += f'Problem_File : {prob_file}\n'
    error_str += f'Problem_Line_Number : {prob_line_num}\n'
    error_str += f'Error_Class : {err_class}\n'
    error_str += f'Error_Script : {err_script}\n'

    telegram_send_message += f'Error_Class : {err_class}\n'
    telegram_send_message += f'Error_Script : {err_script}\n'
    telegram_send_message += f'Problem_Line_Number : {prob_line_num}\n'

    # Write error_log
    try:
        with open(path,'a',encoding='cp949') as err_f:
            err_f.write(error_str)
    except UnicodeEncodeError:
        with open(path,'a',encoding='utf-8') as err_f:
            err_f.write(error_str)
    
def change_date_form(review_date):
    try :

        result_date = datetime.datetime.strftime(review_date,'%Y-%m-%d')
        result =  int(re.sub(r'[^0-9]', '', result_date))

    except Exception as e :
        err_string = f'error : {e}'
        print(err_string)
        input_data = {'reason' : err_string}
        err_logging(input_data)

    return result

def count_receive_reply(review_all,someday_ago):

    cnt = 0
    no_review_cnt = 0

    for review in review_all :
        review_date = review['at']
        
        result = change_date_form(review_date)
        
        if result < someday_ago : # 6개월이 지나면 break
            break
        if review['replyContent'] == None : # 답글이 없으면 카운트
            no_review_cnt += 1
        cnt += 1
        if debug : print(result)

    return cnt,no_review_cnt
        
    
    

def run():
    
    input_file_path = 'input.txt'
    output_file_path = 'output1.txt'
    output2_file_path = 'output2.txt'
    error_file_path = 'error.txt'
    remove_file_path = 'remove.txt'
    
    # Inintialize
    open(output_file_path, 'w').close()
    open(output2_file_path, 'w').close()
    open(remove_file_path, 'w').close()

    try:
        input_lst = [x.strip() for x in open(input_file_path).read().splitlines()]
    except UnicodeDecodeError:
        try:
            input_lst = [x.strip() for x in open(input_file_path, encoding='cp949').read().splitlines()]
        except UnicodeDecodeError:
            input_lst = [x.strip() for x in open(input_file_path, encoding='utf-8').read().splitlines()]
    while '' in input_lst :
        input_lst.remove('')

    

    # TODO: 기능구현
    
    # www.bsabcandles.co.kr
    # '3.35.58.197'

    # host = 'www.bsabcandles.co.kr'
    # user = 'root'
    # password = 'xptmxm12'
    # db = 'cafe-color'

    # conn = ssh_connect(hostname=host,username=user,password=password)

    # Select_sql = "SELECT app_id FROM app_color" # SQL 쿼리
    # query_stdout, query_stderr = execute_sql_query(conn, user, password, db, Select_sql)
    # input_lst = query_stdout.split('\n')[1:]

    total_cnt = len(input_lst)
    start = time.time()
    today = datetime.datetime.now()
    someday_ago_str = today + timedelta(days=-time_delta)
    someday_ago = change_date_form(someday_ago_str)
    print('=='*10,'프로그램 시작','=='*10)
    print(f'''{total_cnt} 개의 패키지를 검사하겠습니다.\n기준일 : {someday_ago_str.strftime('%Y-%m-%d')}''')
    print('=='*28)
    
    for package_idx,input_data in enumerate(input_lst,start=1) :
        try :
            cur_time = datetime.datetime.now().strftime("%H:%M:%S")
            review_flag = True
            # loc = input_data.split('?id=')[1]
            loc = input_data

            lang = 'ko'
            country = 'kr'
            review_all, _ = reviews(
            loc,
            lang=lang, # defaults to 'en'
            country=country, # defaults to 'us'
            sort=Sort.NEWEST, # defaults to Sort.MOST_RELEVANT
            count=999999, # defaults to 100
            filter_score_with=None # defaults to None(means all score)
                )
            review = str(len(review_all))

            result = app(
            loc,  # app id (package name)
            lang='ko', # default: 'en'
            country='kr' # defaul: 'us'
            )

            # >>>>>>프로그램에 사용 되지 않은 앱 정보 json 데이터

            title = result['title'] # 어플 이름
            developer = result['developer'] # 개발사
            installs = result['installs'] #다운로드 수
            star_score = round(result['score'],1) # 별점
            ratings = result['ratings'] # 앱 화면에 있는 리뷰 수
            updated = gmtime(result['updated']) # 앱 업데이트 날짜
            updated = f'{updated.tm_year}-{updated.tm_mon}-{updated.tm_mday} {updated.tm_hour}:{updated.tm_min}:{updated.tm_sec}'
            installs =  int(re.sub(r'[^0-9]', '', installs))

            # >>>>>>>> 프로그램에 사용 되지 않은 앱 정보 json 데이터

            description = result['description'] # 앱 정보 (string)
            descriptionHTML = result['descriptionHTML'] # 앱 정보 (HTML)
            summary = result['summary'] #요약 정보
            minInstalls = result['minInstalls'] # 다운로드 등급(int)
            realInstalls = result['realInstalls'] # 실제 다운로드 수
            reviewss = result['reviews'] # 실제 리뷰 갯수
            histogrm = result['histogram'] # 별점 히스토그램 [0] ~ [4] 별점 5,4,3,2,1
            price = result['price'] # 앱 설치 가격
            free = result['free'] # 무료 어플 (Y/N)
            currency = result['currency'] # 통화 (KRW)
            sale = result['sale'] # 앱 할인 여부
            saleTime = result['saleTime'] # 앱 할인 기간 여부
            originalPrice = result['originalPrice'] # 앱 할인 전 가격
            saleText = result['saleText'] # 앱 할인 문구
            offersIAP = result['offersIAP'] # IAP 작동 여부
            inAppProductPrice = result['inAppProductPrice'] # 인앱 상품 가격
            developerId = result['developerId'] # 구글스토어 개발사 ID
            developerEmail = result['developerEmail'] # 개발자 이메일
            developerWebsite = result['developerWebsite'] # 개발사 사이트
            developerAddress = result['developerAddress'] # 개발사 주소
            privacyPolicy = result['privacyPolicy'] # 개인정보정책
            genre = result['genre'] # 앱 장르
            genreId = result['genreId'] # 앱 장르코드
            icon = result['icon'] # 앱 썸네일
            headerImage = result['headerImage'] # 헤더이미지
            screenshots = result['screenshots'] # 스크린샷
            video = result['video'] # 비디오 url
            videoImage = result['videoImage'] # 비디오 url 이미지
            contentRating = result['contentRating']# 콘텐츠 등급
            contentRatingDescription = result['contentRatingDescription'] # 콘텐츠 등급 설명
            adSupported = result['adSupported'] # 광고상품
            containsAds = result['containsAds'] # 광고유무
            released = result['released'] # 출시일
            version = result['version'] # 버전
            recentChanges = result['recentChanges'] # 최근 바뀐 앱정보 (string)
            recentChangesHTML = result['recentChangesHTML'] # 최근 바뀐 앱정보 (HTML)
            comments = result['comments'] # 댓글 (리뷰x)
            appId = result['appId'] # 패키지명
            url = result['url'] # 앱 스토어 주소


            print(f'''{cur_time} >> {package_idx} / {total_cnt}\n앱 제목 : {title}\n앱 업데이트 날짜 : {updated}\n개발사 : {developer}\n다운로드 수 : {installs}\n별점 : {star_score}\n화면 상 리뷰 수 : {ratings}''')

            if review_all == [] :
                review_all = '리뷰x'
                review_flag = False
                print('리뷰가 존재하지 않습니다.')
                print('=='*27)
                fwrite(output_file_path,f'{loc}\t{title}\t{installs}\t{star_score}\t{ratings}\t{review_all}')
                


            if review_flag :
                
                cnt = count_receive_reply(review_all,someday_ago)
                someday_ago_cnt = cnt[0]
                no_reply_cnt = cnt[1]

                # >>>>>>프로그램에 사용 되는 앱 리뷰 json 데이터

                newest_reviewer = review_all[0]['userName'] #최신 리뷰어
                reply_Content = review_all[0]['replyContent'] # 답글
                newest_review_date = review_all[0]['at'] # 최신 리뷰 날짜
                real_reviews = len(review_all) # 실제 리뷰수
                repliedAt = review_all[0]['repliedAt'] # 답글 날짜

                # >>>>>>프로그램에 사용 되지 않은 앱 정보 json 데이터

                reviewId = review_all[0]['reviewId'] # 리뷰어 ID
                userImage = review_all[0]['userImage'] # 리뷰어 이미지
                content =  review_all[0]['content'] # 리뷰 내용
                score =  review_all[0]['score'] # 리뷰어가 준 별점
                thumbsUpCount = review_all[0]['thumbsUpCount'] # 유용함을 받은 갯수
                reviewCreatedVersion = review_all[0]['reviewCreatedVersion'] # 리뷰을 달았을 당시 어플 버전


                if reply_Content :
                    reply_Content = 'Y'
                

                print(f'''실제 리뷰 수 : {real_reviews}\n최신 리뷰어 : {newest_reviewer}\n최신 리뷰 날짜 : {newest_review_date}\n답글 유무 : {reply_Content}\n답글 날짜 : {repliedAt}\n검사 리뷰 갯수[기준일이내] : {someday_ago_cnt}\n답글이 없는 리뷰[기준일 이내] : {no_reply_cnt}\n{'=='*27}\n''')
                fwrite(output_file_path,f'{loc}\t{title}\t{updated}\t{installs}\t{star_score}\t{ratings}\t{real_reviews}\t{newest_review_date}\t{reply_Content}\t{repliedAt}\t{no_reply_cnt}')
            fwrite(output2_file_path,f'{title}\t{developer}\t{loc}')
        
        except Exception as e :
            if 'not found' in str(e) :
                print(f'{cur_time} >> {package_idx} / {total_cnt} 번째 앱이 존재하지 않습니다.')
                print('=='*27,'\n')
                non_exist_app_str = f'{loc}\t앱 존재x'
                fwrite(output_file_path,non_exist_app_str)
                fwrite(output2_file_path,non_exist_app_str)
                fwrite(remove_file_path,loc)
                continue

            print(f'{cur_time} >> {package_idx} / {total_cnt} 번째 데이터에서 error 발생')
            print(f'Error : {e}')
            print('=='*27,'\n')
            input_data = {'error' : e,'순번' : package_idx, '패키지' : input_data}
            err_str = f'{loc}\terror'
            fwrite(output_file_path,err_str)
            fwrite(output2_file_path,err_str)
            err_logging(input_data)
            
    sec = time.time() - start
    taking_time = str(datetime.timedelta(seconds=sec)).split(".")[0]
    print(f'소요시간 : {taking_time}')
        

# ===============================================================================
#                            Program infomation
# ===============================================================================

__author__ = '김홍연'
__requester__ = '이광헌'
__registration_date__ = '230109'
__latest_update_date__ = '230111'
__version__ = 'v1.00'
__title__ = '20230109_구글플레이 앱 정보 추출 프로그램'
__desc__ = '20230109_구글플레이 앱 정보 추출 프로그램'
__changeLog__ = {
    'v1.00': ['Initial Release.'],
    'v1.01': ['20230111 김홍연 - 앱 업데이트 날짜 추가, 프로그램 실행시, 현재 시간 추가'],
}
version_lst = list(__changeLog__.keys())

full_version_log = '\n'
short_version_log = '\n'

for ver in __changeLog__:
    full_version_log += f'{ver}\n' + '\n'.join(['    - ' + x for x in __changeLog__[ver]]) + '\n'

if len(version_lst) > 5:
    short_version_log += '.\n.\n.\n'
    short_version_log += f'{version_lst[-2]}\n' + '\n'.join(['    - ' + x for x in __changeLog__[version_lst[-2]]]) + '\n'
    short_version_log += f'{version_lst[-1]}\n' + '\n'.join(['    - ' + x for x in __changeLog__[version_lst[-1]]]) + '\n'

# ===============================================================================
#                                 Main Code
# ===============================================================================

if __name__ == '__main__':

    ctypes.windll.kernel32.SetConsoleTitleW(f'{__title__} {__version__} ({__latest_update_date__})')

    sys.stdout.write(f'{__title__} {__version__} ({__latest_update_date__})\n')

    sys.stdout.write(f'{short_version_log if short_version_log.strip() else full_version_log}\n')

    run()