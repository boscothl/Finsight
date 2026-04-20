from django.shortcuts import render
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import BudgetPool, Claim, PolicyDoc
from .serializers import BudgetPoolSerializer, ClaimSerializer
from .services import DocumentAIService


def _build_compliance_prompt(user, query):
    company = user.company
    if not company:
        return (
            "You are a strict financial compliance assistant. "
            "The user has no company configured, so you must ask them to contact admin to complete setup."
            f"\n\nUser question: {query}"
        )

    policy_docs = PolicyDoc.objects.filter(company=company).order_by("id")

    combined_policy_chunks = []
    for doc in policy_docs:
        if not doc.content_text:
            continue
        combined_policy_chunks.append(
            f"[PolicyDoc: {doc.title} | version: {doc.version}]\n{doc.content_text.strip()}"
        )

    combined_policy_text = "\n\n".join(combined_policy_chunks)
    if not combined_policy_text:
        combined_policy_text = "No policy documents are available for this company."

    return f"""
You are the Finsight iOS Compliance Chatbot for company: {company.name}.

Role and strictness requirements:
- You are NOT lenient. Enforce policy exactly as written.
- Do not invent policy rules, thresholds, or approvals.
- If details are missing (amount, category, claim type, date, approver level, purpose), ask concise follow-up questions before giving final judgment.
- If policy text does not clearly cover a case, say it is "not explicitly stated" and request escalation to finance/admin.
- Provide practical next steps for compliant submission.

Response style requirements:
- Keep responses concise and actionable.
- End every answer with either:
  1) a clear compliance decision (Allowed / Not Allowed / Needs Clarification), or
  2) a short list of required follow-up questions.
- Quote or reference the relevant policy section in plain text whenever possible.

Company policy context (source of truth):
{combined_policy_text}

User question:
{query}
"""

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
        
        budget_pool_id = data.get('budget_pool_id')
        budget_pool = None
        if budget_pool_id:
            from api.models import BudgetPool
            budget_pool = BudgetPool.objects.filter(id=budget_pool_id, company=request.user.company).first()

        claim = Claim.objects.create(
            user=request.user,
            merchant=data.get('merchant'),
            amount_hkd=data.get('amount'),
            date=data.get('date') if data.get('date') else None,
            category=data.get('category'),
            note=data.get('note'),
            budget_pool=budget_pool,
            status='pending'
        )
        
        # Save receipt if url provided
        receipt_url = data.get('receipt_url')
        if receipt_url:
            from api.models import ReceiptFile
            ReceiptFile.objects.create(
                claim=claim,
                url=receipt_url,
                ocr_json=data
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
    if not query:
        return Response({'answer': 'Please enter a compliance question.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        from vertexai.generative_models import GenerativeModel
        import vertexai

        vertexai.init(project="finsight-484914", location="us-central1")
        model = GenerativeModel("gemini-2.5-pro")
        prompt = _build_compliance_prompt(request.user, query)
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"Error generating response: {str(e)}"
    
    return Response({'answer': answer}, status=status.HTTP_200_OK)
