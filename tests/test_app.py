import unittest
import tempfile
from pathlib import Path
import app as blog
from app import app


class BlogTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_and_article_links(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('把生活留给真正重要的事', response.get_data(as_text=True))
        self.assertEqual(self.client.get('/posts/less-but-better').status_code, 200)

    def test_category_and_search(self):
        html = self.client.get('/', query_string={'category': '技术手记'}).get_data(as_text=True)
        self.assertIn('写代码，也是一种整理思绪的方式', html)
        self.assertNotIn('href="/posts/mountain-weekend"', html)
        html = self.client.get('/', query_string={'q': '咖啡'}).get_data(as_text=True)
        self.assertIn('一杯咖啡的时间', html)
        self.assertNotIn('href="/posts/mountain-weekend"', html)

    def test_empty_and_escaped_search(self):
        html = self.client.get('/', query_string={'q': '<script>alert(1)</script>'}).get_data(as_text=True)
        self.assertIn('还没有找到', html)
        self.assertNotIn('<script>alert(1)</script>', html)

    def test_about_and_missing(self):
        self.assertEqual(self.client.get('/about').status_code, 200)
        self.assertEqual(self.client.get('/posts/missing').status_code, 404)
        self.assertEqual(self.client.get('/missing').status_code, 404)

    def test_author_and_technical_content(self):
        html = self.client.get('/posts/transformer-intro').get_data(as_text=True)
        self.assertIn('李文豪', html)
        self.assertIn('softmax', html)
        self.assertNotIn('林间', html)
        self.assertEqual(self.client.get('/posts/python-asyncio').status_code, 200)

    def test_publish_validation_persistence_and_escape(self):
        original_db = blog.DB
        try:
            with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
                blog.DB = Path(folder) / 'test.sqlite3'
                blog.init_db()
                self.assertEqual(self.client.post('/write', data={'title': 'x'}).status_code, 400)
                self.assertEqual(self.client.get('/write').status_code, 200)
                with self.client.session_transaction() as state:
                    csrf = state['csrf']
                self.assertEqual(self.client.post('/write', data={'csrf': csrf, 'title': '', 'category': '技术手记', 'body': ''}).status_code, 422)
                response = self.client.post('/write', data={'csrf': csrf, 'title': '测试新文章', 'category': '技术手记', 'body': '唯一正文关键词\n<script>alert(1)</script>'})
                self.assertEqual(response.status_code, 303)
                html = self.client.get(response.location).get_data(as_text=True)
                self.assertIn('唯一正文关键词', html)
                self.assertIn('&lt;script&gt;', html)
                self.assertNotIn('<script>alert(1)</script>', html)
                html = self.client.get('/', query_string={'q': '唯一正文关键词'}).get_data(as_text=True)
                self.assertIn('测试新文章', html)
                blog.init_db()
                self.assertEqual(self.client.get(response.location).status_code, 200)
        finally:
            blog.DB = original_db


if __name__ == '__main__':
    unittest.main()
