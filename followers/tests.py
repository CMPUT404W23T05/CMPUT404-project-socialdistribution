from django.test import TestCase
from .models import Followers 
from authors.models import Author
from django.forms.models import model_to_dict

class ModelTesting(TestCase):

    def setUp(self):

        self.author1 = Author.objects.create(
                type = "author",
                home_host = "http://127.0.0.1:5454/",
                display_name = "Lara Croft",
                profile_url = "http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                author_github = "http://github.com/laracroft",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg"
                )

        self.author2 = Author.objects.create(
                type = "author",
                home_host = "http://127.0.0.1:5454/",
                display_name = "Greg Johnson",
                profile_url = "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                author_github = "http://github.com/gjohnson",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg"
                )

        self.author3 = Author.objects.create(
                type = "author",
                home_host = "http://127.0.0.1:5454/",
                display_name = "John Doe",
                profile_url = "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                author_github = "http://github.com/jdoe",
                profile_image = "https://i.imgur.com/k7XVwpB.jpeg"
                )
    def test_present_fields(self):
        # tests to make sure all the fields remain when we convert from model to dict

        # number of author attributes    
        n = 6
        self.assertEqual(len(model_to_dict(self.author1)), n)


    def test_list_of_friends(self):
        # test to see if Greg Johnson and John Doe are following Lara Croft 
        # friend = someone who follows you

        # pass in author 2 (Greg) as a follower of author 1 (Lara)
        following_author1 = model_to_dict(self.author2)
        self.author1.followers_info.create(**following_author1)

        # pass in author 3 (John) as a follower of author 1 (Lara)
        following_author1 = model_to_dict(self.author3)
        self.author1.followers_info.create(**following_author1)

        # check the number of followers
        all_followers = self.author1.followers_info.all()
        self.assertEqual(len(all_followers), 2)

        # check who the follower is
        self.assertEqual(all_followers[0].display_name, self.author2.display_name)
        self.assertEqual(all_followers[1].display_name, self.author3.display_name)
    
    def test_bidirectional_friends(self):
        # make Lara and Greg follow each other
        
        # pass in author 2 (Greg) as a follower of author 1 (Lara)
        following_author1 = model_to_dict(self.author2)
        self.author1.followers_info.create(**following_author1)

        # pass in author 1 (Lara) as a follower of author 2 (Greg)
        following_author2 = model_to_dict(self.author1)
        self.author2.followers_info.create(**following_author2)

        author1_followers = self.author1.followers_info.all()
        author2_followers = self.author2.followers_info.all()

        # is Greg following Lara?
        self.assertEqual(author1_followers[0].display_name, self.author2.display_name)

        # is Lara following Greg?
        self.assertEqual(author2_followers[0].display_name, self.author1.display_name)
