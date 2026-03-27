from django.shortcuts import render
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import BudgetPool, Claim
from .serializers import BudgetPoolSerializer, ClaimSerializer
from .services import DocumentAIService

# Mobile API Views

class MobileHomeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        pools = BudgetPool.objects.filter(company=user.company)
        claims = Claim.objects.filter(user=user).order_by('-created_at')[:5]

        pool_data = BudgetPoolSerializer(pools, many=True).data
        claim_data = ClaimSerializer(claims, many=True).data

        return Response({
            "pools": pool_data,
            "recent_claims": claim_data,
        })


class MobileBudgetPoolsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pools = BudgetPool.objects.filter(company=request.user.company)
        pool_data = BudgetPoolSerializer(pools, many=True).data
        return Response(pool_data)


class MobileClaimsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        claims = Claim.objects.filter(user=request.user).order_by('-created_at')
        return Response(ClaimSerializer(claims, many=True).data)

    def post(self, request):
        data = request.data
        claim = Claim.objects.create(
            user=request.user,
            merchant=data.get('merchant'),
            amount_hkd=data.get('amount'),
            date=data.get('date') if data.get('date') else None,
            category=data.get('category'),
            note=data.get('note'),
            status='pending'
        )
        return Response(ClaimSerializer(claim).data, status=status.HTTP_201_CREATED)

class MobileUploadReceiptView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'receipt' not in request.FILES:
            return Response({"error": "No receipt file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['receipt']
        mime_type = file_obj.content_type
        
        # Calling the Document AI and GCS upload service
        extracted_data = DocumentAIService.extract_receipt(
            file_data=file_obj,
            mime_type=mime_type,
            original_filename=file_obj.name
        )

        # In a real app, you might save an initial 'Draft' Claim here automatically.
        return Response({
            "message": "Receipt processed successfully",
            "extraction": extracted_data
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compliance_chat_view(request):
    query = request.data.get('query', '')
    try:
        from vertexai.generative_models import GenerativeModel
        import vertexai
        vertexai.init(project="finsight-484914", location="us-central1")
        model = GenerativeModel("gemini-2.5-pro")
        prompt = f"You are a helpful AI assisting an employee with their financial policy queries. Answer this question briefly: {query}"
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"Error generating response: {str(e)}"
    
    return Response({'answer': answer}, status=status.HTTP_200_OK)
