from rest_framework import serializers
from .models import User, Company, BudgetPool, Claim, ReceiptFile

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'company']

class BudgetPoolSerializer(serializers.ModelSerializer):
    utilization_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = BudgetPool
        fields = ['id', 'name', 'group', 'start_date', 'end_date', 'total_budget_hkd', 'remaining_hkd', 'utilization_percentage']

class ReceiptFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptFile
        fields = ['id', 'url', 'ocr_json', 'ocr_confidence']

class ClaimSerializer(serializers.ModelSerializer):
    budget_pool_name = serializers.CharField(source='budget_pool.name', read_only=True)
    receipts = ReceiptFileSerializer(many=True, read_only=True)
    rejection_reason = serializers.SerializerMethodField()
    
    class Meta:
        model = Claim
        fields = ['id', 'status', 'amount_hkd', 'merchant', 'date', 'category', 'note', 'budget_pool', 'budget_pool_name', 'created_at', 'updated_at', 'receipts', 'rejection_reason']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def get_rejection_reason(self, obj):
        if obj.status == 'rejected' or obj.status == 'returned':
            last_approval = obj.approvals.order_by('-decided_at').first()
            if last_approval:
                return last_approval.comment if last_approval.comment else "No specific reason was provided by the admin."
        return None
