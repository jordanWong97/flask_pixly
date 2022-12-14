"""Image View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_image_views.py


import os
from unittest import TestCase

from models import db, Image, Image_Metadata

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///pixly_test"

# Now we can import app
from app import app

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class BaseViewTestCase(TestCase):
    def setUp(self):
        Image_Metadata.query.delete()
        Image.query.delete()

        image = Image(
            image_name="test",
            uploaded_by="test_user",
            notes="notes",
            filename="testfile.jpg",
            amazon_file_path="https://pixlybucket.s3.us-west-1.amazonaws.com/sampleone.JPG"
        )

        db.session.add(image)
        db.session.commit()

        self.image_id = image.id

        image_metadata = Image_Metadata(
            image_id=image.id,
            name="resolution",
            value="high quality",
        )

        db.session.add(image_metadata)
        db.session.commit()

        self.image_metadata_id = image_metadata.id

        self.client = app.test_client()


    def tearDown(self):
        db.session.rollback()


    def test_home_page(self):
        """ tests if home page renders correctly"""

        with self.client as c:

            resp = c.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search', html)
            self.assertIn('Add New Image', html)


    def test_addimage(self):
        """ tests add image page renders correctly """

        with self.client as c:

            resp = c.get('/addimage')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form method="POST"', html)
            self.assertIn('Upload a New Image', html)


    def test_image_detail(self):
        """ tests image detail page renders correctly """

        with self.client as c:

            resp = c.get(f'/image/{self.image_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('class="photo-details"', html)
            self.assertIn('test', html)
            self.assertIn('notes', html)

    def test_image_edit(self):
        """ tests edit image page renders correctly """

        with self.client as c:

            resp = c.get(f'/image/{self.image_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form method="POST"', html)
            self.assertIn('Tone', html)
            self.assertIn('Border', html)

    def test_image_edit_preview(self):
        """ tests edit image preview page renders correctly """

        with self.client as c:

            resp = c.get(f'/image/{self.image_id}/edit/preview')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('"/uploadedit"', html)
            self.assertIn('Image Size', html)
            self.assertIn('Upload Changes', html)

    def test_upload_edit(self):
        """ tests edit image preview page renders correctly """

        with self.client as c:

            resp = c.get('/uploadedit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form method="POST"', html)
            self.assertIn('class="photo-details"', html)
            self.assertIn('Upload Image!', html)

    def test_invalid_routes(self):
        """ tests edit image preview page renders correctly """

        with self.client as c:

            resp = c.get('/wrongroute', follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add New Image', html)
            self.assertIn('Invalid URL route', html)
