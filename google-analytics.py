from pytrends.request import TrendReq
import datetime, json

def fetch_data(search_term, since, until):
    pytrends = TrendReq(timeout=(10,25))
    pytrends.build_payload(kw_list=[search_term], timeframe=str(since.date()) + ' ' + str(until.date()))
    count = pytrends.interest_over_time()
    count.drop('isPartial', axis=1, inplace=True)
    count = count.values.tolist()
    for i in range(0, len(count)):
        count[i] = count[i][0]
    return count
def sort_data(item):
    return datetime.datetime.strptime(item.get('date'), '%Y-%m-%d').date()
def append_data(count, temp, until, data_type, data = [], dates = [], i = 0):
    while temp<=until:
        dates.append(str(temp))
        temp += datetime.timedelta(days=1)
    if data_type == 'daily':
        if len(count) == len(dates):
            for date in dates:
                data.append({'date': str(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()), 'count': count[i]})
                i+=1
        elif len(count)<len(dates):
            for item in count:
                data.append({'date': str(datetime.datetime.strptime(dates[i], '%Y-%m-%d %H:%M:%S').date()), 'count': item})
                i+=1
            while i < len(dates):
                if dates[i] not in data:
                    data.append({'date': str(datetime.datetime.strptime(dates[i], '%Y-%m-%d %H:%M:%S').date()), 'count': 0})
                    i+=1
    elif data_type == 'weekly':
        i = 0
        for date in dates:
            if datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').weekday() == 0:
                data.append({'date': str(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()), 'count': count[i]})
                data.append({'date': str(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date() + datetime.timedelta(days=1)), 'count': count[i]})
                data.append({'date': str(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date() + datetime.timedelta(days=2)), 'count': count[i]})
                data.append({'date': str(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date() + datetime.timedelta(days=3)), 'count': count[i]})
                data.append({'date': str(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date() + datetime.timedelta(days=4)), 'count': count[i]})
                data.append({'date': str(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date() + datetime.timedelta(days=5)), 'count': count[i]})
                data.append({'date': str(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date() + datetime.timedelta(days=6)), 'count': count[i]})
                i+=1
    data.sort(key=sort_data)
    return data
def save_to_json(data, crypto):
    with open('data/' + crypto + '.json', 'r') as file:
        json_data = json.load(file)
    json_data['google_count'] = data
    with open('data/' + crypto + '.json', 'w') as file:
        json.dump(json_data, file)
def main(crypto, search_term, since, until):
    since = datetime.datetime.strptime(since, '%Y-%m-%d')
    until = datetime.datetime.strptime(until, '%Y-%m-%d')
    if int((until-since).days) >= 270:
        data_type = 'weekly'
    else: 
        data_type = 'daily'

    print('Fetching data from google trends...')
    count = fetch_data(search_term, since, until)

    print('Fetched data. Appending it to list...')
    data = append_data(count, since, until, data_type)

    print('Data apended. Saving data to json...')
    save_to_json(data, crypto)

    print('Successfully saved to json.')