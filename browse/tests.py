import datetime

from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from django.utils import timezone
from posts.models import Post


#Helper functions.
def create_post(is_private: bool, content_type: str, pub_date: datetime):
    return Post.objects.create(
                type = "post",
                title = "example post",
                post_id = "http://127.0.0.1:5454/authors/1/posts/1",
                post_source = "http://lastplaceigotthisfrom.com/posts/yyyyy",
                post_origin = "http://whereitcamefrom.com/posts/zzzzz",
                description = "this is an example post for testing",
                content_type = content_type,
                content = "testing... 1,2,3",
                comment_count = 0,
                comments = "http://127.0.0.1:5454/authors/1/posts/1/comments",
                pub_date = pub_date,
                is_unlisted = is_private,
                )

# Create your tests here.
class BrowsePublicPostsViewTests(TestCase):

    def setUp(self):
        setup_test_environment()
        self.client = Client()

    #----------All posts------------
    def test_no_posts(self):
        '''
        When there are no posts, a message indicating such will appear.
        '''

        response = self.client.get(reverse('browse'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No public posts yet!")
        self.assertQuerysetEqual(response.context['public_post_list'], [])

    # No edit functionality (yet)
    # def test_future_posts_do_not_appear(self):
    #     '''
    #     A post with a future published date will not appear until said date.
    #     '''

    def test_future_posts_are_ordered(self):
        '''
        Posts will be organized by their published date.
        '''

        past_date = timezone.now() - datetime.timedelta(days = 1)
        post1 = create_post(is_private=False, content_type='text/plain', pub_date=datetime.now())
        post2 = create_post(is_private=False, content_type='image', pub_date=past_date)

        response = self.client.get(reverse('browse'))
        self.assertQuerysetEqual(response.context['public_post_list'], [post2, post1])

    #----------Private posts------------

    def test_private_post_not_visible(self):
        '''
        When a private post is made, it won't appear in the feed.
        '''
        private_post = create_post(is_private=True, content_type='whatever', pub_date=datetime.now())

        response = self.client.get(reverse('browse'))
        self.assertQuerysetEqual(response.context['public_post_list'], [])

    def test_private_post_lack_date_header(self):
        '''
        When a private post is in made, it won't have a respective date header.
        '''

        pub_date = "2015-03-09T13:07:04+00:00"

        private_post = create_post(is_private=True, content_type='whatever', pub_date=pub_date)

        response = self.client.get(reverse('browse'))

        #Header date format
        self.assertNotContains(response, '03/09/2015')

    def test_private_post_and_public_filtered(self):
        '''
        When a public and private post is made, only the public one will appear in the feed.
        '''

        now = datetime.now()
        private_post = create_post(is_private=True, content_type='whatever', pub_date=now)
        public_post = create_post(is_private=False, content_type='whatever', pub_date=now)

        response = self.client.get(reverse('browse'))

        self.assertQuerysetEqual(response.context['public_post_list'], [])

    #----------Public posts------------

    def test_public_post_has_date_header(self):
        '''
        When a public post is made, it will have a respective date header.
        '''

        pub_date = "2015-03-09T13:07:04+00:00"
        public_post = create_post(is_private=False, content_type='whatever', pub_date=pub_date)

        response = self.client.get(reverse('browse'))

        #Header date format
        self.assertNotContains(response, '03/09/2015')
       
    def test_public_post_is_visible(self):
        '''
        When a public post is made, it will appear in the feed
        '''

        public_post = create_post(is_private=False, content_type='text/plain', pub_date=datetime.now())
        response = self.client.get(reverse('browse'))

        self.assertQuerysetEqual(response.context['public_post_list'], [public_post])

  