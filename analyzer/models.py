from django.db import models

class EngineeringBranch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, default="")
    placement_2024 = models.IntegerField(default=0)
    placement_2026 = models.IntegerField(default=0)
    salary_2024 = models.FloatField(default=0.0)
    future_trends = models.TextField(blank=True, default="")
    future_skills = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=10, default="📚")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def placement_growth(self):
        return self.placement_2026 - self.placement_2024

class Company(models.Model):
    name = models.CharField(max_length=200)
    branch = models.ForeignKey(EngineeringBranch, on_delete=models.CASCADE, related_name='companies')
    description = models.TextField(blank=True, default="")
    website = models.URLField(blank=True, default="")
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'branch']
    
    def __str__(self):
        return f"{self.name}"

class Course(models.Model):
    PLATFORM_CHOICES = [
        ('NPTEL', 'NPTEL'),
        ('Coursera', 'Coursera'),
        ('edX', 'edX'),
        ('Udemy', 'Udemy'),
    ]
    
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]
    
    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    branch = models.ForeignKey(EngineeringBranch, on_delete=models.CASCADE, related_name='courses')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    duration = models.CharField(max_length=100, default="")
    is_free = models.BooleanField(default=False)
    free_details = models.CharField(max_length=100, blank=True, default="")
    
    class Meta:
        ordering = ['branch', 'platform', 'name']
    
    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=200)
    branch = models.ForeignKey(EngineeringBranch, on_delete=models.CASCADE, related_name='projects')
    description = models.TextField(blank=True, default="")
    difficulty = models.CharField(max_length=50, choices=[
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ], default='Medium')
    
    class Meta:
        ordering = ['branch', 'name']
    
    def __str__(self):
        return self.name

class UserFeedback(models.Model):
    user_input = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user_input[:50]}..."