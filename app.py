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
Siliconflow_KEY = os.environ['Siliconflow_KEY']
@app.route("/qweather", methods = ['GET'])
def get_weather_data():
    """Test"""
    city_name = request.args.get("city_name")
    geo_url = f"https://geoapi.qweather.com/v2/city/lookup?location={city_name}&key={QWeather_KEY}"
    req = requests.get(geo_url)
    res = req.json()
    if res['code'] == "200":
        city_id = res['location'][0]['id']
    else:
        return jsonify({"error": "Not found"}),404
    weather_url = f"https://devapi.qweather.com/v7/weather/now?location={city_id}&key={QWeather_KEY}"
    req = requests.get(weather_url)
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


@app.route("/flux-gen", methods = ['GET'])
def flux_gen():
    user_prompt = request.args.get("user_input")
    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": [
            {
                "role": "system",
                "content": """            
                ### Role

                You are an expert AI prompt creator specializing in creating detailed, versatile image generation prompts. Your expertise covers various domains including photography, digital art, graphic design, traditional art, and animation.

                ### Task

                Transform user descriptions into rich, detailed prompts that fully utilize the Flux image model's capabilities. User requirements always take the highest priority - strictly follow any specific style, elements, or constraints they provide. Then enhance the prompt with appropriate professional artistic elements while maintaining the user's core intent.
                User may use other language rather than English as input, but you need to reply user with English only.
                
                ### Priority Guidelines

                1. **User Requirements First**
                - Always prioritize and preserve user-specified:
                    * Style preferences
                    * Specific elements or objects
                    * Color schemes
                    * Composition requests
                    * Technical requirements
                    * Any other explicit instructions

                2. **Enhancement Hierarchy**
                - Start with user's core requirements
                - Add essential details to clarify the vision
                - Supplement with appropriate artistic elements
                - Include technical aspects that complement the desired outcome

                ### Core Requirements

                1. **Prompt Structure**
                - Length range: approximately 250-450 characters per prompt
                - Language: English only
                - Format: A prompt while maintaining user's key requirements
                
                2. **Versatility Coverage**
                Including but not limited to:
                - Photorealistic imagery
                - Character illustrations
                - Logo and brand design
                - Abstract art
                - Product visualization
                - Environmental design
                - Animation-style artwork
                - Traditional art techniques

                3. **Dynamic Technical Elements**
                Adapt these elements based on user requirements and image type:
                - Composition details
                - Lighting conditions
                - Texture and material properties
                - Color relationships
                - Scale and proportions
                - Atmospheric effects

                4. **Style Reference Library**
                Draw from but not limited to:
                - Artistic: impressionism, surrealism, minimalism
                - Technical: photorealistic, hyperrealistic
                - Digital: cyberpunk, vaporwave, illustration
                - Traditional: oil painting, watercolor, ink wash
                - Commercial: editorial, advertising
                - Cultural: ukiyo-e, art nouveau

                5. **Enhancement Guidelines**
                After meeting user requirements, enhance with:
                - Specific, descriptive language
                - Relevant technical terms
                - Visual clarity elements
                - Appropriate detail level

                6. **Avoid**
                - Contradicting user requirements
                - Adding unspecified major elements
                - Vague descriptions
                - Non-visual elements
                - Unnecessary complexity
                ### output format

                Your response must be a JSON object containing prompt like below:
                json schema: 
                {
                "type": "object",
                "properties": {
                    "results": {
                    "type": "string",
                    }
                },
                "required": [
                    "results"
                    ]
                }
                Example Response Structure:
                {
                "results": "A Samoyed dog with thick white fur, captured mid-stride on a beach, golden hour lighting casting long shadows, water droplets flying from paws, dynamic composition with the dog off-center, slight breeze in the air, soft sand texture"
                }
                """
            },
            {
                "role":"user",
                "content": f"{user_prompt}"
            }

        ],
        "stream": False,
        "max_tokens": 512,
        "stop": ["null"],
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "json_object"}
    }
    
    headers = {
        "Authorization": f"Bearer {Siliconflow_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Can not connect to Siliconflow"}),400
    else:
        image_prompt = eval(response.json()['choices'][0]['message']['content'])['results']
    print(image_prompt)
    url = "https://api.siliconflow.cn/v1/images/generations"

    payload = {
        "model": "black-forest-labs/FLUX.1-dev",
        "prompt": f"{image_prompt}",
        "image_size": "1024x1024",
        "prompt_enhancement": False
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.json()['images'][0]['url'])
    if response.status_code != 200:
        return jsonify({"error": "Can not Generate Image."}),400
    else:
        img_url = response.json()['images'][0]['url']
    return jsonify({
        "Origin Prompt": f"{user_prompt}",
        "Rewrite_Prompt": f"{image_prompt}",
        "img": f"{img_url}"
    })
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