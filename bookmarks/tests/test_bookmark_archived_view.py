from typing import List

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from bookmarks.models import Bookmark, Tag, UserProfile
from bookmarks.tests.helpers import BookmarkFactoryMixin, HtmlTestMixin


class BookmarkArchivedViewTestCase(TestCase, BookmarkFactoryMixin, HtmlTestMixin):

    def setUp(self) -> None:
        user = self.get_or_create_test_user()
        self.client.force_login(user)

    def assertVisibleBookmarks(self, response, bookmarks: List[Bookmark], link_target: str = '_blank'):
        html = response.content.decode()
        self.assertContains(response, 'data-is-bookmark-item', count=len(bookmarks))

        for bookmark in bookmarks:
            self.assertInHTML(
                f'<a href="{bookmark.url}" target="{link_target}" rel="noopener" class="">{bookmark.resolved_title}</a>',
                html
            )

    def assertInvisibleBookmarks(self, response, bookmarks: List[Bookmark], link_target: str = '_blank'):
        html = response.content.decode()

        for bookmark in bookmarks:
            self.assertInHTML(
                f'<a href="{bookmark.url}" target="{link_target}" rel="noopener" class="">{bookmark.resolved_title}</a>',
                html,
                count=0
            )

    def assertVisibleTags(self, response, tags: List[Tag]):
        self.assertContains(response, 'data-is-tag-item', count=len(tags))

        for tag in tags:
            self.assertContains(response, tag.name)

    def assertInvisibleTags(self, response, tags: List[Tag]):
        for tag in tags:
            self.assertNotContains(response, tag.name)

    def assertSelectedTags(self, response, tags: List[Tag]):
        soup = self.make_soup(response.content.decode())
        selected_tags = soup.select('p.selected-tags')[0]
        self.assertIsNotNone(selected_tags)

        tag_list = selected_tags.select('a')
        self.assertEqual(len(tag_list), len(tags))

        for tag in tags:
            self.assertTrue(tag.name in selected_tags.text, msg=f'Selected tags do not contain: {tag.name}')

    def test_should_list_archived_and_user_owned_bookmarks(self):
        other_user = User.objects.create_user('otheruser', 'otheruser@example.com', 'password123')
        visible_bookmarks = [
            self.setup_bookmark(is_archived=True),
            self.setup_bookmark(is_archived=True),
            self.setup_bookmark(is_archived=True)
        ]
        invisible_bookmarks = [
            self.setup_bookmark(is_archived=False),
            self.setup_bookmark(is_archived=True, user=other_user),
        ]

        response = self.client.get(reverse('bookmarks:archived'))

        self.assertContains(response, '<ul class="bookmark-list">')  # Should render list
        self.assertVisibleBookmarks(response, visible_bookmarks)
        self.assertInvisibleBookmarks(response, invisible_bookmarks)

    def test_should_list_bookmarks_matching_query(self):
        visible_bookmarks = [
            self.setup_bookmark(is_archived=True, title='searchvalue'),
            self.setup_bookmark(is_archived=True, title='searchvalue'),
            self.setup_bookmark(is_archived=True, title='searchvalue')
        ]
        invisible_bookmarks = [
            self.setup_bookmark(is_archived=True),
            self.setup_bookmark(is_archived=True),
            self.setup_bookmark(is_archived=True)
        ]

        response = self.client.get(reverse('bookmarks:archived') + '?q=searchvalue')

        self.assertContains(response, '<ul class="bookmark-list">')  # Should render list
        self.assertVisibleBookmarks(response, visible_bookmarks)
        self.assertInvisibleBookmarks(response, invisible_bookmarks)

    def test_should_list_tags_for_archived_and_user_owned_bookmarks(self):
        other_user = User.objects.create_user('otheruser', 'otheruser@example.com', 'password123')
        visible_tags = [
            self.setup_tag(),
            self.setup_tag(),
            self.setup_tag(),
        ]
        invisible_tags = [
            self.setup_tag(),  # unused tag
            self.setup_tag(),  # used in archived bookmark
            self.setup_tag(user=other_user),  # belongs to other user
        ]

        # Assign tags to some bookmarks with duplicates
        self.setup_bookmark(is_archived=True, tags=[visible_tags[0]])
        self.setup_bookmark(is_archived=True, tags=[visible_tags[0]])
        self.setup_bookmark(is_archived=True, tags=[visible_tags[1]])
        self.setup_bookmark(is_archived=True, tags=[visible_tags[1]])
        self.setup_bookmark(is_archived=True, tags=[visible_tags[2]])
        self.setup_bookmark(is_archived=True, tags=[visible_tags[2]])

        self.setup_bookmark(is_archived=False, tags=[invisible_tags[1]])
        self.setup_bookmark(is_archived=True, tags=[invisible_tags[2]], user=other_user)

        response = self.client.get(reverse('bookmarks:archived'))

        self.assertVisibleTags(response, visible_tags)
        self.assertInvisibleTags(response, invisible_tags)

    def test_should_list_tags_for_bookmarks_matching_query(self):
        visible_tags = [
            self.setup_tag(),
            self.setup_tag(),
            self.setup_tag(),
        ]
        invisible_tags = [
            self.setup_tag(),
            self.setup_tag(),
            self.setup_tag(),
        ]

        self.setup_bookmark(is_archived=True, tags=[visible_tags[0]], title='searchvalue')
        self.setup_bookmark(is_archived=True, tags=[visible_tags[1]], title='searchvalue')
        self.setup_bookmark(is_archived=True, tags=[visible_tags[2]], title='searchvalue')
        self.setup_bookmark(is_archived=True, tags=[invisible_tags[0]])
        self.setup_bookmark(is_archived=True, tags=[invisible_tags[1]])
        self.setup_bookmark(is_archived=True, tags=[invisible_tags[2]])

        response = self.client.get(reverse('bookmarks:archived') + '?q=searchvalue')

        self.assertVisibleTags(response, visible_tags)
        self.assertInvisibleTags(response, invisible_tags)

    def test_should_display_selected_tags_from_query(self):
        tags = [
            self.setup_tag(),
            self.setup_tag(),
            self.setup_tag(),
            self.setup_tag(),
            self.setup_tag(),
        ]
        self.setup_bookmark(is_archived=True, tags=tags)

        response = self.client.get(reverse('bookmarks:archived') + f'?q=%23{tags[0].name}+%23{tags[1].name}')

        self.assertSelectedTags(response, [tags[0], tags[1]])

    def test_should_open_bookmarks_in_new_page_by_default(self):
        visible_bookmarks = [
            self.setup_bookmark(is_archived=True),
            self.setup_bookmark(is_archived=True),
            self.setup_bookmark(is_archived=True)
        ]

        response = self.client.get(reverse('bookmarks:archived'))

        self.assertVisibleBookmarks(response, visible_bookmarks, '_blank')

    def test_should_open_bookmarks_in_same_page_if_specified_in_user_profile(self):
        user = self.get_or_create_test_user()
        user.profile.bookmark_link_target = UserProfile.BOOKMARK_LINK_TARGET_SELF
        user.profile.save()

        visible_bookmarks = [
            self.setup_bookmark(is_archived=True),
            self.setup_bookmark(is_archived=True),
            self.setup_bookmark(is_archived=True)
        ]

        response = self.client.get(reverse('bookmarks:archived'))

        self.assertVisibleBookmarks(response, visible_bookmarks, '_self')
