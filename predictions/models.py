"""
Models for storing prediction history (optional)
"""

from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    """
    Model to store prediction history
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    
    # Input data (store as JSON for flexibility)
    input_data = models.JSONField(default=dict, help_text="Input features used for prediction")
    
    # Output
    prediction = models.CharField(max_length=255, help_text="Prediction result")
    confidence = models.FloatField(null=True, blank=True, help_text="Confidence score")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_batch = models.BooleanField(default=False, help_text="Is this from batch CSV upload?")
    batch_id = models.CharField(max_length=100, blank=True, null=True, help_text="Group ID for batch predictions")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Predictions'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['batch_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.prediction} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_confidence_percentage(self):
        """Return confidence as percentage string"""
        if self.confidence:
            return f"{self.confidence:.2f}%"
        return "N/A"


class PredictionFile(models.Model):
    """
    Model to store uploaded CSV files for batch predictions
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prediction_files')
    
    # File info
    file = models.FileField(upload_to='prediction_uploads/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    
    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Results
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.filename}"
    
    def progress_percentage(self):
        """Calculate processing progress"""
        if self.total_records == 0:
            return 0
        return (self.processed_records / self.total_records) * 100

class UserProfile(models.Model):
    keycloak_sub = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # App-specific fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    soil_type = models.CharField(max_length=100, blank=True, null=True)
    farm_size = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username or self.email or self.keycloak_sub