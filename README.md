# SocialPost_Studio


This project is a simple Flask web application that generates engaging LinkedIn-style posts based on a topic provided by the user.  
It scrapes related articles from the web, summarizes the content, and uses OpenAI’s language model to create a polished post.  
Additionally, it fetches a relevant image from Unsplash to make the post visually appealing.


## 🚀 Key Features
- Accepts a user topic and searches for related trending articles online.
- Summarizes and reformulates content into a professional LinkedIn-style post.
- Automatically fetches a relevant Unsplash image.
- Simple and attractive web UI with dark theme and bright text for readability.


## ⚠️ Limitations
- Requires internet connectivity for scraping and API requests.
- Unsplash API key must be valid.
- Currently not storing history of generated posts (single result at a time).
- Basic error handling — may fail silently if API rate limits are hit.


## 🛠️ Tools & APIs Used
- **Python Flask** → for the web application framework
- **Requests + BeautifulSoup** → for scraping related articles
- **Unsplash API** → for fetching related images
- **HTML + CSS** → for front-end styling (dark theme, bright text)


## ⚙️ Setup Instructions

1. Clone this repository
2. Install dependencies -> pip install -r requirements.txt
3. Setup API key -> UNSPLASH_API_KEY=your_unsplash_api_key_here
4. Run the flask app -> python app.py
5. Open your browser -> Go to: http://127.0.0.1:5000/ 
  

