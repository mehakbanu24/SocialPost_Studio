import streamlit as st
from flask import Flask, request, redirect, url_for, render_template_string, send_file
import requests
from bs4 import BeautifulSoup
import io
import os
from dotenv import load_dotenv, find_dotenv


UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY') or "cW24D-Id92PLT1pvuFUZ5DIVEhmKD3r-4OTKWcDQSSc"

if not UNSPLASH_API_KEY:
    raise RuntimeError("Set UNSPLASH_API_KEY in environment or edit the script to include it.")

app = Flask(__name__)

BASE_HTML = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>SocialPost Studio — LinkedIn Post Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      .glass { background: rgba(255,255,255,0.1); backdrop-filter: blur(6px); }
      .card { border-radius: 1rem; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
    </style>
  </head>
  <body class="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-purple-800 text-white">
    <div class="container mx-auto p-6">
      <header class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-4xl font-extrabold text-white">🌟 SocialPost Studio</h1>
          <p class="text-gray-100 mt-2">Generate beautiful LinkedIn posts paired with curated articles and Unsplash images.</p>
        </div>
        <div class="text-sm text-gray-200">Built with Flask • Tailwind • Unsplash</div>
      </header>

      <main>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <section class="md:col-span-1 glass p-6 card">
            <h2 class="text-2xl font-semibold mb-3 text-white">✍️ Create a post</h2>
            <form method="POST" action="/generate">
              <label class="block text-gray-200 text-sm mb-1">Topic</label>
              <input name="topic" required placeholder="e.g. AI in healthcare" class="w-full p-3 rounded-md text-black" />

              <label class="block text-gray-200 text-sm mt-4 mb-1">Articles to fetch</label>
              <input name="num_articles" value="5" type="number" min="1" max="10" class="w-full p-3 rounded-md text-black" />

              <label class="block text-gray-200 text-sm mt-4 mb-1">Image size</label>
              <select name="img_size" class="w-full p-3 rounded-md text-black">
                <option value="regular">Regular</option>
                <option value="full">Full</option>
                <option value="small">Small</option>
              </select>

              <button type="submit" class="mt-4 w-full bg-pink-600 hover:bg-pink-500 py-3 rounded-md font-bold text-white shadow-lg">✨ Generate Post</button>
            </form>

            <div class="text-xs text-gray-300 mt-4">💡 Tip: Set your key via environment variable <code>UNSPLASH_API_KEY</code> for production.</div>
          </section>

          <section class="md:col-span-2 glass p-6 card">
            {% if not generated %}
            <div class="text-center py-20">
              <p class="text-2xl font-bold text-white">Ready to create your next LinkedIn post ✨</p>
              <p class="text-gray-200 mt-3">Enter a topic and we'll fetch articles + a curated Unsplash image.</p>
            </div>
            {% else %}

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <img src="{{ image_url }}" alt="unsplash image" class="w-full h-64 object-cover rounded-md shadow-md" onerror="this.style.display='none'" />
                <h3 class="text-xl font-bold mt-4 text-white">🚀 {{ topic }}</h3>
                <p class="text-gray-200 mt-2">{{ summary_plain }}</p>

                <div class="mt-4">
                  <h4 class="font-semibold text-white">🔗 Article links</h4>
                  <ul class="list-disc ml-5 mt-2 text-sm text-gray-100">
                    {% for a in articles %}
                      <li class="mt-2"><a class="underline text-indigo-300 hover:text-pink-400" href="{{ a.link }}" target="_blank">{{ a.title }}</a></li>
                    {% endfor %}
                  </ul>
                </div>

                <div class="mt-4 flex gap-3">
                  <form method="POST" action="/download-image">
                    <input type="hidden" name="image_url" value="{{ image_url }}" />
                    <button class="bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded-md text-white">⬇️ Download Image</button>
                  </form>

                  <button onclick="copyToClipboard()" class="bg-emerald-600 hover:bg-emerald-500 px-3 py-2 rounded-md text-white">📋 Copy Post</button>
                </div>

              </div>

              <div>
                <h4 class="font-semibold text-white">📝 Generated LinkedIn Post</h4>
                <textarea id="postText" class="w-full h-64 mt-2 p-4 rounded-md text-black">{{ post_text }}</textarea>

                <div class="mt-3 text-sm text-gray-200">✏️ You can edit before posting. The text area contains the final post with an actionable takeaway.</div>
              </div>

            </div>

            {% endif %}
          </section>
        </div>
      </main>

      <footer class="mt-8 text-center text-gray-400">Made with ❤️ — SocialPost Studio</footer>
    </div>

    <script>
      function copyToClipboard(){
        const txt = document.getElementById('postText');
        txt.select();
        navigator.clipboard.writeText(txt.value).then(()=>{
          alert('✅ Post copied to clipboard!');
        })
      }
    </script>
  </body>
</html>
'''


def get_related_articles(topic, num_articles=5):
    q = topic.replace(' ', '+')
    url = f'https://www.bing.com/news/search?q={q}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers, timeout=8)
    except Exception:
        return []
    if r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, 'html.parser')
    results = []
    for h in soup.select('a.title')[:num_articles]:
        title = h.get_text(strip=True)
        link = h.get('href')
        results.append({'title': title, 'link': link})
    return results


def get_unsplash_image(topic, size='regular'):
    url = 'https://api.unsplash.com/search/photos'
    headers = {'Authorization': f'Client-ID {UNSPLASH_API_KEY}'}
    params = {'query': topic, 'per_page': 1}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=8)
    except Exception:
        return None
    if r.status_code != 200:
        return None
    data = r.json()
    if not data.get('results'):
        return None
    img = data['results'][0]['urls'].get(size) or data['results'][0]['urls'].get('regular')
    return img


def build_post_text(topic, articles):
    lines = [f"{topic} — quick thoughts:\n"]
    if articles:
        themes = [a['title'] for a in articles[:4]]
        lines.append(" | ".join(themes) + "\n")
    lines.append("Why it matters: Keep learning, prioritize ethical deployment, and look for practical pilot projects that deliver real value.\n")
    lines.append("Actionable takeaway: Pick one small experiment this week to test an idea inspired by these reads.")
    return "\n".join(lines)


@app.route('/', methods=['GET'])
def index():
    return render_template_string(BASE_HTML, generated=False)


@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form.get('topic', '').strip()
    num_articles = int(request.form.get('num_articles', 5))
    img_size = request.form.get('img_size', 'regular')

    if not topic:
        return redirect(url_for('index'))

    articles = get_related_articles(topic, num_articles=num_articles)
    image_url = get_unsplash_image(topic, size=img_size)
    post_text = build_post_text(topic, articles)
    summary_plain = ' | '.join([a['title'] for a in articles[:3]]) if articles else 'No articles found.'

    return render_template_string(BASE_HTML, generated=True, topic=topic, articles=articles,
                                  image_url=image_url, post_text=post_text, summary_plain=summary_plain)


@app.route('/download-image', methods=['POST'])
def download_image():
    image_url = request.form.get('image_url')
    if not image_url:
        return ('', 204)
    try:
        r = requests.get(image_url, stream=True, timeout=10)
    except Exception:
        return ('', 500)
    if r.status_code != 200:
        return ('', 500)
    buf = io.BytesIO(r.content)
    return send_file(buf, mimetype='image/jpeg', as_attachment=True, download_name='unsplash.jpg')


if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)

