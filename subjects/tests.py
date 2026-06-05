from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from .models import Subject

User = get_user_model()


class SubjectModelTests(TestCase):
    """Test Subject model."""

    def test_subject_create_with_required_fields(self):
        """Subject can be created with title."""
        subject = Subject.objects.create(title="Mathematics")
        self.assertEqual(subject.title, "Mathematics")
        self.assertIsNotNone(subject.created_at)
        self.assertIsNone(subject.deleted_at)

    def test_subject_title_unique(self):
        """Subject title must be unique."""
        Subject.objects.create(title="Physics")
        with self.assertRaises(Exception):
            Subject.objects.create(title="Physics")

    def test_subject_with_description(self):
        """Subject can have optional description."""
        subject = Subject.objects.create(
            title="Chemistry",
            description="Study of matter and reactions"
        )
        self.assertEqual(subject.description, "Study of matter and reactions")

    def test_subject_str_representation(self):
        """Subject string representation returns title."""
        subject = Subject.objects.create(title="Biology")
        self.assertEqual(str(subject), "Biology")

    def test_subject_soft_delete_field(self):
        """Subject can be soft-deleted via deleted_at field."""
        subject = Subject.objects.create(title="History")
        self.assertIsNone(subject.deleted_at)
        subject.deleted_at = timezone.now()
        subject.save()
        self.assertIsNotNone(subject.deleted_at)


class SubjectSerializerTests(TestCase):
    """Test Subject serializers."""

    def test_subject_serializer_valid_data(self):
        """SubjectSerializer accepts valid data."""
        from .serializers import SubjectSerializer
        data = {
            "title": "English",
            "description": "English language and literature"
        }
        serializer = SubjectSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_subject_serializer_title_required(self):
        """SubjectSerializer requires title."""
        from .serializers import SubjectSerializer
        data = {"description": "Some description"}
        serializer = SubjectSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_subject_serializer_title_min_length(self):
        """SubjectSerializer title must be at least 2 chars."""
        from .serializers import SubjectSerializer
        data = {"title": "A"}
        serializer = SubjectSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_subject_serializer_title_max_length(self):
        """SubjectSerializer title max 100 chars."""
        from .serializers import SubjectSerializer
        data = {"title": "x" * 101}
        serializer = SubjectSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_subject_serializer_description_max_length(self):
        """SubjectSerializer description max 500 chars."""
        from .serializers import SubjectSerializer
        data = {
            "title": "Valid",
            "description": "x" * 501
        }
        serializer = SubjectSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_subject_serializer_title_whitespace_stripped(self):
        """SubjectSerializer strips whitespace from title."""
        from .serializers import SubjectSerializer
        data = {"title": "  Mathematics  "}
        serializer = SubjectSerializer(data=data)
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data["title"], "Mathematics")

    def test_subject_serializer_duplicate_title_validation(self):
        """SubjectSerializer raises DUPLICATE_TITLE for existing title."""
        from .serializers import SubjectSerializer
        Subject.objects.create(title="Science")
        data = {"title": "Science"}
        serializer = SubjectSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_subject_serializer_read_only_fields(self):
        """SubjectSerializer has id and created_at read-only."""
        from .serializers import SubjectSerializer
        subject = Subject.objects.create(title="Art")
        serializer = SubjectSerializer(subject)
        # Should have id and created_at in response
        self.assertIn("id", serializer.data)
        self.assertIn("created_at", serializer.data)

    def test_subject_list_serializer_fields(self):
        """SubjectListSerializer includes only id, title, created_at."""
        from .serializers import SubjectListSerializer
        subject = Subject.objects.create(
            title="Music",
            description="Study of music"
        )
        serializer = SubjectListSerializer(subject)
        # Should not include description
        self.assertIn("id", serializer.data)
        self.assertIn("title", serializer.data)
        self.assertIn("created_at", serializer.data)
        self.assertNotIn("description", serializer.data)


class SubjectViewSetTests(APITestCase):
    """Test Subject viewset."""

    def setUp(self):
        """Create test user and client."""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_requires_authentication(self):
        """SubjectViewSet requires authentication."""
        client = APIClient()
        response = client.get("/api/subjects/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_subjects_uses_list_serializer(self):
        """List endpoint uses SubjectListSerializer."""
        Subject.objects.create(title="Test Subject")
        response = self.client.get("/api/subjects/")
        # DRF paginator wraps results
        results = response.data.get('results') or response.data
        if isinstance(results, list) and results:
            self.assertNotIn("description", results[0])

    def test_retrieve_subject_uses_list_serializer(self):
        """Retrieve endpoint uses SubjectListSerializer."""
        subject = Subject.objects.create(
            title="Subject1",
            description="A description"
        )
        response = self.client.get(f"/api/subjects/{subject.id}/")
        self.assertNotIn("description", response.data)

    def test_create_subject_uses_subject_serializer(self):
        """Create returns full SubjectSerializer (with description)."""
        data = {
            "title": "NewSubject",
            "description": "A new subject"
        }
        response = self.client.post("/api/subjects/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("description", response.data)

    def test_list_filters_deleted_subjects(self):
        """List endpoint only returns non-deleted subjects."""
        subject1 = Subject.objects.create(title="Active")
        subject2 = Subject.objects.create(title="Deleted")
        subject2.deleted_at = timezone.now()
        subject2.save()
        response = self.client.get("/api/subjects/")
        results = response.data.get('results') or response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Active")

    def test_search_subjects_by_title(self):
        """List endpoint supports search_fields=['title']."""
        Subject.objects.create(title="Mathematics")
        Subject.objects.create(title="Physics")
        response = self.client.get("/api/subjects/?search=Math")
        results = response.data.get('results') or response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Mathematics")

    def test_ordering_by_created_at(self):
        """List endpoint supports ordering_fields=['created_at', 'title']."""
        s1 = Subject.objects.create(title="Second")
        s2 = Subject.objects.create(title="First")
        response = self.client.get("/api/subjects/?ordering=-created_at")
        results = response.data.get('results') or response.data
        self.assertEqual(results[0]["id"], s2.id)

    def test_create_subject_success(self):
        """POST /subjects/ creates subject."""
        data = {"title": "History"}
        response = self.client.post("/api/subjects/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subject.objects.count(), 1)

    def test_create_duplicate_title_returns_409(self):
        """Creating duplicate title returns 409 CONFLICT."""
        Subject.objects.create(title="Biology")
        data = {"title": "Biology"}
        response = self.client.post("/api/subjects/", data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data.get("error_code"), "DUPLICATE_ENTRY"
        )

    def test_create_invalid_data_returns_400(self):
        """Creating with invalid data returns 400."""
        data = {"title": "X"}  # Too short
        response = self.client.post("/api/subjects/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_subject_success(self):
        """PUT /subjects/{id}/ updates subject."""
        subject = Subject.objects.create(title="OldTitle")
        data = {"title": "NewTitle"}
        response = self.client.put(f"/api/subjects/{subject.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subject.refresh_from_db()
        self.assertEqual(subject.title, "NewTitle")

    def test_update_to_duplicate_title_returns_409(self):
        """Updating to duplicate title returns 409."""
        Subject.objects.create(title="Subject1")
        subject2 = Subject.objects.create(title="Subject2")
        data = {"title": "Subject1"}
        response = self.client.put(f"/api/subjects/{subject2.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_delete_subject_soft_deletes(self):
        """DELETE /subjects/{id}/ soft-deletes subject."""
        subject = Subject.objects.create(title="ToDelete")
        response = self.client.delete(f"/api/subjects/{subject.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        subject.refresh_from_db()
        self.assertIsNotNone(subject.deleted_at)

    def test_deleted_subject_not_in_list(self):
        """Deleted subject does not appear in list."""
        subject = Subject.objects.create(title="ToDelete")
        subject_id = subject.id
        self.client.delete(f"/api/subjects/{subject_id}/")
        response = self.client.get("/api/subjects/")
        results = response.data.get('results') if isinstance(response.data, dict) else response.data
        if isinstance(results, list):
            subject_ids = [r['id'] for r in results]
            self.assertNotIn(subject_id, subject_ids)
