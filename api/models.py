from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return self.username

class BudgetPool(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    total_budget_hkd = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_hkd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.remaining_hkd == 0:
            self.remaining_hkd = self.total_budget_hkd
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Claim(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    budget_pool = models.ForeignKey(BudgetPool, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_claims')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount_hkd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    merchant = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Claim #{self.id} by {self.user}"

class ReceiptFile(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='receipts')
    url = models.URLField(max_length=1024, null=True, blank=True)
    ocr_json = models.JSONField(null=True, blank=True)
    ocr_confidence = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Receipt for Claim #{self.claim_id}"

class Approval(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='decisions')
    decision = models.CharField(max_length=20)
    comment = models.TextField(null=True, blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Approval for Claim #{self.claim_id}"

class PolicyDoc(models.Model):
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    url = models.URLField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ReportTemplate(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50) # 'pptx' or 'docx'
    config_json = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name