import requests
import json
from bs4 import BeautifulSoup
from transformers import pipeline
from googlesearch import search
from datetime import datetime, timedelta


class Article:
    def __init__(self, article_id, title, summary, publication_date):
        self.article_id = article_id
        self.title = title
        self.summary = summary
        self.publication_date = publication_date
        self.sentiment = None
        self.preferences = None
        self.feedback = None


class ArticleRecommendationEngine:
    def __init__(self):
        self.article_data = {}

    def update_user_preferences(self, article_id, preferences):
        if article_id in self.article_data:
            self.article_data[article_id].preferences = preferences

    def process_user_feedback(self, article_id, feedback):
        if article_id in self.article_data:
            self.article_data[article_id].feedback = feedback

    def run_autonomous_program(self, user_id, keywords):
        search_query = self.generate_search_query(keywords)
        urls = self.search_urls(search_query, num_results=10)
        articles = self.scrape_articles(urls)
        self.preprocess_articles(articles)
        preferences = self.fetch_user_preferences(user_id)
        if articles:
            self.update_user_preferences(articles[0].article_id, preferences)
        recommendations = self.generate_recommendations(articles)
        return recommendations

    def generate_search_query(self, keywords):
        query = ' '.join(keywords)
        return f"news {query}"

    def search_urls(self, query, num_results=10):
        urls = []
        for url in search(query, num_results=num_results, stop=num_results):
            urls.append(url)
        return urls

    def scrape_articles(self, urls):
        articles = []
        for url in urls:
            article = self.scrape_article(url)
            if article:
                articles.append(article)
        return articles

    def scrape_article(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_id = url.split('/')[-1]
            title = soup.find('title').get_text()
            summary = soup.find('meta', attrs={'name': 'description'})[
                'content']
            publication_date = datetime.now().strftime("%Y-%m-%d")
            return Article(article_id, title, summary, publication_date)
        else:
            raise Exception(f"Failed to scrape article from URL: {url}")

    def preprocess_articles(self, articles):
        nlp = pipeline('sentiment-analysis')
        for article in articles:
            sentiment = nlp(article.summary)
            article.sentiment = sentiment[0]['label']

    def fetch_user_preferences(self, user_id):
        response = requests.get(
            f"https://api.example.com/users/{user_id}/preferences")
        if response.status_code == 200:
            preferences = json.loads(response.content.decode('utf-8'))
            return preferences
        else:
            raise Exception(
                f"Failed to fetch user preferences for user ID: {user_id}")

    def update_article_data(self, articles):
        for article in articles:
            if article.article_id not in self.article_data:
                self.article_data[article.article_id] = article

    def generate_recommendations(self, articles):
        recommendations = []
        for article in articles:
            if article.preferences and article.sentiment == 'POSITIVE':
                recommendations.append(article)
        return recommendations

    def update_article_database(self):
        articles_to_remove = []
        for article_id, article in self.article_data.items():
            publication_date = datetime.strptime(
                article.publication_date, "%Y-%m-%d")
            if (datetime.now() - publication_date).days >= 7:
                articles_to_remove.append(article_id)

        for article_to_remove in articles_to_remove:
            self.article_data.pop(article_to_remove)


if __name__ == "__main__":
    recommendation_engine = ArticleRecommendationEngine()
    user_id = '123'
    keywords = ['technology', 'startup']
    recommended_articles = recommendation_engine.run_autonomous_program(
        user_id, keywords)
    for article in recommended_articles:
        print(f"Article ID: {article.article_id}")
        print(f"Title: {article.title}")
        print(f"Summary: {article.summary}")
        print(f"Publication Date: {article.publication_date}")
        print(f"Sentiment: {article.sentiment}")
        print("---------------------")
