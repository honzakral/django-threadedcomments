from unittest import TestCase, expectedFailure

import django_comments
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.template import Context
from django.template import Template
from django.template import TemplateSyntaxError, loader
from django.test import TransactionTestCase
from threadedcomments.templatetags import threadedcomments_tags as tags
from threadedcomments.util import annotate_tree_properties

PATH_SEPARATOR = getattr(settings, 'COMMENT_PATH_SEPARATOR', '/')
PATH_DIGITS = getattr(settings, 'COMMENT_PATH_DIGITS', 10)


def sanitize_html(html):
    return '\n'.join(i.strip() for i in html.split('\n') if i.strip() != '')


class SanityTests(TransactionTestCase):
    BASE_DATA = {
        'name': 'Eric Florenzano',
        'email': 'floguy@gmail.com',
        'comment': 'This is my favorite Django app ever!',
    }

    def _post_comment(self, data=None, parent=None):
        Comment = django_comments.get_model()
        body = self.BASE_DATA.copy()
        if data:
            body.update(data)
        url = django_comments.get_form_target()
        args = [Site.objects.all()[0]]
        kwargs = {}
        if parent is not None:
            kwargs['parent'] = str(parent.pk)
            body['parent'] = str(parent.pk)
        form = django_comments.get_form()(*args, **kwargs)
        body.update(form.generate_security_data())
        self.client.post(url, body, follow=True)
        return Comment.objects.order_by('-id')[0]

    def test_post_comment(self):
        Comment = django_comments.get_model()
        self.assertEqual(Comment.objects.count(), 0)
        comment = self._post_comment()
        self.assertEqual(comment.tree_path, str(comment.pk).zfill(PATH_DIGITS))
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.last_child, None)

    def test_post_comment_child(self):
        Comment = django_comments.get_model()
        comment = self._post_comment()
        self.assertEqual(comment.tree_path, str(comment.pk).zfill(PATH_DIGITS))
        child_comment = self._post_comment(data={'name': 'ericflo'}, parent=comment)
        comment_pk = str(comment.pk).zfill(PATH_DIGITS)
        child_comment_pk = str(child_comment.pk).zfill(PATH_DIGITS)
        self.assertEqual(child_comment.tree_path, PATH_SEPARATOR.join((comment.tree_path, child_comment_pk)))
        self.assertEqual(comment.pk, child_comment.parent.pk)
        comment = django_comments.get_model().objects.get(pk=comment.pk)
        self.assertEqual(comment.last_child, child_comment)


class HierarchyTest(TransactionTestCase):
    fixtures = ['simple_tree']

    EXPECTED_HTML_PARTIAL = sanitize_html('''
    <ul>
        <li>
            0000000001 ADDED
            <ul>
                <li class="last">
                    0000000001/0000000004 ADDED
                    <ul>
                        <li class="last">
                            0000000001/0000000004/0000000006
                        </li>
                    </ul>
                </li>
            </ul>
        </li>
    </ul>
    <ul>
        <li>
            0000000007
        </li>
    </ul>
    ''')
    EXPECTED_HTML_FULL = sanitize_html('''
    <ul>
        <li>
            0000000001
            <ul>
                <li>
                    0000000001/0000000002
                    <ul>
                        <li>
                            0000000001/0000000002/0000000003
                        </li>
                        <li class="last">
                            0000000001/0000000002/0000000005
                        </li>
                    </ul>
                </li>
                <li class="last">
                    0000000001/0000000004
                    <ul>
                        <li class="last">
                            0000000001/0000000004/0000000006
                        </li>
                    </ul>
                </li>
            </ul>
        </li>
    </ul>
    <ul>
        <li>
            0000000007
        </li>
    </ul>
    ''')

    def test_root_path_returns_empty_for_root_comments(self):
        c = django_comments.get_model().objects.get(pk=7)
        self.assertEqual([], [x.pk for x in c.root_path])

    def test_root_path_returns_only_correct_nodes(self):
        c = django_comments.get_model().objects.get(pk=6)
        self.assertEqual([1, 4], [x.pk for x in c.root_path])

    def test_root_id_returns_self_for_root_comments(self):
        c = django_comments.get_model().objects.get(pk=7)
        self.assertEqual(c.pk, c.root_id)

    def test_root_id_returns_root_for_replies(self):
        c = django_comments.get_model().objects.get(pk=6)
        self.assertEqual(1, c.root_id)

    def test_root_has_depth_1(self):
        c = django_comments.get_model().objects.get(pk=7)
        self.assertEqual(1, c.depth)

    def test_open_and_close_match(self):
        depth = 0
        for x in annotate_tree_properties(django_comments.get_model().objects.all()):
            depth += getattr(x, 'open', 0)
            self.assertEqual(x.depth, depth)
            depth -= len(getattr(x, 'close', []))

        self.assertEqual(0, depth)

    def test_last_flags_set_correctly_only_on_last_sibling(self):
        # construct the tree
        nodes = {}
        for x in django_comments.get_model().objects.all():
            nodes[x.pk] = (x, [])
            if x.parent_id:
                nodes[x.parent_id][1].append(x.pk)

        # check all the comments
        for x in annotate_tree_properties(django_comments.get_model().objects.all()):
            if getattr(x, 'last', False):
                # last comments have a parent
                self.assertTrue(x.parent_id)
                par, siblings = nodes[x.parent_id]

                # and ar last in their child list
                self.assertTrue(x.pk in siblings)
                self.assertEqual(len(siblings) - 1, siblings.index(x.pk))

    def test_rendering_of_partial_tree(self):
        output = loader.render_to_string('sample_tree.html', {'comment_list': django_comments.get_model().objects.all()[5:]})
        self.assertEqual(self.EXPECTED_HTML_PARTIAL, sanitize_html(output))

    def test_rendering_of_full_tree(self):
        output = loader.render_to_string('sample_tree.html', {'comment_list': django_comments.get_model().objects.all()})
        self.assertEqual(self.EXPECTED_HTML_FULL, sanitize_html(output))

    def test_last_child_properly_created(self):
        ct = ContentType.objects.get_for_model(Site)
        Comment = django_comments.get_model()
        new_child_comment = Comment(comment="Comment 8", site_id=1, content_type=ct, object_pk=1, parent_id=1)
        new_child_comment.save()
        comment = Comment.objects.get(pk=1)
        self.assertEqual(comment.last_child, new_child_comment)

    def test_last_child_doesnt_delete_parent(self):
        ct = ContentType.objects.get_for_model(Site)
        Comment = django_comments.get_model()
        comment = Comment.objects.get(pk=1)
        new_child_comment = Comment(comment="Comment 9", site_id=1, content_type=ct, object_pk=1, parent_id=comment.id)
        new_child_comment.save()
        new_child_comment.delete()
        comment = Comment.objects.get(pk=1)

    def test_deletion_of_last_child_marks_parent_as_childless(self):
        ct = ContentType.objects.get_for_model(Site)
        Comment = django_comments.get_model()
        c = Comment.objects.get(pk=6)
        c.delete()
        c = Comment.objects.get(pk=4)
        self.assertEqual(None, c.last_child)

    def test_last_child_repointed_correctly_on_delete(self):
        ct = ContentType.objects.get_for_model(Site)
        Comment = django_comments.get_model()
        comment = Comment.objects.get(pk=1)
        last_child = comment.last_child
        new_child_comment = Comment(comment="Comment 9", site_id=1, content_type=ct, object_pk=1, parent_id=comment.id)

        new_child_comment.save()
        comment = Comment.objects.get(pk=1)
        self.assertEqual(comment.last_child, new_child_comment)
        new_child_comment.delete()
        comment = Comment.objects.get(pk=1)
        self.assertEqual(last_child, comment.last_child)


class SimpleTemplateTagTests(TransactionTestCase):
    fixtures = ['simple_tree']

    def get_comment_count(self):
        template = Template('{% load threadedcomments_tags %}{% get_comment_count for sites.site 1 as foo %}{{ foo }}')
        html = template.render(Context()).strip()
        self.assertEqual(html, '7')

    def test_get_comment_list(self):
        template = Template('{% load threadedcomments_tags %}{% get_comment_list for sites.site 1 as foo %}{{ foo|length }}')
        html = template.render(Context()).strip()
        self.assertEqual(html, '7')

    def test_render_comment_list(self):
        template = Template('{% load threadedcomments_tags %}{% render_comment_list for sites.site 1 %}')
        html = sanitize_html(template.render(Context()))
        self.assertIn('Comment 7', html)

    def test_render_comment_form(self):
        template = Template('{% load threadedcomments_tags %}{% render_comment_form for sites.site 1 %}')
        html = sanitize_html(template.render(Context()))
        self.assertIn(' name="parent" ', html)

    def test_get_comment_form(self):
        template = Template('{% load threadedcomments_tags %}{% get_comment_form for sites.site 1 as foo %}{{ foo.parent }}')
        html = sanitize_html(template.render(Context()))
        self.assertIn(' name="parent" ', html)
        self.assertNotIn('<form', html)


class ManagementCommandTests(TransactionTestCase):
    fixtures = ['simple_tree']

    @expectedFailure
    def test_migrate_comments(self):
        call_command('migrate_comments')

    @expectedFailure
    def test_migrate_threaded_comments(self):
        call_command('migrate_threaded_comments')



# Templatetags tests
##############################################################################

class MockParser:
    "Mock parser object for handle_token()"

    def compile_filter(self, var):
        return var
mock_parser = MockParser()


class MockToken:
    "Mock token object for handle_token()"

    def __init__(self, bits):
        self.contents = self
        self.bits = bits

    def split(self):
        return self.bits


class TestCommentListNode(TestCase):

    """
    {% get_comment_list for [object] as [varname] %}
    {% get_comment_list for [app].[model] [object_id] as [varname] %}
    """
    correct_ct_pk_params = ['get_comment_list', 'for', 'sites.site', '1', 'as', 'var']
    correct_var_params = ['get_comment_list', 'for', 'var', 'as', 'var']

    def test_parsing_fails_for_empty_token(self):
        self.assertRaises(TemplateSyntaxError, tags.get_comment_list, mock_parser, MockToken(['get_comment_list']))

    def test_parsing_fails_if_model_not_exists(self):
        params = self.correct_ct_pk_params[:]
        params[2] = 'not_app.not_model'
        self.assertRaises(TemplateSyntaxError, tags.get_comment_list, mock_parser, MockToken(params))

    def test_parsing_fails_if_object_not_exists(self):
        params = self.correct_ct_pk_params[:]
        params[2] = '1000'
        self.assertRaises(TemplateSyntaxError, tags.get_comment_list, mock_parser, MockToken(params))

    def test_parsing_works_for_ct_pk_pair(self):
        node = tags.get_comment_list(mock_parser, MockToken(self.correct_ct_pk_params))
        self.assertTrue(isinstance(node, tags.CommentListNode))

    def test_parsing_works_for_var(self):
        node = tags.get_comment_list(mock_parser, MockToken(self.correct_var_params))
        self.assertTrue(isinstance(node, tags.CommentListNode))

    def test_flat_parameter_is_passed_into_the_node_for_ct_pk_pair(self):
        params = self.correct_ct_pk_params[:]
        params.append('flat')
        node = tags.get_comment_list(mock_parser, MockToken(params))
        self.assertTrue(isinstance(node, tags.CommentListNode))
        self.assertTrue(node.flat)

    def test_flat_parameter_is_passed_into_the_node_for_var(self):
        params = self.correct_var_params[:]
        params.append('flat')
        node = tags.get_comment_list(mock_parser, MockToken(params))
        self.assertTrue(isinstance(node, tags.CommentListNode))
        self.assertTrue(node.flat)

    def test_root_only_parameter_is_passed_into_the_node_for_var(self):
        params = self.correct_var_params[:]
        params.append('root_only')
        node = tags.get_comment_list(mock_parser, MockToken(params))
        self.assertTrue(isinstance(node, tags.CommentListNode))
        self.assertTrue(node.root_only)

    def test_root_only_parameter_is_passed_into_the_node_for_ct_pk_pair(self):
        params = self.correct_ct_pk_params[:]
        params.append('root_only')
        node = tags.get_comment_list(mock_parser, MockToken(params))
        self.assertTrue(isinstance(node, tags.CommentListNode))
        self.assertTrue(node.root_only)
