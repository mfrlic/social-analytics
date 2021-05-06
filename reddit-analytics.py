from psaw import PushshiftAPI
import json, datetime

def fetch_data(subreddit, since, until, data = []):
    posts = list(PushshiftAPI().search_submissions(subreddit=subreddit, before=int((until+datetime.timedelta(days=1)).timestamp()), after=int((since-datetime.timedelta(days=1)).timestamp()), limit=1000, sort='desc'))
    for post in posts:
        data.append(str(datetime.datetime.fromtimestamp(post.created_utc).date()))
    while datetime.datetime.strptime(data[-1].split(' ')[0], '%Y-%m-%d') > since:
        until = datetime.datetime.strptime(data[-1].split(' ')[0], '%Y-%m-%d')
        posts = list(PushshiftAPI().search_submissions(subreddit=subreddit, before=int((until+datetime.timedelta(days=1)).timestamp()), after=int((since-datetime.timedelta(days=1)).timestamp()), limit=1000, sort='desc'))
        for post in posts:
            data.append(str(datetime.datetime.fromtimestamp(post.created_utc).date()))
    return data
def sort_data(item):
    return datetime.datetime.strptime(item.get('date'), '%Y-%m-%d').date()
def save_to_json(data, crypto, since, until, dates = [], stats_24h = 0):
    temp = until
    while temp >= since:
        dates.append(str(temp))
        temp -= datetime.timedelta(days=1)

    try:
        with open('data/' + crypto + '.json', 'r') as file:
            json_data = json.load(file)
        stats = json_data.get['reddit_count']
    except:
        stats = []

    for date in dates:
        check = 0
        for item in stats:
            if date == item.get('date'):
                check = 1
                break
        if check == 0:
            stats_24h = 0
            for item in data:
                if item == date:
                    stats_24h+=1
            stats.append({'date': date, 'count': stats_24h})
    stats.sort(key=sort_data)

    json_data['reddit_count'] = stats
    with open('data/' + crypto + '.json', 'w') as file:
        json.dump(json_data, file)
def main(crypto, subreddit, since, until):
    since = datetime.datetime.strptime(since, '%Y-%m-%d')
    until = datetime.datetime.strptime(until, '%Y-%m-%d')

    print('Fetching posts...')
    data = fetch_data(subreddit, since, until)

    print('Appending data and saving to json...')
    save_to_json(data, crypto, since.date(), until.date())

    print('Successfully saved to json.')