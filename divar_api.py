import requests
from progress.bar import Bar
import time
from datetime import datetime
import atexit

@atexit.register
def Exit():
    print('exit divar api app.')


def main():
    url = 'https://api.divar.ir/v8/search/1/apartment-sell'
    
    json = {"json_schema": {"category": {"value": "apartment-sell"}},
            "last-post-date": 1650392836073764}
    headers = {"Content-Type": "application/json"}

    api_data_filter = {"json_schema": {
                            "category": {
                                "value": "apartment-sell"},
                            "districts": {
                                "vacancies": [
                                    "74",
                                    "86",
                                    "1028",
                                    "72",
                                    "941"]},
                            #"user_type": {
                                #"value": "شخصی"},
                            "cities": ["1"]},
                      "last-post-date": 1650392836073764}

    # res = requests.post(url, json=json, headers=headers)
    # data = res.json()
    api_data_filter['last-post-date'] = 1673468493086323 # 3-11-01  # json['last-post-date']
    
    
    list_of_tokens = []
    n = 1_000
    bar = Bar('Loading...', fill='X', max=n, suffix='%(percent).2f%%')
    
    start_time = time.time()
    for i in range(n):
        if bar.index % 10 == 0:
            time.sleep(3)
        bar.next()
        # print(round(i/n * 100, 2), '%')
        
        try: 
            res = requests.post(url, json=api_data_filter, headers=headers, timeout=2)
        except Exception as e:
            api_data_filter['last-post-date'] += 1
            print('except: ', e)
            continue
        
        if res.status_code == 200:
            data = res.json()
            api_data_filter['last-post-date'] = data['last_post_date']
        else:
            api_data_filter['last-post-date'] += 1
            print('response: ', res.status_code)
            continue
        
        for widget in data['web_widgets']['post_list']:
            token = widget['data']['token']
            list_of_tokens.append(token)
            # print(token)
            
        if len(list_of_tokens) - len(set(list_of_tokens)) != 0:
            print('duplicate token.', i, api_data_filter['last-post-date'])
            break
        
    end_time = time.time()
    
    list_of_tokens = set(list_of_tokens)
    print(len(list_of_tokens))
    
    # TODO : write to database
    path_data = 'C:/D/hashti/Data/'
    txt_file = open(path_data + '__tokens__.csv', 'a+', encoding='utf8')
    txt_file.write('\n'.join(list_of_tokens))
    txt_file.close()


# %% code
if __name__ == '__main__':
    print('start divar api app')
    while True:
        date = datetime.now()
        if ((date.hour >= 1) and (date.hour < 10)):
            main()
            # n += n * 1.8
            time.sleep(5*60)
        else:
            time.sleep(10)
