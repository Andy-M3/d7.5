import unittest
from news.models import *


class TestUpdateR(unittest, TestCase):
    def test_store(self, id=1):
        a1 = Author.objects.get(id)
        a1.ratingAuthor
        Post.objects.get(id).like()

# Create your tests here.
