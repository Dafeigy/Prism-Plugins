from flask import Flask,request,render_template,jsonify
import requests
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False




@app.route('/')
def home():
    return render_template('index.html')

# QWeather KEY
QWeather_KEY = os.environ['QWeather_KEY']
@app.route("/qweather", methods = ['GET'])
def get_weather_data():
    """Test"""
    city_name = request.args.get("city_name")
    geo_url = f"https://geoapi.qweather.com/v2/city/lookup?location={city_name}&key={QWeather_KEY}"
    req = requests.get(geo_url)
    # print(req.json())
    res = req.json()
    if res['code'] == "200":
        city_id = res['location'][0]['id']
    else:
        return jsonify({"error": "Not found"}),404
    weather_url = f"https://devapi.qweather.com/v7/weather/now?location={city_id}&key={QWeather_KEY}"
    req = requests.get(weather_url)
    # print(req.json())
    res = req.json()
    if res['code'] == "200":
        data = res['now']
        return jsonify({
            "更新时间":data['obsTime'],
            "体感温度":data["feelsLike"],
            "湿度":data['humidity'],
            "温度":data['temp'],
            "天气状况":data['text'],
            "能见度":data['vis']
        })
    else:
        return jsonify({"error": "Internal server error"}), 500
# 错误处理：404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

# 错误处理：500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)