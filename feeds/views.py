from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Announcement, Post, Event, Like, Comment
from .serializers import AnnouncementSerializer, PostSerializer, EventSerializer, LikeSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from employees.models import Employee
from rest_framework.decorators import api_view, permission_classes



class FeedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser:
            posts = Post.objects.all().order_by('-created_at')
        else:
            posts = Post.objects.filter(is_approved = "True").order_by('-created_at')   
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  
        return context
    
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post_instance = serializer.save(user=request.user) 
            userdetail = Employee.objects.get(user=request.user)

            employee_name = f"{userdetail.employee_first_name} {userdetail.employee_last_name}"

            post_instance.user_name = employee_name
            if userdetail.employee_photo:
                    userimage_url = userdetail.employee_photo.url  
                    if userimage_url.startswith('/media/'):
                        userimage_url = userimage_url[7:]  
                    post_instance.user_image = userimage_url
            else:
                    post_instance.user_image = None
            post_instance.save() 

            response_data = serializer.data
            response_data['user_name'] = employee_name
            response_data['user_image'] = userimage_url

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, postid):
        try:
            post = Post.objects.get(postid=postid)  # Get the specific post
            
            # Add the user to the list of users who liked the post
            
            if request.user not in post.liked_users.all():
                
                post.liked_users.add(request.user)
                post.save()
                liked_users = post.liked_users.values_list('id', flat=True)  # Get the list of user IDs who liked the post
              
                return Response({'detail': 'Post liked', 'liked': liked_users}, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Already liked', 'liked': liked_users}, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found', 'liked': []}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, postid):
        try:
            post = Post.objects.get(postid=postid)
            
            # Remove the user from the list of users who liked the post
            if request.user in post.liked_users.all():
                post.liked_users.remove(request.user)
                post.save()
                liked_users = post.liked_users.values_list('id', flat=True)  # Get the updated list of user IDs who liked the post
                return Response({'detail': 'Like removed', 'liked': liked_users}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'detail': 'Like not found', 'liked': liked_users}, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found', 'liked': []}, status=status.HTTP_404_NOT_FOUND)


class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, postid):
        comments = Comment.objects.filter(post=postid).order_by('-id')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, postid):
        try:
            post = Post.objects.get(postid=postid)
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                comment =  serializer.save(user=request.user, post=post)
                userdetails = Employee.objects.get(user=request.user)

                employee_name = f"{userdetails.employee_first_name} {userdetails.employee_last_name}"

                comment.user_name = employee_name
                if userdetails.employee_photo:
                    userimage_url = userdetails.employee_photo.url  
                    if userimage_url.startswith('/media/'):
                        userimage_url = userimage_url[7:]  
                    comment.user_image = userimage_url
                else:
                    comment.user_image = None
                comment.save()  

                response_data = serializer.data
                response_data['user_name'] = employee_name
                response_data['user_image'] = userimage_url

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def get_serializer_context(self):
        """Ensure request context is passed to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request  # Pass request to the serializer context
        return context



class AnnouncementListView(APIView):
    
    def get(self, request):
        announcements = Announcement.objects.all().order_by('-created_at')
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)
    
    
    def post(self, request):
        serializer = AnnouncementSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            print("Announcement")
            print(user)
            # if not hasattr(user, 'employee'):
            #     return Response({'error': 'User does not have an associated department'}, status=status.HTTP_400_BAD_REQUEST)

            announcement = serializer.save(created_by=user, department=user.employee.department)  

            user_details = user.employee
            print(user_details)
            employee_name = f"{user_details.employee_first_name} {user_details.employee_last_name}"

            announcement.user_name = employee_name
            if user_details.employee_photo:
                user_image_url = user_details.employee_photo.url  
                if user_image_url.startswith('/media/'):
                    user_image_url = user_image_url[7:]  
                announcement.user_image = user_image_url
            else:
                announcement.user_image = None

            announcement.save()  

            response_data = serializer.data
            response_data['user_name'] = employee_name
            response_data['user_image'] = user_image_url if user_details.employee_photo else None
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostdeptView(APIView):
    
    def get(self, request):
        userdetails = Employee.objects.get(user=request.user)
        user_department = userdetails.departmant
        announcements = Post.objects.filter(department=user_department).order_by('-created_at')
        
        serializer = PostSerializer(announcements, many=True)
        return Response(serializer.data)
    
class AcknowledgePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(postid=post_id)
            if request.user not in post.acknowledge_users.all():
                post.increment_acknowledge(request.user)
                acknowledged_users = post.acknowledge_users.values_list('id', flat=True)
                return Response({'message': 'Acknowledged successfully', 'acknowledged_users': acknowledged_users}, status=status.HTTP_200_OK)
            else:
                acknowledged_users = post.acknowledge_users.values_list('id', flat=True)
                return Response({'message': 'Already acknowledged', 'acknowledged_users': acknowledged_users}, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        

class AcknowledgeAnnouncementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            announcement = Announcement.objects.get(id=pk)
            if request.user not in announcement.acknowledge_users.all():
                announcement.increment_acknowledge(request.user)
                acknowledged_users = announcement.acknowledge_users.values_list('id', flat=True)
                return Response({'message': 'Acknowledged successfully', 'acknowledged_users': acknowledged_users}, status=status.HTTP_200_OK)
            else:
                acknowledged_users = announcement.acknowledge_users.values_list('id', flat=True)
                return Response({'message': 'Already acknowledged', 'acknowledged_users': acknowledged_users}, status=status.HTTP_400_BAD_REQUEST)
        except Announcement.DoesNotExist:
            return Response({'error': 'Announcement not found'}, status=status.HTTP_404_NOT_FOUND)
        
    
class EventListView(APIView):
    def get(self, request):
        events = Event.objects.all().order_by('date', 'time')
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])  
@permission_classes([IsAuthenticated])    
def approve_feeds(self,pk):
    try:
        post = Post.objects.get(postid=pk)
        post.is_approved = True
        post.status = "Approved"
        post.save() 
        return Response({"message": "Post approved successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Employee.DoesNotExist:
        return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)   

@api_view(['POST'])  
@permission_classes([IsAuthenticated])    
def reject_feeds(self,pk):
    try:
        post = Post.objects.get(postid=pk)
        post.is_approved = False
        post.status = "Rejected"
        post.save() 
        return Response({"message": "Post Rejected successfully."}, status=status.HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND) 