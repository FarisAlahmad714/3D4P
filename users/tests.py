from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from PIL import Image
import tempfile
import os

from .models import CustomUser, MemberApplication, MemberProfile
from .forms import CustomUserCreationForm, MemberProfileForm, UserUpdateForm, ProfileUpdateForm
from .views import SignUpView
from .decorators import verified_member_required

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Test cases for the CustomUser model"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        """Test creating a basic user"""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_member)
        self.assertFalse(user.is_verified)
        self.assertTrue(user.check_password('testpassword123'))
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertFalse(user.is_member)
        self.assertFalse(user.is_verified)
    
    def test_user_str_method(self):
        """Test the string representation of user"""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')
    
    def test_user_optional_fields(self):
        """Test optional fields in user model"""
        from datetime import date
        user = CustomUser.objects.create_user(**self.user_data)
        user.bio = 'Test bio'
        user.date_of_birth = date(1990, 1, 1)
        user.is_member = True
        user.is_verified = True
        user.save()
        
        self.assertEqual(user.bio, 'Test bio')
        self.assertEqual(user.date_of_birth, date(1990, 1, 1))
        self.assertTrue(user.is_member)
        self.assertTrue(user.is_verified)
    
    def test_unique_username_constraint(self):
        """Test that usernames must be unique"""
        CustomUser.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='testuser',  # Same username
                email='different@example.com',
                password='differentpass123'
            )


class MemberApplicationModelTest(TestCase):
    """Test cases for the MemberApplication model"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a simple test image
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'test_image_content',
            content_type='image/jpeg'
        )
    
    def test_create_member_application(self):
        """Test creating a member application"""
        application = MemberApplication.objects.create(
            user=self.user,
            proof_image=self.test_image
        )
        self.assertEqual(application.user, self.user)
        self.assertFalse(application.is_approved)
        self.assertIsNotNone(application.application_date)
    
    def test_application_str_method(self):
        """Test string representation of member application"""
        application = MemberApplication.objects.create(
            user=self.user,
            proof_image=self.test_image
        )
        expected_str = f"Application for {self.user.username}"
        self.assertEqual(str(application), expected_str)
    
    def test_one_to_one_relationship(self):
        """Test that each user can have only one application"""
        MemberApplication.objects.create(
            user=self.user,
            proof_image=self.test_image
        )
        
        # Creating another application for the same user should raise an error
        with self.assertRaises(IntegrityError):
            MemberApplication.objects.create(
                user=self.user,
                proof_image=SimpleUploadedFile(
                    name='test_image2.jpg',
                    content=b'test_image_content2',
                    content_type='image/jpeg'
                )
            )
    
    def test_cascade_delete(self):
        """Test that application is deleted when user is deleted"""
        application = MemberApplication.objects.create(
            user=self.user,
            proof_image=self.test_image
        )
        application_id = application.id
        
        self.user.delete()
        
        with self.assertRaises(MemberApplication.DoesNotExist):
            MemberApplication.objects.get(id=application_id)


class MemberProfileModelTest(TestCase):
    """Test cases for the MemberProfile model"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_auto_creation(self):
        """Test that profile is automatically created when user is created"""
        # Profile should be created automatically via signal
        self.assertTrue(hasattr(self.user, 'memberprofile'))
        profile = self.user.memberprofile
        self.assertEqual(profile.user, self.user)
        self.assertFalse(profile.is_verified)
        self.assertEqual(profile.bio, '')
    
    def test_profile_str_method(self):
        """Test string representation of member profile"""
        profile = self.user.memberprofile
        self.assertEqual(str(profile), self.user.username)
    
    def test_profile_fields(self):
        """Test profile fields can be updated"""
        profile = self.user.memberprofile
        profile.bio = 'Updated bio'
        profile.is_verified = True
        profile.save()
        
        # Refresh from database
        profile.refresh_from_db()
        self.assertEqual(profile.bio, 'Updated bio')
        self.assertTrue(profile.is_verified)


class CustomUserCreationFormTest(TestCase):
    """Test cases for the CustomUserCreationForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'differentpassword456',
            'first_name': 'Test',
            'last_name': 'User'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_weak_password(self):
        """Test form with weak password"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': '123',
            'password2': '123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_duplicate_username(self):
        """Test form with existing username"""
        # Create a user first
        CustomUser.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='testpass123'
        )
        
        form_data = {
            'username': 'testuser',  # Same username
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class SignUpViewTest(TestCase):
    """Test cases for the SignUpView"""
    
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
    
    def test_signup_get(self):
        """Test GET request to signup page"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign up')
        self.assertIn('disclaimer', response.context)
    
    def test_successful_signup(self):
        """Test successful user registration"""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'disclaimer_agreed': 'true'
        }
        
        response = self.client.post(self.signup_url, data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        
        # Check user was created
        user = CustomUser.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@example.com')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('successfully' in str(m) for m in messages))
    
    def test_signup_without_disclaimer(self):
        """Test signup without agreeing to disclaimer"""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'disclaimer_agreed': 'false'  # Not agreed
        }
        
        response = self.client.post(self.signup_url, data=form_data)
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        
        # Check user was not created
        self.assertFalse(CustomUser.objects.filter(username='newuser').exists())
    
    def test_signup_with_proof_image(self):
        """Test signup with proof image creates member application"""
        # Create a simple test image
        test_image = SimpleUploadedFile(
            name='proof.jpg',
            content=b'test_image_content',
            content_type='image/jpeg'
        )
        
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'disclaimer_agreed': 'true'
        }
        files_data = {'proof_image': test_image}
        
        response = self.client.post(self.signup_url, data=form_data, files=files_data)
        self.assertEqual(response.status_code, 302)
        
        # Check member application was created
        user = CustomUser.objects.get(username='newuser')
        self.assertTrue(hasattr(user, 'memberapplication'))


class UserViewsTest(TestCase):
    """Test cases for user-related views"""
    
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_page(self):
        """Test login page loads correctly"""
        login_url = reverse('login')
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)
    
    def test_successful_login(self):
        """Test successful user login"""
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(login_url, data=login_data)
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
        # Check user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_failed_login(self):
        """Test failed login with wrong credentials"""
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(login_url, data=login_data)
        self.assertEqual(response.status_code, 200)  # Stay on login page
        
        # Check user is not logged in
        self.assertFalse('_auth_user_id' in self.client.session)
    
    def test_logout(self):
        """Test user logout"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        logout_url = reverse('logout')
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        
        # Check user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)


class VerifiedMemberDecoratorTest(TestCase):
    """Test cases for the verified_member_required decorator"""
    
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.verified_user = CustomUser.objects.create_user(
            username='verifieduser',
            email='verified@example.com',
            password='testpass123',
            is_verified=True
        )
    
    @verified_member_required
    def dummy_view(self, request):
        """Dummy view for testing decorator"""
        from django.http import HttpResponse
        return HttpResponse('Success')
    
    def test_decorator_with_verified_user(self):
        """Test decorator allows verified users"""
        self.client.login(username='verifieduser', password='testpass123')
        
        # Create a mock request
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.verified_user
        
        response = self.dummy_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_decorator_with_unverified_user(self):
        """Test decorator redirects unverified users"""
        self.client.login(username='testuser', password='testpass123')
        
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user
        
        response = self.dummy_view(request)
        self.assertEqual(response.status_code, 302)  # Should redirect


class UserIntegrationTest(TestCase):
    """Integration tests for user functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_full_user_workflow(self):
        """Test complete user registration and login workflow"""
        # Step 1: Register new user
        signup_data = {
            'username': 'integrationuser',
            'email': 'integration@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'first_name': 'Integration',
            'last_name': 'User',
            'disclaimer_agreed': 'true'
        }
        
        signup_url = reverse('signup')
        response = self.client.post(signup_url, data=signup_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify user exists
        user = CustomUser.objects.get(username='integrationuser')
        self.assertIsNotNone(user)
        
        # Verify profile was created
        self.assertTrue(hasattr(user, 'memberprofile'))
        
        # Step 2: Login with new user
        login_data = {
            'username': 'integrationuser',
            'password': 'complexpassword123'
        }
        
        login_url = reverse('login')
        response = self.client.post(login_url, data=login_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Step 3: Access protected view (if any)
        # This would test accessing user profile or other protected pages
        
        # Step 4: Logout
        logout_url = reverse('logout')
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 302)
        
        # Verify user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)


class UserFormTest(TestCase):
    """Test cases for user-related forms"""
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_update_form(self):
        """Test UserUpdateForm with valid data"""
        form_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        }
        
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        
        updated_user = form.save()
        self.assertEqual(updated_user.username, 'updateduser')
        self.assertEqual(updated_user.email, 'updated@example.com')
    
    def test_profile_update_form(self):
        """Test ProfileUpdateForm with valid data"""
        profile = self.user.memberprofile
        
        form_data = {
            'bio': 'Updated bio content'
        }
        
        form = ProfileUpdateForm(data=form_data, instance=profile)
        self.assertTrue(form.is_valid())
        
        updated_profile = form.save()
        self.assertEqual(updated_profile.bio, 'Updated bio content')


class UserModelSignalsTest(TestCase):
    """Test model signals for user-related models"""
    
    def test_profile_creation_signal(self):
        """Test that MemberProfile is created when user is created"""
        user = CustomUser.objects.create_user(
            username='signaluser',
            email='signal@example.com',
            password='testpass123'
        )
        
        # Profile should be created automatically
        self.assertTrue(hasattr(user, 'memberprofile'))
        profile = user.memberprofile
        self.assertEqual(profile.user, user)
        self.assertFalse(profile.is_verified)
    
    def test_profile_update_signal(self):
        """Test that profile is updated when user is saved"""
        user = CustomUser.objects.create_user(
            username='signaluser2',
            email='signal2@example.com',
            password='testpass123'
        )
        
        # Update user
        user.first_name = 'Updated'
        user.save()
        
        # Profile should still exist and be linked
        self.assertTrue(hasattr(user, 'memberprofile'))
        profile = user.memberprofile
        self.assertEqual(profile.user, user)


class AdminFunctionalityTest(TestCase):
    """Test cases for admin functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create regular user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create member application
        self.test_image = SimpleUploadedFile(
            name='test_proof.jpg',
            content=b'test_image_content',
            content_type='image/jpeg'
        )
        self.application = MemberApplication.objects.create(
            user=self.user,
            proof_image=self.test_image
        )
    
    def test_admin_login(self):
        """Test admin can login to admin panel"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_user_list_view(self):
        """Test admin can view user list"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/users/customuser/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_admin_application_list_view(self):
        """Test admin can view member applications"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/users/memberapplication/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_admin_approve_application_action(self):
        """Test admin can approve applications using bulk action"""
        self.client.login(username='admin', password='adminpass123')
        
        # Simulate selecting application and running approve action
        post_data = {
            'action': 'approve_applications',
            '_selected_action': [str(self.application.id)],
            'index': 0
        }
        
        response = self.client.post(
            '/admin/users/memberapplication/',
            data=post_data,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Refresh objects from database
        self.application.refresh_from_db()
        self.user.refresh_from_db()
        
        # Check application was approved
        self.assertTrue(self.application.is_approved)
        self.assertTrue(self.user.is_verified)
        self.assertTrue(self.user.is_member)
    
    def test_admin_review_applications_view(self):
        """Test custom review applications view"""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get('/admin/users/memberapplication/review-applications/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_admin_review_applications_post(self):
        """Test approving applications through custom review view"""
        self.client.login(username='admin', password='adminpass123')
        
        post_data = {
            'approve': [str(self.application.id)]
        }
        
        response = self.client.post(
            '/admin/users/memberapplication/review-applications/',
            data=post_data,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Refresh objects from database
        self.application.refresh_from_db()
        self.user.refresh_from_db()
        
        # Check application was approved
        self.assertTrue(self.application.is_approved)
        self.assertTrue(self.user.is_verified)
        self.assertTrue(self.user.is_member)
    
    def test_admin_user_filters(self):
        """Test admin user list filters work correctly"""
        self.client.login(username='admin', password='adminpass123')
        
        # Test is_member filter
        response = self.client.get('/admin/users/customuser/?is_member=1')
        self.assertEqual(response.status_code, 200)
        
        # Test is_verified filter
        response = self.client.get('/admin/users/customuser/?is_verified=1')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_application_filters(self):
        """Test admin application list filters work correctly"""
        self.client.login(username='admin', password='adminpass123')
        
        # Test is_approved filter
        response = self.client.get('/admin/users/memberapplication/?is_approved=0')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        
        response = self.client.get('/admin/users/memberapplication/?is_approved=1')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'testuser')  # Not approved yet
    
    def test_non_admin_cannot_access_admin(self):
        """Test regular users cannot access admin panel"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login


class AdminModelAdminTest(TestCase):
    """Test cases for admin model configurations"""
    
    def setUp(self):
        from django.contrib.admin.sites import AdminSite
        from .admin import CustomUserAdmin, MemberApplicationAdmin
        
        self.site = AdminSite()
        self.user_admin = CustomUserAdmin(CustomUser, self.site)
        self.app_admin = MemberApplicationAdmin(MemberApplication, self.site)
        
        # Create test data
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.test_image = SimpleUploadedFile(
            name='test_proof.jpg',
            content=b'test_image_content',
            content_type='image/jpeg'
        )
        self.application = MemberApplication.objects.create(
            user=self.user,
            proof_image=self.test_image
        )
    
    def test_user_admin_list_display(self):
        """Test CustomUserAdmin list_display configuration"""
        expected_fields = ('username', 'email', 'is_member', 'is_verified')
        self.assertEqual(self.user_admin.list_display, expected_fields)
    
    def test_user_admin_list_filter(self):
        """Test CustomUserAdmin list_filter configuration"""
        expected_filters = ('is_member', 'is_verified')
        self.assertEqual(self.user_admin.list_filter, expected_filters)
    
    def test_application_admin_list_display(self):
        """Test MemberApplicationAdmin list_display configuration"""
        expected_fields = ('user', 'application_date', 'is_approved')
        self.assertEqual(self.app_admin.list_display, expected_fields)
    
    def test_application_admin_list_filter(self):
        """Test MemberApplicationAdmin list_filter configuration"""
        expected_filters = ('is_approved',)
        self.assertEqual(self.app_admin.list_filter, expected_filters)
    
    def test_application_admin_actions(self):
        """Test MemberApplicationAdmin has approve action"""
        actions = [action.__name__ for action in self.app_admin.actions]
        self.assertIn('approve_applications', actions)
    
    def test_approve_applications_action_logic(self):
        """Test the approve_applications action logic"""
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/')
        request.user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Mock queryset
        queryset = MemberApplication.objects.filter(id=self.application.id)
        
        # Run the action
        self.app_admin.approve_applications(request, queryset)
        
        # Refresh objects
        self.application.refresh_from_db()
        self.user.refresh_from_db()
        
        # Check changes were applied
        self.assertTrue(self.application.is_approved)
        self.assertTrue(self.user.is_verified)
        self.assertTrue(self.user.is_member)


class AdminSecurityTest(TestCase):
    """Test cases for admin security"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create regular user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create staff user (no superuser privileges)
        self.staff_user = CustomUser.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
    
    def test_superuser_can_access_admin(self):
        """Test superuser can access admin panel"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_regular_user_cannot_access_admin(self):
        """Test regular user cannot access admin panel"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/admin/')
        self.assertNotEqual(response.status_code, 200)
    
    def test_staff_user_can_access_admin(self):
        """Test staff user can access admin panel"""
        self.client.login(username='staff', password='staffpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_unauthenticated_user_redirected(self):
        """Test unauthenticated user is redirected from admin"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login'))
    
    def test_admin_csrf_protection(self):
        """Test admin forms are protected by CSRF"""
        self.client.login(username='admin', password='adminpass123')
        
        # Try to post without CSRF token
        post_data = {
            'action': 'approve_applications',
            '_selected_action': ['1']
        }
        
        response = self.client.post('/admin/users/memberapplication/', data=post_data)
        # Should fail due to CSRF protection
        self.assertNotEqual(response.status_code, 200)


class AdminIntegrationTest(TestCase):
    """Integration tests for admin functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create multiple users with applications
        self.users_with_apps = []
        for i in range(3):
            user = CustomUser.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
            
            test_image = SimpleUploadedFile(
                name=f'test_proof_{i}.jpg',
                content=b'test_image_content',
                content_type='image/jpeg'
            )
            
            app = MemberApplication.objects.create(
                user=user,
                proof_image=test_image
            )
            
            self.users_with_apps.append((user, app))
    
    def test_bulk_approve_multiple_applications(self):
        """Test admin can bulk approve multiple applications"""
        self.client.login(username='admin', password='adminpass123')
        
        # Get all application IDs
        app_ids = [str(app.id) for user, app in self.users_with_apps]
        
        post_data = {
            'action': 'approve_applications',
            '_selected_action': app_ids,
            'index': 0
        }
        
        response = self.client.post(
            '/admin/users/memberapplication/',
            data=post_data,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check all applications were approved
        for user, app in self.users_with_apps:
            app.refresh_from_db()
            user.refresh_from_db()
            
            self.assertTrue(app.is_approved)
            self.assertTrue(user.is_verified)
            self.assertTrue(user.is_member)
    
    def test_admin_workflow_end_to_end(self):
        """Test complete admin workflow from application to approval"""
        self.client.login(username='admin', password='adminpass123')
        
        # Step 1: View pending applications
        response = self.client.get('/admin/users/memberapplication/?is_approved=0')
        self.assertEqual(response.status_code, 200)
        
        # Should see all 3 pending applications
        for user, app in self.users_with_apps:
            self.assertContains(response, user.username)
        
        # Step 2: Use custom review view
        response = self.client.get('/admin/users/memberapplication/review-applications/')
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Approve one application through custom view
        user, app = self.users_with_apps[0]
        post_data = {
            'approve': [str(app.id)]
        }
        
        response = self.client.post(
            '/admin/users/memberapplication/review-applications/',
            data=post_data,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check the application was approved
        app.refresh_from_db()
        user.refresh_from_db()
        
        self.assertTrue(app.is_approved)
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_member)
        
        # Step 4: Verify other applications are still pending
        for i in range(1, 3):
            user, app = self.users_with_apps[i]
            app.refresh_from_db()
            user.refresh_from_db()
            
            self.assertFalse(app.is_approved)
            self.assertFalse(user.is_verified)
            self.assertFalse(user.is_member)
        
        # Step 5: Check approved applications filter
        response = self.client.get('/admin/users/memberapplication/?is_approved=1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.users_with_apps[0][0].username)
        
        # Should not contain pending applications
        for i in range(1, 3):
            self.assertNotContains(response, self.users_with_apps[i][0].username)
