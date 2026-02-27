from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Create your views here.
# @api_view(['POST'])
# def ocr_upload_view(request):
#     # Implementation for OCR upload
#     return Response({'message': 'Success'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def compliance_chat_view(request):
    """
    Receives user question from iOS app.
    Queries Gemini AI with injected compliance policy context.
    Returns: Compliance verdict or explanation.
    """
    # 1. Get user question: query = request.data.get('query')
    # 2. Build Prompt: "You are a compliance officer. Answer ONLY based on this policy doc: [Context]... Question: {query}"
    # 3. Call Vertex AI (Gemini) endpoint
    # 4. Return answer
    return Response({'answer': 'Based on our travel policy, this meal is claimable up to $200.'}, status=status.HTTP_200_OK)
