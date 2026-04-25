from django.db import models
from django.contrib.auth.models import User

class Myevent(models.Model):
    event = models.CharField(max_length=50)
    adress = models.CharField(max_length=100)
    capacity = models.IntegerField(default=1)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    CATOGERY_CHOISES =  [('MUSIC', 'MUSIC'),
                          ('SPORTS', 'SPORTS'),
                          ('SCHOOL', 'SHOOL'),
                          ('WORKSHOP', 'WORKSHOP'),]
    catogery = models.CharField(max_length=50, choices=CATOGERY_CHOISES,  default='MUSIC')
    about = models.CharField(max_length=100)
    @property
    def remaining_capacity(self):
        total_booked = Bookevent.objects.filter(event=self).count()
        return self.capacity - total_booked

    def __str__(self):
        return self.event

    def __str__(self):
        return f"{self.event} by {self.author.username}"

class Myprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    customer_adress = models.CharField(max_length=100)
    gmail = models.EmailField(max_length=100)

    def __str__(self):
        return self.name

class Bookevent(models.Model):
    event = models.ForeignKey(Myevent, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    is_booked = models.BooleanField(default=False)
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.event} is booked by {self.customer.username}"

class Saved_event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Myevent, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.event} by {self.event.author.username}"
    
class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    event = models.ForeignKey(Myevent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    is_booked = models.BooleanField(default=True) # indicates if it's a booking notification

    def __str__(self):
        return f"{self.user.username} notification for '{self.event.event}'"
    
class Messages(models.Model):
    sender = models.ForeignKey(User, related_name='send_massages', on_delete=models.CASCADE)
    reciver = models.ForeignKey(User, related_name='recive_messages', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.sender} send messages to {self.reciver}"
    
class Follow(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{'self.followers.user'} followed by {'self.following.user'}"
    
class Like(models.Model):
    event = models.ForeignKey(Myevent, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.event} is liked by {self.user}"

