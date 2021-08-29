from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
import json
import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbsparta


## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/best', methods=['GET'])
def best_sellers():
    url = 'http://www.aladin.co.kr/ttb/api/ItemList.aspx?includeKey=1&QueryType=Bestseller&output=js&MaxResults=100&Version=20131101&SearchTarget=Book&ttbkey=ttbydm27901710002&CategoryId=1'
    req = requests.get(url)
    response = json.loads(req.text)
    return jsonify({'message': 'success', 'item': response['item']})


@app.route('/search', methods=['GET'])
def search_aladin():
    print(request.args)
    query = request.args['query']
    url = 'http://www.aladin.co.kr/ttb/api/ItemSearch.aspx?ttbkey=ttbydm27901710002&QueryType=Title&MaxResults=9&start=1&SearchTarget=Book&output=js&Version=20131101&includeKey=1&Query='+ query
    req = requests.get(url)
    response = json.loads(req.text)
    return jsonify({'message': 'success', 'item': response['item']})


@app.route('/memo', methods=['GET'])
def listing():
    reviews = list(db.bookreviews.find({}, {'_id': False}))
    return jsonify({'all_reviews': reviews})


## API 역할을 하는 부분
@app.route('/memo', methods=['POST'])
def saving():
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']
    nick_receive = request.form['nick_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    title = soup.select_one('meta[property="og:title"]')['content']
    image = soup.select_one('meta[property="og:image"]')['content']
    description = soup.select_one('meta[property="og:description"]')['content']

    doc = {'title': title, 'image': image, 'desc': description, 'url': url_receive, 'comment': comment_receive,
           'nickname': nick_receive}
    db.bookreviews.insert_one(doc)

    return jsonify({'msg': '저장이 완료되었습니다.!'})





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
