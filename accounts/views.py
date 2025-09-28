from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random

# Temporary in-memory store (use Redis or DB in production)
verification_store = {}

class SendVerificationCode(APIView):
    def post(self, request):
        method = request.data.get("method")  # 'email' or 'sms'
        destination = request.data.get("destination")  # email or phone number

        if method not in ["email", "sms"]:
            return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)

        code = str(random.randint(100000, 999999))
        verification_store[destination] = code

        # Simulate sending (replace with actual email/SMS logic)
        print(f"Sending {code} to {destination} via {method}")

        return Response({"message": f"Verification code sent to {destination}"}, status=status.HTTP_200_OK)

class VerifyCode(APIView):
    def post(self, request):
        destination = request.data.get("destination")
        code = request.data.get("code")

        stored_code = verification_store.get(destination)
        if stored_code == code:
            return Response({"verified": True}, status=status.HTTP_200_OK)
        else:
            return Response({"verified": False}, status=status.HTTP_400_BAD_REQUEST)
